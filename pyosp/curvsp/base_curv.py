# -*- coding: utf-8 -*-

import gdal
from shapely.geometry import Polygon, MultiLineString, Point
import numpy as np
# from scipy.stats import gaussian_kde
from matplotlib.colors import Normalize
from matplotlib import cm
import matplotlib.pyplot as plt
from .._elevation import Point_elevation
from .._slope import Geo_slope
from .._tpi import Tpi
from ..util import read_shape, point_coords
import copy

class Base_curv():    
    """Abstract class for cuvilinear swath profile.

    :param line: path to baseline shapefile
    :type line: str
    :param raster: path to GeoTiff
    :type raster: str
    :param width: maximum allowed width of swath profile
    :type width: Float
    :param line_stepsize: step-size along baseline, defaults to resolution of raster
    :type line_stepsize: float, optional
    :param cross_stepsize: step-size along profilelines, defaults to resolution of raster
    :type cross_stepsize: float, optional
    """
    def __init__(self, line, raster, width,
                 line_stepsize=None, cross_stepsize=None):
        # Empty swath profile is line, width or raster is None
        if None in (line, raster, width):
            return
        else:
            self.line = read_shape(line)
            self.raster = gdal.Open(raster)
            self.width = width
            
        # Identify the boundary of raster
        geoTransform = self.raster.GetGeoTransform()
        cols = self.raster.RasterXSize
        rows = self.raster.RasterYSize
        self.rasterXmin = geoTransform[0]
        self.rasterXmax = geoTransform[0] + geoTransform[1]*(cols-1)
        self.rasterYmax = geoTransform[3]
        self.rasterYmin = geoTransform[3] + geoTransform[5]*(rows-1)
        
        # Using raster resolution if line_stepsize is None
        self.cell_res = geoTransform[1]
        
        if line_stepsize is None:
            self.line_stepsize = self.cell_res
            self.line_p = self._line_points(self.cell_res)
        else:
            self.line_stepsize = line_stepsize
            self.line_p = self._line_points(line_stepsize)
        
        # Using raster resolution if cross_stepsize is None
        if cross_stepsize is None:
            self.cross_stepsize = self.cell_res
        else:
            self.cross_stepsize = cross_stepsize
        
        # swath data
        self.distance = np.arange(0., self.line.length+1e-10, self.line_stepsize)
        self.lines = self._transect_lines()
        self.dat = self.swath_data()
     
    def _line_points(self, line_stepsize):
        nPoints = int(self.line.length // line_stepsize)
        coords = []
        for i in range(nPoints+1):
            p = tuple(self.line.interpolate(line_stepsize*i, normalized=False).coords)
            coords.append(p[0])
            
        return coords
    
    def _transect_lines(self):
        """
        Depend on different terrain type
        """
        pass    
    
    def _segment(self, start=None, end=None):
        if start is not None and isinstance(start, (int, float)):
            start_ind = np.abs(self.distance - start).argmin()
        elif start is not None and len(start) == 2:
            line_coords = np.asarray(self.line_p)
            start_coord = np.asarray(start)
            distance = np.sum((line_coords-start_coord)**2, axis=1)
            start_ind = np.argmin(distance)
        else:
            start_ind=start
                    
        if end is not None and isinstance(start, (int, float)):
            end_ind = np.abs(self.distance - end).argmin()
        elif end is not None and len(end) == 2:
            line_coords = np.asarray(self.line_p)
            end_coord = np.asarray(end)
            distance = np.sum((line_coords-end_coord)**2, axis=1)
            end_ind = np.argmin(distance)
        else:
            end_ind=end
            
        return start_ind, end_ind
    
    def out_polygon(self, start=None, end=None):
        """Generate output polygon.

        :param start: starting position of polygon, defaults to starting point of baseline
        :type start: float or array-like, optional
        :param end: ending position of polygon, defaults to ending point of baseline
        :type end: float or array-like, optional
        :return: polygon of swath area
        """
        start_ind, end_ind = self._segment(start, end)
        line_segment = self.lines[start_ind:end_ind]
            
        try:
            l_points = [x[0] for x in line_segment]
            r_points = [x[-1] for x in line_segment[::-1]]
        except IndexError:
            raise Exception("Empty swath profile, please try reset arguments.")
        
        coords = np.vstack((l_points, r_points))
        poly = Polygon(coords).buffer(0.01)
        return poly
    
    def out_polylines(self, start=None, end=None):
        """Generate output polyline.

        :param start: starting position of Polyline, defaults to start of baseline
        :type start: float or array-like, optional
        :param end: ending position of Polyline, defaults to end of baseline
        :type end: float or array-like, optional
        :return: polylines of swath area
        """
        start_ind, end_ind = self._segment(start, end)
        line_segment = self.lines[start_ind:end_ind]
        
        try:
             l_points = [x[0] for x in line_segment]
             r_points = [x[-1] for x in line_segment[::-1]]
        except IndexError:
            raise Exception("Empty swath profile, please try reset arguments.")
        
        lines = list(zip(l_points, r_points[::-1]))
        
        return MultiLineString(lines)
    
    def swath_data(self):
        """Return a list of elevation data along each profileline
        """
        lines_dat = []
        try:
            for line in self.lines:
                points_temp = []
                for point in line:
                    rasterVal = Point_elevation(point, self.raster).value[0,0]
                    points_temp.append(rasterVal)
                    
                lines_dat.append(points_temp)
        except TypeError:
            pass
            
        return lines_dat
    
    def profile_stat(self, z):
        """Return a list of summary statistics along each profileline
        """
        min_z = [np.nanmin(x) if len(x)>0 else np.nan for x in z]
        max_z = [np.nanmax(x) if len(x)>0 else np.nan for x in z]
        mean_z = [np.nanmean(x) if len(x)>0 else np.nan for x in z]
        q1 = [np.nanpercentile(x, q=25) if len(x)>0 else np.nan for x in z]
        q3 = [np.nanpercentile(x, q=75) if len(x)>0 else np.nan for x in z]
        
        return [min_z, max_z, mean_z, q1, q3]
    
    def plot(self, distance, stat, start=None, end=None, ax=None, color='navy'):         
        """Summary statistics plot.
        """
        start_ind, end_ind = self._segment(start, end)
        if ax is None:
            fig, ax = plt.subplots()
            
        ax.plot(distance[start_ind:end_ind], stat[2][start_ind:end_ind],
                'k-', linewidth=1.5, label='mean elevation')
        ax.fill_between(distance[start_ind:end_ind], stat[0][start_ind:end_ind], 
                        stat[1][start_ind:end_ind], alpha=0.3, facecolor=color,
                        label='min_max relief')
        ax.fill_between(distance[start_ind:end_ind], stat[3][start_ind:end_ind], 
                        stat[4][start_ind:end_ind], alpha=0.7, facecolor=color,
                        label='q1_q3 relief')
        
        ax.set_xlabel("Distance")
        ax.set_ylabel("Elevation")
        ax.legend()
        plt.tight_layout()
        return ax
    
    def density_scatter(self, distance=None, dat=None, bins=20, 
                        start=None, end=None, ax=None, fig=None, 
                        s=1, cmap='jet', **kwargs):
        start_ind, end_ind = self._segment(start, end)
        distance = list(self.distance[start_ind:end_ind] if distance is None else distance[start_ind:end_ind])
        dat = self.dat[start_ind:end_ind] if dat is None else dat[start_ind:end_ind] 

        min_z = np.nanmin(np.nanmin(dat))
        max_z = np.nanmax(np.nanmax(dat))
        bin_e = np.linspace(min_z, max_z, num=bins, endpoint=True)
        bin_center = 0.5*(bin_e[1:]+bin_e[:-1])

        # collect all density data 
        d_ensemble = []
        for ind, ele in enumerate(dat):
            # Calculate the point density
            data, _ = np.histogram(ele, bins=bin_e, density=True)
            d = np.interp(ele, bin_center, data)
            d_ensemble.append(d)

        d_max = max([np.nanmax(s) for s in d_ensemble])
        d_min = min([np.nanmin(s) for s in d_ensemble])
        if ax is None:
            fig, ax = plt.subplots()

        for ind, ele in enumerate(d_ensemble):
            y = np.stack(dat[ind])
            x = np.repeat(distance[ind], len(y))
            idx = ele.argsort()
            y, z = y[idx], ele[idx]
            ax.scatter(x, y, c=z, s=s, cmap=cmap, vmin=d_min, vmax=d_max, **kwargs)
            
        norm = Normalize(vmin=d_min, vmax=d_max)
        cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap=cmap), ax=ax)
        cbar.ax.set_ylabel('Density')
        
        ax.set_xlabel("Distance")
        ax.set_ylabel("Elevation")
        plt.tight_layout()

        return ax

    def profile_plot(self, start=None, end=None, ax=None, color='navy',
                     points=None, p_marker="o", p_size=1,
                     p_color="C3", p_label=None):
        """Plot the swath profile.

        :param start: starting position of plot, defaults to starting point of baseline
        :type start: float or array-like, optional
        :param end: ending position of plot, defaults to ending point of baseline
        :type end: float or array-like, optional
        :param ax: matplotlib axes object, if not will generate one, default None
        :param color: color shading of percentile, defaults to 'navy'
        :type color: str, optional
        :param points: path to points shapefile that are meant to be plotted with SP, defaults to None
        :type points: str, optional
        :param p_marker: marker of points, defaults to "o"
        :type p_marker: str, optional
        :param p_size: size of points, defaults to 1
        :type p_size: int, optional
        :param p_color: color of points, defaults to "C3"
        :type p_color: str, optional
        :param p_label: label (legend) of points, defaults to None
        :type p_label: str, optional
        """
        distance = self.distance
        stat = self.profile_stat(self.dat)
        
        if ax is None:
            fig, ax = plt.subplots()
            
        self.plot(distance, stat, start, end, ax, color)
        
        if points is not None:
            p_coords = point_coords(points)
            dist_array = np.empty(0)
            elev_array = np.empty(0)
            for p in p_coords:
                point = Point(p)
                dist = self.line.project(point)
                elev = Point_elevation(p, self.raster).value
                dist_array = np.append(dist_array, dist)
                elev_array = np.append(elev_array, elev)
                
            ax.scatter(dist_array, elev_array,
                       s=p_size, marker=p_marker, color=p_color, label=p_label)        
                
    def slice_plot(self, loc, ax=None):
        """plot cross-section of swath data.

        :param loc: location of slice, can be coordinate or distance from starting.
        :type loc: float or array-like.
        :param ax: matplotlib axes, defaults to None
        """
        if loc is not None and isinstance(loc, (int, float)):
            loc_ind = np.abs(self.distance - loc).argmin()
        elif loc is not None and len(loc) == 2:
            line_coords = np.asarray(self.line_p)
            loc_coords = np.asarray(loc)
            distance  = np.sum((line_coords-loc_coords)**2, axis=1)
            loc_ind = np.argmin(distance)

        line = self.lines[loc_ind]
        
        d = []
        for point in line:
            d_temp = np.sqrt((point[0]-line[0][0])**2 + (point[1]-line[0][1])**2)
            d.append(d_temp)
            
        if ax is None:
            fig, ax = plt.subplots()
            
        ax.plot(d, self.dat[loc_ind])
        ax.set_xlabel("Distance to left end")
        ax.set_ylabel("Elevation")
        ax.grid()
        plt.tight_layout()
        
    def hist(self, dat=None, ax=None, bins=50):
        """Return a histogram plot.
        """
        dat = self.dat if dat is None else dat

        # see if it is a nested list 
        if any(isinstance(i, list) for i in dat):
            dat_array = np.empty(0)
            for i in dat:
                dat_array = np.append(dat_array, np.hstack(i))
        else:
            dat_array = dat
        
        if ax is None:
            fig, ax = plt.subplots()

        ax.hist(dat_array, bins=bins, histtype='stepfilled', alpha=1, density=True)
        ax.set_xlabel("Elevation")
        ax.set_ylabel("PDF")
        # ax.grid()
        plt.tight_layout()
       
    def slice_hist(self, loc, bins=50):
        """Plot the histogram of slice.

        :param loc: location of slice, can be coordinate or distance from starting.
        :type loc: float or array-like
        :param bins: number of bins, defaults to 50
        :type bins: int, optional
        """
        if loc is not None and isinstance(loc, (int, float)):
            loc_ind = np.abs(self.distance - loc).argmin()
        elif loc is not None and len(loc) == 2:
            line_coords = np.asarray(self.line_p)
            loc_coords = np.asarray(loc)
            distance  = np.sum((line_coords-loc_coords)**2, axis=1)
            loc_ind = np.argmin(distance)

        dat = self.dat[loc_ind]
        
        self.hist(dat=dat, bins=bins)
    
    def cross_dat(self, dat=None, start=None, end=None):
        """Generate cross-swath data.

        :param dat: Swath data passed to calculate cross-swath, defaults to all swath data.
        :type dat: list, optional
        :param start: Starting position of cross-swath, defaults to starting point of baseline
        :type start: float or array-like, optional
        :param end: Ending position of cross-swath, defaults to ending point of baseline
        :type end: float or array-like, optional
        :return: A dict specify distance from the baseline, and corresponding swath data.
        :rtype: dict
        """
        start_ind, end_ind = self._segment(start, end)
        dat = self.dat[start_ind:end_ind] if dat is None else dat
         
        # only baseline point was restored as tuple, others were lists
        left = []
        right = []
        for i in self.lines[start_ind:end_ind]:
            left_num = i.index([x for x in i if isinstance(x, tuple)][0])
            right_num = len(i) - left_num - 1
            left.append(left_num)
            right.append(right_num)
            
        left_max = max(left)
        right_max = max(right)
        left_dist = -1 * np.arange((left_max+1)*self.cross_stepsize-1e-10,
                                   step=self.cross_stepsize)
        right_dist = np.arange((right_max+1)*self.cross_stepsize-1e-10,
                               step=self.cross_stepsize)
        distance = np.hstack((left_dist[::-1], right_dist[1:None]))
        
        # cross_matrix = np.zeros((len(distance), len(self.lines[start:end])))
        cross_profile = []
        for count, ele in enumerate(dat):
            line_dat = np.vstack(ele).flatten()
            line_pad = np.pad(line_dat, 
                             (left_max-left[count], right_max-right[count]),
                             'constant', constant_values=np.nan)
            cross_profile.append(line_pad)
        
        return {'distance': distance,
                'cross_matrix': list(map(list, zip(*cross_profile)))}
    
    def cross_plot(self, start=None, end=None, ax=None, color='navy'):
        """Return the plot of cross-profile.

        :param start: Starting position of cross-swath, defaults to starting point of baseline
        :type start: float or array-like, optional
        :param end: Ending position of cross-swath, defaults to ending point of baseline
        :type end: float or array-like, optional
        :param ax: matplotlib axes object, defaults to None
        :param color: color of quartiles, defaults to 'navy'
        :type color: str, optional
        """
        # start_ind, end_ind = self._segment(start, end)
        dat = self.cross_dat(start=start, end=end)
        
        distance = dat['distance']
        cross = dat['cross_matrix']
        cross_stat = self.profile_stat(cross)
        
        # default to plot all along cross direction
        start = None
        end = None
        
        self.plot(distance, cross_stat, start, end, ax, color)
    
    def post_tpi(self, radius, min_val=float("-inf"), max_val=float("inf"),
                 start=None, end=None, ax=None, color='navy',
                 cross=False, plot=False):
        """Post-processing swath data according to TPI criteria.

        :param radius: TPI radius
        :type radius: float
        :param min_val: minimal TPI threshold, defaults to float("-inf")
        :type min_val: float, optional
        :param max_val: maximal TPI threshold, defaults to float("inf")
        :type max_val: float, optional
        :param start: starting point, can be coordinates or distance
        :type start: float or array-like, optional
        :param end: ending point, can be coordinates or distance
        :type end: float or array-like, optional
        :param ax: matplotlib axes object, defaults to None
        :param color: color of quartiles, defaults to 'navy'
        :type color: str, optional
        :param cross: plot the processed cross-swath profile, defaults to False
        :type cross: bool, optional
        :param plot: plot the processed swath profile, defaults to False
        :type plot: bool, optional
        :return: a list contain distance and processed elevation data
        :rtype: list
        """
        start_ind, end_ind = self._segment(start, end)
        
        lines_val = copy.deepcopy(self.dat[start_ind:end_ind])
        for line_ind, line in enumerate(self.lines[start_ind:end_ind]):
            for point_ind, point in enumerate(line):
                point_val = Tpi(point, self.raster, radius).index
                if not min_val <= point_val <= max_val:
                    lines_val[line_ind][point_ind] = np.nan
             
        distance  = self.distance[start_ind:end_ind]
        values = lines_val
        
        if cross == True:
           cross_dat = self.cross_dat(dat=lines_val, start=start, end=end)
           distance = cross_dat['distance']
           values = cross_dat['cross_matrix']
        
        if plot == True:
            post_stat = self.profile_stat(values)
            self.plot(distance=distance, stat=post_stat, ax=ax, color=color)

        return [distance, values]
        
    def post_elev(self, min_val=float("-inf"), max_val=float("inf"),
                  start=None, end=None, ax=None, color='navy',
                  cross=False, plot=False): 
        """Post-processing swath data according to elevation criteria.

        :param min_val: minimal elevation threshold, defaults to float("-inf")
        :type min_val: float, optional
        :param max_val: maximal elevation threshold, defaults to float("inf")
        :type max_val: float, optional
        :param start: starting point, can be coordinates or distance 
        :type start: float or array-like, optional
        :param end: ending point, can be coordinates or distance
        :type end: float or array-like, optional
        :param ax: matplotlib axes object, defaults to None
        :param color: color of quartiles, defaults to 'navy'
        :type color: str, optional
        :param cross: plot the processed cross-swath profile, defaults to False
        :type cross: bool, optional
        :param plot: plot the processed swath profile, defaults to False
        :type plot: bool, optional
        :return: a list contain distance and processed elevation data
        :rtype: list
        """
        start_ind, end_ind = self._segment(start, end)
        
        lines_val = copy.deepcopy(self.dat[start_ind:end_ind])
        for line_ind, line in enumerate(self.lines[start_ind:end_ind]):
            for point_ind, point in enumerate(line):
                point_val = Point_elevation(point, self.raster).value
                if not min_val <= point_val <= max_val:
                    lines_val[line_ind][point_ind] = np.nan
             
        distance  = self.distance[start_ind:end_ind]
        values = lines_val
        
        if cross == True:
           cross_dat = self.cross_dat(dat=lines_val, start=start, end=end)
           distance = cross_dat['distance']
           values = cross_dat['cross_matrix']
        
        if plot == True:
            post_stat = self.profile_stat(values)
            self.plot(distance=distance, stat=post_stat, ax=ax, color=color)

        return [distance, values]

    def post_slope(self, min_val=0., max_val=90.,
                   start=None, end=None, ax=None, color='navy',
                   cross=False, plot=False):                  
        """Post-processing swath data according to slope criteria.

        :param min_val: minimal slope threshold, defaults to float("-inf")
        :type min_val: float, optional
        :param max_val: maximal slope threshold, defaults to float("inf")
        :type max_val: float, optional
        :param start: starting point, can be coordinates or distance 
        :type start: float or array-like, optional
        :param end: ending point, can be coordinates or distance
        :type end: float or array-like, optional
        :param ax: matplotlib axes object, defaults to None
        :param color: color of quartiles, defaults to 'navy'
        :type color: str, optional
        :param cross: plot the processed cross-swath profile, defaults to False
        :type cross: bool, optional
        :param plot: plot the processed swath profile, defaults to False
        :type plot: bool, optional
        :return: a list contain distance and processed slope data
        :rtype: list
        """
        start_ind, end_ind = self._segment(start, end)
        
        lines_val = copy.deepcopy(self.dat[start_ind:end_ind])
        for line_ind, line in enumerate(self.lines[start_ind:end_ind]):
            for point_ind, point in enumerate(line):
                point_val = Geo_slope(point, self.raster, self.cell_res).value
                if not min_val <= point_val <= max_val:
                    lines_val[line_ind][point_ind] = np.nan
        
        distance = self.distance[start_ind:end_ind]
        values = lines_val
        
        if cross == True:
            cross_dat = self.cross_dat(dat=lines_val, start=start, end=end)
            distance = cross_dat['distance']
            values = cross_dat['cross_matrix']
        
        if plot == True:
            post_stat = self.profile_stat(values)
            self.plot(distance=distance, stat=post_stat, ax=ax, color=color)
            
        return [distance, values]
        
