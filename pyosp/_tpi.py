# -*- coding: utf-8 -*-

import numpy as np

from ._elevation import _pixel_index

__all__ = ["Tpi"]


class Tpi:
    def __init__(self, point_coord, raster, radius):
        """Calculate the TPI value of the point.

        TPI is the point value minus the mean of the other valid cells in a
        square window of half-width ``radius`` around it. NoData cells are
        excluded. Points outside the raster or on NoData return NaN.

        :param point_coord: point coodinates
        :type point_coord: array-like
        :param raster: GeoRaster read by GDAL
        :type raster: GDAL dataset
        :param radius: radius of TPI window
        :type radius: float
        """
        self.p = point_coord
        self.raster = raster
        self.cols = raster.RasterXSize
        self.rows = raster.RasterYSize
        self.geoTransform = raster.GetGeoTransform()
        self.radiusInPixel = int(radius / self.geoTransform[1])
        self.band = raster.GetRasterBand(1)
        self.nodata = self.band.GetNoDataValue()

    def point_position(self):
        " Define the point position on the raster"
        x, y = _pixel_index(self.p, self.geoTransform)
        return y, x

    def _inside(self):
        py, px = self.point_position()
        return 0 <= px < self.cols and 0 <= py < self.rows

    def _mask_nodata(self, arr):
        arr = arr.astype(float)
        if self.nodata is not None:
            arr[arr == self.nodata] = np.nan
        return arr

    def avg_window(self):
        "Calculate the average raster value within the window, exclude the central point."
        if not self._inside():
            return np.nan
        py, px = self.point_position()
        xmin = max(0, px - self.radiusInPixel)
        xmax = min(self.cols, px + self.radiusInPixel + 1)
        ymin = max(0, py - self.radiusInPixel)
        ymax = min(self.rows, py + self.radiusInPixel + 1)
        arr = self._mask_nodata(
            self.band.ReadAsArray(
                xoff=xmin, yoff=ymin, win_xsize=xmax - xmin, win_ysize=ymax - ymin
            )
        )
        # exclude the central cell
        arr[py - ymin, px - xmin] = np.nan
        n = np.sum(~np.isnan(arr))
        if n == 0:
            return np.nan
        return np.nansum(arr) / n

    def point_value(self):
        if not self._inside():
            return np.array([np.nan])
        py, px = self.point_position()
        return self._mask_nodata(
            self.band.ReadAsArray(xoff=px, yoff=py, win_xsize=1, win_ysize=1)[0]
        )

    @property
    def value(self):
        return self.point_value() - self.avg_window()
