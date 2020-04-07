import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import shapefile as shp
import shapely.geometry as geom
from shapely.ops import polygonize
import geopandas as gpd


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

#sets elevation of bin based on how many polygons the bin is contained in
def setElevation(polygons,bin):
    containCount = 0
    binLoc = Point(bin.x,bin.y)
    for shape in polygons:
        if binLoc.within(shape):
            containCount += 1
    return containCount

#Maui elevation map shape file
sf = shp.Reader("NewElevation/Maui_Elevation_contours_100ft.shp")
#plots shapefile
#fig = plt.figure()
#rect = fig.patch
#list of polygons equal to topography lines
#elevLines = []

for shape in sf.shapeRecords():
    x = [i[0]- 740134 for i in shape.shape.points[:]]
    y = [i[1]- 2277470 for i in shape.shape.points[:]]

#    #Creates tuple (x,y) for creating Polygons
#    coordPairs = [(x[i],y[i]) for i in range(0, len(x))]
#    tempLine = LineString(coordPairs)
#    elevLines.append(tempLine)
    plt.plot(x,y,'c',linewidth = 0.3)
#
#elevPolygons = polygonize(elevLines)
#for shape in elevPolygons:
#    x,y =shape.exterior.xy
#    plt.plot(x,y,'c',linewidth = 0.3)
#testBin = bin(38468.5,23767.1)
#factor = setElevation(elevPolygons,testBin)
#print(factor)
plt.show()
