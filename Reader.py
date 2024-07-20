import netCDF4 as nc
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
class Reader:
    def __init__(self, STATIONS_FILE="", STATION_TO_NODE_DISTANCES_FILE="", NODES_FILE="", format=""):
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = STATION_TO_NODE_DISTANCES_FILE
        self.NODES_FILE = NODES_FILE
        self.format = format
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
        
    def getValuesForPoints(self, nodesIndex, dataType, dataset):
        if(dataType == "post"):
            pointsValuesX = []
            pointsValuesY = []
            dataX = dataset.variables["spd"][::]
            dataY = dataset.variables["dir"][::]
            for nodeIndex in nodesIndex:
                valuesX = []
                valuesY = []
                for index in range(len(dataX)):
                    valuesX.append(dataX[index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
                    valuesY.append(dataY[index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
                pointsValuesX.append(valuesX)
                pointsValuesY.append(valuesY)
            return (pointsValuesX, pointsValuesY)
        if(dataType == "gfs"):
            pointsValuesX = []
            pointsValuesY = []
            dataX = dataset.variables["wind_u"][::]
            dataY = dataset.variables["wind_v"][::]
            for nodeIndex in nodesIndex:
                valuesX = []
                valuesY = []
                for index in range(len(dataX)):
                    valuesX.append(dataX[index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
                    valuesY.append(dataY[index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
                pointsValuesX.append(valuesX)
                pointsValuesY.append(valuesY)
            return (pointsValuesX, pointsValuesY)
        if(dataType == "fort"):
            pointsValuesX = []
            pointsValuesY = []
            dataX = dataset.variables["windx"][::]
            dataY = dataset.variables["windy"][::]
            for nodeIndex in nodesIndex:
                valuesX = []
                valuesY = []
                for index in range(len(dataX)):
                    valuesX.append(dataX[index][int(nodeIndex)])
                    valuesY.append(dataY[index][int(nodeIndex)])
                pointsValuesX.append(valuesX)
                pointsValuesY.append(valuesY)
            return (pointsValuesX, pointsValuesY)
        if(dataType == "rad"):
            pointsValuesX = []
            pointsValuesY = []
            dataX = dataset.variables["radstress_x"][::]
            dataY = dataset.variables["radstress_y"][::]
            for nodeIndex in nodesIndex:
                valuesX = []
                valuesY = []
                for index in range(len(dataX)):
                    valuesX.append(dataX[index][int(nodeIndex)])
                    valuesY.append(dataY[index][int(nodeIndex)])
                pointsValuesX.append(valuesX)
                pointsValuesY.append(valuesY)
            return (pointsValuesX, pointsValuesY)
        if(dataType == "rain"):
            pointsValues = []
            data = dataset.variables["precipitation"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "water"):
            pointsValues = []
            data = dataset.variables["zeta"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "swh"):
            pointsValues = []
            data = dataset.variables["swan_HS"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "mwd"):
            pointsValues = []
            data = dataset.variables["swan_DIR"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "mwp"):
            pointsValues = []
            data = dataset.variables["swan_TMM10"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "pwp"):
            pointsValues = []
            data = dataset.variables["swan_TPS"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
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
            
            
    def getCoordinates(self, spaceSparseness, dataset):
        nodesIndex = []
        pointsLatitudes = []
        pointsLongitudes = []
        points = []
        if(self.format == "GFS" or self.format == "POST"):
            latitudes = dataset.variables["lat"][::]
            longitudes = dataset.variables["lon"][::]
            for latitudeIndex, latitude in enumerate(latitudes):
                for longitudeIndex, longitude in enumerate(longitudes):
                    nodesIndex.append(str((latitudeIndex, longitudeIndex)))
                    pointsLatitudes.append(latitude)
                    pointsLongitudes.append(longitude)
        elif(self.format == "FORT"):
            latitudes = dataset.variables["y"][::]
            longitudes = dataset.variables["x"][::]
            for index in range(len(latitudes)):
                nodesIndex.append(str(index))
                pointsLatitudes.append(latitudes[index])
                pointsLongitudes.append(longitudes[index])
        nodesIndex = nodesIndex[::spaceSparseness]
        pointsLatitudes = pointsLatitudes[::spaceSparseness]
        pointsLongitudes = pointsLongitudes[::spaceSparseness]
        return (pointsLatitudes, pointsLongitudes), nodesIndex
        
    def getCoordinatesGrid(self, spaceSparseness, dataset):
        nodesIndex = []
        points = []
        if(self.format == "GFS" or self.format == "POST"):
            latitudes = dataset.variables["lat"][::spaceSparseness]
            longitudes = dataset.variables["lon"][::spaceSparseness]
            for latitudeIndex in range(len(latitudes)):
                for longitudeIndex in range(len(longitudes)):
                    nodesIndex.append(str((latitudeIndex, longitudeIndex)))
                    
        elif(self.format == "FORT"):
            latitudes = dataset.variables["y"][::]
            longitudes = dataset.variables["x"][::]
            for index in range(len(latitudes)):
                nodesIndex.append(str(index))
        return (latitudes, longitudes), nodesIndex
   
    def getMap(self, dataset, dataType, times, spaceSparseness, timeSparseness, data):
        print("getting map", dataType, flush=True)
        mapValuesX = []
        mapValuesY = []
        mapValues = []
        
        mapNodes = []
        mapNodesLatitudes = []
        mapNodesLongitudes = []
        
        if(self.format == "GFS" or self.format == "POST"):
            value = self.getValuesGrid(spaceSparseness, timeSparseness, dataType, dataset)
            nodes, nodesIndex = self.getCoordinatesGrid(spaceSparseness, dataset)
        elif(self.format == "FORT"):
            value = self.getValues(spaceSparseness, timeSparseness, dataType, dataset)
            nodes, nodesIndex = self.getCoordinates(spaceSparseness, dataset)
        if(dataType == "post" or dataType == "gfs" or dataType == "fort" or dataType == "rad"):
            mapValuesX = value[0]
            mapValuesY = value[1]
        else:
            mapValues = value
        mapNodesLatitudes = nodes[0]
        mapNodesLongitudes = nodes[1]
        mapNodes = nodesIndex
#         print(len(points))
        
        data["map_data"] = {}
        data["map_data"]["map_times"] = times[::timeSparseness]
        data["map_data"]["map_points"] = mapNodes
        data["map_data"]["map_pointsLatitudes"] = mapNodesLatitudes
        data["map_data"]["map_pointsLongitude"] = mapNodesLongitudes
        if(dataType == "rad"):
            data["map_data"]["map_radstressX"] = mapValuesX
            data["map_data"]["map_radstressY"] = mapValuesY
        elif(dataType == "gfs" or dataType == "fort"):
            data["map_data"]["map_windsX"] = mapValuesX
            data["map_data"]["map_windsY"] = mapValuesY
        elif(dataType == "post"):
            data["map_data"]["map_speeds"] = mapValuesX
            data["map_data"]["map_directions"] = mapValuesY
        else:
            data["map_data"]["map_" + dataType] = mapValues
        return data
            
    def getNetcdfProperties(self, NETCDF_FILE, dataType):
        if(self.format == "POST"):
            dataset = nc.Dataset(NETCDF_FILE)["Main"]
        else:
            dataset = nc.Dataset(NETCDF_FILE)
        metadata = dataset.__dict__
#         print(dataset.variables)

        datasetTimeDescription = dataset.variables["time"].units
#         Add UTC time marker if not existing in cold start date
        if(not ("Z" in datasetTimeDescription)):
            coldStartDateText = datasetTimeDescription[14: 24] + "T" + datasetTimeDescription[25:] + "Z"
        else:
            coldStartDateText = datasetTimeDescription[14: 24] + "T" + datasetTimeDescription[25:]
        coldStartDate = datetime.fromisoformat(coldStartDateText)
        print("coldStartDate", coldStartDate, flush=True)

        minT = float(dataset.variables["time"][0].data)
        maxT = float(dataset.variables["time"][-1].data)
        times = []
        print(minT, flush=True)
        print(maxT, flush=True)
        if(self.format == "POST" or self.format == "GFS"):
#             print("deltaT of data")
            windDeltaT = timedelta(minutes=maxT - minT)
#             print(windDeltaT)

#             print("number of timesteps")
            timesteps = len(dataset.variables["time"][:])
#             print(timesteps)

            for index in range(timesteps):
#                 print("timedelta", timedelta(minutes=float(dataset.variables["time"][index].data)))
                time = coldStartDate + timedelta(minutes=float(dataset.variables["time"][index].data))
#                 time.replace(timezone.utc)
#                 print("tzinfo", time.tzinfo)
                times.append(time.timestamp())
#                 print(times)
#                 quit()

#             print("start of data (seconds since coldstart)")
            startDate = coldStartDate + timedelta(minutes=float(minT))
            endDate = coldStartDate + timedelta(minutes=float(maxT))
            print("startDate", startDate, flush=True)
            print("endDate", endDate, flush=True)
#         
            # GFS Data is grid based system
#             print("min max latitude and longitude")
            minLatitude = dataset.variables["lat"][0].data
            minLongitude = dataset.variables["lon"][0].data
            maxLatitude = dataset.variables["lat"][-1].data
            maxLongitude = dataset.variables["lon"][-1].data

#             print("minLatitude", minLatitude)
#             print("minLongitude", minLongitude)
#             print("maxLatitude", maxLatitude)
#             print("maxLongitude", maxLongitude)

            deltaLatitude = maxLatitude - minLatitude
            deltaLongitude = maxLongitude - minLongitude

            print("deltaLatitude", deltaLatitude, flush=True)
            print("deltaLongitude", deltaLongitude, flush=True)

            deltaNodesLatitude = len(dataset.variables["lat"][:])
            deltaNodesLongitude = len(dataset.variables["lon"][:])

            print("deltaNodesLatitude", deltaNodesLatitude, flush=True)
            print("deltaNodesLongitude", deltaNodesLongitude, flush=True)
        elif(self.format == "FORT"):
    #         print("deltaT of data")
            windDeltaT = timedelta(seconds=maxT - minT)
     #        print(windDeltaT)

    #         print("number of timesteps")
            timesteps = len(dataset.variables["time"][:])
    #         print(timesteps)

            for index in range(timesteps):
                time = coldStartDate + timedelta(seconds=float(dataset.variables["time"][index].data))
                times.append(time.timestamp())

    #         print("start of data (seconds since coldstart)")
            startDate = coldStartDate + timedelta(seconds=float(minT))
            endDate = coldStartDate + timedelta(seconds=float(maxT))
    #         print("startDate", startDate)
    #         print("endDate", endDate)
        
            # Grid origin is top right? Maybe not, Node based system!
            # y is latitude, x is longitude
            node0 = (float(dataset.variables["y"][0].data), float(dataset.variables["x"][0].data))
    #         print("node0 (lat, long)", node0)

            numberOfNodes = dataset.variables["x"].shape[0]

#         print("number of nodes", numberOfNodes)
        
        if (dataType == "swh"):
            print("significant wave height at node200000", flush=True)
        
            swhX0 = dataset.variables["swan_HS"][0][200000]

            print("swhX0", swhX0, flush=True)
        elif (dataType == "mwd"):
            print("mean wave direction at node200000", flush=True)
        
            mwdX0 = dataset.variables["swan_DIR"][0][200000]

            print("mwdX0", mwdX0, flush=True)
        elif (dataType == "mwp"):
            print("mean wave period at node200000", flush=True)
        
            mwpX0 = dataset.variables["swan_TMM10"][0][200000]

            print("mwpX0", mwpX0, flush=True)
        elif (dataType == "pwp"):
            print("peak wave period at node200000", flush=True)
        
            tpsX0 = dataset.variables["swan_TPS"][0][200000]

            print("tpsX0", tpsX0, flush=True)
        elif (dataType == "rad"):
            print("radiation stress gradient at node200000", flush=True)
        
            radX0 = dataset.variables["radstress_x"][0][200000]
            radY0 = dataset.variables["radstress_y"][0][200000]

            print("radX0", radX0, flush=True)
            print("radY0", radY0, flush=True)
        elif (dataType == "fort"):
            print("wind at node0")
        
            windX0 = dataset.variables["windx"][0][0]
            windY0 = dataset.variables["windy"][0][0]

            print("windX0", windX0, flush=True)
            print("windY0", windY0, flush=True)
        elif (dataType == "water"):
            print("water at node0", flush=True)
            
            zeta0 = dataset.variables["zeta"][0][0]
            print("zeta0", zeta0, flush=True)
            
        elif (dataType == "rain"):
            print("rain at (0,0)", flush=True)
            
            rain0 = dataset.variables["precipitation"][0][0][0]
            print("rain", rain0, flush=True)
        elif (dataType == "gfs"):
            print("Wind at t=0, point(0, 0)", flush=True)
            windX0 = dataset.variables["wind_u"][0][0][0]
            windY0 = dataset.variables["wind_v"][0][0][0]
            print("windX000", windX0, flush=True)
            print("windY000", windY0, flush=True)
        elif (dataType == "post"):
            speed0 = dataset.variables["spd"][0][0][0]
            direction0 = dataset.variables["dir"][0][0][0]
            print("speed0", speed0, flush=True)
            print("direction0", direction0, flush=True)

        return dataset, times
        
        
    def initializeClosestNodes(self, dataset, thresholdDistance):
        # Find node indexes that are closest to NOS_Stations
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
        stationToNodeDistancesDict = {}
        for stationKey in stationsDict["NOS"].keys():
            stationToNodeDistancesDict[stationKey] = {}
        # recreate station to node distances calculations dictionary
        print("retreving coordinates for all nodes", flush=True)
        (nodesLatitudes, nodesLongitudes), nodesIndex = self.getCoordinates(1, dataset)
        for index in range(len(nodesIndex)):
            node = (nodesLatitudes[index], nodesLongitudes[index])
            nodeIndex = nodesIndex[index]
#             print(node)
            if(node[0] <= 90 and node[0] >= -90):
                for stationKey in stationsDict["NOS"].keys():
#                     print(stationKey)
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
#         if(self.format == "GFS" or self.format == "POST"):
#             deltaNodesLatitude = len(dataset.variables["lat"][:])
#             deltaNodesLongitude = len(dataset.variables["lon"][:])
#             for longitudeIndex in range(deltaNodesLongitude):
#                 for latitudeIndex in range(deltaNodesLatitude):
#                     node = (float(dataset.variables["lat"][latitudeIndex].data), float(dataset.variables["lon"][longitudeIndex].data))
#                     nodeIndex = str((latitudeIndex, longitudeIndex))
#                     if(node[0] <= 90 and node[0] >= -90):
#                         for stationKey in stationsDict["NOS"].keys():
#                             stationDict = stationsDict["NOS"][stationKey]
#                             stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
# #                             distance and threshold in kilometers
#                             distance = haversine.haversine(stationCoordinates, node)
# #                             print("stationCoordinates", stationCoordinates)
# #                             print("distance", distance)
#                             if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
#                                 stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                                 stationToNodeDistancesDict[stationKey]["distance"] = distance
#                                 stationToNodeDistancesDict[stationKey]["closestNodes"] = []
#                             elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
#                                 stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                                 stationToNodeDistancesDict[stationKey]["distance"] = distance
#                             if(thresholdDistance > distance):
# #                                 print("Found a closest node", node, nodeIndex, "distance ", distance, "station", stationKey)
#                                 stationToNodeDistancesDict[stationKey]["closestNodes"].append(nodeIndex)
#                     else:
#                         badNodes.append(nodeIndex)
#                         print("bad node", nodeIndex, node)
#                 if(longitudeIndex % 100 == 0):
#                     print("longitudeIndex", longitudeIndex)
#                         
#         if(self.format == "FORT"):
#             numberOfNodes = dataset.variables["x"].shape[0]
#             for nodeIndex in range(numberOfNodes):
#         #     There are nodes in the gulf of mexico between node 400000 - 500000 for rivc1 map
#         #     for nodeIndex in range(100000):
#         #         nodeIndex = nodeIndex + 400000
#                 node = (float(dataset.variables["y"][nodeIndex].data), float(dataset.variables["x"][nodeIndex].data))
#                 if(node[0] <= 90 and node[0] >= -90):
#                     for stationKey in stationsDict["NOS"].keys():
#                         stationDict = stationsDict["NOS"][stationKey]
#                         stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
#                         distance = haversine.haversine(stationCoordinates, node)
#                         if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
#                             stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                             stationToNodeDistancesDict[stationKey]["distance"] = distance
#                             stationToNodeDistancesDict[stationKey]["closestNodes"] = []
#                         elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
#                             stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                             stationToNodeDistancesDict[stationKey]["distance"] = distance
#                         if(thresholdDistance > distance):
# #                             print("Found a closest node", node, nodeIndex, "distance ", distance, "station", stationKey)
#                             stationToNodeDistancesDict[stationKey]["closestNodes"].append(nodeIndex)
#                 else:
#                     badNodes.append(nodeIndex)
#                     print("bad node", nodeIndex, node)
# #                 Print progress
#                 if(nodeIndex % 50000 == 0):
#                     print("nodeIndex", nodeIndex, node)

#         print("stationToNodeDistancesDict", stationToNodeDistancesDict)

        with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
            json.dump(stationToNodeDistancesDict, outfile)
                
        with open(self.STATION_TO_NODE_DISTANCES_FILE) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
        
        nodes = {"NOS": {}}
    
        for stationKey in stationToNodeDistancesDict.keys():
            stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
            nodeIndex = stationToNodeDistanceDict["nodeIndex"]
            closestNodes = stationToNodeDistancesDict[stationKey]["closestNodes"]
#             nodes["NOS"][nodeIndex] = {}
#             nodes["NOS"][nodeIndex]["closestNodes"] = closestNodes
#             nodes["NOS"][nodeIndex]["stationKey"] = stationKey
            nodes["NOS"][stationKey] = {}
            nodes["NOS"][stationKey]["closestNodes"] = closestNodes
            nodes["NOS"][stationKey]["nodeIndex"] = nodeIndex
            if(self.format == "GFS" or self.format == "POST"):
                nodes["NOS"][stationKey]["latitude"] = float(dataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                nodes["NOS"][stationKey]["longitude"] = float(dataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
            if(self.format == "FORT"):
                nodes["NOS"][stationKey]["latitude"] = float(dataset.variables["y"][int(nodeIndex)].data)
                nodes["NOS"][stationKey]["longitude"] = float(dataset.variables["x"][int(nodeIndex)].data)
            
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
        
    def generateDataFilesWithInterpolation(self, dataset, dataType, times, spaceSparseness, timeSparseness, DATA_FILE):
        
        with open(self.NODES_FILE) as outfile:
            nodes = json.load(outfile)
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
            
        data = {}
        data = self.getMap(dataset, dataType, times, spaceSparseness, timeSparseness, data)
                
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
                if(self.format == "GFS" or self.format == "POST"):
                    x = float(dataset.variables["lon"][self.extractLongitudeIndex(closestNode)].data)
                    y = float(dataset.variables["lat"][self.extractLatitudeIndex(closestNode)].data)
                elif(self.format == "FORT"):
                    x = float(dataset.variables["x"][int(closestNode)].data)
                    y = float(dataset.variables["y"][int(closestNode)].data)
                point = (x, y)
                points.append(point)
        print("getting time series data for closest nodes", flush=True)
        values = self.getValuesForPoints(nodesIndex, dataType, dataset)
        if(dataType == "post" or dataType == "gfs" or dataType == "fort" or dataType == "rad"):
            pointsValuesX.extend(values[0])
            pointsValuesY.extend(values[1])
        else:
            pointsValues.extend(values)
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
        if(dataType == "rad" or dataType == "gfs" or dataType == "fort" or dataType == "post"):
            interpolatorX = scipy.interpolate.LinearNDInterpolator(points, pointsValuesX)
            interpolatorY = scipy.interpolate.LinearNDInterpolator(points, pointsValuesY)
        else:
            interpolator = scipy.interpolate.LinearNDInterpolator(points, pointsValues)
        for stationKey in nodes["NOS"].keys():
            nodeIndex = nodes["NOS"][stationKey]["nodeIndex"]
            data[stationKey] = {}
            data[stationKey]["nodeIndex"] = nodeIndex
            latitude = ""
            longitude = ""
            if(self.format == "GFS" or self.format == "POST"):
                latitude = float(dataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                longitude = float(dataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
            elif(self.format == "FORT"):
                latitude = float(dataset.variables["y"][int(nodeIndex)].data)
                longitude = float(dataset.variables["x"][int(nodeIndex)].data)
            data[stationKey]["latitude"] = latitude
            data[stationKey]["longitude"] = longitude
            data[stationKey]["times"] = times
            stationDict = stationsDict["NOS"][stationKey]
            stationLatitude = float(stationDict["latitude"])
            stationLongitude = float(stationDict["longitude"])
            stationCoordinates = (stationLongitude, stationLatitude)
            print("interpolating data for station", stationKey, "at", stationCoordinates, flush=True)
            if(dataType == "rad" or dataType == "gfs" or dataType == "fort" or dataType == "post"):
                interpolatedValuesX = interpolatorX(stationLongitude, stationLatitude)
                interpolatedValuesY = interpolatorY(stationLongitude, stationLatitude)
            else:
                interpolatedValues = interpolator(stationLongitude, stationLatitude)
            if(dataType == "rad"):
                data[stationKey]["radstressX"] = interpolatedValuesX
                data[stationKey]["radstressY"] = interpolatedValuesY
            elif(dataType == "gfs" or dataType == "fort"):
                data[stationKey]["windsX"] = interpolatedValuesX
                data[stationKey]["windsY"] = interpolatedValuesY
            elif(dataType == "post"):
                data[stationKey]["speeds"] = interpolatedValuesX
                data[stationKey]["directions"] = interpolatedValuesY
            else:
                data[stationKey][dataType] = interpolatedValues
        
        print("Writing data to", DATA_FILE, flush=True)
        with open(DATA_FILE, "w") as outfile:
            json.dump(data, outfile, cls=NumpyEncoder)
        
         
class GFSRainReader:
    def __init__(self, GFS_RAIN_FILE="", STATIONS_FILE="", GFS_RAIN_DATA_FILE=""):
        temp_directory = "wind_temp/"
        self.GFS_RAIN_FILE = GFS_RAIN_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "GFS_Station_To_Node_Distances.json"
        self.GFS_NODES_FILE = temp_directory + "GFS_Nodes.json"
        self.GFS_RAIN_DATA_FILE = GFS_RAIN_DATA_FILE
        self.GFS_NODES_WIND_DATA_FILE = temp_directory + "GFS_Nodes_Wind_Data.json"
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.GFS_NODES_FILE, format="GFS")
    
    def generateRainDataForStations(self):
        print("Rain file", flush=True)
        print(self.GFS_RAIN_FILE, flush=True)
        rainDataset, timesRain = self.reader.getNetcdfProperties(self.GFS_RAIN_FILE, "rain")
        initializeClosestRainNodes = True
        if(initializeClosestRainNodes):
            thresholdDistance = 20
#             thresholdDistance = 100
            self.reader.initializeClosestNodes(rainDataset, thresholdDistance)
        interpolateValues = True
        spaceSparseness = 1
        timeSparseness = 1
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(rainDataset, "rain", timesRain, spaceSparseness, timeSparseness, self.GFS_RAIN_DATA_FILE)
        else:
            self.reader.generateDataFiles(rainDataset, "rain", timesRain, self.GFS_RAIN_DATA_FILE)
        return (datetime.fromtimestamp(timesRain[0], timezone.utc), datetime.fromtimestamp(timesRain[-1], timezone.utc))
            
class GFSWindReader:
    def __init__(self, GFS_WIND_FILE="", STATIONS_FILE="", GFS_WIND_DATA_FILE=""):
        temp_directory = "wind_temp/"
        self.GFS_WIND_FILE = GFS_WIND_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "GFS_Station_To_Node_Distances.json"
        self.GFS_NODES_FILE = temp_directory + "GFS_Nodes.json"
        self.GFS_WIND_DATA_FILE = GFS_WIND_DATA_FILE
        self.GFS_NODES_WIND_DATA_FILE = temp_directory + "GFS_Nodes_Wind_Data.json"
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.GFS_NODES_FILE, format="GFS")
    
    def generateWindDataForStations(self):
        print("Wind file", flush=True)
        print(self.GFS_WIND_FILE, flush=True)
        windDataset, timesWind = self.reader.getNetcdfProperties(self.GFS_WIND_FILE, "gfs")
        initializeClosestWindNodes = True
        if(initializeClosestWindNodes):
            thresholdDistance = 20
#             thresholdDistance = 100
#             Use higher threshold distance if working with 306 data?
#             thresholdDistance = 800
            self.reader.initializeClosestNodes(windDataset, thresholdDistance)
        interpolateValues = True
        spaceSparseness = 1
        timeSparseness = 1
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(windDataset, "gfs", timesWind, spaceSparseness, timeSparseness, self.GFS_WIND_DATA_FILE)
        else:
            self.reader.generateDataFiles(windDataset, "gfs", timesWind, self.GFS_WIND_DATA_FILE)
        return (datetime.fromtimestamp(timesWind[0], timezone.utc), datetime.fromtimestamp(timesWind[-1], timezone.utc))
            
class Fort74Reader:
    def __init__(self, ADCIRC_WIND_FILE="", STATIONS_FILE="", ADCIRC_WIND_DATA_FILE=""):
        temp_directory = "wind_temp/"
        self.ADCIRC_WIND_FILE = ADCIRC_WIND_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "ADCIRC_Station_To_Node_Distances.json"
        self.ADCIRC_NODES_FILE = temp_directory + "ADCIRC_Nodes.json"
        self.ADCIRC_WIND_DATA_FILE = ADCIRC_WIND_DATA_FILE
        self.ADCIRC_NODES_WIND_DATA_FILE = temp_directory + "ADCIRC_Nodes_Wind_Data.json"
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.ADCIRC_NODES_FILE, format="FORT")
    
    def generateWindDataForStations(self):
        print("Wind file", flush=True)
        print(self.ADCIRC_WIND_FILE, flush=True)
        windDataset, timesWind = self.reader.getNetcdfProperties(self.ADCIRC_WIND_FILE, "fort")
        initializeClosestWindNodes = True
        if(initializeClosestWindNodes):
            thresholdDistance = 0.1
            self.reader.initializeClosestNodes(windDataset, thresholdDistance)
        spaceSparseness = 10
        timeSparseness = 1
        interpolateValues = True
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(windDataset, "fort", timesWind, spaceSparseness, timeSparseness, self.ADCIRC_WIND_DATA_FILE)
        else:
            self.reader.generateDataFiles(windDataset, "fort", timesWind, self.ADCIRC_WIND_DATA_FILE)
        return (datetime.fromtimestamp(timesWind[0], timezone.utc), datetime.fromtimestamp(timesWind[-1], timezone.utc))
  
class Fort63Reader:
    def __init__(self, ADCIRC_WATER_FILE="", STATIONS_FILE="", ADCIRC_WATER_DATA_FILE=""):
        temp_directory = "water_temp/"
        self.ADCIRC_WATER_FILE = ADCIRC_WATER_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "ADCIRC_Station_To_Node_Distances.json"
        self.ADCIRC_NODES_FILE = temp_directory + "ADCIRC_Nodes.json"
        self.ADCIRC_WATER_DATA_FILE = ADCIRC_WATER_DATA_FILE
        self.ADCIRC_NODES_WIND_DATA_FILE = temp_directory + "ADCIRC_Nodes_Water_Data.json"
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.ADCIRC_NODES_FILE, format="FORT")
    
    def generateWindDataForStations(self):
        print("Water file", flush=True)
        print(self.ADCIRC_WATER_FILE, flush=True)
        waterDataset, timesWater = self.reader.getNetcdfProperties(self.ADCIRC_WATER_FILE, "water")
        initializeClosestWaterNodes = True
        if(initializeClosestWaterNodes):
#             thresholdDistance = 10
            thresholdDistance = 0.1
            self.reader.initializeClosestNodes(waterDataset, thresholdDistance)
        spaceSparseness = 1
#         spaceSparseness = 10
        timeSparseness = 1
        interpolateValues = True
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(waterDataset, "water", timesWater, spaceSparseness, timeSparseness, self.ADCIRC_WATER_DATA_FILE)
        else:
            self.reader.generateDataFiles(waterDataset, "water", timesWater, self.ADCIRC_WATER_DATA_FILE)
        return (datetime.fromtimestamp(timesWater[0], timezone.utc), datetime.fromtimestamp(timesWater[-1], timezone.utc))
                  
class PostWindReader:
    def __init__(self, POST_WIND_FILE="", STATIONS_FILE="", POST_WIND_DATA_FILE=""):
        temp_directory = "wind_temp/"
        self.POST_WIND_FILE = POST_WIND_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "Post_Station_To_Node_Distances.json"
        self.POST_NODES_FILE = temp_directory + "Post_Nodes.json"
        self.POST_WIND_DATA_FILE = POST_WIND_DATA_FILE
        self.POST_NODES_WIND_DATA_FILE = temp_directory + "Post_Nodes_Wind_Data.json"
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.POST_NODES_FILE, format="POST")
    
    def generateWindDataForStations(self):
        print("start, ", datetime.now(), flush=True)
        print("Wind file", flush=True)
        print(self.POST_WIND_FILE, flush=True)
        windDataset, timesWind = self.reader.getNetcdfProperties(self.POST_WIND_FILE, "post")
        initializeClosestWindNodes = True
        if(initializeClosestWindNodes):
            thresholdDistance = 0.05
            #If working with post low res high altitude, the threshold distance needs to be increased
            #Because there is no longer a high density of points in the post wind
#             thresholdDistance = 20
            self.reader.initializeClosestNodes(windDataset, thresholdDistance)
        interpolateValues = True
        spaceSparseness = 10
#         Uncomment for low res wind post generation
#         spaceSparseness = 1
        timeSparseness = 1
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(windDataset, "post", timesWind, spaceSparseness, timeSparseness, self.POST_WIND_DATA_FILE)
        else:
            self.reader.generateDataFiles(windDataset, "post", timesWind, self.POST_WIND_DATA_FILE)
        return (datetime.fromtimestamp(timesWind[0], timezone.utc), datetime.fromtimestamp(timesWind[-1], timezone.utc))
        print("end, ", datetime.now(), flush=True)
   

class WaveReader:
    def __init__(
        self,
        WAVE_SWH_FILE="",
        WAVE_MWD_FILE="",
        WAVE_MWP_FILE="",
        WAVE_PWP_FILE="",
        WAVE_RAD_FILE="",
        STATIONS_FILE="", 
        WAVE_SWH_DATA_FILE="",
        WAVE_MWD_DATA_FILE="",
        WAVE_MWP_DATA_FILE="",
        WAVE_PWP_DATA_FILE="",
        WAVE_RAD_DATA_FILE=""):
        temp_directory = "wave_temp/"
        self.WAVE_SWH_FILE=WAVE_SWH_FILE
        self.WAVE_MWD_FILE=WAVE_MWD_FILE
        self.WAVE_MWP_FILE=WAVE_MWP_FILE
        self.WAVE_PWP_FILE=WAVE_PWP_FILE
        self.WAVE_RAD_FILE=WAVE_RAD_FILE
        self.WAVE_SWH_DATA_FILE=WAVE_SWH_DATA_FILE
        self.WAVE_MWD_DATA_FILE=WAVE_MWD_DATA_FILE
        self.WAVE_MWP_DATA_FILE=WAVE_MWP_DATA_FILE
        self.WAVE_PWP_DATA_FILE=WAVE_PWP_DATA_FILE
        self.WAVE_RAD_DATA_FILE=WAVE_RAD_DATA_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "Wave_Station_To_Node_Distances.json"
        self.WAVE_NODES_FILE = temp_directory + "Wave_Nodes.json"
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.WAVE_NODES_FILE, format="FORT")
    
    def generateWaveDataForStations(self):
        print("Wave files", flush=True)
        print(self.WAVE_SWH_FILE, flush=True)
        print(self.WAVE_MWD_FILE, flush=True)
        print(self.WAVE_MWP_FILE, flush=True)
        print(self.WAVE_PWP_FILE, flush=True)
        print(self.WAVE_RAD_FILE, flush=True)
        swhDataset, timesSWH = self.reader.getNetcdfProperties(self.WAVE_SWH_FILE, "swh")
        mwdDataset, timesMWD = self.reader.getNetcdfProperties(self.WAVE_MWD_FILE, "mwd")
        mwpDataset, timesMWP = self.reader.getNetcdfProperties(self.WAVE_MWP_FILE, "mwp")
        pwpDataset, timesPWP = self.reader.getNetcdfProperties(self.WAVE_PWP_FILE, "pwp")
        radDataset, timesRAD = self.reader.getNetcdfProperties(self.WAVE_RAD_FILE, "rad")
        timesEqual = True
        if(timesSWH == timesMWD == timesMWP == timesPWP == timesRAD):
            timesEqual = True
        if(timesEqual):
                spaceSparseness = 10
                timeSparseness = 1
                initializeClosestWaveNodes = True
                if(initializeClosestWaveNodes):
                    thresholdDistance = 0.1
                    self.reader.initializeClosestNodes(swhDataset, thresholdDistance)
                interpolateValues = True
                if(interpolateValues):
                    self.reader.generateDataFilesWithInterpolation(swhDataset, "swh", timesSWH, spaceSparseness, timeSparseness, self.WAVE_SWH_DATA_FILE)
                    self.reader.generateDataFilesWithInterpolation(mwdDataset, "mwd", timesSWH, spaceSparseness, timeSparseness, self.WAVE_MWD_DATA_FILE)
                    self.reader.generateDataFilesWithInterpolation(mwpDataset, "mwp", timesSWH, spaceSparseness, timeSparseness, self.WAVE_MWP_DATA_FILE)
                    self.reader.generateDataFilesWithInterpolation(pwpDataset, "pwp", timesSWH, spaceSparseness, timeSparseness, self.WAVE_PWP_DATA_FILE)
                    self.reader.generateDataFilesWithInterpolation(radDataset, "rad", timesSWH, spaceSparseness, timeSparseness, self.WAVE_RAD_DATA_FILE)
                else:
                    self.reader.generateDataFiles(swhDataset, "swh", timesSWH, self.WAVE_SWH_DATA_FILE)
                    self.reader.generateDataFiles(mwdDataset, "mwd", timesSWH, self.WAVE_MWD_DATA_FILE)
                    self.reader.generateDataFiles(mwpDataset, "mwp", timesSWH, self.WAVE_MWP_DATA_FILE)
                    self.reader.generateDataFiles(pwpDataset, "pwp", timesSWH, self.WAVE_PWP_DATA_FILE)
                    self.reader.generateDataFiles(radDataset, "rad", timesSWH, self.WAVE_RAD_DATA_FILE)
                return (datetime.fromtimestamp(timesSWH[0], timezone.utc), datetime.fromtimestamp(timesSWH[-1], timezone.utc))
