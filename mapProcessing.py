import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import shapefile as shp
import shapely.geometry as geom
from shapely.ops import polygonize
from shapely.strtree import STRtree
import geopandas as gpd
import gdal
import rasterio


#Class for bin object on map figure
class bin:
    #object instantiation
    def __init__(self,posX, posY):
        self.x = posX
        self.y = posY
        self.moisture = 0
        self.temperature = 0
        self.elevation = 0
        self.xRange = (posX-1,posX+1)
        self.yRange = (posY-1,posY-1)

    #Adjustes temperature for elevation
    def tempElevationCorrection(self):
        if self.elevation >= 1000 :
            if self.moisture < 5:
                #if dry temp changes at rate of 5.4 F per 1000 ft
                self.temperature += self.elevation/1000 * 5.4
            else:
                #if wet temp changes at rate of 3.3 F per 1000 ft
                self.temperature += self.elevation/1000 * 3.3

#Generates daily temperature for year
#alter cosine function to have a period of 365, and range from [73,93]
def dailyTemp(day):
    trigInput = (day*2*math.pi)/365
    dayTemp = math.cos(trigInput)*-10+83
    return dayTemp

#Generates hourly temperature for day
#alter cosine function to have period of 24, and range from [dayTemp-2,dayTemp+2]
def hourlyTemp(dayTemp,hour):
    trigInput = (hour*math.pi)/12
    hourTemp = math.cos(trigInput)*-2+dayTemp
    return hourTemp

#Sets elevation of bin based on location
def setElevation(bin, data):
    geoSet = data['geometry']
    geoTree = STRtree(geoSet)
    binPoint = geom.Point(bin.x,bin.y)
    #Finds nearest geometry to bin location
    result = geoTree.nearest(binPoint)
    #Parses geopanda to find location of result also getting elevation
    for index, row in data.iterrows():
        if row['geometry'] == result:
            bin.elevation = row['CONTOUR']

#Maui elevation map shape file
fp = "maucntrs100.shp/maucntrs100.shp"
data = gpd.read_file(fp)

testBin = bin(767479,2320580)
setElevation(testBin,data)
print(testBin.elevation)

#print(data['geometry'])
fig, ax = plt.subplots(1,1)

data.plot(column = 'CONTOUR',ax=ax, legend = True,linewidth = 0.3)
plt.show()
