# -*- coding: utf-8 -*-

import math

import numpy as np


def _pixel_index(point, geoTransform):
    """Return the (col, row) of the raster cell containing ``point``.

    Uses floor so that points left of / above the raster origin map to
    negative indices instead of being truncated into the first row/column.
    """
    col = math.floor((point[0] - geoTransform[0]) / geoTransform[1])
    row = math.floor((geoTransform[3] - point[1]) / -geoTransform[5])
    return col, row


def _read_cell(raster, col, row):
    """Read a single cell as float, or NaN if outside the raster or NoData."""
    if not (0 <= col < raster.RasterXSize and 0 <= row < raster.RasterYSize):
        return np.nan
    band = raster.GetRasterBand(1)
    val = band.ReadAsArray(col, row, 1, 1).astype(float)[0, 0]
    nodata = band.GetNoDataValue()
    if nodata is not None and (val == nodata or np.isnan(val)):
        return np.nan
    return val


class Point_elevation:
    """Get point elevation by given raster.

    Points outside the raster or on NoData cells return NaN.

    :param point: point coordinates
    :type point: array-like
    :param raster: GeoRaster read by GDAL
    :type raster: GDAL dataset
    """

    def __init__(self, point, raster):
        self.p = point
        self.raster = raster
        self.geoTransform = self.raster.GetGeoTransform()

    def point_position(self):
        return _pixel_index(self.p, self.geoTransform)

    @property
    def value(self):
        px, py = self.point_position()
        return np.array([[_read_cell(self.raster, px, py)]])
