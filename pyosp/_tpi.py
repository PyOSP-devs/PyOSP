# -*- coding: utf-8 -*-

import numpy as np

class Tpi():
    def __init__(self, point_coord, raster, radius):
        """Calculate the TPI value of the point

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
        
    def point_position(self):
        " Define the point position on the raster"
        x = int((self.p[0] - self.geoTransform[0]) / self.geoTransform[1])
        y = int((self.geoTransform[3] - self.p[1]) / -self.geoTransform[5])
        return y, x
    
    def avg_window(self):
        "Calculate the average raster value within the window, exclude the central point."
        py, px = self.point_position()
        xmin = max(0, px-self.radiusInPixel)
        xmax = min(self.cols, px+self.radiusInPixel+1)
        ymin = max(0, py-self.radiusInPixel)
        ymax = min(self.rows, py+self.radiusInPixel+1)
        arr = self.raster.ReadAsArray(xoff=xmin, yoff=ymin, xsize=xmax-xmin, ysize=ymax-ymin)
        # Treat small values as no data
        arr[arr < -1e20] = np.nan
        avg = (np.nansum(arr)-self.point_value()) / (np.sum(~np.isnan(arr))-1)
        return avg 
    
    def point_value(self):
        py, px =self.point_position()
        return self.raster.ReadAsArray(xoff=px, yoff=py, xsize=1, ysize=1)[0]
    
    @property
    def value(self):
        return self.point_value() - self.avg_window() 