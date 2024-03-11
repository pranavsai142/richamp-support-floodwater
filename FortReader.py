import netCDF4 as nc
import haversine
import json
from datetime import datetime, timedelta


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

class FortReader:
    def __init__(self, FORT_74_FILE_NAME, NOS_STATIONS_FILE_NAME, ADCIRC_WIND_DATA_FILE_NAME):
        self.FORT_74_FILE_NAME = FORT_74_FILE_NAME
        self.NOS_STATIONS_FILE_NAME = NOS_STATIONS_FILE_NAME
        self.NOS_STATION_TO_NODE_DISTANCES_FILE_NAME = "RICHAMP_Station_To_Node_Distances.json"
        self.NOS_ADCIRC_NODES_FILE_NAME = "RICHAMP_ADCIRC_Nodes.json"
        self.NOS_ADCIRC_WIND_DATA_FILE_NAME = ADCIRC_WIND_DATA_FILE_NAME
        self.NOS_ADCIRC_NODES_WIND_DATA_FILE_NAME = "RICHAMP_Nodes_Wind_Data.json"
        
    def generateWindDataForStations(self, NOS_ADCIRC_WIND_DATA_FILE_NAME):
        self.NOS_ADCIRC_WIND_DATA_FILE_NAME = NOS_ADCIRC_WIND_DATA_FILE_NAME
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
    
            with open(self.NOS_ADCIRC_WIND_DATA_FILE_NAME, "w") as outfile:
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

    
  
