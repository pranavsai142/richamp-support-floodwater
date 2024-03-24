import netCDF4 as nc
import haversine
import json
from datetime import datetime, timedelta
import os


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
        self.STATIONS_FILE=STATIONS_FILE
        self.WAVE_SWH_DATA_FILE=WAVE_SWH_DATA_FILE
        self.WAVE_MWD_DATA_FILE=WAVE_MWD_DATA_FILE
        self.WAVE_MWP_DATA_FILE=WAVE_MWP_DATA_FILE
        self.WAVE_PWP_DATA_FILE=WAVE_PWP_DATA_FILE
        self.WAVE_RAD_DATA_FILE=WAVE_RAD_DATA_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "Wave_Station_To_Node_Distances.json"
        self.NODES_FILE = temp_directory + "Wave_Nodes.json"
    
    def extractLatitudeIndex(self, nodeIndex):
        return int(nodeIndex[1: nodeIndex.find(",")])
    def extractLongitudeIndex(self, nodeIndex):
        return int(nodeIndex[nodeIndex.find(",") + 1: nodeIndex.find(")")]) 
             
    def getNetcdfProperties(self, NETCDF_FILE, dataType):
        dataset = nc.Dataset(NETCDF_FILE)
        metadata = dataset.__dict__

        datasetTimeDescription = dataset.variables["time"].units
        coldStartDateText = datasetTimeDescription[14: 24] + "T" + datasetTimeDescription[25:]
        coldStartDate = datetime.fromisoformat(coldStartDateText)
#         print("coldStartDate", coldStartDate)

        minT = float(dataset.variables["time"][0].data)
        maxT = float(dataset.variables["time"][-1].data)
#         print(minT)
#         print(maxT)

#         print("deltaT of data")
        windDeltaT = timedelta(seconds=maxT - minT)
 #        print(windDeltaT)

#         print("number of timesteps")
        timesteps = len(dataset.variables["time"][:])
#         print(timesteps)

        times = []
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
            print("significant wave height at node200000")
        
            swhX0 = dataset.variables["swan_HS"][0][200000]

            print("swhX0", swhX0)
        if (dataType == "mwd"):
            print("mean wave direction at node200000")
        
            mwdX0 = dataset.variables["swan_DIR"][0][200000]

            print("mwdX0", mwdX0)
        if (dataType == "mwp"):
            print("mean wave period at node200000")
        
            mwpX0 = dataset.variables["swan_TMM10"][0][200000]

            print("mwpX0", mwpX0)
        if (dataType == "pwp"):
            print("peak wave period at node200000")
        
            tpsX0 = dataset.variables["swan_TPS"][0][200000]

            print("tpsX0", tpsX0)
        if (dataType == "rad"):
            print("radiation stress gradient at node200000")
        
            radX0 = dataset.variables["radstress_x"][0][200000]
            radY0 = dataset.variables["radstress_y"][0][200000]

            print("radX0", radX0)
            print("radY0", radY0)
        
        return dataset, times
    
        
    def initializeClosestNodes(self, dataset):
        # Find node indexes that are closest to NOS_Stations
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)

        stationToNodeDistancesDict = {}
        for stationKey in stationsDict["NOS"].keys():
            stationToNodeDistancesDict[stationKey] = {}
        # recreate station to node distances calculations dictionary
        numberOfNodes = dataset.variables["x"].shape[0]
        for nodeIndex in range(numberOfNodes):
    #     There are nodes in the gulf of mexico between node 400000 - 500000 for rivc1 map
    #     for nodeIndex in range(100000):
    #         nodeIndex = nodeIndex + 400000
            node = (float(dataset.variables["y"][nodeIndex].data), float(dataset.variables["x"][nodeIndex].data))
            if(node[0] <= 90 and node[0] >= -90):
                for stationKey in stationsDict["NOS"].keys():
                    stationDict = stationsDict["NOS"][stationKey]
                    stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
                    distance = haversine.haversine(stationCoordinates, node)
                    if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
                    elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
            else:
                badNodes.append(nodeIndex)
                print("bad node", nodeIndex, node)

        #     Print progress
            if(nodeIndex % 50000 == 0):
                print("on node", nodeIndex, node)

        print("stationToNodeDistancesDict", stationToNodeDistancesDict)

        with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
            json.dump(stationToNodeDistancesDict, outfile)
                
        with open(self.STATION_TO_NODE_DISTANCES_FILE) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
        
        nodes = {"NOS": {}}
    
        for stationKey in stationToNodeDistancesDict.keys():
            stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
            nodeIndex = stationToNodeDistanceDict["nodeIndex"]
            nodes["NOS"][nodeIndex] = {}
            nodes["NOS"][nodeIndex]["latitude"] = float(dataset.variables["y"][int(nodeIndex)].data)
            nodes["NOS"][nodeIndex]["longitude"] = float(dataset.variables["x"][int(nodeIndex)].data)
            nodes["NOS"][nodeIndex]["stationKey"] = stationKey
            
        with open(self.NODES_FILE, "w") as outfile:
            json.dump(nodes, outfile)
    
    def generateDataFiles(self, dataset, dataType, times, DATA_FILE):
    
        with open(self.NODES_FILE) as outfile:
            nodes = json.load(outfile)
            
        data = {}
        for nodeIndex in nodes["NOS"].keys():
