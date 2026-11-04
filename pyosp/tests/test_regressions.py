# -*- coding: utf-8 -*-
"""Regression tests for bugs found in the 2026 code review.

All tests use small synthetic rasters so the expected values can be
computed independently.
"""

import contextlib
import io

import numpy as np
import pytest
from osgeo import gdal, ogr

import pyosp

NODATA = -9999.0


def _raster(path, arr, nodata=None, gt=(0.0, 1.0, 0.0, 100.0, 0.0, -1.0)):
    ds = gdal.GetDriverByName("GTiff").Create(
        str(path), arr.shape[1], arr.shape[0], 1, gdal.GDT_Float32
    )
    ds.SetGeoTransform(gt)
    band = ds.GetRasterBand(1)
    band.WriteArray(arr.astype("float32"))
    if nodata is not None:
        band.SetNoDataValue(nodata)
    ds = None
    return str(path)


def _shape(path, geom_type, coords):
    ds = ogr.GetDriverByName("ESRI Shapefile").CreateDataSource(str(path))
    lyr = ds.CreateLayer("", None, geom_type)
    feat = ogr.Feature(lyr.GetLayerDefn())
    geom = ogr.Geometry(geom_type)
    for x, y in coords:
        geom.AddPoint_2D(x, y)
    feat.SetGeometry(geom)
    lyr.CreateFeature(feat)
    ds = None
    return str(path)


def _quiet(fn, *args, **kwargs):
    """Call fn without the progress bar output."""
    with contextlib.redirect_stdout(io.StringIO()):
        return fn(*args, **kwargs)


@pytest.fixture
def ramp(tmp_path):
    """100 x 100 raster, 1 m cells, z = column + 10, NoData in top-left 5x5."""
    arr = np.tile(np.arange(100, dtype=float), (100, 1)) + 10
    arr[:5, :5] = NODATA
    return _raster(tmp_path / "ramp.tif", arr, nodata=NODATA)


@pytest.fixture
def noisy(tmp_path):
    """60 x 60 random raster without NoData."""
    rng = np.random.default_rng(0)
    return _raster(tmp_path / "noisy.tif", rng.normal(100, 5, (60, 60)))


# --------------------------------------------------------------------------
# curvilinear swath direction


CURV_CASES = [
    (pyosp.Orig_curv, {}),
    (pyosp.Elev_curv, {}),
    (pyosp.Slope_curv, {}),
    (pyosp.Tpi_curv, {"tpi_radius": 3}),
]
DIRECTIONS = {
    "north": [(50, 30), (50, 70)],
    "south": [(50, 70), (50, 30)],
    "east": [(30, 50), (70, 50)],
    "west": [(70, 50), (30, 50)],
}


@pytest.mark.parametrize("direction", sorted(DIRECTIONS))
@pytest.mark.parametrize("cls,kwargs", CURV_CASES, ids=lambda c: getattr(c, "__name__", ""))
def test_axis_aligned_baselines(tmp_path, ramp, cls, kwargs, direction):
    """East-west and due-north baselines used to raise
    ZeroDivisionError / UnboundLocalError."""
    coords = DIRECTIONS[direction]
    line = _shape(tmp_path / "line.shp", ogr.wkbLineString, coords)
    sp = _quiet(cls, line, ramp, width=20, **kwargs)

    assert len(sp.lines) == len(sp.distance)
    (x0, y0), (x1, y1) = coords
    dx, dy = x1 - x0, y1 - y0
    # Orig_curv keeps the point at exactly width/2, the others stop before it
    n_side = 10 if cls is pyosp.Orig_curv else 9
    for transect in sp.lines:
        assert len(transect) == 2 * n_side + 1
        base = next(p for p in transect if isinstance(p, tuple))
        left = transect[0]
        # left end of the transect is on the left of the travel direction
        cross = dx * (left[1] - base[1]) - dy * (left[0] - base[0])
        assert cross > 0


