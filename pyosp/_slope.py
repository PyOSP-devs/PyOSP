# -*- coding: utf-8 -*-

import numpy as np

class Geo_slope():
    def __init__(self, point, raster, cell_size):
        self.p = point
        self.raster = raster
        self.geoTransform = self.raster.GetGeoTransform()
        self.cell_size = cell_size
        
    def point_position(self):
        x = int((self.p[0] - self.geoTransform[0]) / self.geoTransform[1])
        y = int((self.geoTransform[3] - self.p[1]) / -self.geoTransform[5])
        return y, x
    
    def raster_window(self):
        py, px = self.point_position()
        rasterMatrix = self.raster.ReadAsArray()
        
        #pad to the edge
        rasterPad = np.pad(rasterMatrix, (1,), 'edge')   
                
        return rasterPad[py:py+3, px:px+3]
    
    @property
    def value(self):
        window = self.raster_window()
        
        rise = ((window[0,2] + 2*window[1,2] + window[2,2]) -
                (window[0,0] + 2*window[1,0] + window[2,0])) / \
                (8 * self.cell_size)
        run =  ((window[2,0] + 2*window[2,1] + window[2,2]) -
                (window[0,0] + 2*window[0,1] + window[0,2])) / \
                (8 * self.cell_size)
        dist = np.sqrt(np.square(rise) + np.square(run))
        
        return np.arctan(dist)*180 / np.pi
    
