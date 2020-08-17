    # -*- coding: utf-8 -*-

import numpy as np
from ..util import pairwise, progressBar
from .base_curv import Base_curv
from .._elevation import Point_elevation


class Orig_curv(Base_curv):
    def __init__(self, line, raster, width, line_stepsize=None, cross_stepsize=None): 
            
        super(Orig_curv,self).__init__(line, raster, width,
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
        
        nPoints = int(self.width/2 // self.cross_stepsize)
        slope = -(p2[0]-p1[0])/(p2[1]-p1[1])
        for i in range(nPoints):
            dx = np.sqrt((self.cross_stepsize*(i+1))**2 / (slope**2+1))
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
            rasterVal = Point_elevation(p_left, self.raster).value
            if not (
            (self.rasterXmin <= p_left[0] <= self.rasterXmax) and 
            (self.rasterYmin <= p_left[1] <= self.rasterYmax) and
            (rasterVal > -1e20)  
            ):
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
        
        nPoints = int(self.width/2 // self.cross_stepsize)
        slope = -(p2[0]-p1[0])/(p2[1]-p1[1])
        for i in range(nPoints):
            dx = np.sqrt((self.cross_stepsize*(i+1))**2 / (slope**2+1))
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
            rasterVal = Point_elevation(p_right, self.raster).value
            if not (
            (self.rasterXmin <= p_right[0] <= self.rasterXmax) and 
            (self.rasterYmin <= p_right[1] <= self.rasterYmax) and
            (rasterVal > -1e20)
            ):
                break
                        
            transect_temp.append(p_right)
            
        return transect_temp
            
