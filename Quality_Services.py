import requests, arcpy
import numpy as np

SERVICES_URL = "https://lpdaacsvc.cr.usgs.gov/services/appeears-api/"

''' list all available products that can be decoded '''
def listProducts():
    productInfo = requests.get('{}/quality?format=json'.format(SERVICES_URL)).json()
    productList = list(set(i[1] for l in productInfo for i in l.items() if i[0] == 'ProductAndVersion'))
    return(sorted(productList))
	
''' list all quality layers associated with a product '''
def listQALayers(product):
    qaLayerInfo = requests.get('{}/quality/{}?format=json'.format(SERVICES_URL, product)).json()
    qaLayerList = list(set(l[0] for i in qaLayerInfo for k, l in i.items() if k == 'QualityLayers'))
    return(qaLayerList)
    
''' get list of bit-field names '''
def listQualityBitField (product, qualityLayer):
    bitFieldInfo = requests.get('{}/quality/{}/{}?format=json'.format(SERVICES_URL, product, qualityLayer)).json()
    bitFieldNames = list(set(i[1] for l in bitFieldInfo for i in l.items() if i[0] == 'Name'))
    return bitFieldNames
    
''' Specify whether the user is interested in all of the bit fields or
a single bit field. Default is set to all. '''
def defineQualityBitField(product, qualityLayer, bitField = 'ALL'):
    if bitField == 'ALL':
        return listQualityBitField(product, qualityLayer)
    else:
        return [bitField]
        
''' Function to assemble the output raster path and name '''
def outName(outputLocation, outputName, bitField):
    bf = bitField.replace(' ', '_').replace('/', '_')
    outputFileName = '{}/{}_{}.tif'.format(outputLocation, outputName, bf)
    return outputFileName
    
''' Function to decode the input raster layer. Requires that an empty
qualityCache dictionary variable is created. '''
def qualityDecodeInt(product, qualityLayer, intValue, bitField, qualityCache):
    quality = None
    if intValue in qualityCache:
        quality = qualityCache[intValue]
    else:
        quality = requests.get('{}/quality/{}/{}/{}?format=json'.format(SERVICES_URL, product, qualityLayer, intValue)).json()
        qualityCache[intValue] = quality
    return int(quality[bitField]['bits'][2:])
    #return quality[bitField]['description'], int(quality[bitField]['bits'][2:])
    
''' Function to decode an input array '''
def qualityDecodeArray(product, qualityLayer, intValue, bitField, qualityCache):
    qualityDecodeInt_Vect = np.vectorize(qualityDecodeInt)
    qualityDecodeArr = qualityDecodeInt_Vect(product, qualityLayer, intValue, bitField, qualityCache)
    return qualityDecodeArr
    
def qualityDecoder(inRst, outWorkspace, outFileName, product, qualityLayer, bitField):
    SERVICES_URL = "https://lpdaacsvc.cr.usgs.gov/services/appeears-api/"
    ''' Read in the input raster layer. '''
    inRaster = arcpy.Raster(inRst)
    
    ''' Get spatial reference info for inRaster '''
    spatialRef = arcpy.Describe(inRaster).spatialReference
    cellSize = arcpy.Describe(inRaster).meanCellWidth
    extent = arcpy.Describe(inRaster).Extent
    llc = arcpy.Point(extent.XMin,extent.YMin)
    noDataVal = inRaster.noDataValue
    
    ''' Convert inRaster to a Numpy Array. '''
    inArray = arcpy.RasterToNumPyArray(inRaster)
    
    # ClEAN-UP
    inRaster = None
    
    bitFieldList = defineQualityBitField(product, qualityLayer, bitField)
    # Set up a cache to store decoded values
    qualityCache = {}
    ''' Loop through all of the bit fields or execute on the specified 
    bit field. '''
    for f in bitFieldList:
        qualityDecoded = qualityDecodeArray(product, qualityLayer, inArray, f, qualityCache)
        qualityRaster = arcpy.NumPyArrayToRaster(qualityDecoded, llc, cellSize, cellSize)
        qualityDecoded = None
        arcpy.DefineProjection_management(qualityRaster, spatialRef)
        qualityRaster.save(outName(outWorkspace, outFileName, f))
        qualityRaster = None
        ''' Edit raster attribute table '''
        # Get all the quality information from the quality cache and pull
        # out unique values for the bit field... See: http://stackoverflow.com/questions/6280978/how-to-uniqify-a-list-of-dict-in-python
        qualityAttributes = [dict(y) for y in set(tuple(i[f].items()) for i in qualityCache.values())]
        r = outName(outWorkspace, outFileName, f)
        arcpy.AddField_management(r, "Descr", "TEXT", "","", 150)
        fields = ("Value", "Descr")
        with arcpy.da.UpdateCursor(r, fields) as cursor:
            for row in cursor:
                for q in qualityAttributes:
                    if row[0] == int(q['bits'][2:]):
                        row[1] = q['description']
                        cursor.updateRow(row)
                    else:
                        continue