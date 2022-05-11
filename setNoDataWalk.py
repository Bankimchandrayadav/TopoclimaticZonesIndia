# -*- coding: utf-8 -*-
"""
Created on Wed Oct 17 21:24:00 2019
Modified on Thu Oct 31 12:51:00 2019
@author: bcyadav
Source: https://gis.stackexchange.com/questions/163685/reclassify-a-raster-value-to-9999-and-set-it-to-the-nodata-value-using-python-a/163705
"""

#%% importing req libs
from osgeo import gdal
import numpy as np
import os

#%% function to read the geotiff file
def readFile(filename):
    # returns xsize, ysize, geotransform, geoprojection and data values of the band
    dsIn = gdal.Open(filename)
    band = dsIn.GetRasterBand(1)
    
    
    return dsIn.RasterXSize, dsIn.RasterYSize, dsIn.GetGeoTransform(), dsIn.GetProjection(), band.ReadAsArray()

    # if projection needs to be taken from external file

#    file_ext = gdal.Open(r'D:\#Unpublished\5_DCompar\CHIRPS Data\Final Data\1_JAN_MEAN_CHIRPS.tif')
#    return dsIn.RasterXSize, dsIn.RasterYSize, dsIn.GetGeoTransform(), file_ext.GetProjection(), band.ReadAsArray()



#%% function to write the modified file
def writeFile(filename, geotransform, geoproj, arr):
    # reading argument attributes
    (x,y) = arr.shape
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    outDataType = gdal.GDT_Float32
    
    # creating out file
    dsOut = driver.Create(filename, y, x, 1, outDataType)
    dsOut.GetRasterBand(1).WriteArray(arr)
    dsOut.SetGeoTransform(geotransform)
    dsOut.SetProjection(geoproj)
    dsOut.GetRasterBand(1).SetNoDataValue(-9999.0)

#%% script starts here

rootDir = r'D:\#Unpublished\1_Maneri Basin\Data\HAR10\yearly'
c = 0
for dirname, subdirnames, filenames in os.walk(rootDir):
    print('='*70,'\nFound directory: {}'.format(dirname))
    print('No. of subdirectories here: {}'.format(len(subdirnames)))
    print('All files here: {}\n'.format(len(filenames)))
    for filename in filenames:
        filename = os.path.join(dirname, filename)
        if filename.upper().endswith('TIF'):
            
            # reading file
            print('reading file: {}'.format(filename))
            [xsize,ysize,geotransform,geoproj,arr] = readFile(filename)
            
            # setting data value <0 to np.NaN
            arr[arr<0] = -9999.0
            
            # writing file
            print('setting no data and overwriting ...')
            writeFile(filename, geotransform, geoproj, arr)
            print('done\n')
            c+=1
print('='*70,'\nTotal files processed: {} ... leaving now... nice working with you'.format(c),'='*70)
#%%







































    
    
    