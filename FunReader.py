import numpy as np
import haversine
import json
from datetime import datetime, timedelta, timezone
import os
import scipy.interpolate
from Encoders import NumpyEncoder


# Here I will write about the fort files

# Fort 74 contains an hour by hour forecast with the wind vector x and y components

# The time is measured in seconds coldstartdate + time = time of forecast
# To access metadata of fort files, use dataset.__dict__ variable on netCDF dataset
# key rundes contains information with coldstart date
# To see dimensions of variables, use dataset.dimensions
# To see information on variables, use dataset.variables
# To get data for a variable, use dataset.variables["time"]

# FORT_74_FILE_NAME = "112123.fort.74.nc"
# FORT_74_FILE_NAME = "ricv1_122223_fort.74.nc"
# FORT_74_FILE_NAME = "ec95d_120923_fort.74.nc"
# FORT_74_FILE_NAME = "ec95d_120923_forecast_fort.74.nc"
# FORT_74_FILE_NAME = "ricv1_postnotworking_fort.74.nc"
# FORT_74_FILE_NAME = "Lee_Floodwater_LeftTrack_Advisory36_fort.74.nc"
# NOS_STATIONS_FILE_NAME = "NOS_Stations.json"
# NOS_STATION_TO_NODE_DISTANCES_FILE_NAME = "NOS_Station_To_Node_Distances.json"
# NOS_ADCIRC_NODES_FILE_NAME = "NOS_ADCIRC_Nodes.json"
# NOS_ADCIRC_WIND_DATA_FILE_NAME = "NOS_ADCIRC_Wind_Data.json"
# NOS_ADCIRC_NODES_WIND_DATA_FILE_NAME = "NOS_ADCIRC_Nodes_Wind_Data.json"
# NOS_STATION_TO_NODE_DISTANCES_FILE_NAME = "NOS_Station_To_Floodwater_Node_Distances.json"
# NOS_ADCIRC_NODES_FILE_NAME = "NOS_Floodwater_Nodes.json"
# NOS_ADCIRC_WIND_DATA_FILE_NAME = "NOS_Floodwater_Wind_Data.json"
# NOS_ADCIRC_NODES_WIND_DATA_FILE_NAME = "NOS_Floodwater_Nodes_Wind_Data.json"
class FunReader:
    def __init__(self, STATIONS_FILE="", STATION_TO_NODE_DISTANCES_FILE="", NODES_FILE="", BACKGROUND_AXIS=[]):
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = STATION_TO_NODE_DISTANCES_FILE
        self.NODES_FILE = NODES_FILE
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
    def extractLatitudeIndex(self, nodeIndex):
        return int(nodeIndex[1: nodeIndex.find(",")])
    def extractLongitudeIndex(self, nodeIndex):
        return int(nodeIndex[nodeIndex.find(",") + 1: nodeIndex.find(")")])
        
    def getValue(self, index, nodeIndex, dataType, dataset):
        if(dataType == "post"):
            valueX = float(dataset.variables["spd"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            valueY = float(dataset.variables["dir"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            return(valueX, valueY)
        elif(dataType == "gfs"):
            valueX = float(dataset.variables["wind_u"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            valueY = float(dataset.variables["wind_v"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            return(valueX, valueY)
        elif(dataType == "rain"):
            return float(dataset.variables["precipitation"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
        elif(dataType == "fort"):
            valueX = dataset.variables["windx"][index][int(nodeIndex)]
            valueY = dataset.variables["windy"][index][int(nodeIndex)]
            return (valueX, valueY)
        elif(dataType == "water"):
            return float(dataset.variables["zeta"][index][int(nodeIndex)])
        elif(dataType == "swh"):
            return float(dataset.variables["swan_HS"][index][int(nodeIndex)])
        elif(dataType == "mwd"):
            return float(dataset.variables["swan_DIR"][index][int(nodeIndex)])
        elif(dataType == "mwp"):
           return float(dataset.variables["swan_TMM10"][index][int(nodeIndex)])
        elif(dataType == "pwp"):
            return float(dataset.variables["swan_TPS"][index][int(nodeIndex)])
        elif(dataType == "rad"):
            valueX = float(dataset.variables["radstress_x"][index][int(nodeIndex)])
            valueY = float(dataset.variables["radstress_y"][index][int(nodeIndex)])
            return(valueX, valueY)
        
    def getValuesForPoints(self, latitudes, longitudes, values, nodesIndex, dataType):
        pointsValues = []
        data = values
        for nodeIndex in nodesIndex:
            pointValues = []
            for index in range(len(data)):
                pointValues.append(data[index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            pointsValues.append(pointValues)
        return pointsValues
            
            
    def getValuesGrid(self, spaceSparseness, timeSparseness, dataType, dataset):
        if(dataType == "post"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["spd"][::][::][::]
            dataY = dataset.variables["dir"][::][::][::]
            for index in range(0, len(dataX), timeSparseness):
                lineX = []
                lineY = []
                for latitudeIndex in range(0, len(dataX[index]), spaceSparseness):
                    pointX = []
                    pointY = []
                    for longitudeIndex in range(0, len(dataX[index][latitudeIndex]), spaceSparseness):
                        pointX.append(float(dataX[index][latitudeIndex][longitudeIndex]))
                        pointY.append(float(dataY[index][latitudeIndex][longitudeIndex]))
                    lineX.append(pointX)
                    lineY.append(pointY)
                valuesX.append(lineX)
                valuesY.append(lineY)   
            return (valuesX, valuesY)
        elif(dataType == "gfs"):
            dataX = dataset.variables["wind_u"][::][::][::]
            dataY = dataset.variables["wind_v"][::][::][::]
            return (dataX, dataY)
        elif(dataType == "rain"):
            data = dataset.variables["precipitation"][::][::][::]
            return data
        elif(dataType == "fort"):
            dataX = dataset.variables["windx"][::][::]
            dataY = dataset.variables["windy"][::][::]
            return (dataX, dataY)
        elif(dataType == "water"):
            data = dataset.variables["zeta"][::][::]
            return data
        elif(dataType == "swh"):
            data = dataset.variables["swan_HS"][::][::]
            return data
        elif(dataType == "mwd"):
            data = dataset.variables["swan_DIR"][::][::]
            return data
        elif(dataType == "mwp"):
            data = dataset.variables["swan_TMM10"][::][::]
            return data
        elif(dataType == "pwp"):
            data = dataset.variables["swan_TPS"][::][::]
            return data
        elif(dataType == "rad"):
            dataX = dataset.variables["radstress_x"][::][::]
            dataY = dataset.variables["radstress_y"][::][::]
            return (dataX, dataY)
                 
    def getValues(self, spaceSparseness, timeSparseness, dataType, dataset):
        if(dataType == "post"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["spd"][::][::][::]
            dataY = dataset.variables["dir"][::][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index]).flatten()[::spaceSparseness]
                subsetDataY = np.array(dataY[index]).flatten()[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return (valuesX, valuesY)
        elif(dataType == "gfs"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["wind_u"][::][::][::]
            dataY = dataset.variables["wind_v"][::][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index]).flatten()[::spaceSparseness]
                subsetDataY = np.array(dataY[index]).flatten()[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return (valuesX, valuesY)
        elif(dataType == "rain"):
            values = []
            data = dataset.variables["precipitation"][::][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index]).flatten()[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "fort"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["windx"][::][::]
            dataY = dataset.variables["windy"][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index])[::spaceSparseness]
                subsetDataY = np.array(dataY[index])[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return (valuesX, valuesY)
        elif(dataType == "water"):
            values = []
            data = dataset.variables["zeta"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "swh"):
            values = []
            data = dataset.variables["swan_HS"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "mwd"):
            values = []
            data = dataset.variables["swan_DIR"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index]).flatten()[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "mwp"):
            values = []
            data = dataset.variables["swan_TMM10"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "pwp"):
            values = []
            data = dataset.variables["swan_TPS"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "rad"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["radstress_x"][::][::]
            dataY = dataset.variables["radstress_y"][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index])[::spaceSparseness]
                subsetDataY = np.array(dataY[index])[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return(valuesX, valuesY)
            
            
    def getCoordinates(self, latitudes, longitudes):
        nodesIndex = []
        pointsLatitudes = []
        pointsLongitudes = []
        points = []
        for latitudeIndex, latitude in enumerate(latitudes):
            for longitudeIndex, longitude in enumerate(longitudes):
                nodesIndex.append(str((latitudeIndex, longitudeIndex)))
                pointsLatitudes.append(latitude)
                pointsLongitudes.append(longitude)
        return (pointsLatitudes, pointsLongitudes), nodesIndex
        
    def getCoordinatesGrid(self, latitudes, longitudes):
        nodesIndex = []
        points = []
        for latitudeIndex in range(len(latitudes)):
            for longitudeIndex in range(len(longitudes)):
                nodesIndex.append(str((latitudeIndex, longitudeIndex)))
                    
        return (latitudes, longitudes), nodesIndex

# Example background axis
# SOUTH_NEW_ENGLAND_AXIS = [-71.905117442267496, -71.0339945492675, 42.200717972845119, 41.028319358056874]
    def isOutsideBackground(self, point):
        if(point[0] > self.BACKGROUND_AXIS[0] and point[0] < self.BACKGROUND_AXIS[1]):
            if(point[1] > self.BACKGROUND_AXIS[3] and point[1] < self.BACKGROUND_AXIS[2]):
                return False
        return True
   
    def findTriangleIndicesOutsideBackground(self, triangles, dataset):
        latitudes = dataset.variables["y"][::]
        longitudes = dataset.variables["x"][::]
        maskedIndices = []
        for index, triangle in enumerate(triangles):
            point0 = [longitudes[triangle[0]], latitudes[triangle[0]]]
            point1 = [longitudes[triangle[1]], latitudes[triangle[1]]]
            point2 = [longitudes[triangle[2]], latitudes[triangle[2]]]
            if(self.isOutsideBackground(point0) or self.isOutsideBackground(point1) or self.isOutsideBackground(point2)):
                maskedIndices.append(True)
            else:
                maskedIndices.append(False)
        return maskedIndices
                
#    TODO: Get map background bounds and mask triangles with any vertices that fall outside of bounds
    def getTriangles(self, dataset):
        trianglesOffByOne = np.array(dataset.variables["element"][:])
        triangles = trianglesOffByOne - 1
        maskedIndices = self.findTriangleIndicesOutsideBackground(triangles, dataset)
#         xCoordinates = dataset.variables["x"]
#         yCoordinates = dataset.variables["y"]
#         triangleXCoordinates = []
#         triangleYCoordinates = []
#         print(len(xCoordinates))
#         print(len(yCoordinates))
#         print(np.min(triangles, axis=0))
#         for triangle in triangles:
#             triangleXCoordinates.append([xCoordinates[triangle[0]], xCoordinates[triangle[1]], xCoordinates[triangle[2]]])
#             triangleYCoordinates.append([yCoordinates[triangle[0]], yCoordinates[triangle[1]], yCoordinates[triangle[2]]])
#             
#         triangleAreas = []
#         badIndices = []
#         for index, triangleXCoordinate in enumerate(triangleXCoordinates):
#             x1 = triangleXCoordinate[0]
#             x2 = triangleXCoordinate[1]
#             x3 = triangleXCoordinate[2]
#             y1 = triangleYCoordinates[index][0]
#             y2 = triangleYCoordinates[index][1]
#             y3 = triangleYCoordinates[index][2]
#             print(x1, x2, x3)
#             if ((x1 < -71.9) or (x2 < -71.9) or (x3 < -71.9)):
#                 badIndices.append(index)
#             area = (0.5) * np.abs(((x1 * (y2 - y3)) + (x2 * (y3 - y1)) + (x3*(y1 - y2))))
#             triangleAreas.append(area)
# #             print(area)
#                 
#         for index in badIndices:
#             area = triangleAreas[index]
#             print("index, area", index, area)
#         print(badIndices)
#         print(len(triangles), len(badIndices))
        return triangles, maskedIndices
        
    def getMap(self, latitudes, longitudes, values, dataType, times, data):
        print("getting map", dataType, flush=True)
        mapValuesX = []
        mapValuesY = []
        mapValues = []
        
        mapNodes = []
        mapNodesLatitudes = []
        mapNodesLongitudes = []
        
        mapValues = values
        nodes, nodesIndex = self.getCoordinatesGrid(latitudes, longitudes)


        mapNodesLatitudes = nodes[0]
        mapNodesLongitudes = nodes[1]
        mapNodes = nodesIndex
#         print(len(points))
        
        data["map_data"] = {}
        data["map_data"]["map_times"] = times
        data["map_data"]["map_points"] = mapNodes
        data["map_data"]["map_pointsLatitudes"] = mapNodesLatitudes
        data["map_data"]["map_pointsLongitude"] = mapNodesLongitudes
        if(dataType == "gfs" or dataType == "fort"):
            data["map_data"]["map_windsX"] = mapValuesX
            data["map_data"]["map_windsY"] = mapValuesY
        else:
            data["map_data"]["map_" + dataType] = mapValues
        return data
            
    def getProperties(self, OUTPUT_FOLDER, startDateObject, timeDelta, dataType):
#         print(dataset.variables)
        files = os.listdir(OUTPUT_FOLDER)
        etaFiles = []
        for file in files:
            if file[0:4] == "eta_":
                etaFiles.append(file)
        etaFiles.sort()
#         print(etaFiles)
        numTimes = len(etaFiles)
#         print(numTimes, startDateObject, timeDelta)
        times = []
        for timeIndex in range(numTimes):
            times.append((startDateObject + (timeDelta * timeIndex)).timestamp())
#         print(times)
#       Generate lat lon grid based on BACKGROUND_AXIS and funwave grid size
#        First, find and initialize funwave grid size based on reading a data file
        gridInitialized = False
        deltaNodesLatitude = 0
        deltaNodesLongitude = 0

        
        if (dataType == "eta"):
            etaValues = []
            for etaFile in etaFiles:
                with open(OUTPUT_FOLDER + etaFile) as file:
                    lines = file.readlines()
                    etaValue = []
                    for line in lines:
                        etaLine = []
                        data = line.split("   ")[1::]
                        if(not gridInitialized):
                            deltaNodesLongitude = len(data)
                            deltaNodesLatitude = len(lines)
                            gridInitialized = True
                        for value in data:
                            etaLine.append(float(value))
                        etaValue.append(etaLine)
                    etaValues.append(etaValue)
            print(deltaNodesLongitude, deltaNodesLatitude)
            deltaNodesLongitude = deltaNodesLongitude
            deltaNodesLatitude = deltaNodesLatitude

            print("etaX0", etaValues[0][0][0], flush=True)
#         Then map a linspace of the background bounds to the nodes in the grid
        latitudes = []
        longitudes = []
        print(self.BACKGROUND_AXIS)
        longitudes = np.linspace(self.BACKGROUND_AXIS[0], self.BACKGROUND_AXIS[1], num=deltaNodesLongitude)
        latitudes = np.linspace(self.BACKGROUND_AXIS[3], self.BACKGROUND_AXIS[2], num=deltaNodesLatitude)
        print(max(longitudes), min(latitudes))
        print(times[0])
        return times, latitudes, longitudes, etaValues
        
        
    def initializeClosestNodes(self, latitudes, longitudes, thresholdDistance, dataType):
        # Find node indexes that are closest to NOS_Stations
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
        stationToNodeDistancesDict = {}
        if(dataType == "eta"):
            stationKeys = stationsDict["NOS"].keys()
        for stationKey in stationKeys:
            stationToNodeDistancesDict[stationKey] = {}
        # recreate station to node distances calculations dictionary
        print("retreving coordinates for all nodes", flush=True)
        (nodesLatitudes, nodesLongitudes), nodesIndex = self.getCoordinates(latitudes, longitudes)
        for index in range(len(nodesIndex)):
            node = (nodesLatitudes[index], nodesLongitudes[index])
            nodeIndex = nodesIndex[index]
#             print(node)
            if(node[0] <= 90 and node[0] >= -90):
                for stationKey in stationKeys:
#                     print(stationKey)
                    if(dataType == "eta"):
                        stationDict = stationsDict["NOS"][stationKey]
                    stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
    #                             distance and threshold in kilometers
                    distance = haversine.haversine(stationCoordinates, node)
#                     print("stationCoordinates", stationCoordinates)
#                     print("distance", distance)
                    if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
                        stationToNodeDistancesDict[stationKey]["closestNodes"] = []
                    elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
                    if(thresholdDistance > distance):
    #                                 print("Found a closest node", node, nodeIndex, "distance ", distance, "station", stationKey)
                        stationToNodeDistancesDict[stationKey]["closestNodes"].append(nodeIndex)
            else:
                badNodes.append(nodeIndex)
                print("bad node", nodeIndex, node, flush=True)
            if(index % 100000 == 0):
                print("index", index, flush=True)

        with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
            json.dump(stationToNodeDistancesDict, outfile)
                
        with open(self.STATION_TO_NODE_DISTANCES_FILE) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
        
        nodes = {"NOS": {}}
    
        for stationKey in stationToNodeDistancesDict.keys():
            stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
            nodeIndex = stationToNodeDistanceDict["nodeIndex"]
            closestNodes = stationToNodeDistancesDict[stationKey]["closestNodes"]
            nodes["NOS"][stationKey] = {}
            nodes["NOS"][stationKey]["closestNodes"] = closestNodes
            nodes["NOS"][stationKey]["nodeIndex"] = nodeIndex
            nodes["NOS"][stationKey]["latitude"] = float(latitudes[self.extractLatitudeIndex(nodeIndex)])
            nodes["NOS"][stationKey]["longitude"] = float(longitudes[self.extractLongitudeIndex(nodeIndex)])

            
        with open(self.NODES_FILE, "w") as outfile:
            json.dump(nodes, outfile)
            
    
    
    def generateDataFiles(self, dataset, dataType, times, DATA_FILE):
    
        with open(self.NODES_FILE) as outfile:
            nodes = json.load(outfile)
            
        data = {}
        print("Reading data", dataType, flush=True)
        for stationKey in nodes["NOS"].keys():
#                 print("getting wind data for node", nodeIndex)
            data[stationKey] = {}
            nodeIndex = nodes["NOS"][stationKey]["nodeIndex"]
            data[stationKey]["nodeIndex"] = nodeIndex
            data[stationKey]["times"] = times
            if(self.format == "GFS" or self.format == "POST"):
                data[stationKey]["latitude"] = float(dataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                data[stationKey]["longitude"] = float(dataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
            elif(self.format == "FORT"):
                data[stationKey]["latitude"] = float(dataset.variables["y"][int(nodeIndex)].data)
                data[stationKey]["longitude"] = float(dataset.variables["x"][int(nodeIndex)].data)

            values = []
            valuesX = []
            valuesY = []
            for index in range(len(times)):
                value = self.getValue(index, closestNode, dataType, dataset)
                if(type(value) is float):
                    values.append(value)
                else:
                    valuesX.append(value[0])
                    valuesY.append(value[1])

#           Write values
            if(dataType == "rad"):
                data[stationKey]["radstressX"] = valuesX
                data[stationKey]["radstressY"] = valuesY
            elif(dataType == "gfs" or dataType == "fort"):
                data[stationKey]["windsX"] = valuesX
                data[stationKey]["windsY"] = valuesY
            elif(dataType == "post"):
                data[stationKey]["speeds"] = valuesX
                data[stationKey]["directions"] = valuesY
            else:
                data[stationKey][dataType] = values
    
        with open(DATA_FILE, "w") as outfile:
            json.dump(data, outfile)
        
    def generateDataFilesWithInterpolation(self, latitudes, longitudes, values, dataType, times, DATA_FILE):
        
        with open(self.NODES_FILE) as outfile:
            nodes = json.load(outfile)
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
            
        data = {}
        data = self.getMap(latitudes, longitudes, values, dataType, times, data)
                
        print("Interpolating", dataType, flush=True)
        nodesIndex = []
        points = []
        pointsValues = []
        pointsValuesX = []
        pointsValuesY = []
        for stationKey in nodes["NOS"].keys():
            print("Getting coordinates for closest nodes around station",  stationKey, flush=True)
#                 print("getting wind data for node", nodeIndex)
            for closestNode in nodes["NOS"][stationKey]["closestNodes"]:
                nodesIndex.append(closestNode)
                x = 0.0
                y = 0.0
                x = float(longitudes[self.extractLongitudeIndex(closestNode)])
                y = float(latitudes[self.extractLatitudeIndex(closestNode)])
                point = (x, y)
                points.append(point)
        print("getting time series data for closest nodes", flush=True)
        pointsValues = self.getValuesForPoints(latitudes, longitudes, values, nodesIndex, dataType)
#                 for index in range(len(times)):
# #                     print("getttingTime")
#                     value = self.getValue(index, closestNode, dataType, dataset)
#                     if(type(value) is float):
#                         values.append(value)
#                     else:
#                         valuesX.append(value[0])
#                         valuesY.append(value[1])
#                 pointsValues.append(values)
#                 pointsValuesX.append(valuesX)
#                 pointsValuesY.append(valuesY)
#             Interpolate values
        print("initializing interpolator", flush=True)
        interpolator = scipy.interpolate.LinearNDInterpolator(points, pointsValues)
        for stationKey in nodes["NOS"].keys():
            nodeIndex = nodes["NOS"][stationKey]["nodeIndex"]
            data[stationKey] = {}
            data[stationKey]["nodeIndex"] = nodeIndex
            latitude = ""
            longitude = ""
            latitude = float(latitudes[self.extractLatitudeIndex(nodeIndex)])
            longitude = float(longitudes[self.extractLongitudeIndex(nodeIndex)])
            data[stationKey]["latitude"] = latitude
            data[stationKey]["longitude"] = longitude
            data[stationKey]["times"] = times
            if(dataType == "eta"):
                stationDict = stationsDict["NOS"][stationKey]
            stationLatitude = float(stationDict["latitude"])
            stationLongitude = float(stationDict["longitude"])
            stationCoordinates = (stationLongitude, stationLatitude)
            print("interpolating data for station", stationKey, "at", stationCoordinates, flush=True)
            interpolatedValues = interpolator(stationLongitude, stationLatitude)
            data[stationKey][dataType] = interpolatedValues
        
        print("Writing data to", DATA_FILE, flush=True)
        with open(DATA_FILE, "w") as outfile:
            json.dump(data, outfile, cls=NumpyEncoder)
        
         
class EtaReader:
    def __init__(self, OUTPUT_FOLDER="", STATIONS_FILE="", ETA_DATA_FILE="", BACKGROUND_AXIS=[], startDateObject=None, timeDelta=None):
        temp_directory = ETA_DATA_FILE[0:ETA_DATA_FILE.rfind("/") + 1]
        self.OUTPUT_FOLDER = OUTPUT_FOLDER
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "Fun_Station_To_Node_Distances.json"
        self.FUN_NODES_FILE = temp_directory + "Fun_Nodes.json"
        self.ETA_DATA_FILE = ETA_DATA_FILE
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.startDateObject = startDateObject
        self.timeDelta = timeDelta
        self.reader = FunReader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.FUN_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS)
    
    def generateFunDataForStations(self):
        print("Eta file", flush=True)
        print(self.ETA_DATA_FILE, flush=True)
        timesEta, latitudesEta, longitudesEta, valuesEta = self.reader.getProperties(self.OUTPUT_FOLDER, self.startDateObject, self.timeDelta, "eta")
        initializeClosestFunNodes = True
        if(initializeClosestFunNodes):
            thresholdDistance = 20
#             thresholdDistance = 100
            self.reader.initializeClosestNodes(latitudesEta, longitudesEta, thresholdDistance, "eta")
        interpolateValues = True
        spaceSparseness = 1
        timeSparseness = 1
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(latitudesEta, longitudesEta, valuesEta, "eta", timesEta, self.ETA_DATA_FILE)
        else:
            self.reader.generateDataFiles(rainDataset, "rain", timesRain, self.GFS_RAIN_DATA_FILE)
        return (datetime.fromtimestamp(timesEta[0], timezone.utc), datetime.fromtimestamp(timesEta[-1], timezone.utc))