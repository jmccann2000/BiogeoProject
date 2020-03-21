from osgeo import gdal
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import elevation

#http://planning.hawaii.gov/gis/download-gis-data/ contains maui gis data

fileName = "hillmau.tif\hillmau.tif"
gdalData = gdal.Open(fileName)
gdalBand = gdalData.GetRasterBand(1)
noDataVal = gdalBand.GetNoDataValue()

#Convert to numpy arary
dataArray = gdalData.ReadAsArray().astype(np.float)
dataArray

#Plot out data with Matplotlib's 'contour'
fig = plt.figure(figsize = (24, 16))
ax = fig.add_subplot(111)
plt.contour(dataArray, cmap = "viridis",
            levels = list(range(0, 1500, 100)))
plt.title("Elevation Contours of Maui, Hawaii")
cbar = plt.colorbar()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()
