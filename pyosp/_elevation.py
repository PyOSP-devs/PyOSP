# -*- coding: utf-8 -*-

class Point_elevation():
    def __init__(self, point, raster):
        self.p = point
        self.raster = raster
        self.geoTransform = self.raster.GetGeoTransform()

    def point_position(self):
        x = int((self.p[0] - self.geoTransform[0]) / self.geoTransform[1])
        y = int((self.geoTransform[3] - self.p[1]) / -self.geoTransform[5])
        return x, y
    
    @property
    def value(self):
        px, py = self.point_position()
        return self.raster.ReadAsArray(px, py, 1, 1)
