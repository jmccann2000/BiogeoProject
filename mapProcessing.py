import numpy as np
import matplotlib.pyplot as plt
import elevation
import math
import shapefile as shp

#Class for bin object on map figure
class bin:
    #object instantiation
    def __init__(self,posX, posY):
        self.x = posX
        self.y = posY
        self.moisture = 0
        self.temperature = 0
        self.elevation = 0

    #Determines if bin is considered dry
    def isDry(self):
        returnVal = True
        if(self.moisture > 5):
            returnVal = False
        return returnVal

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

#Adjustes temperature for elevation, implement later, probably needs to be in class "bin"
#def tempElevationCorrection(hourTemp,elevation):

#Maui elevation map shape file
sf = shp.Reader("maucntrs100.shp/maucntrs100.shp")

#plots shapefile
plt.figure()
for shape in sf.shapeRecords():
    x = [i[0] for i in shape.shape.points[:]]
    y = [i[1] for i in shape.shape.points[:]]
    plt.plot(x,y)
plt.show()
