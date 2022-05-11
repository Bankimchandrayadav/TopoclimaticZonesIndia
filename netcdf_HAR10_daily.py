# -*- coding: utf-8 -*-
"""
Created on Tue Nov 9 14:35:21 2019

@author: bcyadav
"""
#%% Importing libs
import xarray as xr
import os
import numpy as np
import pandas as pd
import openpyxl as oxl


#%% Getting lat lons and station names from an excel file into 3 lists
def readL(srcfile):
    latlons = pd.read_excel(srcfile)
    lats = latlons['lat'].tolist()
    lons = latlons['lon'].tolist()
    stns = latlons['Name'].tolist()

    return lats, lons, stns


#%%  extracting prcp values
def ext(year):
    '''extracts prcp values'''
    # read data array
    ds = xr.open_dataset('har_d10km_d_2d_prcp_{}.nc'.format(year)).prcp
    # make an empty np array
    prcps = np.zeros((len(ds.time), len(stns)))
    # read lat and lon arrays from dataset
    lon_arr = ds.lon.values
    lat_arr = ds.lat.values
    # loop over stations (46 here)
    for n in range(len(stns)):
        print('\n...processing station no. {}: {}'.format(n+1, stns[n]))
        
        # find lat lon matching with that of station
        dist_sq = (lat_arr-lats[n])**2 + (lon_arr-lons[n])**2
        [row, col] = np.where(dist_sq == dist_sq.min())
        
        # loop over dates (365/366)
        for i in range(len(ds.time)):
            prcps[i,n] = ds.isel(time = i).values[row,col]
        print('done...moving to next station')
        
    # convert fromm mm/hr to mm/day
    prcps *=24
    # converting to data frame for easy excel writing
    df = pd.DataFrame(prcps)
    df.index = ds.time.values
    df.columns = stns
    return df

    
    
#%% appending values to an excel file 
def wrt(year):    
    
    print ('\n\n... writing data to an excel file')
    
    workbook1 = oxl.load_workbook('har10daily.xlsx')
    writer = pd.ExcelWriter('har10daily.xlsx', engine='openpyxl') 
    writer.book = workbook1
    df.to_excel( writer, sheet_name = year )
    writer.save()
    writer.close()
    print('...done')
    
    
#%% script starts here
# source file of stn lat lons
srcfile =  r"D:\#Unpublished\5_DCompar\Station Data\SatDataAtStations.xlsx"
lats, lons, stns = readL(srcfile) # reads lat lons of stations

# year for processing
year = '2005' 
df = ext(year) # extracts data from data arrays
wrt(year) # writes extracted data to excel

