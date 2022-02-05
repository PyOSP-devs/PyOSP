# -*- coding: utf-8 -*-

import pytest
import os, sys
import pyosp
import numpy as np
import pickle

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
dat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../datasets/")


class TestPost:
    def test_outPolygon(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        polygon = orig.out_polygon(start=coords[1], end=coords[0])
        px, py = polygon.exterior.xy
        assert 108.44225 == pytest.approx(px[0], 0.001)
        assert 108.44225 == pytest.approx(px[-1], 0.001)
        assert 28.5506 == pytest.approx(py[0], 0.001)
        assert 28.5506 == pytest.approx(py[-1], 0.001)

    def test_outPolyline(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        polylines = orig.out_polylines(start=coords[1], end=coords[0])
        lineBounds = polylines.bounds
        assert 72.595 == pytest.approx(lineBounds[0], 0.001)
        assert 134.606 == pytest.approx(lineBounds[3], 0.001)

    def test_profile_plot(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        orig = orig_homo()
        orig.profile_plot(
            start=0, end=100, color="maroon", points=start_end, s=5, marker="s"
        )
        assert True

    def test_density_scatter(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        orig.density_scatter(bins=20, start=coords[1], end=coords[0], cmap="jet", s=1)
        assert True

    def test_slice_plot(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        orig.slice_plot(loc=coords[1])
        assert True

    def test_slice_hist(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        orig.slice_hist(loc=coords[1], bins=20)
        assert True

    def test_cross_dat(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        data_path = os.path.join(dat, "cross_data.txt")
        data_valid = pickle.load(open(data_path, "rb"))
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        cross_dat = orig.cross_dat(start=coords[1], end=coords[0])
        assert all(
            [a == b for a, b in zip(cross_dat["distance"], data_valid["distance"])]
        )
        # assert all(
        #     [
        #         a == b
        #         for a, b in zip(
        #             [np.nanmean(p) for p in cross_dat["cross_matrix"]],
        #             [np.nanmean(p) for p in data_valid["cross_matrix"]],
        #         )
        #     ]
        # )

    def test_cross_plot(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        orig = orig_homo()
        orig.cross_plot(color="maroon", points=start_end)
        assert True

    def test_post_tpi(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        data_path = os.path.join(dat, "tpi_valid.txt")
        data_valid = pickle.load(open(data_path, "rb"))
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        post_dat = orig.post_tpi(
            radius=50,
            min_val=0,
            max_val=100,
            start=coords[1],
            end=coords[0],
            cross=True,
        )
        mean_valid = np.nanmean(np.hstack(data_valid[1][50]))
        mean_post = np.nanmean(np.hstack(post_dat[1][50]))
        assert all([a == b for a, b in zip(post_dat[0], data_valid[0])])
        assert 0 == pytest.approx(mean_valid-mean_post, 5.)

    def test_post_slope(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        data_path = os.path.join(dat, "slope_valid.txt")
        data_valid = pickle.load(open(data_path, "rb"))
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        post_dat = orig.post_slope(
            min_val=2, max_val=10, start=coords[1], end=coords[0], cross=True
        )
        mean_valid = np.nanmean(np.hstack(data_valid[1][50]))
        mean_post = np.nanmean(np.hstack(post_dat[1][50]))
        assert all([a == b for a, b in zip(post_dat[0], data_valid[0])])
        assert mean_valid == mean_post

    def test_post_elev(self, orig_homo):
        start_end = os.path.join(dat, "homo_start_end.shp")
        data_path = os.path.join(dat, "elev_valid.txt")
        data_valid = pickle.load(open(data_path, "rb"))
        coords = pyosp.point_coords(start_end)
        orig = orig_homo()
        post_dat = orig.post_elev(
            min_val=5, max_val=20, start=coords[1], end=coords[0], cross=True
        )
        mean_valid = np.nanmean(np.hstack(data_valid[1][50]))
        mean_post = np.nanmean(np.hstack(post_dat[1][50]))
        assert all([a == b for a, b in zip(post_dat[0], data_valid[0])])
        assert mean_valid == mean_post
