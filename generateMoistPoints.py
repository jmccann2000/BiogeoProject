import numpy as np
import matplotlib.pyplot as plt
import matplotlib as m
#m.use("Agg")

import matplotlib.animation as animation
import math
import shapefile as shp
import shapely.geometry as geom
from shapely.ops import polygonize
from shapely.strtree import STRtree
import shapely.wkt
import geopandas as gpd
import pandas as pd
import rasterio
from scipy import interpolate



class bin:
    #object instantiation
    def __init__(self,posX, posY):
        self.x = posX
        self.y = posY
        self.moisture = 0
        self.temperature = 0
        self.elevation = -100

def setMoisture(bin, shapeData, tree, baseMap):
    binPoint = geom.Point(bin.x,bin.y)
    if baseMap.contains(binPoint):
        result = tree.nearest(binPoint)
        closestIndex = shapeData.loc[shapeData['geometry']==result].index[0]
        bin.moisture = shapeData.iloc[closestIndex,0]

#Generates moisture values for every point in mesh
def generateMoisturePoints(xPoints,yPoints,shapeData, tree, baseMap):
    counter = 1
    moist_list = []
    for x in np.nditer(xPoints):
        for y in np.nditer(yPoints):
            tempBin = bin(x,y)
            setMoisture(tempBin,shapeData,tree,baseMap)
            moist_list.append(tempBin.moisture)
            print('on data: ',counter,' moisture: ',tempBin.moisture)
            counter += 1
    return moist_list

#Maui moisture data
fp = "maucntrs100.shp/maucntrs100.shp"
data = gpd.read_file(fp)


x_grid = np.arange(738641,813939,1000)
y_grid = np.arange(2277308,2328217,1000)

#Maui moisture data
#Reades in polygon for Moisture of maui
file1 = open('moisturePolygons', 'r')
Lines = file1.readlines()

moistPolys = []

for line in Lines:
    if("POLYGON" in line):
        tempPoly = shapely.wkt.loads(line)
        moistPolys.append(tempPoly)

df = pd.DataFrame({'moisture': [0,10,20,20,30,30,40,50,60,60,70,70],
                    'geometry': moistPolys})
gdf = gpd.GeoDataFrame(df, geometry = 'geometry')

geoSet = gdf['geometry']
geoTree = STRtree(geoSet)

with open('base.txt', 'r') as file:
    baseData = file.read()

mauiBase = shapely.wkt.loads(baseData)

bruh = generateMoisturePoints(x_grid,y_grid, gdf, geoTree, mauiBase)
print(bruh)