#                 print("getting wind data for node", nodeIndex)
            data[nodeIndex] = {}
            data[nodeIndex]["latitude"] = float(dataset.variables["y"][int(nodeIndex)].data)
            data[nodeIndex]["longitude"] = float(dataset.variables["x"][int(nodeIndex)].data)
            data[nodeIndex]["stationKey"] = nodes["NOS"][nodeIndex]["stationKey"]
            data[nodeIndex]["times"] = times
            values = []
            valuesX = []
            valuesY = []
            for index in range(len(times)):
                if(dataType == "swh"):
                    values.append(float(dataset.variables["swan_HS"][index][int(nodeIndex)]))
                elif(dataType == "mwd"):
                    values.append(float(dataset.variables["swan_DIR"][index][int(nodeIndex)]))
                elif(dataType == "mwp"):
                    values.append(float(dataset.variables["swan_TMM10"][index][int(nodeIndex)]))
                elif(dataType == "pwp"):
                    values.append(float(dataset.variables["swan_TPS"][index][int(nodeIndex)]))
                elif(dataType == "rad"):
                    radStressX = valuesX.append(float(dataset.variables["radstress_x"][index][int(nodeIndex)]))
                    radStressY = valuesY.append(float(dataset.variables["radstress_y"][index][int(nodeIndex)]))

            if(dataType == "rad"):
                data[nodeIndex]["radstressX"] = valuesX
                data[nodeIndex]["radstressY"] = valuesY
            else:
                data[nodeIndex][dataType] = values
    
        with open(DATA_FILE, "w") as outfile:
            json.dump(data, outfile)
            
    def generateWaveDataForStations(self):
        print("Wave files")
        print(self.WAVE_SWH_FILE)
        print(self.WAVE_MWD_FILE)
        print(self.WAVE_MWP_FILE)
        print(self.WAVE_PWP_FILE)
        print(self.WAVE_RAD_FILE)
        swhDataset, timesSWH = self.getNetcdfProperties(self.WAVE_SWH_FILE, "swh")
        mwdDataset, timesMWD = self.getNetcdfProperties(self.WAVE_MWD_FILE, "mwd")
        mwpDataset, timesMWP = self.getNetcdfProperties(self.WAVE_MWP_FILE, "mwp")
        pwpDataset, timesPWP = self.getNetcdfProperties(self.WAVE_PWP_FILE, "pwp")
        radDataset, timesRAD = self.getNetcdfProperties(self.WAVE_RAD_FILE, "rad")
        
        timesEqual = False
        if(timesSWH == timesMWD == timesMWP == timesPWP == timesRAD):
            timesEqual = True
        
        if(timesEqual):
            initializeClosestWaveNodes = False
            if(initializeClosestWaveNodes):
                self.initializeClosestNodes(swhDataset)
            self.generateDataFiles(swhDataset, "swh", timesSWH, self.WAVE_SWH_DATA_FILE)
            self.generateDataFiles(mwdDataset, "mwd", timesMWD, self.WAVE_MWD_DATA_FILE)
            self.generateDataFiles(mwpDataset, "mwp", timesMWP, self.WAVE_MWP_DATA_FILE)
            self.generateDataFiles(pwpDataset, "pwp", timesPWP, self.WAVE_PWP_DATA_FILE)
            self.generateDataFiles(radDataset, "rad", timesRAD, self.WAVE_RAD_DATA_FILE)
            return (timesSWH[0], timesSWH[-1])


