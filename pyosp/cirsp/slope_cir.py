# -*- coding: utf-8 -*-

import numpy as np
import gdal
from .base_cir import Base_cir
from .._slope import Geo_slope
from .._elevation import Point_elevation
from ..util import progressBar
import warnings

class Slope_cir(Base_cir):
    def __init__(self, center, raster, radius, 
                 min_slope=float("-inf"),
                 ng_start=0, ng_end=360,
                 ng_stepsize=1, radial_stepsize=None):
        self.min_slope = min_slope
        # self.max_slope = max_slope
        self.cell_size = gdal.Open(raster).GetGeoTransform()[1]
            
        super(Slope_cir,self).__init__(center, raster, radius,
                                      ng_start, ng_end,
                                      ng_stepsize, radial_stepsize)
        
    def _radial_lines(self):
        num = (self.ng_end - self.ng_start) // self.ng_stepsize
        sector = list(np.arange(self.ng_start, self.ng_end+0.00001,
                                self.ng_stepsize))
        radial_line = list(np.arange(0., self.radius+0.00001,
                                     self.radial_stepsize))
        
        lines = []
        for ng in sector:
            line_temp = []
            line_elev = []
            line_slope = []
            slope = np.radians(ng)
            for r in radial_line:
                dx = r * np.cos(slope)
                dy = r * np.sin(slope)
                p = [self.center.x+dx, self.center.y+dy]
                
                p_elev = Point_elevation(p, self.raster).value
                p_slope= Geo_slope(p, self.raster, self.cell_size).value
                
                line_temp.append(p)
                line_elev.append(p_elev)
                line_slope.append(p_slope)
                
             # find the maximum elevation point of the line
            max_ind = line_elev.index(max(line_elev))
            
            if max_ind == len(line_elev)-1:
                lines.append(line_temp)
                warnings.warn("Radius is small, not reach the rim top.") 
            elif all(i > self.min_slope for i in line_slope[max_ind:None]):
                lines.append(line_temp)   
            elif all(i < self.min_slope for i in line_slope[max_ind:None]):
                raise Exception("allowed minimum slope is too big "
                                "or radius is too small")             
            else:
                for i in range(max_ind, len(line_elev)):
                    if line_slope[i] < self.min_slope:
                        lines.append(line_temp[0:i])
                        break
                
            current = sector.index(ng)
            progressBar(current, num)
         
        return lines