# --------------------------------------------------------------------------
# start / end selection


@pytest.fixture
def diag(tmp_path, ramp):
    line = _shape(tmp_path / "diag.shp", ogr.wkbLineString, [(20, 20), (80, 80)])
    return _quiet(pyosp.Orig_curv, line, ramp, width=10)


def test_segment_mixed_inputs(diag):
    """end was checked with isinstance(start, ...), so these raised."""
    idx20 = int(np.abs(diag.distance - 20.0).argmin())
    assert diag._segment(None, 20.0) == (None, idx20 + 1)
    assert diag._segment(5.0, diag.line_p[30]) == (
        int(np.abs(diag.distance - 5.0).argmin()),
        31,
    )
    assert diag._segment(np.int64(5), np.float64(20.0))[1] == idx20 + 1
    assert diag.profile_plot(end=20.0) is not None
    assert diag.slice_plot(np.int64(10)) is not None


def test_segment_includes_end(diag):
    """The transect nearest `end` used to be dropped."""
    s, e = diag._segment(0.0, diag.distance[-1])
    assert len(diag.lines[s:e]) == len(diag.lines)


# --------------------------------------------------------------------------
# sampling outside the raster and NoData


def test_point_elevation_outside_and_nodata(ramp):
    ds = gdal.Open(ramp)
    assert np.isnan(pyosp.Point_elevation((-1000, 1000), ds).value[0, 0])
    assert np.isnan(pyosp.Point_elevation((150, 50), ds).value[0, 0])
    assert np.isnan(pyosp.Point_elevation((2.5, 97.5), ds).value[0, 0])  # NoData
    assert pyosp.Point_elevation((40.5, 50.5), ds).value[0, 0] == 50.0


def test_float32_max_nodata(tmp_path):
    """ArcGIS-style NoData (-3.4e38) must match after the float32 -> float cast."""
    arr = np.ones((10, 10))
    nd = -3.4028230607370965e38
    arr[0, 0] = nd
    ras = _raster(tmp_path / "f32.tif", arr, nodata=nd, gt=(0, 1, 0, 10, 0, -1))
    assert np.isnan(pyosp.Point_elevation((0.5, 9.5), gdal.Open(ras)).value[0, 0])


def test_radius_beyond_raster(tmp_path, ramp):
    center = _shape(tmp_path / "c.shp", ogr.wkbPoint, [(50, 50)])
    cir = _quiet(pyosp.Orig_cir, center, ramp, radius=200)
    pts = np.array([p for line in cir.lines for p in line])
    assert pts[:, 0].min() >= 0 and pts[:, 0].max() < 100
    assert pts[:, 1].min() > 0 and pts[:, 1].max() <= 100


def test_baseline_starting_outside_raster(tmp_path, ramp):
    line = _shape(tmp_path / "out.shp", ogr.wkbLineString, [(-30, -30), (50, 50)])
    sp = _quiet(pyosp.Elev_curv, line, ramp, width=10)
    assert any(sp.lines) and not all(sp.lines)
    assert not np.isnan(np.hstack([d for d in sp.dat if d])).any()


def test_nodata_not_in_swath_data(tmp_path, ramp):
    line = _shape(tmp_path / "corner.shp", ogr.wkbLineString, [(1, 99), (1, 60)])
    for cls in (pyosp.Orig_curv, pyosp.Elev_curv):
        sp = _quiet(cls, line, ramp, width=4)
        vals = np.hstack([d for d in sp.dat if d])
        assert NODATA not in vals


# --------------------------------------------------------------------------
# TPI and slope


def test_tpi_matches_brute_force(noisy):
    ds = gdal.Open(noisy)
    arr = ds.ReadAsArray().astype(float)
    for row, col in [(30, 30), (0, 0), (59, 10), (2, 57)]:
        # raster origin is (0, 100) with 1 m cells; p is the cell centre
        p = (col + 0.5, 100.0 - row - 0.5)
        r = 4
        win = arr[max(row - r, 0) : row + r + 1, max(col - r, 0) : col + r + 1]
        expected = arr[row, col] - (win.sum() - arr[row, col]) / (win.size - 1)
        got = pyosp.Tpi(p, ds, r).value
        assert float(got[0]) == pytest.approx(expected)