class PostReader:
    def __init__(self, POST_WIND_FILE="", STATIONS_FILE="", POST_WIND_DATA_FILE=""):
        temp_directory = "wind_temp/"
        self.POST_WIND_FILE = POST_WIND_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "Post_Station_To_Node_Distances.json"
        self.POST_NODES_FILE = temp_directory + "Post_Nodes.json"
        self.POST_WIND_DATA_FILE = POST_WIND_DATA_FILE
        self.POST_NODES_WIND_DATA_FILE = temp_directory + "Post_Nodes_Wind_Data.json"
        
    def extractLatitudeIndex(self, nodeIndex):
        return int(nodeIndex[1: nodeIndex.find(",")])
    def extractLongitudeIndex(self, nodeIndex):
        return int(nodeIndex[nodeIndex.find(",") + 1: nodeIndex.find(")")])
    
    def generateWindDataForStations(self):
        print(self.POST_WIND_FILE)
        windDataset = nc.Dataset(self.POST_WIND_FILE)["Main"]
        windMetadata = windDataset.__dict__
        print(windMetadata)
        print(windDataset.variables)
        print(windDataset.variables["time"].units)

#         rainDataset = nc.Dataset(self.GFS_RAIN_FILE)
#         rainMetadata = rainDataset.__dict__
#         print(rainMetadata)
#         print(rainDataset.variables)
#         print(rainDataset.variables["time"].units)
#         quit()

        windDatasetTimeDescription = windDataset.variables["time"].units
        coldStartDateText = windDatasetTimeDescription[14: 24] + "T" + windDatasetTimeDescription[25:]
        coldStartDate = datetime.fromisoformat(coldStartDateText)
        print("coldStartDate", coldStartDate)

        minT = float(windDataset.variables["time"][0].data)
        maxT = float(windDataset.variables["time"][-1].data)
        print(minT)
        print(maxT)

        print("deltaT of data")
        windDeltaT = timedelta(minutes=maxT - minT)
        print(windDeltaT)

        print("number of timesteps")
        timesteps = len(windDataset.variables["time"][:])
        print(timesteps)

        times = []
        for index in range(timesteps):
            time = coldStartDate + timedelta(minutes=float(windDataset.variables["time"][index].data))
            times.append(time.timestamp())

        print("start of wind data (seconds since coldstart)")
        startDate = coldStartDate + timedelta(minutes=float(minT))
        endDate = coldStartDate + timedelta(minutes=float(maxT))
        print("startDate", startDate)
        print("endDate", endDate)

        # GFS Data is grid based system
        print("min max latitude and longitude")
        minLatitude = windDataset.variables["lat"][0].data
        minLongitude = windDataset.variables["lon"][0].data
        maxLatitude = windDataset.variables["lat"][-1].data
        maxLongitude = windDataset.variables["lon"][-1].data

        print("minLatitude", minLatitude)
        print("minLongitude", minLongitude)
        print("maxLatitude", maxLatitude)
        print("maxLongitude", maxLongitude)

        deltaLatitude = maxLatitude - minLatitude
        deltaLongitude = maxLongitude - minLongitude

        print("deltaLatitude", deltaLatitude)
        print("deltaLongitude", deltaLongitude)

        deltaNodesLatitude = len(windDataset.variables["lat"][:])
        deltaNodesLongitude = len(windDataset.variables["lon"][:])

        print("deltaNodesLatitude", deltaNodesLatitude)
        print("deltaNodesLongitude", deltaNodesLongitude)

        print("Wind at t=0, point(0, 0)")
