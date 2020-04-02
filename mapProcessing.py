import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import elevation
import math
import shapefile as shp

#Class for bin object on map figure
class bin:
    #object instantiation
    def __init__(self,posX, posY):
        testBin.elevation = 2000
        testBin.temperature = 50
        testBin.tempElevationCorrection()
        self.assertEquals(testBin.temperature,56.6)

        self.x = posX
        self.y = posY
        self.moisture = 0
        self.temperature = 0
        self.elevation = 0

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

#Maui elevation map shape file
sf = shp.Reader("../maucntrs100/maucntrs100.shp")

#plots shapefile
fig = plt.figure()
rect = fig.patch

for shape in sf.shapeRecords():
    x = [i[0] for i in shape.shape.points[:]]
    y = [i[1] for i in shape.shape.points[:]]
    plt.plot(x,y,'c',linewidth = 0.3)
plt.show()
