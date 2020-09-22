# -*- coding: utf-8 -*-


import numpy as np

from ..util import progressBar
from .base_cir import Base_cir
from .._elevation import Point_elevation

class Orig_cir(Base_cir):
    """Original circular swath profile characterization.

    :param center: path to center shapefile 
    :type center: str 
    :param raster: path to GeoRaster 
    :type raster: str 
    :param radius: radius of swath area
    :type radius: float
    :param ng_start: starting angle
    :type ng_start: int, optional
    :param ng_end: ending angle
    :type ng_end: int, optional
    :param ng_stepsize: angular step-size, defaults to 1
    :type ng_stepsize: int, optional
    :param radial_stepsize: radial step-size, defaults to None
    :type radial_stepsize: int, optional
    """
    def __init__(self, center, raster, radius,
                 ng_start=0, ng_end=360,
                 ng_stepsize=1, radial_stepsize=None): 

        super(Orig_cir,self).__init__(center, raster, radius,
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
            slope = np.radians(ng)
            for r in radial_line:
                dx = r * np.cos(slope)
                dy = r * np.sin(slope)
                p = [self.center.x+dx, self.center.y+dy]

                rasterVal = Point_elevation(p, self.raster).value
                if not (
                (self.rasterXmin <= p[0] <= self.rasterXmax) and 
                (self.rasterYmin <= p[1] <= self.rasterYmax) and
                (rasterVal > -1e20)  
                ):
                    break
                
                line_temp.append(p)
            
            lines.append(line_temp)
            
            current = sector.index(ng)
            progressBar(current, num)
         
        return lines
