# -*- coding: utf-8 -*-

import numpy as np
from .base_cir import Base_cir
from .._tpi import Tpi
from .._elevation import Point_elevation
from ..util import progressBar
import warnings


class Tpi_cir(Base_cir):
    """Elevation-based circular swath profile characterization.

    :param center: path to center shapefile
    :type center: str
    :param raster: path to GeoRaster
    :type raster: str
    :param radius: radius of swath area
    :type radius: float
    :param tpi_radius: radius of TPI window
    :type tpi_radius: float
    :param min_tpi: minimal TPI threshold of swath apron
    :type min_tpi: float, defaults to -inf
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
        tpi_radius,
        min_tpi=float("-inf"),
        ng_start=0,
        ng_end=360,
        ng_stepsize=1,
        radial_stepsize=None,
    ):
        self.tpi_radius = tpi_radius
        self.min_tpi = min_tpi
        # self.max_tpi= max_tpi

        super(Tpi_cir, self).__init__(
            center, raster, radius, ng_start, ng_end, ng_stepsize, radial_stepsize
        )

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

    def _radial_lines(self):
        num = (self.ng_end - self.ng_start) // self.ng_stepsize
        sector = list(np.arange(self.ng_start, self.ng_end + 0.00001, self.ng_stepsize))
        radial_line = list(np.arange(0.0, self.radius + 0.00001, self.radial_stepsize))

        lines = []
        for ng in sector:
            line_temp = []
            line_elev = []
            line_tpi = []
            slope = np.radians(ng)
            for r in radial_line:
                dx = r * np.cos(slope)
                dy = r * np.sin(slope)
                p = [self.center.x + dx, self.center.y + dy]

                p_elev = Point_elevation(p, self.raster).value
                p_tpi = Tpi(p, self.raster, self.tpi_radius).value

                if not (
                    (self.rasterXmin <= p[0] <= self.rasterXmax)
                    and (self.rasterYmin <= p[1] <= self.rasterYmax)
                    and (p_elev > -1e20)
                ):
                    break

                line_temp.append(p)
                line_elev.append(p_elev)
                line_tpi.append(p_tpi)

            # find the maximum elevation point of the line
            max_ind = line_elev.index(max(line_elev))

            if max_ind == len(line_elev) - 1:
                lines.append(line_temp)
                warnings.warn("Radius is small, not reach the rim top.")
            elif all(i > self.min_tpi for i in line_tpi[max_ind:None]):
                lines.append(line_temp)
            elif all(i < self.min_tpi for i in line_tpi[max_ind:None]):
                raise Exception(
                    "allowed minimum TPI is too big " "or radius is too small"
                )
            else:
                for i in range(max_ind, len(line_elev)):
                    if line_tpi[i] < self.min_tpi:
                        lines.append(line_temp[0:i])
                        break

            current = sector.index(ng)
            progressBar(current, num)

        return lines
