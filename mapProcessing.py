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
        self.xRange = (posX-1,posX+1)
        self.yRange = (posY-1,posY-1)

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
def tempElevationCorrection(elevation):
    #if self.moisture < 5:
        #if dry temp changes at rate of 5.4 F per 1000 ft
    return elevation/1000 * 5.4
    #else:
        #if wet temp changes at rate of 3.3 F per 1000 ft
    #    return elevation/1000 * 3.3

def generateTemp(xPoints, yPoints, elevation):
    temp_list = []
    for x in range(0,np.size(xPoints)):
        for y in range(0,np.size(yPoints)):
            pointElev = elevation[x,y]
            if pointElev < 0:
                temp = 0
            else:
                temp = tempElevationCorrection(pointElev)
            temp_list.append(temp)
    return temp_list

#Animation for colormap
def animate(day):
    dayTempArray = np.full((np.size(x_grid),np.size(y_grid)),dailyTemp(day))
    dayTempArray[mask] = 0
    actualTemp = np.subtract(dayTempArray,elevChangesCorrected)
    land.set_array(actualTemp[:-1,:-1].flatten('K'))

#Resample elevation grid creation
x_grid = np.arange(738641,813939,1000)
y_grid = np.arange(2277308,2328217,1000)
x_mesh,y_mesh = np.meshgrid(y_grid,x_grid)

#Creates array of elevations
elevData = np.array(fileToArray('elevResample.txt')).astype(np.float)
elevReshape = np.reshape(elevData, (np.size(x_grid),np.size(y_grid)))
elevFinal = np.rot90(elevReshape, 2)

#Mask to array values that are not land
mask = elevFinal < 0

#Creates array of temperature change due to elevation
elevationChanges = np.array(generateTemp(x_grid,y_grid,elevFinal))
elevChangesCorrected = np.reshape(elevationChanges,(np.size(x_grid),np.size(y_grid)))

#Creates 2d array of values for temperature and masks values not on land
dayTempArray = np.full((np.size(x_grid),np.size(y_grid)),dailyTemp(18))
dayTempArray[mask] = 0

#Subtracts elevationTempChange from the current temperature
actualTemp = np.subtract(dayTempArray,elevChangesCorrected)

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

fig, ax = plt.subplots(2,2, constrained_layout=True)

#Remove all x and y tick values
ax[0,0].set_yticklabels([])
ax[0,0].set_xticklabels([])
ax[0,1].set_yticklabels([])
ax[0,1].set_xticklabels([])
ax[1,1].set_yticklabels([])
ax[1,1].set_xticklabels([])
ax[1,0].set_yticklabels([])
ax[1,0].set_xticklabels([])

#Titles of subplots
ax[0,0].set_title('Plant Coverage')
ax[0,1].set_title('Temperature (F)')
ax[1,1].set_title('Plant Data')
ax[1,0].set_title('Moisture')

ax[0,1].set(xlim=(2277308,2327400), ylim =(738641,813939))

land = ax[0,1].pcolormesh(x_mesh,y_mesh,actualTemp,cmap = my_cmap, vmin = 0, vmax = 75)
plt.colorbar(land, ax=ax[0,1])
anim = animation.FuncAnimation(fig, animate, interval = 1)
plt.show()
#anim.save('myAnimation.gif', writer='imagemagick', fps=30)



#Reades in polygon for basemap of maui
#with open('base.txt', 'r') as file:
#    baseData = file.read()
#
#mauiBase = shapely.wkt.loads(baseData)
