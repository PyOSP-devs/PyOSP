# -*- coding: utf-8 -*-

import numpy as np
from osgeo import gdal
from .base_cir import Base_cir
from .._slope import Geo_slope
from .._elevation import Point_elevation
from ..util import progressBar
import warnings


class Slope_cir(Base_cir):
    """Slope_based circular swath profile characterization.

    :param center: path to center shapefile
    :type center: str
    :param raster: path to GeoRaster
    :type raster: str
    :param radius: radius of swath area
    :type radius: float
    :param min_slope: minimal slope threshold of swath apron
    :type min_slope: float
    :param ng_start: starting angle
    :type ng_start: int, optional
    :param ng_end: ending angle
    :type ng_end: int, optional
    :param ng_stepsize: angular step-size, defaults to 1
    :type ng_stepsize: int, optional
    :param radial_stepsize: radial step-size, defaults to None
    :type radial_stepsize: int, optional
    """

    def __init__(
        self,
        center,
        raster,
        radius,
        min_slope=float("-inf"),
        ng_start=0,
        ng_end=360,
        ng_stepsize=1,
        radial_stepsize=None,
    ):
        self.min_slope = min_slope
        # self.max_slope = max_slope
        self.cell_size = gdal.Open(raster).GetGeoTransform()[1]

        super(Slope_cir, self).__init__(
            center, raster, radius, ng_start, ng_end, ng_stepsize, radial_stepsize
        )

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

    def _radial_lines(self):
        sector = self._sector()
        num = len(sector)
        radial_line = list(np.arange(0.0, self.radius + 0.00001, self.radial_stepsize))

        lines = []
        for ng in sector:
            line_temp = []
            line_elev = []
            line_slope = []
            slope = np.radians(ng)
            for r in radial_line:
                dx = r * np.cos(slope)
                dy = r * np.sin(slope)
                p = [self.center.x + dx, self.center.y + dy]

                p_elev = Point_elevation(p, self.raster).value
                p_slope = Geo_slope(p, self.raster, self.cell_size).value

                if not (
                    (self.rasterXmin <= p[0] <= self.rasterXmax)
                    and (self.rasterYmin <= p[1] <= self.rasterYmax)
                    and (p_elev > -1e20)
                ):
                    break

                line_temp.append(p)
                line_elev.append(p_elev)
                line_slope.append(p_slope)

            if not line_elev:
                raise ValueError(
                    "No valid raster data along the {} degree ray; "
                    "check that the center lies inside the raster.".format(ng)
                )

            # find the maximum elevation point of the line
            max_ind = line_elev.index(max(line_elev))

            if max_ind == len(line_elev) - 1:
                lines.append(line_temp)
                warnings.warn("Radius is small, not reach the rim top.")
            elif all(i > self.min_slope for i in line_slope[max_ind:None]):
                lines.append(line_temp)
            elif all(i < self.min_slope for i in line_slope[max_ind:None]):
                raise Exception(
                    "allowed minimum slope is too big " "or radius is too small"
                )
            else:
                # cut at the first value below the threshold beyond the rim;
                # keep the whole line if none is below (values equal to it)
                cut = next(
                    (
                        i
                        for i in range(max_ind, len(line_slope))
                        if line_slope[i] < self.min_slope
                    ),
                    len(line_slope),
                )
                lines.append(line_temp[0:cut])

            current = sector.index(ng) + 1
            progressBar(current, num)

        return lines
