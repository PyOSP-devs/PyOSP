# -*- coding: utf-8 -*-

import pytest
import os, sys
from collections import namedtuple
from pyosp import *

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
dat = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../datasets/")

homo_line = os.path.join(dat, "homo_baseline.shp")
homo_raster = os.path.join(dat, "homo_mount.tif")

cir_center = os.path.join(dat, "center.shp")
cir_raster = os.path.join(dat, "crater.tif")


@pytest.fixture(scope="module")
def base_homo(**kwargs):
    def _base_homo(**kwargs):
        return Base_curv(line=homo_line, raster=homo_raster, width=100, **kwargs)

    return _base_homo


@pytest.fixture(scope="module")
def orig_homo(**kwargs):
    def _orig_homo(**kwargs):
        return Orig_curv(line=homo_line, raster=homo_raster, width=100, **kwargs)

    return _orig_homo


@pytest.fixture(scope="module")
def elev_homo(**kwargs):
    def _elev_homo(**kwargs):
        return Elev_curv(
            line=homo_line, raster=homo_raster, width=100, min_elev=0.01, **kwargs
        )

    return _elev_homo


@pytest.fixture(scope="module")
def slope_homo(**kwargs):
    def _slope_homo(**kwargs):
        return Slope_curv(
            line=homo_line, raster=homo_raster, width=100, min_slope=1, **kwargs
        )

    return _slope_homo


@pytest.fixture(scope="module")
def tpi_homo(**kwargs):
    def _tpi_homo(**kwargs):
        return Tpi_curv(
            line=homo_line,
            raster=homo_raster,
            width=100,
            tpi_radius=50,
            min_tpi=-5,
            **kwargs
        )

    return _tpi_homo


@pytest.fixture(scope="module")
def base_cir(**kwargs):
    def _base_cir(**kwargs):
        return Base_cir(
            cir_center,
            cir_raster,
            radius=80,
            ng_start=0,
            ng_end=300,
            ng_stepsize=1,
            radial_stepsize=None,
            **kwargs
        )

    return _base_cir


@pytest.fixture(scope="module")
def orig_cir(**kwargs):
    def _orig_cir(**kwargs):
        return Orig_cir(
            cir_center,
            cir_raster,
            radius=80,
            ng_start=0,
            ng_end=300,
            ng_stepsize=1,
            radial_stepsize=None,
            **kwargs
        )

    return _orig_cir


@pytest.fixture(scope="module")
def elev_cir(**kwargs):
    def _elev_cir(**kwargs):
        return Elev_cir(
            cir_center,
            cir_raster,
            radius=80,
            min_elev=4,
            ng_start=0,
            ng_end=300,
            ng_stepsize=1,
            radial_stepsize=None,
            **kwargs
        )

    return _elev_cir


@pytest.fixture(scope="module")
def slope_cir(**kwargs):
    def _slope_cir(**kwargs):
        return Slope_cir(
            cir_center,
            cir_raster,
            radius=80,
            min_slope=13,
            ng_start=0,
            ng_end=300,
            ng_stepsize=1,
            radial_stepsize=None,
            **kwargs
        )

    return _slope_cir


@pytest.fixture(scope="module")
def tpi_cir(**kwargs):
    def _tpi_cir(**kwargs):
        return Tpi_cir(
            cir_center,
            cir_raster,
            radius=80,
            tpi_radius=50,
            min_tpi=2,
            ng_start=0,
            ng_end=300,
            ng_stepsize=1,
            radial_stepsize=None,
            **kwargs
        )

    return _tpi_cir
