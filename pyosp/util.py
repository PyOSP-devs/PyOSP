# -*- coding: utf-8 -*-

# import gdal
import ogr
import json
import itertools
from shapely.geometry import shape
import numpy as np
import sys

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def grouped(iterable):
    "s -> (s0, s1), (s2, s3), (s4, s5), ..."
    a = iter(iterable)
    return zip(a, a)

def read_shape(shapefile):
    file = ogr.Open(shapefile)
    layer = file.GetLayer(0)
    feature = layer.GetFeature(0)
    read = feature.ExportToJson()
    outshape = shape(json.loads(read)["geometry"])
    return outshape

def point_coords(shapefile):
    file = ogr.Open(shapefile)
    layer = file.GetLayer(0)
    coords = []
    for feature in layer:
        read = feature.ExportToJson()
        coords.append(json.loads(read)["geometry"]['coordinates'])
        
    return coords

def write_polygon(poly, out_file):
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(out_file)
    layer = ds.CreateLayer('', None, ogr.wkbPolygon)
    # Add one attribute
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    defn = layer.GetLayerDefn()
    
    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', 1)

    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(poly.wkb)
    feat.SetGeometry(geom)
    
    layer.CreateFeature(feat)

    # Save and close everything
    ds = layer = feat = geom = None
    
def write_polylines(poly, out_file):
    driver = ogr.GetDriverByName('Esri Shapefile')
    ds = driver.CreateDataSource(out_file)
    layer = ds.CreateLayer('', None, ogr.wkbLineString)
    # Add one attribute
    layer.CreateField(ogr.FieldDefn('id', ogr.OFTInteger))
    defn = layer.GetLayerDefn()
    
    # Create a new feature (attribute and geometry)
    feat = ogr.Feature(defn)
    feat.SetField('id', 1)

    # Make a geometry, from Shapely object
    geom = ogr.CreateGeometryFromWkb(poly.wkb)
    feat.SetGeometry(geom)
    
    layer.CreateFeature(feat)

    # Save and close everything
    ds = layer = feat = geom = None
    
def progressBar(current, total, width=25):
    bar_width = width
    block = int(round(bar_width * current/total))
    text = "\rProcessing: [{0}] {1} of {2} lineSteps".\
             format("#"*block + "-"*(bar_width-block), current, total)

    sys.stdout.write(text)
    sys.stdout.flush()  
 
def geo_slope(point, raster, cell_size):
    geoTransform = raster.GetGeoTransform()
    px = int((point[0] - geoTransform[0]) / geoTransform[1])
    py = int((geoTransform[3] - point[1]) / -geoTransform[5])
    
    rasterMatrix = raster.ReadAsArray()
    #pad to the edge
    rasterPad = np.pad(rasterMatrix, (1,), 'edge')  
    window = rasterPad[py:py+3, px:px+3]
    
    rise = ((window[0,2] + 2*window[1,2] + window[2,2]) -
            (window[0,0] + 2*window[1,0] + window[2,0])) / \
           (8 * cell_size)
    run =  ((window[2,0] + 2*window[2,1] + window[2,2]) -
            (window[0,0] + 2*window[0,1] + window[0,2])) / \
           (8 * cell_size)
    dist = np.sqrt(np.square(rise) + np.square(run))
    
    return np.arctan(dist)*180 / np.pi
    
    