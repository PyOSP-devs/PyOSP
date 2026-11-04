# -*- coding: utf-8 -*-

import numpy as np

from ._elevation import _pixel_index

__all__ = ["Geo_slope"]


class Geo_slope:
    def __init__(self, point, raster, cell_size):
        """Return a geo-slope value of the point.

        Points outside the raster, or whose 3x3 window contains NoData,
        return NaN.

        :param point: point coordinates
        :type point: array-like
        :param raster: GeoRaster read by GDAL
        :type raster: GDAL dataset
        :param cell_size: cell-size for slope calculation
        :type cell_size: float
        """
        self.p = point
        self.raster = raster
        self.geoTransform = self.raster.GetGeoTransform()
        self.cell_size = cell_size

    def point_position(self):
        x, y = _pixel_index(self.p, self.geoTransform)
        return y, x

    def raster_window(self):
        """Return the 3x3 window centred on the point.

        Only the window is read from disk. Cells beyond the raster edge are
        filled with the nearest edge value, as before.
        """
        py, px = self.point_position()
        cols, rows = self.raster.RasterXSize, self.raster.RasterYSize
        if not (0 <= px < cols and 0 <= py < rows):
            return None

        xmin, xmax = max(px - 1, 0), min(px + 2, cols)
        ymin, ymax = max(py - 1, 0), min(py + 2, rows)
        band = self.raster.GetRasterBand(1)
        window = band.ReadAsArray(xmin, ymin, xmax - xmin, ymax - ymin).astype(float)

        nodata = band.GetNoDataValue()
        if nodata is not None:
            window[window == nodata] = np.nan

        pad = (
            (ymin - (py - 1), (py + 2) - ymax),
            (xmin - (px - 1), (px + 2) - xmax),
        )
        return np.pad(window, pad, "edge")

    @property
    def value(self):
        window = self.raster_window()
        if window is None:
            return np.nan

        rise = (
            (window[0, 2] + 2 * window[1, 2] + window[2, 2])
            - (window[0, 0] + 2 * window[1, 0] + window[2, 0])
        ) / (8 * self.cell_size)
        run = (
            (window[2, 0] + 2 * window[2, 1] + window[2, 2])
            - (window[0, 0] + 2 * window[0, 1] + window[0, 2])
        ) / (8 * self.cell_size)
        dist = np.sqrt(np.square(rise) + np.square(run))

        return np.arctan(dist) * 180 / np.pi