#         wind speed(time, lat, long)
        windSpeed000 = windDataset.variables["spd"][0][0][0]
        windDir000 = windDataset.variables["dir"][0][0][0]
        print("windSpeed000", windSpeed000)
        print("windDir000", windDir000)

        # Find node indexes that are closest to NOS_Stations
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
    
        stationToNodeDistancesDict = {}

        # Set to true to recreate station to node distances calculations dictionary
        initializeStationToNodeDistancesDict = True
        if(initializeStationToNodeDistancesDict):
            for stationKey in stationsDict["NOS"].keys():
                stationToNodeDistancesDict[stationKey] = {}

            for longitudeIndex in range(deltaNodesLongitude):
                for latitudeIndex in range(deltaNodesLatitude):
                    node = (float(windDataset.variables["lat"][latitudeIndex].data), float(windDataset.variables["lon"][longitudeIndex].data))
                    nodeIndex = str((latitudeIndex, longitudeIndex))
                    if(node[0] <= 90 and node[0] >= -90):
                        for stationKey in stationsDict["NOS"].keys():
                            stationDict = stationsDict["NOS"][stationKey]
                            stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
                            distance = haversine.haversine(stationCoordinates, node)
                            if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
                                stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                                stationToNodeDistancesDict[stationKey]["distance"] = distance
                            elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
                                stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                                stationToNodeDistancesDict[stationKey]["distance"] = distance
                    else:
                        badNodes.append(nodeIndex)
                        print("bad node", nodeIndex, node)
        
            print("stationToNodeDistancesDict", stationToNodeDistancesDict)

            with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
                json.dump(stationToNodeDistancesDict, outfile)

        with open(self.STATION_TO_NODE_DISTANCES_FILE) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
  
        nodes = {"NOS": {}}
    
        initializeNodesDict = True
        if(initializeNodesDict):
            for stationKey in stationToNodeDistancesDict.keys():
                stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
                nodeIndex = stationToNodeDistanceDict["nodeIndex"]
                nodes["NOS"][nodeIndex] = {}
                nodes["NOS"][nodeIndex]["latitude"] = float(windDataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                nodes["NOS"][nodeIndex]["longitude"] = float(windDataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
                nodes["NOS"][nodeIndex]["stationKey"] = stationKey
                
            with open(self.POST_NODES_FILE, "w") as outfile:
                json.dump(nodes, outfile)

        with open(self.POST_NODES_FILE) as outfile:
            nodes = json.load(outfile)

        initializeWindDataDict = True
        if(initializeWindDataDict):
            windData = {}
            for nodeIndex in nodes["NOS"].keys():
#                 print("getting wind data for node", nodeIndex)
                windData[nodeIndex] = {}
                windData[nodeIndex]["latitude"] = float(windDataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                windData[nodeIndex]["longitude"] = float(windDataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
                windData[nodeIndex]["stationKey"] = nodes["NOS"][nodeIndex]["stationKey"]
                windData[nodeIndex]["times"] = times
                windSpeeds = []
                windDirs = []
                for index in range(timesteps):
                    windSpeeds.append(float(windDataset.variables["spd"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)]))
                    windDirs.append(float(windDataset.variables["dir"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)]))
                windData[nodeIndex]["speeds"] = windSpeeds
                windData[nodeIndex]["directions"] = windDirs
    
            with open(self.POST_WIND_DATA_FILE, "w") as outfile:
                json.dump(windData, outfile)
            
        initializeGFSNodesWindDataDict = False
        if(initializeGFSNodesWindDataDict):
            postNodesWindData = {}
            for longitudeIndex in range(deltaNodesLongitude):
                for latitudeIndex in range(deltaNodesLatitude):
                    nodeIndex = str((latitudeIndex, longitudeIndex))
                    postNodesWindData[nodeIndex] = {}
                    postNodesWindData[nodeIndex]["latitude"] = float(windDataset.variables["lat"][latitudeIndex].data)
                    postNodesWindData[nodeIndex]["longitude"] = float(windDataset.variables["lon"][longitudeIndex].data)
                    postNodesWindData[nodeIndex]["times"] = times
                    windSpeeds = []
                    windDirs = []
                    for index in range(timesteps):
                        windSpeeds.append(float(windDataset.variables["spd"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)]))
                        windDirs.append(float(windDataset.variables["dir"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)]))
                    postNodesWindData[nodeIndex]["speeds"] = windSpeeds
                    postNodesWindData[nodeIndex]["directions"] = windDirs
    
            with open(self.POST_NODES_WIND_DATA_FILE, "w") as outfile:
                json.dump(postNodesWindData, outfile)
        
        return (startDate, endDate)

