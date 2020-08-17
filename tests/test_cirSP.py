# -*- coding: utf-8 -*-

import pytest
import os, sys
import pyosp
import numpy as np

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
dat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class TestCir:
    def test_elev_cir(self, elev_cir):
        """
        Data INSIDE of border should fall in geo-parameter range.
        OUTSIDE should not.
        """
        elev = elev_cir()
        lines = elev.lines
        
        p_in = [x[-1] for x in lines[90:181]]
        gradient = [np.radians(ng) for ng in range(90,181)]
        p_dat_in = []
        p_dat_out = []
        for ind, point in enumerate(p_in):
            p_out = [point[0] + np.cos(gradient[ind])*elev.radial_stepsize,
                     point[1] + np.sin(gradient[ind])*elev.radial_stepsize]
            
            dat_in = pyosp.Point_elevation(point, elev.raster).value
            dat_out = pyosp.Point_elevation(p_out, elev.raster).value
            
            p_dat_in.append(dat_in)
            p_dat_out.append(dat_out)
            
        assert all(i < 4 for i in p_dat_out)
        
    def test_slope_cir(self, slope_cir):
        """
        Data INSIDE of border should fall in geo-parameter range.
        OUTSIDE should not.
        """
        slope = slope_cir()
        lines = slope.lines
        cell_res = slope.raster.GetGeoTransform()[1]
        
        p_in = [x[-1] for x in lines[90:181]]
        gradient = [np.radians(ng) for ng in range(90,181)]
        p_dat_in = []
        p_dat_out = []
        for ind, point in enumerate(p_in):
            p_out = [point[0] + np.cos(gradient[ind])*slope.radial_stepsize,
                     point[1] + np.sin(gradient[ind])*slope.radial_stepsize]
            
            dat_in = pyosp.Geo_slope(point, slope.raster, cell_res).value
            dat_out = pyosp.Geo_slope(p_out, slope.raster, cell_res).value
            
            p_dat_in.append(dat_in)
            p_dat_out.append(dat_out)
            
        assert all(i < 13 for i in p_dat_out)
        
    def test_tpi_cir(self, tpi_cir):
        """
        Data INSIDE of border should fall in geo-parameter range.
        OUTSIDE should not.
        """
        tpi = tpi_cir()
        lines = tpi.lines
        
        p_in = [x[-1] for x in lines[90:181]]
        gradient = [np.radians(ng) for ng in range(90,181)]
        p_dat_in = []
        p_dat_out = []
        for ind, point in enumerate(p_in):
            p_out = [point[0] + np.cos(gradient[ind])*tpi.radial_stepsize,
                     point[1] + np.sin(gradient[ind])*tpi.radial_stepsize]
            
            dat_in = pyosp.Tpi(point, tpi.raster, tpi.tpi_radius).index
            dat_out = pyosp.Tpi(p_out, tpi.raster, tpi.tpi_radius).index
            
            p_dat_in.append(dat_in)
            p_dat_out.append(dat_out)
            
        assert all(i < 2 for i in p_dat_out)