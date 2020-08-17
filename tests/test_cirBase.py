# -*- coding: utf-8 -*-

import os, sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
dat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class TestBaseCir:

    def test_initial(self, base_cir):
        """Test the setup"""
        base = base_cir()
        assert base.radial_stepsize == base.raster.GetGeoTransform()[1]
        assert len(base.distance) == base.radius // base.radial_stepsize + 1
        