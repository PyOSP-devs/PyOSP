# -*- coding: utf-8 -*-

import pytest
import os, sys
import pyosp
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
dat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../datasets/")

@pytest.fixture()
def dxdy(orig_homo):
    orig = orig_homo()
    p1 = orig.lines[len(orig.lines)//2][0]
    p2 = orig.lines[len(orig.lines)//2][1]
    slope = (p2[1]-p1[1]) / (p2[0]-p1[0])
    dx = np.sqrt(orig.cross_stepsize**2 / (slope**2+1))
    dy = dx * slope
    yield dx, dy

class TestCurv:
    def test_elev_homo(self, elev_homo, dxdy):
        """
        Double sides test.
        All points WITHIN polygon should fall in geo-parameter range.
        All points OUTSIDE should not.
        """
        elev = elev_homo()
        lines = elev.lines
        dx, dy = dxdy
        
        points_left = [x[0] for x in lines[50:150]]
        points_right = [x[-1] for x in lines[50:150]]
        p_dat_in = []
        p_dat_out = []
        for point in points_left:
            p_out = [point[0]-dx, point[1]-dy]
            
            p_elev_in = pyosp.Point_elevation(point, elev.raster).value
            p_elev_out = pyosp.Point_elevation(p_out, elev.raster).value
            
            p_dat_in.append(p_elev_in)
            p_dat_out.append(p_elev_out)
            
        assert all(i >= 0.01 for i in p_dat_in)
        assert all(i < 0.01 for i in p_dat_out)
        
        p_dat_in = []
        p_dat_out = []
        for point in points_right:
            p_out = [point[0]+dx, point[1]+dy]
            
            p_elev_in = pyosp.Point_elevation(point, elev.raster).value
            p_elev_out = pyosp.Point_elevation(p_out, elev.raster).value
            
            p_dat_in.append(p_elev_in)
            p_dat_out.append(p_elev_out)
            
        assert all(i >= 0.01 for i in p_dat_in)
        assert all(i < 0.01 for i in p_dat_out)
        
    def test_slope_homo(self, slope_homo, dxdy):
        """
        Double sides test.
        All points WITHIN polygon should fall in geo-parameter range.
        All points OUTSIDE should not.
        """
        slope = slope_homo()
        lines = slope.lines
        dx, dy = dxdy
        
        points_left = [x[0] for x in lines[50:150]]
        points_right = [x[-1] for x in lines[50:150]]
        p_dat_in = []
        p_dat_out = []
        for point in points_left:
            p_out = [point[0]-dx, point[1]-dy]
            
            dat_in = pyosp.Geo_slope(point, slope.raster, slope.cell_res).value
            dat_out = pyosp.Geo_slope(p_out, slope.raster, slope.cell_res).value
            
            p_dat_in.append(dat_in)
            p_dat_out.append(dat_out)
            
        assert all(i >= 1 for i in p_dat_in)
        assert all(i < 1 for i in p_dat_out)
        
        p_dat_in = []
        p_dat_out = []
        for point in points_right:
            p_out = [point[0]+dx, point[1]+dy]
            
            dat_in = pyosp.Geo_slope(point, slope.raster, slope.cell_res).value
            dat_out = pyosp.Geo_slope(p_out, slope.raster, slope.cell_res).value
            
            p_dat_in.append(dat_in)
            p_dat_out.append(dat_out)
            
        assert all(i >= 1 for i in p_dat_in)
        assert all(i < 1 for i in p_dat_out)
        
    def test_tpi_homo(self, tpi_homo, dxdy):
        """
        Double sides test.
        All points WITHIN polygon should fall in geo-parameter range.
        All points OUTSIDE should not.
        """
        tpi = tpi_homo()
        lines = tpi.lines
        dx, dy = dxdy
        
        points_left = [x[0] for x in lines[50:100]]
        points_right = [x[-1] for x in lines[50:100]]
        p_dat_in = []
        p_dat_out = []
        for point in points_left:
            p_out = [point[0]-dx, point[1]-dy]
            
            dat_in = pyosp.Tpi(point, tpi.raster, tpi.tpi_radius).value
            dat_out = pyosp.Tpi(p_out, tpi.raster, tpi.tpi_radius).value
            p_dat_in.append(dat_in)
            p_dat_out.append(dat_out)
            
        assert all(i >= -5 for i in p_dat_in)
        assert all(i < -5 for i in p_dat_out)
        
        p_dat_in = []
        p_dat_out = []
        for point in points_right:
            p_out = [point[0]+dx, point[1]+dy]
            
            dat_in = pyosp.Tpi(point, tpi.raster, tpi.tpi_radius).value
            dat_out = pyosp.Tpi(p_out, tpi.raster, tpi.tpi_radius).value
            p_dat_in.append(dat_in)
            p_dat_out.append(dat_out)
            
        assert all(i >= -5 for i in p_dat_in)
        assert all(i < -5 for i in p_dat_out)
            
            
            
    