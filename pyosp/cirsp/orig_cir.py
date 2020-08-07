# -*- coding: utf-8 -*-


import numpy as np
from .base_cir import Base_cir
from ..util import progressBar

class Orig_cir(Base_cir):
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
                
                line_temp.append(p)
            
            lines.append(line_temp)
            
            current = sector.index(ng)
            progressBar(current, num)
         
        return lines
        

    