class GFSReader:
    def __init__(self, GFS_WIND_FILE="", GFS_RAIN_FILE="", STATIONS_FILE="", GFS_WIND_DATA_FILE="", GFS_RAIN_DATA_FILE=""):
        temp_directory = "wind_temp/"
        self.GFS_WIND_FILE = GFS_WIND_FILE
        self.GFS_RAIN_FILE = GFS_RAIN_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "GFS_Station_To_Node_Distances.json"
        self.GFS_NODES_FILE = temp_directory + "GFS_Nodes.json"
        self.GFS_WIND_DATA_FILE = GFS_WIND_DATA_FILE
        self.GFS_RAIN_DATA_FILE = GFS_RAIN_DATA_FILE
        self.GFS_NODES_WIND_DATA_FILE = temp_directory + "GFS_Nodes_Wind_Data.json"
        
    def extractLatitudeIndex(self, nodeIndex):
        return int(nodeIndex[1: nodeIndex.find(",")])
    def extractLongitudeIndex(self, nodeIndex):
        return int(nodeIndex[nodeIndex.find(",") + 1: nodeIndex.find(")")])
    
    def generateWindDataForStations(self):
        print(self.GFS_WIND_FILE)
        windDataset = nc.Dataset(self.GFS_WIND_FILE)
        windMetadata = windDataset.__dict__
        print(windMetadata)
        print(windDataset.variables)
        print(windDataset.variables["time"].units)

        rainDataset = nc.Dataset(self.GFS_RAIN_FILE)
        rainMetadata = rainDataset.__dict__
        print(rainMetadata)
        print(rainDataset.variables)
        print(rainDataset.variables["time"].units)

        windDatasetTimeDescription = windDataset.variables["time"].units
        coldStartDateText = windDatasetTimeDescription[14: 24] + "T" + windDatasetTimeDescription[25:]
        coldStartDate = datetime.fromisoformat(coldStartDateText)
        print("coldStartDate", coldStartDate)

        minT = windDataset.variables["time"][0].data
        maxT = windDataset.variables["time"][-1].data
        print(minT)
        print(maxT)

        print("deltaT of data")
        windDeltaT = timedelta(minutes=maxT - minT)
        print(windDeltaT)

        print("number of timesteps")
        timesteps = len(windDataset.variables["time"][:])
        print(timesteps)

        times = []
        for index in range(timesteps):
            time = coldStartDate + timedelta(minutes=float(windDataset.variables["time"][index].data))
            times.append(time.timestamp())

        print("start of wind data (seconds since coldstart)")
        startDate = coldStartDate + timedelta(minutes=float(minT))
        endDate = coldStartDate + timedelta(minutes=float(maxT))
        print("startDate", startDate)
        print("endDate", endDate)

        # GFS Data is grid based system
        print("min max latitude and longitude")
        minLatitude = windDataset.variables["lat"][0].data
        minLongitude = windDataset.variables["lon"][0].data
        maxLatitude = windDataset.variables["lat"][-1].data
        maxLongitude = windDataset.variables["lon"][-1].data

        print("minLatitude", minLatitude)
        print("minLongitude", minLongitude)
        print("maxLatitude", maxLatitude)
        print("maxLongitude", maxLongitude)

        deltaLatitude = maxLatitude - minLatitude
        deltaLongitude = maxLongitude - minLongitude

        print("deltaLatitude", deltaLatitude)
        print("deltaLongitude", deltaLongitude)

        deltaNodesLatitude = len(windDataset.variables["lat"][:])
        deltaNodesLongitude = len(windDataset.variables["lon"][:])

        print("deltaNodesLatitude", deltaNodesLatitude)
        print("deltaNodesLongitude", deltaNodesLongitude)

        print("Wind at t=0, point(0, 0)")
        windX000 = windDataset.variables["wind_u"][0][0][0]
        windY000 = windDataset.variables["wind_v"][0][0][0]
        print("windX000", windX000)
        print("windY000", windY000)

        # Find node indexes that are closest to NOS_Stations
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
    
        stationToNodeDistancesDict = {}

        # Set to true to recreate station to node distances calculations dictionary
        initializeStationToNodeDistancesDict = True
        if(initializeStationToNodeDistancesDict):
            for stationKey in stationsDict["NOS"].keys():
                stationToNodeDistancesDict[stationKey] = {}

            for longitudeIndex in range(deltaNodesLongitude):
                for latitudeIndex in range(deltaNodesLatitude):
                    node = (float(windDataset.variables["lat"][latitudeIndex].data), float(windDataset.variables["lon"][longitudeIndex].data))
                    nodeIndex = str((latitudeIndex, longitudeIndex))
                    if(node[0] <= 90 and node[0] >= -90):
                        for stationKey in stationsDict["NOS"].keys():
                            stationDict = stationsDict["NOS"][stationKey]
                            stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
                            distance = haversine.haversine(stationCoordinates, node)
                            if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
                                stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                                stationToNodeDistancesDict[stationKey]["distance"] = distance
                            elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
                                stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                                stationToNodeDistancesDict[stationKey]["distance"] = distance
                    else:
                        badNodes.append(nodeIndex)
                        print("bad node", nodeIndex, node)
        
            print("stationToNodeDistancesDict", stationToNodeDistancesDict)

            with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
                json.dump(stationToNodeDistancesDict, outfile)

        with open(self.STATION_TO_NODE_DISTANCES_FILE) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
  
        gfsNodes = {"NOS": {}}
    
        initializeGFSNodesDict = True
        if(initializeGFSNodesDict):
            for stationKey in stationToNodeDistancesDict.keys():
                stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
                nodeIndex = stationToNodeDistanceDict["nodeIndex"]
                gfsNodes["NOS"][nodeIndex] = {}
                gfsNodes["NOS"][nodeIndex]["latitude"] = float(windDataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                gfsNodes["NOS"][nodeIndex]["longitude"] = float(windDataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
                gfsNodes["NOS"][nodeIndex]["stationKey"] = stationKey
                
            with open(self.GFS_NODES_FILE, "w") as outfile:
                json.dump(gfsNodes, outfile)

        with open(self.GFS_NODES_FILE) as outfile:
            gfsNodes = json.load(outfile)

        initializeGFSWindDataDict = True
        if(initializeGFSWindDataDict):
            gfsWindData = {}
            for nodeIndex in gfsNodes["NOS"].keys():
#                 print("getting wind data for node", nodeIndex)
                gfsWindData[nodeIndex] = {}
                gfsWindData[nodeIndex]["latitude"] = float(windDataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                gfsWindData[nodeIndex]["longitude"] = float(windDataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
                gfsWindData[nodeIndex]["stationKey"] = gfsNodes["NOS"][nodeIndex]["stationKey"]
                gfsWindData[nodeIndex]["times"] = times
                windsX = []
                windsY = []
                for index in range(timesteps):
                    windsX.append(float(windDataset.variables["wind_u"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)]))
                    windsY.append(float(windDataset.variables["wind_v"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)]))
                gfsWindData[nodeIndex]["windsX"] = windsX
                gfsWindData[nodeIndex]["windsY"] = windsY
    
            with open(self.GFS_WIND_DATA_FILE, "w") as outfile:
                json.dump(gfsWindData, outfile)
                
        initializeGFSRainDataDict = True
        if(initializeGFSRainDataDict):
            gfsRainData = {}
            for nodeIndex in gfsNodes["NOS"].keys():
                gfsRainData[nodeIndex] = {}
                gfsRainData[nodeIndex]["latitude"] = float(rainDataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                gfsRainData[nodeIndex]["longitude"] = float(rainDataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
                gfsRainData[nodeIndex]["stationKey"] = gfsNodes["NOS"][nodeIndex]["stationKey"]
                gfsRainData[nodeIndex]["times"] = times
                rains = []
                for index in range(timesteps):
                    rains.append(float(rainDataset.variables["rain"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)]))
                gfsRainData[nodeIndex]["rains"] = rains
        
            with open(self.GFS_RAIN_DATA_FILE, "w") as outfile:
                json.dump(gfsRainData, outfile)
            
        initializeGFSNodesWindDataDict = False
        if(initializeGFSNodesWindDataDict):
            gfsNodesWindData = {}
            for longitudeIndex in range(deltaNodesLongitude):
                for latitudeIndex in range(deltaNodesLatitude):
                    nodeIndex = str((latitudeIndex, longitudeIndex))
                    gfsNodesWindData[nodeIndex] = {}
                    gfsNodesWindData[nodeIndex]["latitude"] = float(windDataset.variables["lat"][latitudeIndex].data)
                    gfsNodesWindData[nodeIndex]["longitude"] = float(windDataset.variables["lon"][longitudeIndex].data)
                    gfsNodesWindData[nodeIndex]["times"] = times
                    windsX = []
                    windsY = []
                    for index in range(timesteps):
                        windsX.append(float(windDataset.variables["wind_u"][index][longitudeIndex][latitudeIndex]))
                        windsY.append(float(windDataset.variables["wind_v"][index][longitudeIndex][latitudeIndex]))
                    gfsNodesWindData[nodeIndex]["windsX"] = windsX
                    gfsNodesWindData[nodeIndex]["windsY"] = windsY
    
            with open(self.GFS_NODES_WIND_DATA_FILE, "w") as outfile:
                json.dump(adcircNodesWindData, outfile)
        
        return (startDate, endDate)

class FortReader:
    def __init__(self, FORT_74_FILE_NAME, NOS_STATIONS_FILE_NAME, ADCIRC_WIND_DATA_FILE_NAME):
        self.FORT_74_FILE_NAME = FORT_74_FILE_NAME
        self.NOS_STATIONS_FILE_NAME = NOS_STATIONS_FILE_NAME
        self.NOS_STATION_TO_NODE_DISTANCES_FILE_NAME = "RICHAMP_Station_To_Node_Distances.json"
        self.NOS_ADCIRC_NODES_FILE_NAME = "RICHAMP_ADCIRC_Nodes.json"
        self.ADCIRC_WIND_DATA_FILE_NAME = ADCIRC_WIND_DATA_FILE_NAME
        self.NOS_ADCIRC_NODES_WIND_DATA_FILE_NAME = "RICHAMP_Nodes_Wind_Data.json"
        
    def generateWindDataForStations(self):
        print(self.FORT_74_FILE_NAME)
        windDataset = nc.Dataset(self.FORT_74_FILE_NAME)
        windMetadata = windDataset.__dict__
        print(windMetadata)
        print(windDataset.variables["time"].units)

        windDatasetTimeDescription = windDataset.variables["time"].units
        coldStartDateText = windDatasetTimeDescription[14: 24] + "T" + windDatasetTimeDescription[25:]
        coldStartDate = datetime.fromisoformat(coldStartDateText)
        print("coldStartDate", coldStartDate)

        minT = windDataset.variables["time"][0].data
        maxT = windDataset.variables["time"][-1].data
        print(minT)
        print(maxT)

        print("deltaT of data")
        windDeltaT = timedelta(seconds=maxT - minT)
        print(windDeltaT)

        print("number of timesteps")
        timesteps = len(windDataset.variables["time"][:])
        print(timesteps)

        times = []
        for index in range(timesteps):
            time = coldStartDate + timedelta(seconds=float(windDataset.variables["time"][index].data))
            times.append(time.timestamp())

        print("start of wind data (seconds since coldstart)")
        startDate = coldStartDate + timedelta(seconds=float(minT))
        endDate = coldStartDate + timedelta(seconds=float(maxT))
        print("startDate", startDate)
        print("endDate", endDate)

        # Grid origin is top right? Maybe not, Node based system!
        # y is latitude, x is longitude
        node0 = (float(windDataset.variables["y"][0].data), float(windDataset.variables["x"][0].data))
        print("node0 (lat, long)", node0)

        numberOfNodes = windDataset.variables["x"].shape[0]

        print("number of nodes", numberOfNodes)

        print("wind at node0")

        windX0 = windDataset.variables["windx"][0][0]
        windY0 = windDataset.variables["windy"][0][0]

        print("windX0", windX0)
        print("windY0", windY0)

        # Find node indexes that are closest to NOS_Stations
        with open(self.NOS_STATIONS_FILE_NAME) as stations_file:
            stationsDict = json.load(stations_file)
    
        stationToNodeDistancesDict = {}

        # Set to true to recreate station to node distances calculations dictionary
        initializeStationToNodeDistancesDict = False 
        if(initializeStationToNodeDistancesDict):
            for stationKey in stationsDict["NOS"].keys():
                stationToNodeDistancesDict[stationKey] = {}

            for nodeIndex in range(numberOfNodes):
        #     There are nodes in the gulf of mexico between node 400000 - 500000 for rivc1 map
        #     for nodeIndex in range(100000):
        #         nodeIndex = nodeIndex + 400000
                node = (float(windDataset.variables["y"][nodeIndex].data), float(windDataset.variables["x"][nodeIndex].data))
                if(node[0] <= 90 and node[0] >= -90):
                    for stationKey in stationsDict["NOS"].keys():
                        stationDict = stationsDict["NOS"][stationKey]
                        stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
                        distance = haversine.haversine(stationCoordinates, node)
                        if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
                            stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                            stationToNodeDistancesDict[stationKey]["distance"] = distance
                        elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
                            stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                            stationToNodeDistancesDict[stationKey]["distance"] = distance
                else:
                    badNodes.append(nodeIndex)
                    print("bad node", nodeIndex, node)
    
            #     Print progress
                if(nodeIndex % 50000 == 0):
                    print("on node", nodeIndex, node)
        
            print("stationToNodeDistancesDict", stationToNodeDistancesDict)

            with open(self.NOS_STATION_TO_NODE_DISTANCES_FILE_NAME, "w") as outfile:
                json.dump(stationToNodeDistancesDict, outfile)

        with open(self.NOS_STATION_TO_NODE_DISTANCES_FILE_NAME) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
  
        adcircNodes = {"NOS": {}}
    
        initializeAdcircNodesDict = False
        if(initializeAdcircNodesDict):
            for stationKey in stationToNodeDistancesDict.keys():
                stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
                nodeIndex = stationToNodeDistanceDict["nodeIndex"]
                adcircNodes["NOS"][nodeIndex] = {}
                adcircNodes["NOS"][nodeIndex]["latitude"] = float(windDataset.variables["y"][nodeIndex].data)
                adcircNodes["NOS"][nodeIndex]["longitude"] = float(windDataset.variables["x"][nodeIndex].data)
                adcircNodes["NOS"][nodeIndex]["stationKey"] = stationKey
    
            with open(self.NOS_ADCIRC_NODES_FILE_NAME, "w") as outfile:
                json.dump(adcircNodes, outfile)

        with open(self.NOS_ADCIRC_NODES_FILE_NAME) as outfile:
            adcircNodes = json.load(outfile)

        initializeAdcircWindDataDict = True
        if(initializeAdcircWindDataDict):
            adcircWindData = {}
            for nodeIndex in adcircNodes["NOS"].keys():
                adcircWindData[nodeIndex] = {}
                adcircWindData[nodeIndex]["latitude"] = float(windDataset.variables["y"][int(nodeIndex)].data)
                adcircWindData[nodeIndex]["longitude"] = float(windDataset.variables["x"][int(nodeIndex)].data)
                adcircWindData[nodeIndex]["stationKey"] = adcircNodes["NOS"][nodeIndex]["stationKey"]
                adcircWindData[nodeIndex]["times"] = times
                windsX = []
                windsY = []
                for index in range(timesteps):
                    windsX.append(windDataset.variables["windx"][index][int(nodeIndex)])
                    windsY.append(windDataset.variables["windy"][index][int(nodeIndex)])
                adcircWindData[nodeIndex]["windsX"] = windsX
                adcircWindData[nodeIndex]["windsY"] = windsY
    
            with open(self.ADCIRC_WIND_DATA_FILE_NAME, "w") as outfile:
                json.dump(adcircWindData, outfile)
    
        initializeAdcircNodesWindDataDict = False
        if(initializeAdcircNodesWindDataDict):
            adcircNodesWindData = {}
            for nodeIndex in range(numberOfNodes):
                if(nodeIndex % 50000 == 0):
                    adcircNodesWindData[nodeIndex] = {}
                    adcircNodesWindData[nodeIndex]["latitude"] = float(windDataset.variables["y"][int(nodeIndex)].data)
                    adcircNodesWindData[nodeIndex]["longitude"] = float(windDataset.variables["x"][int(nodeIndex)].data)
                    adcircNodesWindData[nodeIndex]["times"] = times
                    windsX = []
                    windsY = []
                    for index in range(timesteps):
                        windsX.append(windDataset.variables["windx"][index][int(nodeIndex)])
                        windsY.append(windDataset.variables["windy"][index][int(nodeIndex)])
                    adcircNodesWindData[nodeIndex]["windsX"] = windsX
                    adcircNodesWindData[nodeIndex]["windsY"] = windsY
    
            with open(self.NOS_ADCIRC_NODES_WIND_DATA_FILE_NAME, "w") as outfile:
                json.dump(adcircNodesWindData, outfile)
        return (startDate, endDate)

    
  
