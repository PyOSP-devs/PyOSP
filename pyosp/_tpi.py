# -*- coding: utf-8 -*-

import numpy as np

class Tpi():
    def __init__(self, point_coord, raster, radius=None):
        self.p = point_coord
        self.raster = raster
        self.geoTransform = self.raster.GetGeoTransform()
        self.radius = int(radius / self.geoTransform[1])
        
        # change nodata to nan, assuming a small value was given 
        self.rasterMatrix = self.raster.ReadAsArray()
        self.rasterMatrix[self.rasterMatrix < -1e10] = np.nan
        
    def point_position(self):
        x = int((self.p[0] - self.geoTransform[0]) / self.geoTransform[1])
        y = int((self.geoTransform[3] - self.p[1]) / -self.geoTransform[5])
        return y, x
    
    def raster_window(self):
        py, px = self.point_position()
        
        #pad nan to range out of raster
        rasterPad = np.pad(self.rasterMatrix, (self.radius+1,), 
                           mode='constant', constant_values=(np.nan,))  
                
        return rasterPad[py:(py+2*self.radius+1), 
                         px:(px+2*self.radius+1)]
    
    def point_value(self):
        return self.rasterMatrix[self.point_position()]
    
    @property
    def index(self):
        outer = self.window * self.raster_window()
        inner = self.point_value()
        return inner - (np.nansum(outer)/np.count_nonzero(~np.isnan(outer)))
    
    @property
    def window(self):
        win = np.ones((2*self.radius+1, 2*self.radius+1))
        r_y, r_x = win.shape[0]//2, win.shape[1]//2
        win[r_y, r_x] = 0    # remove the central cell
        return win
    