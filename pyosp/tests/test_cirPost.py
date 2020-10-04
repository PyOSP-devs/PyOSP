# -*- coding: utf-8 -*-

import pytest
import os, sys
import pyosp
import numpy as np
import pickle

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
dat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../datasets/")

class TestPost:
    def test_outPolygon(self, orig_cir):
        orig = orig_cir()
        polygon = orig.out_polygon()
        px, py = polygon.exterior.xy
        assert len(px) == 303 
        assert len(py) == 303

    def test_outpolylines(self, orig_cir):
        orig = orig_cir()
        polylines = orig.out_polylines()
        bounds = polylines.bounds
        assert 20.8771 == pytest.approx(bounds[0], 0.001)
        assert 179.2956 == pytest.approx(bounds[2], 0.001)

    def test_polyring(self, orig_cir):
        orig = orig_cir()
        polyring = orig.out_polyring(start=10, end=30)
        assert 2052.88 == pytest.approx(polyring.area, 0.01)

    def test_profilePlot(self, orig_cir):
        orig = orig_cir()
        orig.profile_plot(color="maroon", p_coords=[ [40,40] ], s=3, c="k")
        assert True

    def test_slicePlot(self, orig_cir):
        orig = orig_cir()
        orig.slice_plot(angle=200)
        assert True

    def test_slicePolyline(self, orig_cir):
        orig = orig_cir()
        polyline = orig.slice_polyline(angle=200)
        bounds = polyline.bounds
        assert 25.65404 == pytest.approx(bounds[0], 0.001)
        assert 100.08637 == pytest.approx(bounds[2], 0.001)

    def test_hist(self, orig_cir):
        orig = orig_cir()
        orig.hist(bins=20)
        assert True
    
    def test_sliceHist(self, orig_cir):
        orig = orig_cir()
        orig.slice_hist(angle=200, bins=20)
        assert True