def test_tpi_ignores_nodata(ramp):
    ds = gdal.Open(ramp)
    # window of radius 4 around cell (row 6, col 6) overlaps the NoData block
    arr = ds.ReadAsArray().astype(float)
    win = arr[2:11, 2:11]
    valid = win[(win != NODATA)]
    expected = arr[6, 6] - (valid.sum() - arr[6, 6]) / (valid.size - 1)
    assert float(pyosp.Tpi((6.5, 93.5), ds, 4).value[0]) == pytest.approx(expected)


def _old_slope(arr, row, col, cell):
    """The previous implementation: pad the whole raster, take 3x3 window."""
    w = np.pad(arr, (1,), "edge")[row : row + 3, col : col + 3]
    rise = ((w[0, 2] + 2 * w[1, 2] + w[2, 2]) - (w[0, 0] + 2 * w[1, 0] + w[2, 0])) / (
        8 * cell
    )
    run = ((w[2, 0] + 2 * w[2, 1] + w[2, 2]) - (w[0, 0] + 2 * w[0, 1] + w[0, 2])) / (
        8 * cell
    )
    return np.degrees(np.arctan(np.hypot(rise, run)))


def test_slope_window_matches_full_raster(noisy):
    ds = gdal.Open(noisy)
    arr = ds.ReadAsArray().astype(float)
    for row, col in [(30, 30), (0, 0), (0, 30), (59, 59), (30, 59), (59, 0)]:
        p = (col + 0.5, 100.0 - row - 0.5)
        assert pyosp.Geo_slope(p, ds, 1.0).value == pytest.approx(
            _old_slope(arr, row, col, 1.0)
        )
    assert np.isnan(pyosp.Geo_slope((-5, 50), ds, 1.0).value)


def test_slope_on_ramp(ramp):
    # z rises 1 m per 1 m cell -> 45 degrees
    assert pyosp.Geo_slope((50.5, 50.5), gdal.Open(ramp), 1.0).value == pytest.approx(45)


# --------------------------------------------------------------------------
# circular swath


@pytest.fixture
def center(tmp_path):
    return _shape(tmp_path / "center.shp", ogr.wkbPoint, [(50.5, 49.5)])


def test_full_circle_has_no_duplicate_ray(ramp, center):
    cir = _quiet(pyosp.Orig_cir, center, ramp, radius=20)
    assert len(cir.lines) == 360
    assert cir.slice_polyline(360).equals(cir.slice_polyline(0))


def test_partial_sector_keeps_end_ray(ramp, center):
    cir = _quiet(pyosp.Orig_cir, center, ramp, radius=20, ng_start=0, ng_end=300)
    assert len(cir.lines) == 301


def test_cir_profile_x_axis(ramp, center):
    cir = _quiet(pyosp.Orig_cir, center, ramp, radius=20)
    x = cir.profile_plot().lines[0].get_xdata()
    assert np.allclose(np.diff(x), cir.radial_stepsize)


def test_elev_cir_keeps_ray_equal_to_threshold(tmp_path, center):
    """A ray whose values beyond the rim equal min_elev was silently dropped."""
    rows, cols = np.mgrid[0:100, 0:100]
    r = np.hypot(cols + 0.5 - 50.5, (100 - rows - 0.5) - 49.5)
    z = np.where(r <= 20, 10 + r, np.where(r < 25, 30 - 5 * (r - 20), 5.0))
    ras = _raster(tmp_path / "rim.tif", z)
    cir = _quiet(pyosp.Elev_cir, center, ras, radius=40, min_elev=5)
    assert len(cir.lines) == 360
