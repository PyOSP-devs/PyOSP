# -*- coding: utf-8 -*-

import numpy as np
import gdal
import sys
from ..util import pairwise, progressBar
from .._slope import Geo_slope
from .base_curv import Base_curv

class Slope_curv(Base_curv):
    def __init__(self, line, raster, width,
                 min_slope=0., max_slope=90.,
                 line_stepsize=None, cross_stepsize=None):
        self.min_slope = min_slope
        self.max_slope = max_slope
        self.cell_size = gdal.Open(raster).GetGeoTransform()[1]
        
        super(Slope_curv,self).__init__(line, raster, width,
                                        line_stepsize, cross_stepsize)
        
    def __repr__(self):
        return("{}".format(self.__class__.__name__))
        
    def _transect_lines(self):
        lines = []
        num = len(self.line_p)
        
        for p1, p2 in pairwise(self.line_p):
            if p2 == self.line_p[-1]:
                line_left_1 = self._swath_left(p1,p2)
                line_right_1 = self._swath_right(p1,p2)
                line_1 = line_left_1 + line_right_1
                
                line_left_2 = self._swath_left(p1,p2,endPoint=True)
                line_right_2 = self._swath_right(p1,p2,endPoint=True)
                line_2 = line_left_2 + line_right_2
                
                lines.append(line_1)
                lines.append(line_2)
                                
                current = self.line_p.index(p2) + 1 # processed two points at last step
                progressBar(current, num)
            else:
                line_left = self._swath_left(p1,p2)
                line_right = self._swath_right(p1,p2)
                line = line_left + line_right
                
                lines.append(line)
                
                current = self.line_p.index(p2)
                progressBar(current, num)
                
        return lines
            
    def _swath_left(self, p1, p2, endPoint=False):
        # if touch the end point, using same slope for both last two points
        if endPoint:
            p_m = p2
        else:
            p_m = p1
        
        transect_temp = [p_m]
        
        # nPoints = int(self.width // self.cross_stepsize)
        slope = -(p2[0]-p1[0])/(p2[1]-p1[1])
        for i in range(1,sys.maxsize,1):
            dx = np.sqrt((self.cross_stepsize*i)**2 / (slope**2+1))
            dy = dx * abs(slope)
            
            if slope >= 0 and p2[0] < p1[0] and p2[1] >= p1[1]:
                p_left = [p_m[0]-dx, p_m[1]-dy]
            elif slope >= 0 and p2[0] >= p1[0] and p2[1] < p1[1]:
                p_left = [p_m[0]+dx, p_m[1]+dy]
            elif slope < 0 and p2[0] < p1[0] and p2[1] < p1[1]:
                p_left = [p_m[0]+dx, p_m[1]-dy]
            elif slope < 0 and p2[0] >= p1[0] and p2[1] >= p1[1]:
                p_left = [p_m[0]-dx, p_m[1]+dy]
            
            # discard point out of bounds
            if not (
            (self.rasterXmin < p_left[0] < self.rasterXmax) and 
            (self.rasterYmin < p_left[1] < self.rasterYmax)
            ):
                break
            
            # break if maximum width reached
            if self.width is not None:
                hw = np.sqrt(dx**2 + dy**2)
                if hw >= self.width/2:
                    break
            
            p_slope = Geo_slope(p_left, self.raster, self.cell_size).value
 
            if not self.min_slope <= p_slope <= self.max_slope:
                break
            
            transect_temp.insert(0,p_left)
            
        return transect_temp
    
    def _swath_right(self, p1, p2, endPoint=False):
        # if touch the end point, using same slope for both last two points
        if endPoint:
            p_m = p2
        else:
            p_m = p1
        
        transect_temp = []
        
        # nPoints = int(self.width // self.cross_stepsize)
        slope = -(p2[0]-p1[0])/(p2[1]-p1[1])
        for i in range(1,sys.maxsize,1):
            dx = np.sqrt((self.cross_stepsize*i)**2 / (slope**2+1))
            dy = dx * abs(slope)
            
            if slope >= 0 and p2[0] < p1[0] and p2[1] >= p1[1]:
                p_right = [p_m[0]+dx, p_m[1]+dy]
            elif slope >= 0 and p2[0] >= p1[0] and p2[1] < p1[1]:
                p_right = [p_m[0]-dx, p_m[1]-dy]
            elif slope < 0 and p2[0] < p1[0] and p2[1] < p1[1]:
                p_right = [p_m[0]-dx, p_m[1]+dy]
            elif slope < 0 and p2[0] >= p1[0] and p2[1] >= p1[1]:
                p_right = [p_m[0]+dx, p_m[1]-dy]
            
            # discard point out of bounds
            if not (
            (self.rasterXmin < p_right[0] < self.rasterXmax) and 
            (self.rasterYmin < p_right[1] < self.rasterYmax)
            ):
                break
            
            if self.width is not None:
                hw = np.sqrt(dx**2 + dy**2)
                if hw >= self.width/2:
                    break
            
            p_slope = Geo_slope(p_right, self.raster, self.cell_size).value
            
            if not self.min_slope <= p_slope <=self.max_slope:
                break
            
            transect_temp.append(p_right)
            
        return transect_temp
        
        
        
        
