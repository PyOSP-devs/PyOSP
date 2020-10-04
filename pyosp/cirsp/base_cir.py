# -*- coding: utf-8 -*-

import gdal
from shapely.geometry import Polygon, LineString, MultiLineString
import numpy as np
import matplotlib.pyplot as plt
from .._elevation import Point_elevation
from ..util import read_shape

class Base_cir():
    """Abstract class for circular swath profile.

    :param center: path to center shapefile 
    :type center: str 
    :param raster: path to GeoRaster 
    :type raster: str 
    :param radius: radius of swath area
    :type radius: float
    :param ng_start: starting angle
    :type ng_start: int, optional
    :param ng_end: ending angle
    :type ng_end: int, optional
    :param ng_stepsize: angular step-size, defaults to 1
    :type ng_stepsize: int, optional
    :param radial_stepsize: radial step-size, defaults to None
    :type radial_stepsize: int, optional
    """
    def __init__(self, center, raster, radius,
                 ng_start=None, ng_end=None,
                 ng_stepsize=1, radial_stepsize=None):
        # Empty swath profile is line or raster is None
        if center is None or raster is None:
            return
        else:
            self.center = read_shape(center)
            self.raster = gdal.Open(raster)
            
        self.radius = radius
            
        # Identify the boundary of raster
        geoTransform = self.raster.GetGeoTransform()
        cols = self.raster.RasterXSize
        rows = self.raster.RasterYSize
        self.rasterXmin = geoTransform[0]
        self.rasterXmax = geoTransform[0] + geoTransform[1]*(cols-1)
        self.rasterYmax = geoTransform[3]
        self.rasterYmin = geoTransform[3] + geoTransform[5]*(rows-1)
        
        # Angular parameters
        if not (
            (0. <= ng_start <= 360) and 
            (0. <= ng_end <= 360)
            ):
            raise AttributeError("start and end values should be "
                                 "between 0 and 360.")
        else:
            if ng_start >= ng_end:
                raise AttributeError("angular start point should be "
                                     "less than end.")
                
        self.ng_start = ng_start
        self.ng_end = ng_end
        self.ng_stepsize = ng_stepsize
        
        # Using cell size if radial_stepsize is None
        if radial_stepsize is None:
            self.radial_stepsize = geoTransform[1]
        else:
            self.radial_stepsize = radial_stepsize
                
        # swath data 
        self.distance = np.arange(0., self.radius+1e-10,
                                  self.radial_stepsize)
        self.lines = self._radial_lines()
        if self.lines == None:
            return
        else:
            self.dat_steps = max(len(x) for x in self.lines)
            self.dat = self.swath_data()
               
    def _radial_lines(self):
        """
        Depend on different swath methods
        """
        pass    
    
    def out_polygon(self):
        "Return a shapely polygon object"
        try:
            coords = list(self.center.coords) + [x[-1] for x in self.lines]
        except IndexError:
            raise Exception("Empty swath profile, please try reset arguments.")
            
        poly = Polygon(coords)
        return poly
    
    def out_polylines(self):       
        "Return a shapely polyline object"
        l_points = [x[0] for x in self.lines]
        r_points = [x[-1] for x in self.lines[::-1]]
        
        lines = list(zip(l_points, r_points[::-1]))
        return MultiLineString(lines)

    def out_polyring(self, start=None, end=None):
        "Return a polygon showing a range of distances"
        if start is not None and isinstance(start, (int, float)):
            start_ind = np.abs(self.distance - start).argmin()
        else:
            start_ind = 0

        if end is not None and isinstance(end, (int, float)):
            end_ind = np.abs(self.distance - end).argmin()
        else:
            end_ind = len(self.distance) - 1

        l_points = []
        r_points = []
        for x in self.lines:
            if end_ind <= len(x)-1:
                l_points.append(x[start_ind])
                r_points.append(x[end_ind])
            elif start_ind <= len(x)-1 and end_ind > len(x)-1:
                l_points.append(x[start_ind])
                r_points.append(x[-1])
            else:
                l_points.append(x[-1])
                r_points.append(x[-1])

        poly = Polygon(l_points + r_points[::-1])
        return poly
    
    def swath_data(self):
        "Return a list of elevation data along each profileline"
        lines_dat = []
        for line in self.lines:
            points_temp = []
            for point in line:
                rasterVal = Point_elevation(point, self.raster).value
                points_temp.append(rasterVal)
            
            line_temp = np.append(points_temp,
                                  np.repeat(np.nan, self.dat_steps-len(points_temp)))
            lines_dat.append(line_temp)

        return lines_dat
    
    def profile_stat(self):
        "Return a list of summary statistics along each profileline"
        min_z = [np.nanmin(x) for x in list(zip(*self.dat))]
        max_z = [np.nanmax(x) for x in list(zip(*self.dat))]
        mean_z = [np.nanmean(x) for x in list(zip(*self.dat))]
        q1 = [np.nanpercentile(x, q=25) for x in list(zip(*self.dat))]
        q3 = [np.nanpercentile(x, q=75) for x in list(zip(*self.dat))]
        
        return [min_z, max_z, mean_z, q1, q3]
    
    def profile_plot(self, ax=None, color='navy', p_coords=None, **kwargs):
        d = np.linspace(0, self.radial_stepsize*self.dat_steps, self.dat_steps,
                        endpoint=True)
        stat = self.profile_stat()

        if ax is None:
            fig, ax = plt.subplots()
            
        ax.plot(d, stat[2], 'k-', label='mean elevation')
        ax.fill_between(d, stat[0], stat[1], alpha=0.3, facecolor=color,
                        label='min_max relief')
        ax.fill_between(d, stat[3], stat[4], alpha=0.7, facecolor=color,
                        label='q1_q3 relief')
        
        if p_coords is not None:
            dist_array = np.empty(0)
            elev_array = np.empty(0)
            for p in p_coords:
                dist = np.linalg.norm(np.array(p)-np.array(self.center.coords))
                elev = Point_elevation(p, self.raster).value
                dist_array = np.append(dist_array, dist)
                elev_array = np.append(elev_array, elev)
                
            ax.scatter(dist_array, elev_array, **kwargs)

        ax.set_xlabel("Distance")
        ax.set_ylabel("Elevation")
        ax.legend()
        plt.tight_layout()
        return ax
        
    def slice_plot(self, angle, ax=None):
        """Plot cross-section of swath data.

        :param angle: the angle of cross-section wrt horizontal line
        :type angle: int
        """
        if not self.ng_start <= angle <=self.ng_end:
            raise ValueError("angle should be between ng_start and ng_end.")
        
        sector = np.arange(self.ng_start, self.ng_end+1e-10,
                           self.ng_stepsize)
        ng_ind = np.abs(sector - angle).argmin()
        points = self.lines[ng_ind]
        values = self.dat[ng_ind]
        values = values[~np.isnan(values)]
        
        d = []
        for point in points:
            d_temp = np.sqrt((point[0]-points[0][0])**2
                             +(point[1]-points[0][1])**2)
            d.append(d_temp)

        if ax is None:
            fig, ax = plt.subplots()
        
        ax.plot(d, values)
        ax.set_xlabel("Distance to center")
        ax.set_ylabel("Elevation")
        ax.grid()
        plt.tight_layout()
        return ax
        
    def slice_polyline(self, angle):
        """Return the polyline of cross-section

        :param angle: angle of cross-section wrt horizontal line
        :type angle: int
        :return: a shapely polyline object
        """
        if not self.ng_start <= angle <=self.ng_end:
            raise Exception("angle should be between ng_start and ng_end.")
            
        sector = np.arange(self.ng_start, self.ng_end+1e-10,
                           self.ng_stepsize)
        ng_ind = np.abs(sector - angle).argmin()
        points = self.lines[ng_ind]
        line = list((points[0], points[-1]))
        
        return LineString(line)
        
        
    def hist(self, bins=50, ax=None):
        "Return a histogram plot"
        dat = np.hstack(self.dat)

        if ax is None:
            fig, ax = plt.subplots()

        ax.hist(dat, bins=bins, histtype='stepfilled', alpha=1, density=True)
        ax.set_xlabel("Elevation")
        ax.set_ylabel("PDF")
        ax.grid()
        plt.tight_layout()
        return ax
        
    def slice_hist(self, angle, bins=10, ax=None):
        """Plot the histogram of slice 

        :param angle: angle of cross-section wrt horizontal line
        :type angle: int
        :param bins: number of bins, defaults to 10
        :type bins: int, optional
        """
        if not self.ng_start <= angle <=self.ng_end:
            raise ValueError("angle should be between ng_start and ng_end.")
        
        sector = np.arange(self.ng_start, self.ng_end+1e-10,
                           self.ng_stepsize)
        ng_ind = np.abs(sector - angle).argmin()
        dat = self.dat[ng_ind]
        
        if ax is None:
            fig, ax = plt.subplots()

        ax.hist(dat, bins=bins, histtype='stepfilled', alpha=1, density=True)
        ax.set_xlabel("Elevation")
        ax.set_ylabel("PDF")
        ax.grid()
        plt.tight_layout()
        return ax
        
        
        
        
        