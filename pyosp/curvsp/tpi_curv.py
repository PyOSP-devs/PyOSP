# -*- coding: utf-8 -*-

import numpy as np
import sys
from ..util import pairwise, progressBar
from .._tpi import Tpi
from .base_curv import Base_curv
from osgeo import gdal


class Tpi_curv(Base_curv):
    """TPI-based swath profile characterization.

    :param line: path to baseline shapefile
    :type line: str
    :param raster: path to GeoTiff
    :type raster: str
    :param width: maximum allowed width of swath profile
    :type width: float
    :param tpi_radius: radius of TPI window
    :type tpi_radius: float
    :param min_tpi: minimal TPI threshold, defaults to float("-inf")
    :type min_tpi: float, optional
    :param max_tpi: maximal TPI threshold, defaults to float("inf")
    :type max_tpi: float, optional
    :param line_stepsize: step-size along baseline, defaults to resolution of raster
    :type line_stepsize: float, optional
    :param cross_stepsize: step-size along profilelines, defaults to resolution of raster
    :type cross_stepsize: float, optional
    """

    def __init__(
        self,
        line,
        raster,
        width,
        tpi_radius,
        min_tpi=float("-inf"),
        max_tpi=float("inf"),
        line_stepsize=None,
        cross_stepsize=None,
    ):
        self.tpi_radius = tpi_radius
        self.min_tpi = min_tpi
        self.max_tpi = max_tpi

        super(Tpi_curv, self).__init__(
            line, raster, width, line_stepsize, cross_stepsize
        )

    def __repr__(self):
        return "{}".format(self.__class__.__name__)

    def _transect_lines(self):
        lines = []
        num = len(self.line_p)
        for p1, p2 in pairwise(self.line_p):
            if p2 == self.line_p[-1]:
                line_left_1 = self._swath_left(p1, p2)
                line_right_1 = self._swath_right(p1, p2)
                line_1 = line_left_1 + line_right_1

                line_left_2 = self._swath_left(p1, p2, endPoint=True)
                line_right_2 = self._swath_right(p1, p2, endPoint=True)
                line_2 = line_left_2 + line_right_2

                lines.append(line_1)
                lines.append(line_2)

                current = self.line_p.index(p2) + 1  # processed two points at last step
                progressBar(current, num)
            else:
                line_left = self._swath_left(p1, p2)
                line_right = self._swath_right(p1, p2)
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

        rasterVal = Tpi(p_m, self.raster, self.tpi_radius).value
        if not (
            (self.rasterXmin <= p_m[0] <= self.rasterXmax)
            and (self.rasterYmin <= p_m[1] <= self.rasterYmax)
            and (self.min_tpi <= rasterVal <= self.max_tpi)
        ):
            transect_temp = []
        else:
            transect_temp = [p_m]
            slope = -(p2[0] - p1[0]) / (p2[1] - p1[1])
            for i in range(1, sys.maxsize, 1):
                dx = np.sqrt((self.cross_stepsize * i) ** 2 / (slope ** 2 + 1))
                dy = dx * abs(slope)

                if slope >= 0 and p2[0] < p1[0] and p2[1] >= p1[1]:
                    p_left = [p_m[0] - dx, p_m[1] - dy]
                elif slope >= 0 and p2[0] >= p1[0] and p2[1] < p1[1]:
                    p_left = [p_m[0] + dx, p_m[1] + dy]
                elif slope < 0 and p2[0] < p1[0] and p2[1] < p1[1]:
                    p_left = [p_m[0] + dx, p_m[1] - dy]
                elif slope < 0 and p2[0] >= p1[0] and p2[1] >= p1[1]:
                    p_left = [p_m[0] - dx, p_m[1] + dy]

                # discard point out of bounds
                if not (
                    (self.rasterXmin <= p_left[0] <= self.rasterXmax)
                    and (self.rasterYmin <= p_left[1] <= self.rasterYmax)
                ):
                    break

                # break if maximum width reached
                if self.width is not None:
                    hw = np.sqrt(dx ** 2 + dy ** 2)
                    if hw >= self.width / 2:
                        break

                p_index = Tpi(p_left, self.raster, self.tpi_radius).value
                if self.min_tpi <= p_index <= self.max_tpi:
                    transect_temp.insert(0, p_left)
                else:
                    break

        return transect_temp

    def _swath_right(self, p1, p2, endPoint=False):
        # if touch the end point, using same slope for both last two points
        if endPoint:
            p_m = p2
        else:
            p_m = p1

        transect_temp = []
        slope = -(p2[0] - p1[0]) / (p2[1] - p1[1])
        for i in range(1, sys.maxsize, 1):
            dx = np.sqrt((self.cross_stepsize * i) ** 2 / (slope ** 2 + 1))
            dy = dx * abs(slope)

            if slope >= 0 and p2[0] < p1[0] and p2[1] >= p1[1]:
                p_right = [p_m[0] + dx, p_m[1] + dy]
            elif slope >= 0 and p2[0] >= p1[0] and p2[1] < p1[1]:
                p_right = [p_m[0] - dx, p_m[1] - dy]
            elif slope < 0 and p2[0] < p1[0] and p2[1] < p1[1]:
                p_right = [p_m[0] - dx, p_m[1] + dy]
            elif slope < 0 and p2[0] >= p1[0] and p2[1] >= p1[1]:
                p_right = [p_m[0] + dx, p_m[1] - dy]

            # discard point out of bounds
            if not (
                (self.rasterXmin <= p_right[0] <= self.rasterXmax)
                and (self.rasterYmin <= p_right[1] <= self.rasterYmax)
            ):
                break

            # break if maximum width reached
            if self.width is not None:
                hw = np.sqrt(dx ** 2 + dy ** 2)
                if hw >= self.width / 2:
                    break

            p_index = Tpi(p_right, self.raster, self.tpi_radius).value
            if self.min_tpi <= p_index <= self.max_tpi:
                transect_temp.append(p_right)
            else:
                break

        return transect_temp
