import arcpy
from arcpy import env
from arcpy.sa import *
env.workspace = "D:/#Unpublished/1_Maneri Basin/1_Basin/Basin Shape File"

inRaster = "NonMonsoon_Temperature.tif"
inSQLClause = "VALUE>20"

arcpy.CheckOutExtension("Spatial")

# attExtract = ExtractByAttributes(inRaster, inSQLClause)
# attExtract.save("D:/#Unpublished/1_Maneri Basin/1_Basin/Basin Shape File/useless.tif")
