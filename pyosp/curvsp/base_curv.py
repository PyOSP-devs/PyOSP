# -*- coding: utf-8 -*-

import gdal
from shapely.geometry import Polygon, MultiLineString, Point
import numpy as np
import matplotlib.pyplot as plt
from .._elevation import Point_elevation
from .._slope import Geo_slope
from .._tpi import Tpi
from ..util import read_shape
import copy

class Base_curv():
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
        min_z = [np.nanmin(x) if len(x)>0 else np.nan for x in z]
        max_z = [np.nanmax(x) if len(x)>0 else np.nan for x in z]
        mean_z = [np.nanmean(x) if len(x)>0 else np.nan for x in z]
        q1 = [np.nanpercentile(x, q=25) if len(x)>0 else np.nan for x in z]
        q3 = [np.nanpercentile(x, q=75) if len(x)>0 else np.nan for x in z]
        
        return [min_z, max_z, mean_z, q1, q3]
    
    def plot(self, distance, stat, start=None, end=None, ax=None, color='navy'):         
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
        # ax.grid()
        plt.tight_layout()
            
    def profile_plot(self, start=None, end=None, ax=None, color='navy',
                     p_coords=None, p_marker="o", p_size=1,
                     p_color="C3", p_label=None):
        distance = self.distance
        stat = self.profile_stat(self.dat)
        
        if ax is None:
            fig, ax = plt.subplots()
            
        self.plot(distance, stat, start, end, ax, color)
        
        if p_coords is not None:
            line_coords = np.array(self.line_p)
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
                
    def slice_plot(self, loc, ax=None, label=None):
        if not min(self.distance) <= loc <= max(self.distance):
            raise ValueError("Slice location should within the range of swath profile")
        
        loc_ind = np.abs(self.distance - loc).argmin()
        line = self.lines[loc_ind]
        
        d = []
        for point in line:
            d_temp = np.sqrt((point[0]-line[0][0])**2 + (point[1]-line[0][1])**2)
            d.append(d_temp)
            
        if ax is None:
            fig, ax = plt.subplots()
            
        ax.plot(d, self.dat[loc_ind], label=label)
        ax.set_xlabel("Distance to left end")
        ax.set_ylabel("Elevation")
        ax.grid()
        plt.tight_layout()
        
    def hist(self, dat=None, ax=None, bins=50):
        dat = self.dat if dat is None else dat
        
        dat_array = np.empty(0)
        for i in dat:
            dat_array = np.append(dat_array, np.hstack(i))
        
        if ax is None:
            fig, ax = plt.subplots()

        ax.hist(dat_array, bins=bins, histtype='stepfilled', alpha=1, normed=True)
        ax.set_xlabel("Elevation")
        ax.set_ylabel("PDF")
        # ax.grid()
        plt.tight_layout()
        
    def slice_hist(self, loc, bins=10):
        if not min(self.distance) <= loc <= max(self.distance):
            raise ValueError("Slice location should within the range of swath profile")
        
        loc_ind = np.abs(self.distance - loc).argmin()
        dat = self.dat[loc_ind]
        
        fig, ax = plt.subplots()
        ax.hist(dat, bins=bins, histtype='stepfilled', alpha=1, normed=True)
        ax.set_xlabel("Elevation")
        ax.set_ylabel("PDF")
        ax.grid()
        plt.tight_layout()
    
    def cross_dat(self, dat=None, start=None, end=None):
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
        # start_ind, end_ind = self._segment(start, end)
        dat = self.cross_dat(start=start, end=end)
        
        distance = dat['distance']
        cross = dat['cross_matrix']
        cross_stat = self.profile_stat(cross)
        
        # default to plot all along cross direction
        start = None
        end = None
        
        self.plot(distance, cross_stat, start, end, ax, color)
    
    #TODO: post_tpi and post_elevation           
    def post_tpi(self, radius, min_val=float("-inf"), max_val=float("inf"),
                 start=None, end=None, ax=None, color='navy',
                 cross=False, plot=True):
        start_ind, end_ind = self._segment(start, end)
        
        lines_coord = []
        lines_val = []
        for line_ind, line in enumerate(self.lines):
            coords_temp = []
            points_temp = []
            for point_ind, point in enumerate(line):
                point_val = Tpi(point, self.raster, radius).index
                if min_val <= point_val <= max_val:
                    coords_temp.append(self.lines[line_ind][point_ind])
                    points_temp.append(self.dat[line_ind][point_ind])
             
            lines_coord.append(coords_temp)    
            lines_val.append(points_temp)
        
        distance  = self.distance
        values = lines_val
        
        if cross == True:
           cross_dat = self.cross_dat(lines=lines_coord, dat=lines_val,
                                      start=start, end=end)
           distance = cross_dat['distance']
           values = cross_dat['cross_matrix']
        
        return [distance, values]
        
        if plot == True:
            post_stat = self.profile_stat(values)
            self.plot(distance, post_stat, start, end, ax, color)
        
    def post_elev(self, min_val=float("-inf"), max_val=float("inf"),
                  start=None, end=None, ax=None, color='navy',
                  plot=True):
        if start is not None:
            start = np.abs(self.distance - start).argmin()
        
        if end is not None:
            end = np.abs(self.distance - end).argmin()
            
        lines_val = []
        for line_ind, line in enumerate(self.lines):
            points_temp = []
            for point_ind, point in enumerate(line):
                point_val = Point_elevation(point, self.raster).value
                if min_val <= point_val <= max_val:
                    points_temp.append(self.dat[line_ind][point_ind])
            
            lines_val.append(points_temp)
        
        distance  = self.distance
        
        return [distance, lines_val]
        
        if plot == True:
            post_stat = self.profile_stat(lines_val)
            self.plot(distance, post_stat, start, end, ax, color)
                    
    def post_slope(self, min_val=0., max_val=90.,
                   start=None, end=None, ax=None, color='navy',
                   cross=False, plot=False):                  
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
        



        
        
            
            
            
        
        
