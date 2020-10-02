# -*- coding: utf-8 -*-

import pytest
import os, sys
from pyosp import point_coords

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
dat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../datasets/")

class TestBaseHomo:
    # @pytest.mark.parametrize('base_homo', [
    #     dict(line_stepsize=None, cross_stepsize=None),
    #     dict(line_stepsize=100)
    #     ], indirect=True)
    def test_initial(self, base_homo):
        """Test the setup"""
        base = base_homo(line_stepsize=None, cross_stepsize=None)
        assert base.line_stepsize == base.cell_res
        assert base.cross_stepsize == base.cell_res
        assert len(base.distance) == base.line.length // base.line_stepsize + 1
        assert len(base.line_p) == len(base.distance)
        
    def test_segment(self, base_homo):
        """Test the start and end of chosen segment:
            start == line.length / 2
            end  == line.length / 4
        """
        start_end = os.path.join(dat, 'homo_start_end.shp')
        coords = point_coords(start_end)
        base = base_homo(line_stepsize=None, cross_stepsize=None)
        start_ind, end_ind = base._segment(coords[1], coords[0])
        assert abs(start_ind-len(base.distance)/4) <= 3
        assert abs(end_ind-len(base.distance)/2) <= 3
        
        # if given values are distances
        start_distance = base.distance[len(base.distance)//4]
        end_distance = base.distance[len(base.distance)//2]
        start_ind, end_ind = base._segment(start_distance, end_distance)
        assert abs(start_ind-len(base.distance)/4) <= 3
        assert abs(end_ind-len(base.distance)/2) <= 3
        
        