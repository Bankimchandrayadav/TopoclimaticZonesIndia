# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 14:38:21 2019

@author: bcyadav
"""
#%% Importing libs
import xarray as xr
import os
import numpy as np
import pandas as pd
import openpyxl as oxl


#%% Getting lat lons and station names from an excel file into 3 lists
latlons = pd.read_excel(r"D:\#Unpublished\5_DCompar\Station Data\SatDataAtStations.xlsx")
lats = latlons['lat'].tolist()
lons = latlons['lon'].tolist()
stns = latlons['Name'].tolist()
            
            
#%%  extracting prcp values
def ext():
    ''' function for extracting precipitation values for all files[365] in dir at all station locations 
    (list of lat lons)'''
    prcps = np.zeros((len(ncFiles), len(stns)))
    for n in range(len(stns)):
        print('\n...processing station no. {}: {}'.format(n+1, stns[n]))
        for i in range(len(ncFiles)):
            ds = xr.open_dataset(ncFiles[i]).precipitation
            prcps[i,n] = ds.sel(lon = lons[n], lat = lats[n], method = 'nearest').values
        print('done...moving to next station')
        
    # converting to data frame for easy excel writing
    df = pd.DataFrame(prcps)
    return df
    
    
#%% appending values to an excel file 
def wrt(year):    
    print ('\n\n... writing data to an excel file')
    # changing row and col names of the above data frame
    # changing row names first (dates)
    dates = []
    for j in range(len(ncFiles)):
        dates.append( int(ncFiles[j][-14:-6]) )
    df.index = dates
    # then col names
    df.columns = stns
    # write this df to excel 
    workbook1 = oxl.load_workbook('trmm_daily.xlsx')
    writer = pd.ExcelWriter('trmm_daily.xlsx', engine='openpyxl') 
    writer.book = workbook1
    df.to_excel( writer, sheet_name=year )
    writer.save()
    writer.close()
    print('...done')
    
    
#%% script starts here
#%% here we just need to change the ws and hence sheet name in excel workbook loaded
ws = r"D:\#Unpublished\1_Maneri Basin\Data\TRMM_NETCDF\Daily_1998-2009\1998"
ncFiles = []
for dirpath, subdir, files in os.walk(ws):
    for file in files:
        file = os.path.join(dirpath, file)
        if file.upper().endswith('.NC4'):
            ncFiles.append(file)

#%% call this fun to extract prcp values     
df = ext()

#%% call this fun to write result into excel file 
year = '1998' 
wrt(year)

