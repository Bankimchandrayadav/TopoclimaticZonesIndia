import arcpy
import os

arcpy.CheckOutExtension("Spatial")
arcpy.env.overwriteOutput = True
ws = r'D:\#Unpublished\1_Maneri Basin\Data\TRMM_NETCDF\JA_only'

walk = arcpy.da.Walk(ws, topdown=True, datatype="RasterDataset")
for dirpath, dirnames, filenames in walk:
    print "Processing folder:", dirpath

    rasters = []
    for filename in filenames:
        tifname = dirpath[-4:]
        raster = os.path.join(dirpath, filename)
        if filename.upper().endswith('.TIF'):
            if filename.upper().startswith('SUM') == False:
                rasters.append(raster)
    print " - rasters found:", len(rasters)

    if len(rasters) != 0:
        print " - calculating sum..."
        ras_cal = arcpy.sa.CellStatistics(rasters, "MEAN", "DATA")
        ras_cal_name = os.path.join(dirpath,'mean_{0}.tif'.format(tifname))
        ras_cal.save(ras_cal_name)
        print " - performing cell statistics:", ras_cal_name
    else:
        print " - skipping folder..."

print "Finished..."


