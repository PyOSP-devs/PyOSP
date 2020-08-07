# -*- coding: utf-8 -*-

# import gdal
# import ogr
# from shapely.geometry import Polygon, MultiLineString
import numpy as np
# import matplotlib.pyplot as plt
# import matplotlib.patches as mpatches
# import itertools
from .util import pairwise
from .tpi import Tpi
from .base import SwathBase

class SwathCurvilinear(SwathBase):
    def __init__(self, line, raster, radius, tpi,
                 line_size=None, cross_size=None):
        self.radius = radius 
        # tpi threshold
        self.tpi = tpi
        
        super(SwathRiver,self).__init__(line, raster, line_size, cross_size)

    def _transect_lines(self):
        lines = []
        j=0
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
                
                j += 2
                print("Finished {} points".format(j))
            else:
                line_left = self._swath_left(p1,p2)
                line_right = self._swath_right(p1,p2)
                line = line_left + line_right
                
                lines.append(line)
                
                j += 1
                print("Finished {} points".format(j))
                
        return lines
    
    def _swath_left(self, p1, p2, endPoint=False):
        # if touch the end point, using same slope for both last two points
        if endPoint:
            p_m = p2
        else:
            p_m = p1
        
        transect_temp = [p_m]
        slope = -(p2[0]-p1[0])/(p2[1]-p1[1])
        for i in range(1,int(1e6),1):
            dx = np.sqrt(self.cross_size**2 / (slope**2+1)) * i
            dy = dx * slope
            p_left = [p_m[0]-dx, p_m[1]-dy]
            
            # discard point out of bounds
            if not (
            (self.rasterXmin <= p_left[0] <= self.rasterXmax) and 
            (self.rasterYmin <= p_left[1] <= self.rasterYmax)
            ):
                break
            
            p_index = Tpi(p_left, self.raster, self.radius).index
            
            if p_index < self.tpi:
                transect_temp.insert(0,p_left)
            else:
                break
            
        return transect_temp
    
    def _swath_right(self, p1, p2, endPoint=False):
        # if touch the end point, using same slope for both last two points
        if endPoint:
            p_m = p2
        else:
            p_m = p1
        
        transect_temp = [p_m]
        slope = -(p2[0]-p1[0])/(p2[1]-p1[1])
        for i in range(1,int(1e6),1):
            dx = np.sqrt(self.cross_size**2 / (slope**2+1)) * i
            dy = dx * slope
            p_right = [p_m[0]+dx, p_m[1]+dy]
            
            # discard point out of bounds
            if not (
            (self.rasterXmin <= p_right[0] <= self.rasterXmax) and 
            (self.rasterYmin <= p_right[1] <= self.rasterYmax)
            ):
                break

            p_index = Tpi(p_right, self.raster, self.radius).index                
            
            if p_index < self.tpi:
                transect_temp.append(p_right)
            else:
                break
            
        return transect_temp
