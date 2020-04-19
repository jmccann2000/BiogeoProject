import numpy as np
import matplotlib.pyplot as plt
import matplotlib as m
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



#Class for bin object on map figure
class bin:
    #object instantiation
    def __init__(self,posX, posY):
        self.x = posX
        self.y = posY
        self.moisture = 0
        self.temperature = 0
        self.elevation = -100

#Class defining plant types for growth display
class plant:
    def __init__(self,preferedTemp,preferedMoist):
        self.temp = preferedTemp
        self.moisture = preferedMoist

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

#Creates array from things in text file
def fileToArray(file_path):
    contents = ""
    #Converts all lines in file to one string
    with open(file_path) as f:
        for line in f.readlines():
            contents += line
    #Splits string into array
    return contents.split(',')

#Generates 100x100 temperature change for elevation
def generateElevationPoints(xPoints,yPoints,shapeData, tree, baseMap):
    counter = 1
    elev_list = []
    for x in np.nditer(xPoints):
        for y in np.nditer(yPoints):
            tempBin = bin(x,y)
            setElevation(tempBin,shapeData,tree,baseMap)
            elev_list.append(tempBin.elevation)
            print('on data: ',counter,' elevation: ',tempBin.elevation)
            counter += 1
    return elev_list


#Sets elevation of bin based on location
def setElevation(bin, shapeData, tree, baseMap):
    binPoint = geom.Point(bin.x,bin.y)
    #Finds nearest geometry to bin location
    if(binPoint.within(baseMap)):
        result = tree.nearest(binPoint)
        closestIndex = shapeData.loc[data['geometry']==result].index[0]
        bin.elevation = shapeData.iloc[closestIndex,0]

#Adjustes temperature for elevation
def tempElevationCorrection(elevation, moisture):
    if moisture < 20:
        #if dry temp changes at rate of 5.4 F per 1000 ft
        return elevation/1000 * 5.4
    else:
        #if wet temp changes at rate of 3.3 F per 1000 ft
        return elevation/1000 * 3.3

def generateTemp(xPoints, yPoints, elevation, moisture):
    temp_list = []
    for x in range(0,np.size(xPoints)):
        for y in range(0,np.size(yPoints)):
            pointElev = elevation[x,y]
            pointMoist = moisture[x,y]
            if pointElev < 0:
                temp = 0
            else:
                temp = tempElevationCorrection(pointElev, pointMoist)
            temp_list.append(temp)
    return temp_list

#Gets top,bottom,left, and right neighor values if present
def getNeighbors(x,y,array):
    returnArray = []
    if(x-1 >= 0):
        returnArray.append(array[x-1,y])
    if(x+1 < array.shape[0]):
        returnArray.append(array[x+1,y])
    if(y-1 >= 0):
        returnArray.append(array[x,y-1])
    if(y+1 < array.shape[1]):
        returnArray.append(array[x,y+1])
    return returnArray


#Generates points with habitability values from 0-10, used for plant spread
def generateHabitability(plant, moistureList, tempAvgList, xVals, yVals):
    habitList = []
    for x in range(0, np.size(xVals)):
        for y in range(0, np.size(yVals)):
            neighborTemps = getNeighbors(x,y,tempAvgList)
            neighborMoist = getNeighbors(x,y,moistureList)
            neighborTempAvg = np.average(neighborTemps)
            neighborMoistAvg = np.average(neighborMoist)

            habitVal = 0

            if abs(neighborMoistAvg - plant.moisture) < 10:
                habitVal = habitVal + 5
            elif abs(neighborMoistAvg - plant.moisture) < 20:
                habitVal = habitVal + 2
            if abs(neighborTempAvg - plant.temp) < 1:
                habitVal = habitVal + 5
            elif abs(neighborTempAvg - plant.temp) < 5:
                habitVal = habitVal + 2

            habitList.append(habitVal)

    return habitList

#Animation for colormap
def animate(day):
    dayTempArray = np.full((np.size(x_grid),np.size(y_grid)),dailyTemp(day))
    dayTempArray[notLandMask] = 0
    actualTemp = np.subtract(dayTempArray,elevChangesCorrected)
    land.set_array(actualTemp[:-1,:-1].flatten('K'))

#Resample elevation grid creation
x_grid = np.arange(738641,813939,1000)
y_grid = np.arange(2277308,2328217,1000)
x_mesh,y_mesh = np.meshgrid(y_grid,x_grid)

#Creates array of elevations
elevData = np.array(fileToArray('elevResample.txt')).astype(np.float)
elevFinal = np.reshape(elevData, (np.size(x_grid),np.size(y_grid)))

#Creates array of moisture
moistData = np.array(fileToArray('moistureResample.txt')).astype(np.float)
moistFinal = np.reshape(moistData, (np.size(x_grid),np.size(y_grid)))

#Mask to array values that are not land
notLandMask = elevFinal < 0

#Creates array of temperature change due to elevation
elevationChanges = np.array(generateTemp(x_grid,y_grid,elevFinal,moistFinal))
elevChangesCorrected = np.reshape(elevationChanges,(np.size(x_grid),np.size(y_grid)))

#Creates 2d array of values for temperature and masks values not on land
dayTempArray = np.full((np.size(x_grid),np.size(y_grid)),dailyTemp(18))
dayTempArray[notLandMask] = 0

#Subtracts elevationTempChange from the current temperature
actualTemp = np.subtract(dayTempArray,elevChangesCorrected)

#Generate habitability
dryPlant = plant(45, 20)
dryHabitability  = generateHabitability(dryPlant, moistFinal, actualTemp, x_grid, y_grid)
dryHabFinal = np.reshape(dryHabitability,(np.size(x_grid),np.size(y_grid)))
dryHabFinal[notLandMask] = -10


#Colormap
cdict = {'red': ((0.0, 0.0, 0.0),
                (0.5, 1.0, 0.5),
                (1.0, 1.0, 0.5)),
         'green': ((0.0, 0.0, 0.0),
                   (0.5, 1.0, 0.0),
                   (1.0, 0.1, 0.0)),
         'blue': ((0.0, 0.0, 0.0),
                  (0.5, 1.0, 0.7),
                  (0.9, 0.2, 0.0),
                  (1.0, 0.0, 0.0))}

my_cmap = m.colors.LinearSegmentedColormap('my_colormap',cdict,256)

fig, ax = plt.subplots(1,1)

#Remove all x and y tick values
ax.set_yticklabels([])
ax.set_xticklabels([])

#Title
ax.set_title('Temperature over year')

#Limits to prevent animation from being shakey
ax.set(xlim=(2277308,2327400), ylim =(738641,813939))

land = ax.pcolormesh(x_mesh,y_mesh,dryHabFinal,cmap = my_cmap, vmin = -10, vmax = 10)
plt.colorbar(land, ax=ax)
#anim = animation.FuncAnimation(fig, animate, interval = 1)
plt.show()
