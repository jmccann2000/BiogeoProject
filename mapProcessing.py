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

def avgTemp(elevChanges):
    averageTemp = np.zeros((np.size(x_grid),np.size(y_grid)))
    for day in range(0,365):
        dayTempArray = np.full((np.size(x_grid),np.size(y_grid)),dailyTemp(day))
        actualTemp = np.subtract(dayTempArray,elevChanges)
        averageTemp = np.add(averageTemp, actualTemp)

    divisorForAvg = np.full((np.size(x_grid),np.size(y_grid)),365)
    finalAvgTemp = np.divide(averageTemp,divisorForAvg)

    return finalAvgTemp

#Generates points with habitability values from 0-10, used for plant spread
#also propagates disctionary with x,y position and habitability
def generateHabitability(dict,plant, moistureList, tempAvgList, xVals, yVals):
    habitList = []
    for x in range(0, np.size(xVals)):
        for y in range(0, np.size(yVals)):
            neighborTemps = getNeighbors(x,y,tempAvgList)
            neighborMoist = getNeighbors(x,y,moistureList)
            neighborTempAvg = np.average(neighborTemps)
            neighborMoistAvg = np.average(neighborMoist)

            habitVal = 0

            if abs(neighborMoistAvg - plant.moisture) < 10 and abs(neighborTempAvg - plant.temp) < 2:
                habitVal = habitVal + 5
            elif abs(neighborMoistAvg - plant.moisture) < 30 and abs(neighborTempAvg - plant.temp) < 2:
                habitVal = habitVal + 2
            elif abs(neighborMoistAvg - plant.moisture) < 20 and abs(neighborTempAvg - plant.temp) < 7:
                habitVal = habitVal + 2

            dict[(x,y)] = habitVal

            habitList.append(habitVal)

    return habitList

#CalculatesDistance between points
def calculateDistance(x1,y1,x2,y2):
     dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
     return dist

def closestPop(pointX,pointY):
    minDist = 1000
    global currentPopulation
    if(currentPopulation[pointX,pointY] == 0):
        for x in range(0, currentPopulation.shape[0]):
            for y in range(0, currentPopulation.shape[1]):
                if(currentPopulation[x,y] > 500):
                    tempDist = calculateDistance(pointX,pointY,x,y)
                    if(tempDist<minDist):
                        minDist = tempDist
    return minDist
#Searches map for closest habitable area, used in determining if plant can survive to make it to new area
def nearestHabitat(dict, habitArray):
    closestDist = 100
    closestPoint = (18,35)

    global notLandMask
    global currentPopulation
    for x in range(0, habitArray.shape[0]):
        for y in range(0, habitArray.shape[1]):
            if(not notLandMask[x,y]):
                keyVal = dict.get((x,y))
                if(keyVal > 0):
                    dist = closestPop(x,y)
                    if(dist < closestDist):
                        closestDist = dist
                        closestPoint = (x,y)
    return closestPoint, closestDist

#Spreads population to habitable area if close enough
def popDispersal(population,habitability):
    global posHabitDict
    global notLandMask

    nearestPoint,distance = nearestHabitat(posHabitDict,habitability)
    if(distance < 10):
        population[nearestPoint[0],nearestPoint[1]] = 100

#Handles when population would spread to neighboring points
def populationSpread():
    global currentPopulation
    for x in range(0, currentPopulation.shape[0]):
        for y in range(0, currentPopulation.shape[1]):
            if(currentPopulation[x,y] == 0):
                neighbors = np.asarray(getNeighbors(x,y,currentPopulation))
                popHab = np.where(neighbors>=500)
                if(np.size(popHab) > 0):
                    currentPopulation[x,y] = 100

#Animation for temperature
def animateTemp(day):
    dayTempArray = np.full((np.size(x_grid),np.size(y_grid)),dailyTemp(day))
    actualTemp = np.subtract(dayTempArray,elevChangesCorrected)
    actualTemp[notLandMask] = 0
    land.set_array(actualTemp[:-1,:-1].flatten('K'))

#Animation for population
def animateGrowth(day):
    global currentPopulation
    global growthRates
    global testHabFinal
    global maxPopulation
    prevDayPop = currentPopulation.copy()
    #Prevents populations over max population
    popMaxMask = currentPopulation < maxPopulation
    #Spreads population
    populationSpread()
    #Changes population for day
    np.multiply(currentPopulation, growthRates,out = currentPopulation, where = popMaxMask)
    #Makes sure not land is visually distinct
    currentPopulation[notLandMask] = -1000

    if(np.array_equal(prevDayPop, currentPopulation)):
        popDispersal(currentPopulation,testHabFinal)

    land.set_array(currentPopulation[:-1,:-1].flatten())

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

#Average year temp of every point, used for creating ranges
yearAvgTemp = avgTemp(elevChangesCorrected)
yearAvgTemp[notLandMask] = 0

#Creates 2d array of values for temperature and masks values not on land
dayTempArray = np.full((np.size(x_grid),np.size(y_grid)),dailyTemp(18))
dayTempArray[notLandMask] = 0

#Subtracts elevationTempChange from the current temperature
actualTemp = np.subtract(dayTempArray,elevChangesCorrected)

#Dict of all points with habitabilities
posHabitDict = {}

#Generate habitability
testPlant = plant(80, 20)
testHabitability  = generateHabitability(posHabitDict,testPlant, moistFinal, yearAvgTemp, x_grid, y_grid)
testHabFinal = np.reshape(testHabitability,(np.size(x_grid),np.size(y_grid)))
testHabFinal[notLandMask] = -10

#Creation of array containing max populations
maxPopulation = np.zeros((np.size(x_grid),np.size(y_grid)))

goodHabMask = testHabFinal == 5
medHabMask = testHabFinal == 2

maxPopulation[goodHabMask] = 4000
maxPopulation[medHabMask] = 2500

#Creation of array of rates to multiply population by to get growth every day
growthRates = np.zeros((np.size(x_grid),np.size(y_grid)))
growthRates[goodHabMask] = 10
growthRates[medHabMask] = 5

#Array used for tracking population on a given day
currentPopulation = np.zeros((np.size(x_grid),np.size(y_grid)))
currentPopulation[notLandMask] = -1000
currentPopulation[18,35] = 100

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

#my_cmap = m.colors.LinearSegmentedColormap('my_colormap',cdict,256)

earthColor = plt.cm.get_cmap('gist_earth')

fig, ax = plt.subplots(1,1)

#Remove all x and y tick values
ax.set_yticklabels([])
ax.set_xticklabels([])

#Title
ax.set_title('Temperature over year')

#Limits to prevent animation from being shakey
ax.set(xlim=(2277308,2327400), ylim =(738641,813939))

land = ax.pcolormesh(x_mesh,y_mesh,currentPopulation,cmap = earthColor.reversed(), vmin = -1000, vmax = 6000)
plt.colorbar(land, ax=ax)
anim = animation.FuncAnimation(fig, animateGrowth, interval = 50)
plt.show()
