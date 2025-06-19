import os
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
from matplotlib.cm import ScalarMappable
from matplotlib.tri import Triangulation
from datetime import datetime, timezone
import imageio
import gc
from geographiclib.geodesic import Geodesic


SMALL_SIZE = 14
MEDIUM_SIZE = 18
BIGGER_SIZE = 22

plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
plt.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

class Grapher:
    DATE_FORMAT = "%m/%d/%y-%HZ"    
    CONVERT_TO_WATER_DEPTH = False
    
    DEPTH_LINE_7M = -7.0
    DEPTH_LINE_20M = -20.0
    DISTANCE_LINE_9000M = 9000.0
        
    def extractLatitudeIndex(self, nodeIndex):
        return int(nodeIndex[1: nodeIndex.find(",")])
    
    def extractLongitudeIndex(self, nodeIndex):
        return int(nodeIndex[nodeIndex.find(",") + 1: nodeIndex.find(")")])
    
    def vectorSpeed(self, x,y):
        return math.sqrt(x**2 + y**2)
    
    def vectorDirection(self, x,y):
        degrees = math.degrees(math.atan2(-y,x))
        if(degrees < 0):
            return degrees + 360
        return degrees
    
    def unixTimeToDeltaHours(self, timestamp, startDate):
        startDateTimestamp = datetime.timestamp(startDate)
#         Difference in timestamp between startDate and 1938 date
        timestampDelta = timestamp - startDateTimestamp
#         startDateTimestamp - (-987120000.0)
#         return datetime.fromtimestamp(timestamp, timezone.utc)
#         timestamp = (-987120000.0) + timestampDelta
        return datetime.fromtimestamp(timestamp, timezone.utc)
        delta = datetime.fromtimestamp(timestamp, timezone.utc) - startDate
        return delta.total_seconds()/3600
    
    def extrapolateWindToTenMeterHeight(self, windVelocity, altitude):
        return windVelocity
    #     WIND_PROFILE_EXPONENT = 0.11
    #     return windVelocity * ((10.0/altitude)**WIND_PROFILE_EXPONENT)
    
    def plotExtendedLines(self, ax, runupIndex, index, runupLabel):
        # Get coordinates for waterline (two points)
        waterline_lon1 = float(self.datapointsWaterlineLongitudes[runupIndex][index][0])
        waterline_lat1 = float(self.datapointsWaterlineLatitudes[runupIndex][index][0])
        waterline_lon2 = float(self.datapointsWaterlineLongitudes[runupIndex][index][1])
        waterline_lat2 = float(self.datapointsWaterlineLatitudes[runupIndex][index][1])
    
        # Get coordinates for runup line (two points)
        runup_lon1 = float(self.datapointsRunupLongitudes[runupIndex][index][0])
        runup_lat1 = float(self.datapointsRunupLatitudes[runupIndex][index][0])
        runup_lon2 = float(self.datapointsRunupLongitudes[runupIndex][index][1])
        runup_lat2 = float(self.datapointsRunupLatitudes[runupIndex][index][1])
    
        # Initialize geodesic calculator
        geod = Geodesic.WGS84
    
        # Calculate waterline properties
        water_g = geod.Inverse(waterline_lat1, waterline_lon1, waterline_lat2, waterline_lon2)
        water_length = water_g['s12']
        water_azi1 = water_g['azi1']  # Forward azimuth from point 1
        water_azi2 = water_g['azi2']  # Forward azimuth from point 2
    
        # Calculate runup line properties
        runup_g = geod.Inverse(runup_lat1, runup_lon1, runup_lat2, runup_lon2)
        runup_length = runup_g['s12']
        runup_azi1 = runup_g['azi1']
        runup_azi2 = runup_g['azi2']
    
        # Calculate extension distance (10x original length)
        water_ext_dist = water_length * 10
        runup_ext_dist = runup_length * 10
    
        # Extend waterline - backward from point 1
        water_back = geod.Direct(waterline_lat1, waterline_lon1, water_azi1 + 180, water_ext_dist)
        water_extend_back_lon = water_back['lon2']
        water_extend_back_lat = water_back['lat2']
    
        # Extend waterline - forward from point 2
        water_forward = geod.Direct(waterline_lat2, waterline_lon2, water_azi2, water_ext_dist)
        water_extend_forward_lon = water_forward['lon2']
        water_extend_forward_lat = water_forward['lat2']
    
        # Extend runup - backward from point 1
        runup_back = geod.Direct(runup_lat1, runup_lon1, runup_azi1 + 180, runup_ext_dist)
        runup_extend_back_lon = runup_back['lon2']
        runup_extend_back_lat = runup_back['lat2']
    
        # Extend runup - forward from point 2
        runup_forward = geod.Direct(runup_lat2, runup_lon2, runup_azi2, runup_ext_dist)
        runup_extend_forward_lon = runup_forward['lon2']
        runup_extend_forward_lat = runup_forward['lat2']
    
        # Create lists for plotting
        waterline_lons = [water_extend_back_lon, waterline_lon1, waterline_lon2, water_extend_forward_lon]
        waterline_lats = [water_extend_back_lat, waterline_lat1, waterline_lat2, water_extend_forward_lat]
        runup_lons = [runup_extend_back_lon, runup_lon1, runup_lon2, runup_extend_forward_lon]
        runup_lats = [runup_extend_back_lat, runup_lat1, runup_lat2, runup_extend_forward_lat]
    
        # Plot the extended lines
        ax.plot(waterline_lons, waterline_lats,
                label=runupLabel, zorder=3, alpha=0.7,
                marker=".", color="green")
        ax.plot(runup_lons, runup_lats,
                label=runupLabel, zorder=3, alpha=0.7,
                marker=".", color="red")
                
    def findMatchingIndices(self, string_array, match_string):
        return [i for i, s in enumerate(string_array) if match_string in s]

    # Usage example:
    # plot_extended_lines(self, ax, runupIndex, index, runupLabel)

    def __init__(self, dataToGraph={}, STATIONS_FILE="", backgroundMap="", backgroundAxis=[], titlePrefix=""):
        print("Initializing grapher", flush=True)
        self.obsExists = False
        self.gaugeExists = False
        self.tideExists = False
        self.buoyExists = False
        self.assetExists = False
        self.windExists = False
        self.wavesExists = False
        self.rainExists = False
        self.waterExists = False
        self.stillwaterExists = False
        self.tidewaterExists = False
        self.etaExists = False
        self.meshExists = False
        self.runupExists = False
        
        self.windStartDate = None
        self.waveStartDate = None
        self.rainStartDate = None
        self.waterStartDate = None
        self.etaStartDate = None
        self.runupStartDate = None
        
        self.windType = ""
        
        self.backgroundMap = backgroundMap
        self.backgroundAxis = backgroundAxis
        
        self.titlePrefix=titlePrefix
        
        if("OBS" in dataToGraph):
            self.obsExists = True
        if("GAUGE" in dataToGraph):
            self.gaugeExists = True
        if("TIDE" in dataToGraph):
            self.tideExists = True
        if("POST" in dataToGraph or "GFS" in dataToGraph or "FORT" in dataToGraph):
            self.windExists = True
        if("SWH" in dataToGraph or "MWD" in dataToGraph or "MWP" in dataToGraph or "PWP" in dataToGraph or "RAD" in dataToGraph):
            self.wavesExists = True
        if("BUOY" in dataToGraph):
            self.buoyExists = True
        if("RAIN" in dataToGraph):
            self.rainExists = True
        if("WATER" in dataToGraph):
            self.waterExists = True
        if("STILLWATER" in dataToGraph):
            self.stillwaterExists = True
        if("TIDEWATER" in dataToGraph):
            self.tidewaterExists = True
        if("ETA" in dataToGraph):
            self.etaExists = True
        if("MESH" in dataToGraph):
            self.meshExists = True
        if("ASSET" in dataToGraph):
            self.assetExists = True
        if("RUNUP" in dataToGraph):
            self.runupExists = True
        with open(STATIONS_FILE) as outfile:
            self.obsMetadata = json.load(outfile)
            
                
#         There are 3 possible perturbations. 
#          Graphing wave data on wave mesh, and also trying to graph GFS data
#           Graphing wave data on wave mesh, and also graphing POST data
#          Graphing wave data on wave mesh, and also graphing GFS/POST data and graphing OBS
#          3 sets of lat, long, labels, and times are needed, assuming that each datatype,
#           even if multiple files are contained, are internally consistent with respect to the timedelta of the data,
#         i.e. even if wave data is comprised of 5 files, the same datapointsTimes array can  be used to
#          graph the 5 timeseries, saving some space as well.

#          On second thought, the assumption that each data type will be internally consistent
#           with timedeltas does not hold for observational data, as some stations may have more data
#           than others. the obsDatapointsTimes will be structurally different from the forecsated
#           wind and waves because the observational will have timestamps for each station's wind data
#           while the forecasted data will have one master timestamp array for all the nodes being examined.

#          UPDATE: Added another perturbation by adding rain data
        
        obsLabelsInitialized = False
        self.obsLongitudes = []
        self.obsLatitudes = []
        self.obsLabels = []
        
        self.obsDatapointsTimes = []
        self.obsDatapointsDirections = []
        self.obsDatapointsSpeeds = []
        self.obsDatapointsHeights = []
        
        gaugeLabelsInitialized = False
        self.gaugeLongitudes = []
        self.gaugeLatitudes = []
        self.gaugeLabels = []
        
        self.gaugeDatapointsTimes = []
        self.gaugeDatapointsRains = []
        
        tideLabelsInitialized = False
        self.tideLongitudes = []
        self.tideLatitudes = []
        self.tideLabels = []
        
        self.tideDatapointsTimes = []
        self.tideDatapointsWaters = []
    
        self.tideDatapointsPredictionTimes = []
        self.tideDatapointsPredictionWaters = []
        
        self.windLongitudes = []
        self.windLatitudes = []
        self.windLabels = []
        self.windTimes = []
        
        self.maxWind = 20
        self.mapWindPoints = []
        self.mapWindPointsLatitudes = []
        self.mapWindPointsLongitudes = []
        self.mapWindTimes = []
        self.mapWindTriangles = []
        self.mapWindMaskedTriangles = []
        self.mapSpeeds = []
        self.mapDirections = []
        
        self.datapointsDirections = []
        self.datapointsSpeeds = []
        
        self.waterLongitudes = []
        self.waterLatitudes = []
        self.waterLabels = []
        self.waterTimes = []
        
        self.maxWater = 5
        self.mapWaterPoints = []
        self.mapWaterTimes = []
        self.mapWaterPointsLatitudes = []
        self.mapWaterPointsLongitudes = []
        self.mapWaterTriangles = []
        self.mapWaterMaskedTriangles = []
        self.mapWaters = []
        
        self.datapointsWaters = []
        
        self.stillwaterTimes = []
        self.datapointsStillwaters = []
        
        self.tidewaterTimes = []
        self.datapointsTidewaters = []
        
        self.etaLongitudes = []
        self.etaLatitudes = []
        self.etaLabels = []
        self.etaTimes = []
        
        self.maxEta = 5
        self.mapEtaPoints = []
        self.mapEtaTimes = []
        self.mapEtaPointsLatitudes = []
        self.mapEtaPointsLongitudes = []
        self.mapEta = []
        
        self.datapointsEta = []
        
        self.rainLongitudes = []
        self.rainLatitudes = []
        self.rainLabels = []
        self.rainTimes = []
        
        self.maxRain = 15
        self.mapRainPoints = []
        self.mapRainTimes = []
        self.mapRainPointsLatitudes = []
        self.mapRainPointsLongitudes = []
        self.mapRains = []
        
        self.datapointsRains = []
        
        self.waveLongitudes = []
        self.waveLatitudes = []
        self.waveLabels = []
        self.waveTimes = []
        
        self.datapointsSWH = []
        self.datapointsMWD = []
        self.datapointsMWP = []
        self.datapointsPWP = []
        self.datapointsRADMag = []
        self.datapointsRADDir = []
        
        buoyLabelsInitialized = False
        self.buoyLongitudes = []
        self.buoyLatitudes = []
        self.buoyLabels = []
        
        self.buoyDatapointsTimes = []
        self.buoyDatapointsSWH = []
        self.buoyDatapointsMWD = []
        self.buoyDatapointsMWP = []
        self.buoyDatapointsPWP = []
        
        self.maxSWH = 3
        self.mapWavePoints = []
        self.mapWavePointsLatitude = []
        self.mapWavePointsLongitude = []
        self.mapWaveTriangles = []
        self.mapWaveMaskedTriangles = []
        self.mapWaveTimes = []
        self.mapSWH = []
        
        
       
        self.elevationLongitudes = []
        self.elevationLatitudes = []
        self.elevationLabels = []
        
        self.datapointsElevation = []
        
        assetLabelsInitialized = False
        self.assetLongitudes = []
        self.assetLatitudes = []
        self.assetLabels = []
        
        self.assetDatapointsElevation = []
        
        self.maxElevation = 10
        self.mapElevationPoints = []
        self.mapElevationPointsLatitudes = []
        self.mapElevationPointsLongitudes = []
        self.mapElevationTriangles = []
        self.mapElevationMaskedTriangles = []
        self.mapElevation = []
        
        self.maxRunup = 1
        self.runupLongitudes = []
        self.runupLatitudes = []
        self.runupLabels = []
        self.runupSurfDistance = []
        self.runupOffshoreDistance = []
        self.runupAverageSlope = []
        
        self.runupTimes = []
        self.datapointsRunup = []
        self.datapointsRunupHolmanHigh = []
        self.datapointsRunupHolmanMid = []
        self.datapointsRunupHolmanLow = []
        self.datapointsSetupHolmanHigh = []
        self.datapointsSetupHolmanMid = []
        self.datapointsSetupHolmanLow = []
        self.datapointsSwashHolmanHigh = []
        self.datapointsSwashHolmanMid = []
        self.datapointsSwashHolmanLow = []
        self.datapointsSwashHolmanIncident = []
        self.datapointsSwashHolmanInfragravity = []
        self.datapointsSetupStockdon = []
        self.datapointsSetupStockdonLow = []
        self.datapointsSwashStockdonIncident = []
        self.datapointsSwashStockdonInfragravity = []
        self.datapointsSwashStockdonLow = []
        self.datapointsRunupStockdon = []
        self.datapointsRunupStockdonNoSetup = []
        self.datapointsRunupStockdonLow = []
        self.datapointsSetupAdcirc = []
        self.datapointsRunupAdcirc = []
        
        self.datapointsWavelength = []
        self.datapointsIribarren = []
        self.datapointsSteepness = []
        self.datapointsWaterlineLongitudes = []
        self.datapointsWaterlineLatitudes = []
        self.datapointsRunupLongitudes = []
        self.datapointsRunupLatitudes = []
        self.runupAverageSlopes = []
        
        self.datapointsDuneHeights = []
    

#        So loading obs, wind, and waves should be able to cover and set all available data

        windType = ""
        if("OBS" in dataToGraph):
            with open(dataToGraph["OBS"]) as outfile:
                obsDataset = json.load(outfile)
        if("POST" in dataToGraph):  
            self.windType = "POST"
            with open(dataToGraph["POST"]) as outfile:
                windDataset = json.load(outfile)
        if("GFS" in dataToGraph):
            self.windType = "GFS"
            with open(dataToGraph["GFS"]) as outfile:
                windDataset = json.load(outfile)
        if("FORT" in dataToGraph):
            self.windType = "FORT"
            with open(dataToGraph["FORT"]) as outfile:
                windDataset = json.load(outfile)
        if("GAUGE" in dataToGraph):
            with open(dataToGraph["GAUGE"]) as outfile:
                gaugeDataset = json.load(outfile)
        if("TIDE" in dataToGraph):
            with open(dataToGraph["TIDE"]) as outfile:
                tideDataset = json.load(outfile)
        if("BUOY" in dataToGraph):
            with open(dataToGraph["BUOY"]) as outfile:
                buoyDataset = json.load(outfile)
        if("ASSET" in dataToGraph):
            with open(dataToGraph["ASSET"]) as outfile:
                assetDataset = json.load(outfile)
        if("ETA" in dataToGraph):
            with open(dataToGraph["ETA"]) as outfile:
                etaDataset = json.load(outfile)

                  
        if(self.windExists):
            windTimestampsInitialized = False
            for stationKey in windDataset.keys():
                if(stationKey == "map_data"):
                    self.mapWindPoints = windDataset["map_data"]["map_points"]
                    self.mapWindPointsLatitudes = windDataset["map_data"]["map_pointsLatitudes"]
                    self.mapWindPointsLongitudes = windDataset["map_data"]["map_pointsLongitude"]
                    self.mapWindTimes = windDataset["map_data"]["map_times"]
                    if(self.windType == "FORT"):
                        self.mapWindTriangles = windDataset["map_data"]["map_triangles"]
                        self.mapWindMaskedTriangles = windDataset["map_data"]["map_maskedTriangles"]
                        mapWindsX = windDataset["map_data"]["map_windsX"]
                        mapWindsY = windDataset["map_data"]["map_windsY"]
                        for index in range(len(self.mapWindTimes)):
                            lineSpeed = []
                            lineDirection = []
                            for nodeIndex in range(len(mapWindsX[index])):
                                pointSpeed = self.vectorSpeed(mapWindsX[index][nodeIndex], mapWindsY[index][nodeIndex])
                                if(pointSpeed > self.maxWind):
                                    self.maxWind = pointSpeed
                                lineSpeed.append(pointSpeed)
                                lineDirection.append(self.vectorDirection(mapWindsX[index][nodeIndex], mapWindsY[index][nodeIndex]))
                            self.mapSpeeds.append(pointSpeeds)
                            self.mapDirections.append(pointDirections)
                    elif(self.windType == "GFS"):
                        mapWindsX = windDataset["map_data"]["map_windsX"]
                        mapWindsY = windDataset["map_data"]["map_windsY"]
                        for index in range(len(self.mapWindTimes)):
                            mapSpeed = []
                            mapDirection = []
                            for latitudeIndex in range(len(mapWindsX[index])):
                                lineSpeed = []
                                lineDirection = []
                                for longitudeIndex in range(len(mapWindsX[index][latitudeIndex])):
                                    pointSpeed = self.vectorSpeed(mapWindsX[index][latitudeIndex][longitudeIndex], mapWindsY[index][latitudeIndex][longitudeIndex])
                                    pointDirection = self.vectorDirection(mapWindsX[index][latitudeIndex][longitudeIndex], mapWindsY[index][latitudeIndex][longitudeIndex])
                                    if(pointSpeed > self.maxWind):
                                        self.maxWind = pointSpeed
                                    lineSpeed.append(pointSpeed)
                                    lineDirection.append(pointDirection)
                                mapSpeed.append(lineSpeed)
                                mapDirection.append(lineDirection)
                            self.mapSpeeds.append(mapSpeed)
                            self.mapDirections.append(mapDirection)
                    elif(self.windType == "POST"):
                        self.mapSpeeds = windDataset["map_data"]["map_speeds"]
                        self.mapDirections = windDataset["map_data"]["map_directions"]
                        for index in range(len(self.mapWindTimes)):
                            for latitudeIndex in range(len(self.mapSpeeds[index])):
                                for longitudeIndex in range(len(self.mapSpeeds[index][latitudeIndex])):
                                    pointSpeed = self.mapSpeeds[index][latitudeIndex][longitudeIndex]
                                    if(pointSpeed > self.maxWind):
                                        self.maxWind = pointSpeed
                else:
                    nodeIndex = windDataset[stationKey]["nodeIndex"]
                    if(not self.obsExists or (stationKey in obsDataset.keys())):
                        self.windLabels.append(nodeIndex)
                        self.windLatitudes.append(windDataset[stationKey]["latitude"])
                        self.windLongitudes.append(windDataset[stationKey]["longitude"])
                    
                        if(not obsLabelsInitialized):
                            self.obsLabels.append(self.obsMetadata["NOS"][stationKey]["name"])
                            self.obsLatitudes.append(float(self.obsMetadata["NOS"][stationKey]["latitude"]))
                            self.obsLongitudes.append(float(self.obsMetadata["NOS"][stationKey]["longitude"]))
                    
                        datapointDirections = []
                        datapointSpeeds = []
                        for index in range(len(windDataset[stationKey]["times"])):
                            if(self.windStartDate == None):
                                self.windStartDate = datetime.fromtimestamp(int(windDataset[stationKey]["times"][index]), timezone.utc)
                            if(not windTimestampsInitialized):
                                self.windTimes.append(self.unixTimeToDeltaHours(windDataset[stationKey]["times"][index], self.windStartDate))
                            if(self.windType == "GFS" or self.windType == "FORT"):
                                windX = windDataset[stationKey]["windsX"][index]
                                windY = windDataset[stationKey]["windsY"][index]
                                windSpeed = self.vectorSpeed(windX, windY)
                                windDirection = self.vectorDirection(windX, windY)
                            elif(self.windType == "POST"):
                                windSpeed = windDataset[stationKey]["speeds"][index]
                                windDirection = windDataset[stationKey]["directions"][index]
                            datapointDirections.append(windDirection)
                            datapointSpeeds.append(windSpeed)
                        windTimestampsInitialized = True
                        self.datapointsDirections.append(datapointDirections)
                        self.datapointsSpeeds.append(datapointSpeeds)
                        if(self.obsExists):
                            obsTimes = []
                            obsSpeeds = []
                            obsDirections = []
    #                         Height is not station altitude, it is sea surface height
                            obsHeights = []
                            for index in range(len(obsDataset[stationKey]["times"])):
                                obsTimes.append(self.unixTimeToDeltaHours(obsDataset[stationKey]["times"][index], self.windStartDate))
                                obsSpeed = obsDataset[stationKey]["speeds"][index]
                                obsDirection = obsDataset[stationKey]["directions"][index]
                                obsHeight = obsDataset[stationKey]["heights"][index]
                                obsSpeeds.append(obsSpeed)
                                obsDirections.append(obsDirection)
                                obsHeights.append(obsHeight)
                            self.obsDatapointsTimes.append(obsTimes)
                            self.obsDatapointsSpeeds.append(obsSpeeds)
                            self.obsDatapointsDirections.append(obsDataset[stationKey]["directions"])
                            self.obsDatapointsHeights.append(obsHeights)
            obsLabelsInitialized = True
                        
        if(self.rainExists):
            with open(dataToGraph["RAIN"]) as outfile:
                rainDataset = json.load(outfile)
                
            rainTimestampsInitialized = False
            for stationKey in rainDataset.keys():
                if(stationKey == "map_data"):
                    self.mapRainTimes = rainDataset["map_data"]["map_times"]
                    self.mapRainPoints = rainDataset["map_data"]["map_points"]
                    self.mapRainPointsLatitudes = rainDataset["map_data"]["map_pointsLatitudes"]
                    self.mapRainPointsLongitudes = rainDataset["map_data"]["map_pointsLongitude"]
                    self.mapRains = rainDataset["map_data"]["map_rain"]
                    for index in range(len(self.mapRainTimes)):
                        for latitudeIndex in range(len(self.mapRains[index])):
                            for longitudeIndex in range(len(self.mapRains[index][latitudeIndex])):
                                pointRain = self.mapRains[index][latitudeIndex][longitudeIndex]
                                if(pointRain > self.maxRain):
                                    self.maxRain = pointRain
                else:
                    nodeIndex = rainDataset[stationKey]["nodeIndex"]
                    if(not self.gaugeExists or (stationKey in gaugeDataset.keys())):
                        self.rainLabels.append(nodeIndex)
                        self.rainLatitudes.append(rainDataset[stationKey]["latitude"])
                        self.rainLongitudes.append(rainDataset[stationKey]["longitude"])
                    
                        if(not gaugeLabelsInitialized):
                            self.gaugeLabels.append(self.obsMetadata["USGS"][stationKey]["name"])
                            self.gaugeLatitudes.append(float(self.obsMetadata["USGS"][stationKey]["latitude"]))
                            self.gaugeLongitudes.append(float(self.obsMetadata["USGS"][stationKey]["longitude"]))
    
                        datapointRains = []
                        for index in range(len(rainDataset[stationKey]["times"])):
                            if(self.rainStartDate == None):
                                self.rainStartDate = datetime.fromtimestamp(int(rainDataset[stationKey]["times"][index]), timezone.utc)
                            if(not rainTimestampsInitialized):
                                self.rainTimes.append(self.unixTimeToDeltaHours(rainDataset[stationKey]["times"][index], self.rainStartDate))
                            datapointRains.append(rainDataset[stationKey]["rain"][index])
                        rainTimestampsInitialized = True
                        self.datapointsRains.append(datapointRains)
                        
                        if(self.gaugeExists):
                            gaugeTimes = []
                            gaugeRains = []
        #                         Height is not station altitude, it is sea surface height
                            for index in range(len(gaugeDataset[stationKey]["times"])):
                                gaugeTimes.append(self.unixTimeToDeltaHours(gaugeDataset[stationKey]["times"][index], self.rainStartDate))
                                gaugeRain = gaugeDataset[stationKey]["rain"][index]
                                gaugeRains.append(gaugeRain)
                            self.gaugeDatapointsTimes.append(gaugeTimes)
                            self.gaugeDatapointsRains.append(gaugeRains)
            gaugeLabelsInitialized = True
            
            
  
        if(self.meshExists):
            with open(dataToGraph["MESH"]) as outfile:
                meshDataset = json.load(outfile)
                
            for stationKey in meshDataset.keys():
                if(stationKey == "map_data"):
                    self.mapElevationTriangles = meshDataset["map_data"]["map_triangles"]
                    self.mapElevationMaskedTriangles = meshDataset["map_data"]["map_maskedTriangles"]
                    self.mapElevationPoints = meshDataset["map_data"]["map_points"]
                    self.mapElevationPointsLatitudes = meshDataset["map_data"]["map_pointsLatitudes"]
                    self.mapElevationPointsLongitudes = meshDataset["map_data"]["map_pointsLongitude"]
                    self.mapElevation = meshDataset["map_data"]["map_elevation"]
                    for nodeIndex in range(len(self.mapElevation)):
                        pointElevation = self.mapElevation[nodeIndex]
                        if(pointElevation > self.maxElevation):
                            self.maxElevation = pointElevation
                else:
                    nodeIndex = meshDataset[stationKey]["nodeIndex"]
                    if(not self.meshExists or (stationKey in meshDataset.keys())):
                        self.elevationLabels.append(nodeIndex)
                        self.elevationLatitudes.append(meshDataset[stationKey]["latitude"])
                        self.elevationLongitudes.append(meshDataset[stationKey]["longitude"])
                
                        if(not assetLabelsInitialized):
                            self.assetLabels.append(self.obsMetadata["ASSET"][stationKey]["name"])
                            self.assetLatitudes.append(float(self.obsMetadata["ASSET"][stationKey]["latitude"]))
                            self.assetLongitudes.append(float(self.obsMetadata["ASSET"][stationKey]["longitude"]))

                        elevation = meshDataset[stationKey]["elevation"]
                        self.datapointsElevation.append(elevation)
                    
                        if(self.assetExists):
                            assetElevation = assetDataset[stationKey]["elevation"]
                            self.assetDatapointsElevation.append(assetElevation)
            assetLabelsInitialized = True
            
        if(self.waterExists):
            with open(dataToGraph["WATER"]) as outfile:
                waterDataset = json.load(outfile)
                
            if(self.stillwaterExists):
                with open(dataToGraph["STILLWATER"]) as outfile:
                    stillwaterDataset = json.load(outfile)
                    
            if(self.tidewaterExists):
                with open(dataToGraph["TIDEWATER"]) as outfile:
                    tidewaterDataset = json.load(outfile)
                
            waterTimestampsInitialized = False
            stillwaterTimestampsInitialized = False
            tidewaterTimestampsInitialized = False
            for stationKey in waterDataset.keys():
                if(stationKey == "map_data"):
                    self.mapWaterTriangles = waterDataset["map_data"]["map_triangles"]
                    self.mapWaterMaskedTriangles = waterDataset["map_data"]["map_maskedTriangles"]
                    self.mapWaterTimes = waterDataset["map_data"]["map_times"]
                    self.mapWaterPoints = waterDataset["map_data"]["map_points"]
                    self.mapWaterPointsLatitudes = waterDataset["map_data"]["map_pointsLatitudes"]
                    self.mapWaterPointsLongitudes = waterDataset["map_data"]["map_pointsLongitude"]
                    self.mapWaters = waterDataset["map_data"]["map_water"]
                    for index in range(len(self.mapWaterTimes)):
                        for nodeIndex in range(len(self.mapWaters[index])):
                            pointWater = self.mapWaters[index][nodeIndex]
                            if(pointWater > self.maxWater):
                                self.maxWater = pointWater
                else:
                    nodeIndex = waterDataset[stationKey]["nodeIndex"]
                    if(not self.tideExists or (stationKey in tideDataset.keys())):
                        self.waterLabels.append(nodeIndex)
                        self.waterLatitudes.append(waterDataset[stationKey]["latitude"])
                        self.waterLongitudes.append(waterDataset[stationKey]["longitude"])
                    
                        if(not tideLabelsInitialized):
                            self.tideLabels.append(self.obsMetadata["NOS"][stationKey]["name"])
                            self.tideLatitudes.append(float(self.obsMetadata["NOS"][stationKey]["latitude"]))
                            self.tideLongitudes.append(float(self.obsMetadata["NOS"][stationKey]["longitude"]))

                        datapointWaters = []
                        for index in range(len(waterDataset[stationKey]["times"])):
                            if(self.waterStartDate == None):
                                self.waterStartDate = datetime.fromtimestamp(int(waterDataset[stationKey]["times"][index]), timezone.utc)
                            if(not waterTimestampsInitialized):
                                self.waterTimes.append(self.unixTimeToDeltaHours(waterDataset[stationKey]["times"][index], self.waterStartDate))
                            datapointWaters.append(waterDataset[stationKey]["water"][index])
                        waterTimestampsInitialized = True
                        if(self.CONVERT_TO_WATER_DEPTH and stationKey in meshDataset.keys()):
                            stationElevation = meshDataset[stationKey]["elevation"]
                            datapointWaters = np.array(datapointWaters) + (stationElevation * -1)
                        self.datapointsWaters.append(datapointWaters)
                        if(self.stillwaterExists):
                            datapointStillwaters = []
                            for index in range(len(stillwaterDataset[stationKey]["times"])):
                                if(not stillwaterTimestampsInitialized):
                                    self.stillwaterTimes.append(self.unixTimeToDeltaHours(stillwaterDataset[stationKey]["times"][index], self.waterStartDate))
                                datapointStillwaters.append(stillwaterDataset[stationKey]["water"][index])
                            stillwaterTimestampsInitialized = True
                            self.datapointsStillwaters.append(datapointStillwaters)
                        if(self.tidewaterExists):
                            datapointTidewaters = []
                            for index in range(len(tidewaterDataset[stationKey]["times"])):
                                if(not tidewaterTimestampsInitialized):
                                    self.tidewaterTimes.append(self.unixTimeToDeltaHours(tidewaterDataset[stationKey]["times"][index], self.waterStartDate))
                                datapointTidewaters.append(tidewaterDataset[stationKey]["water"][index])
                            tidewaterTimestampsInitialized = True
                            if(self.CONVERT_TO_WATER_DEPTH and stationKey in meshDataset.keys()):
                                stationElevation = meshDataset[stationKey]["elevation"]
                                datapointTidewaters = np.array(datapointTidewaters) + (stationElevation * -1)
                            self.datapointsTidewaters.append(datapointTidewaters)
                        if(self.tideExists):
                            tideTimes = []
                            tideWaters = []
                #                         Height is not station altitude, it is sea surface height
                            for index in range(len(tideDataset[stationKey]["times"])):
                                tideTimes.append(self.unixTimeToDeltaHours(tideDataset[stationKey]["times"][index], self.waterStartDate))
                                tideWater = tideDataset[stationKey]["water"][index]
                                tideWaters.append(tideWater)
                            self.tideDatapointsTimes.append(tideTimes)
                            self.tideDatapointsWaters.append(tideWaters)
                            tidePredictionTimes = []
                            tidePredictionWaters = []
                #                         Height is not station altitude, it is sea surface height
                            for index in range(len(tideDataset[stationKey]["prediction_times"])):
                                tidePredictionTimes.append(self.unixTimeToDeltaHours(tideDataset[stationKey]["prediction_times"][index], self.waterStartDate))
                                tidePredictionWater = tideDataset[stationKey]["prediction_water"][index]
                                tidePredictionWaters.append(tidePredictionWater)
                            self.tideDatapointsPredictionTimes.append(tidePredictionTimes)
                            self.tideDatapointsPredictionWaters.append(tidePredictionWaters)
            tideLabelsInitialized = True
                      
                      
        
        if(self.etaExists):
            with open(dataToGraph["ETA"]) as outfile:
                etaDataset = json.load(outfile)
                
            etaTimestampsInitialized = False
            for stationKey in etaDataset.keys():
                if(stationKey == "map_data"):
                    self.mapEtaTimes = etaDataset["map_data"]["map_times"]
                    self.mapEtaPoints = etaDataset["map_data"]["map_points"]
                    self.mapEtaPointsLatitudes = etaDataset["map_data"]["map_pointsLatitudes"]
                    self.mapEtaPointsLongitudes = etaDataset["map_data"]["map_pointsLongitude"]
                    self.mapEta = etaDataset["map_data"]["map_eta"]
                    for index in range(len(self.mapEtaTimes)):
                        for latitudeIndex in range(len(self.mapEta[index])):
                            for longitudeIndex in range(len(self.mapEta[index][latitudeIndex])):
                                pointEta = self.mapEta[index][latitudeIndex][longitudeIndex]
                                if(pointEta > self.maxEta):
                                    self.maxEta = pointEta
                else:
                    nodeIndex = etaDataset[stationKey]["nodeIndex"]
                    if(not self.etaExists or (stationKey in etaDataset.keys())):
                        self.etaLabels.append(nodeIndex)
                        self.etaLatitudes.append(etaDataset[stationKey]["latitude"])
                        self.etaLongitudes.append(etaDataset[stationKey]["longitude"])
                    
                        if(not tideLabelsInitialized):
                            self.tideLabels.append(self.obsMetadata["NOS"][stationKey]["name"])
                            self.tideLatitudes.append(float(self.obsMetadata["NOS"][stationKey]["latitude"]))
                            self.tideLongitudes.append(float(self.obsMetadata["NOS"][stationKey]["longitude"]))
    
                        datapointEta = []
                        for index in range(len(etaDataset[stationKey]["times"])):
                            if(self.etaStartDate == None):
                                self.etaStartDate = datetime.fromtimestamp(int(etaDataset[stationKey]["times"][index]), timezone.utc)
                            if(not etaTimestampsInitialized):
                                self.etaTimes.append(self.unixTimeToDeltaHours(etaDataset[stationKey]["times"][index], self.etaStartDate))
                            datapointEta.append(etaDataset[stationKey]["eta"][index])
                        etaTimestampsInitialized = True
                        self.datapointsEta.append(datapointEta)
                        if(self.tideExists):
                            tideTimes = []
                            tideWaters = []
                #                         Height is not station altitude, it is sea surface height
                            for index in range(len(tideDataset[stationKey]["times"])):
                                tideTimes.append(self.unixTimeToDeltaHours(tideDataset[stationKey]["times"][index], self.waterStartDate))
                                tideWater = tideDataset[stationKey]["water"][index]
                                tideWaters.append(tideWater)
                            self.tideDatapointsTimes.append(tideTimes)
                            self.tideDatapointsWaters.append(tideWaters)
                            tidePredictionTimes = []
                            tidePredictionWaters = []
                #                         Height is not station altitude, it is sea surface height
                            for index in range(len(tideDataset[stationKey]["prediction_times"])):
                                tidePredictionTimes.append(self.unixTimeToDeltaHours(tideDataset[stationKey]["prediction_times"][index], self.waterStartDate))
                                tidePredictionWater = tideDataset[stationKey]["prediction_water"][index]
                                tidePredictionWaters.append(tidePredictionWater)
                            self.tideDatapointsPredictionTimes.append(tidePredictionTimes)
                            self.tideDatapointsPredictionWaters.append(tidePredictionWaters)
            tideLabelsInitialized = True                      
  
        if(self.wavesExists):
            swhExists = False
            mwdExists = False
            mwpExists = False
            pwpExists = False
            radExists = False
            iteratorDataset = None
            if("SWH" in dataToGraph):
                swhExists = True
                with open(dataToGraph["SWH"]) as outfile:
                    swhDataset = json.load(outfile)
                    if(iteratorDataset == None):
                        iteratorDataset = swhDataset
            if("MWD" in dataToGraph):
                mwdExists = True
                with open(dataToGraph["MWD"]) as outfile:
                    mwdDataset = json.load(outfile)
                    if(iteratorDataset == None):
                        iteratorDataset = mwdDataset
            if("MWP" in dataToGraph):
                mwpExists = True
                with open(dataToGraph["MWP"]) as outfile:
                    mwpDataset = json.load(outfile)
                    if(iteratorDataset == None):
                        iteratorDataset = mwpDataset
            if("PWP" in dataToGraph):
                pwpExists = True
                with open(dataToGraph["PWP"]) as outfile:
                    pwpDataset = json.load(outfile)
                    if(iteratorDataset == None):
                        iteratorDataset = pwpDataset
            if("RAD" in dataToGraph):
                radExists = True
                with open(dataToGraph["RAD"]) as outfile:
                    radDataset = json.load(outfile)
                    if(iteratorDataset == None):
                        iteratorDataset = radDataset
            
            waveTimestampsInitialized = False
            for stationKey in iteratorDataset.keys():
                if(stationKey == "map_data"):
                    self.mapWaveTriangles = swhDataset["map_data"]["map_triangles"]
                    self.mapWaveMaskedTriangles = swhDataset["map_data"]["map_maskedTriangles"]
                    self.mapWaveTimes = swhDataset["map_data"]["map_times"]
                    self.mapWavePoints = swhDataset["map_data"]["map_points"]
                    self.mapWavePointsLatitudes = swhDataset["map_data"]["map_pointsLatitudes"]
                    self.mapWavePointsLongitudes = swhDataset["map_data"]["map_pointsLongitude"]
                    self.mapSWH = swhDataset["map_data"]["map_swh"]
                    for index in range(len(self.mapWaveTimes)):
                        for nodeIndex in range(len(self.mapSWH[index])):
                            pointSWH = self.mapSWH[index][nodeIndex]
                            if(pointSWH > self.maxSWH):
                                self.maxSWH = pointSWH
                else:
                    nodeIndex = iteratorDataset[stationKey]["nodeIndex"]
                    if(not self.buoyExists or (stationKey in buoyDataset.keys())):
                        self.waveLabels.append(nodeIndex)
                        self.waveLatitudes.append(iteratorDataset[stationKey]["latitude"])
                        self.waveLongitudes.append(iteratorDataset[stationKey]["longitude"])
                        if(not buoyLabelsInitialized):
                            self.buoyLabels.append(self.obsMetadata["NDBC"][stationKey]["name"])
                            self.buoyLatitudes.append(float(self.obsMetadata["NDBC"][stationKey]["latitude"]))
                            self.buoyLongitudes.append(float(self.obsMetadata["NDBC"][stationKey]["longitude"]))

                        datapointSWH = []
                        datapointMWD = []
                        datapointMWP = []
                        datapointPWP = []
                        datapointRADMag = []
                        datapointRADDir = []
                        for index in range(len(iteratorDataset[stationKey]["times"])):
                            if(self.waveStartDate == None):
                                self.waveStartDate = datetime.fromtimestamp(int(iteratorDataset[stationKey]["times"][index]), timezone.utc)
                            if(not waveTimestampsInitialized):
                                self.waveTimes.append(self.unixTimeToDeltaHours(iteratorDataset[stationKey]["times"][index], self.waveStartDate))
                            if(swhExists):
                                datapointSWH.append(swhDataset[stationKey]["swh"][index])
                            if(mwdExists):
                                datapointMWD.append(mwdDataset[stationKey]["mwd"][index])
                            if(mwpExists):
                                datapointMWP.append(mwpDataset[stationKey]["mwp"][index])
                            if(pwpExists):
                                datapointPWP.append(pwpDataset[stationKey]["pwp"][index])
                            if(radExists):
                                radX = radDataset[stationKey]["radstressX"][index]
                                radY = radDataset[stationKey]["radstressY"][index]
                                radMag = self.vectorSpeed(radX, radY)
                                radDir = self.vectorDirection(radX, radY)
                                datapointRADMag.append(radMag)
                                datapointRADDir.append(radDir)
                        waveTimestampsInitialized = True
                        self.datapointsSWH.append(datapointSWH)
                        self.datapointsMWD.append(datapointMWD)
                        self.datapointsMWP.append(datapointMWP)
                        self.datapointsPWP.append(datapointPWP)
                        self.datapointsRADMag.append(datapointRADMag)
                        self.datapointsRADDir.append(datapointRADDir) 
                        if(self.buoyExists):
                            buoyTimes = []
                            buoySWH = []
                            buoyMWD = []
                            buoyMWP = []
                            buoyPWP = []
                #                         Height is not station altitude, it is sea surface height
                            for index in range(len(buoyDataset[stationKey]["times"])):
                                buoyTimes.append(self.unixTimeToDeltaHours(buoyDataset[stationKey]["times"][index], self.waveStartDate))
                                buoySWH.append(buoyDataset[stationKey]["swh"][index])
                                buoyMWD.append(buoyDataset[stationKey]["mwd"][index])
                                buoyMWP.append(buoyDataset[stationKey]["mwp"][index])
                                buoyPWP.append(buoyDataset[stationKey]["pwp"][index])
                            self.buoyDatapointsTimes.append(buoyTimes)
                            self.buoyDatapointsSWH.append(buoySWH)
                            self.buoyDatapointsMWD.append(buoyMWD)
                            self.buoyDatapointsMWP.append(buoyMWP)
                            self.buoyDatapointsPWP.append(buoyPWP)
   
            buoyLabelsInitialized = True     
            
        if(self.runupExists):
            with open(dataToGraph["RUNUP"]) as outfile:
                runupDataset = json.load(outfile)
                
            runupTimestampsInitialized = False
            for stationKey in runupDataset.keys():
                nodeIndex = runupDataset[stationKey]["nodeIndex"]
                self.runupLabels.append(nodeIndex)
                self.runupLatitudes.append(runupDataset[stationKey]["latitude"])
                self.runupLongitudes.append(runupDataset[stationKey]["longitude"])
                self.runupSurfDistance.append(str(round(runupDataset[stationKey]["surfDistance"], 2)))
                self.runupOffshoreDistance.append(str(round(runupDataset[stationKey]["offshoreDistance"], 2)))
                self.runupAverageSlope.append(str(round(runupDataset[stationKey]["averageSlope"], 5)))
                datapointRunup = []
                datapointWavelength = []
                datapointIribarren = []
                datapointSteepness = []
                tangentLatitudes = []
                tangentLongitudes = []
                runupLatitudes = []
                runupLongitudes = []
                datapointAverageSlopes = []
                datapointHolmanHigh = []
                datapointHolmanMid = []
                datapointHolmanLow = []
                datapointHolmanHighSetup = []
                datapointHolmanMidSetup = []
                datapointHolmanLowSetup = []
                datapointHolmanHighSwash = []
                datapointHolmanMidSwash = []
                datapointHolmanLowSwash = []
                datapointHolmanSwashIncident = []
                datapointHolmanSwashInfragravity = []
                datapointStockdonSetup = []
                datapointStockdonSetupLow = []
                datapointStockdonSwashIncident = []
                datapointStockdonSwashInfragravity = []
                datapointStockdonSwashLow = []
                datapointStockdonRunup = []
                datapointStockdonRunupNoSetup = []
                datapointStockdonRunupLow = []
                datapointAdcircSetup = []
                datapointAdcircRunup = []
                datapointDuneHeights = []
                
                for index in range(len(runupDataset[stationKey]["times"])):
                    if(self.runupStartDate == None):
                        self.runupStartDate = datetime.fromtimestamp(int(runupDataset[stationKey]["times"][index]), timezone.utc)
                    if(not runupTimestampsInitialized):
                        self.runupTimes.append(self.unixTimeToDeltaHours(runupDataset[stationKey]["times"][index], self.runupStartDate))
                    datapointRunup.append(runupDataset[stationKey]["runup"][index])
                    datapointWavelength.append(runupDataset[stationKey]["wavelength"][index])
                    datapointIribarren.append(runupDataset[stationKey]["iribarren"][index])
                    datapointSteepness.append(runupDataset[stationKey]["steepness"][index])
                    waterlineKey = runupDataset[stationKey]["waterlineKeys"][index]
                    if("d" in stationKey):
                        generalStationKey = stationKey[0:stationKey.index("d")]
                    elif(len(stationKey) == 3):
                        generalStationKey = stationKey[0:-1]
                    else:
                        generalStationKey = stationKey
                    waterlineLatitude = float(self.obsMetadata["NORMAL"][generalStationKey][waterlineKey]["latitude"])
                    waterlineLongitude = float(self.obsMetadata["NORMAL"][generalStationKey][waterlineKey]["longitude"])
                    waterlineTangentLatitude = float(self.obsMetadata["TANGENT"][generalStationKey][waterlineKey]["latitude"])
                    waterlineTangentLongitude = float(self.obsMetadata["TANGENT"][generalStationKey][waterlineKey]["longitude"])
                    tangentLatitude = [waterlineLatitude, waterlineTangentLatitude]
                    tangentLongitude = [waterlineLongitude, waterlineTangentLongitude]
                    tangentLatitudes.append(tangentLatitude)
                    tangentLongitudes.append(tangentLongitude)
                    runupLatitudes.append([runupDataset[stationKey]["runupWaterlineLatitudes"][index], runupDataset[stationKey]["runupTangentLatitudes"][index]])
                    runupLongitudes.append([runupDataset[stationKey]["runupWaterlineLongitudes"][index], runupDataset[stationKey]["runupTangentLongitudes"][index]])
                    datapointAverageSlopes.append(runupDataset[stationKey]["averageSlopes"][index])
                    datapointHolmanHigh.append(runupDataset[stationKey]["runupHolmanHigh"][index])
                    datapointHolmanMid.append(runupDataset[stationKey]["runupHolmanMid"][index])
                    datapointHolmanLow.append(runupDataset[stationKey]["runupHolmanLow"][index])
                    datapointHolmanHighSetup.append(runupDataset[stationKey]["setupHolmanHigh"][index])
                    datapointHolmanMidSetup.append(runupDataset[stationKey]["setupHolmanMid"][index])
                    datapointHolmanLowSetup.append(runupDataset[stationKey]["setupHolmanLow"][index])
                    datapointHolmanHighSwash.append(runupDataset[stationKey]["swashHolmanHigh"][index])
                    datapointHolmanMidSwash.append(runupDataset[stationKey]["swashHolmanMid"][index])
                    datapointHolmanLowSwash.append(runupDataset[stationKey]["swashHolmanLow"][index])
                    datapointHolmanSwashIncident.append(runupDataset[stationKey]["swashHolmanIncident"][index])
                    datapointHolmanSwashInfragravity.append(runupDataset[stationKey]["swashHolmanInfragravity"][index])
                    datapointStockdonSetup.append(runupDataset[stationKey]["setupStockdon"][index])
                    datapointStockdonSetupLow.append(runupDataset[stationKey]["setupStockdonLow"][index])
                    datapointStockdonSwashIncident.append(runupDataset[stationKey]["swashStockdonIncident"][index])
                    datapointStockdonSwashInfragravity.append(runupDataset[stationKey]["swashStockdonInfragravity"][index])
                    datapointStockdonSwashLow.append(runupDataset[stationKey]["swashStockdonLow"][index])
                    datapointStockdonRunup.append(runupDataset[stationKey]["runupStockdon"][index])
                    datapointStockdonRunupNoSetup.append(runupDataset[stationKey]["runupStockdonNoSetup"][index])
                    datapointStockdonRunupLow.append(runupDataset[stationKey]["runupStockdonLow"][index])
                    datapointAdcircSetup.append(runupDataset[stationKey]["setupAdcirc"][index])
                    datapointAdcircRunup.append(runupDataset[stationKey]["runupAdcirc"][index])
                    datapointDuneHeights.append(runupDataset[stationKey]["duneHeights"][index])
                    
                runupTimestampsInitialized = True
                self.datapointsRunup.append(datapointRunup)    
                self.datapointsWavelength.append(datapointWavelength)
                self.datapointsIribarren.append(datapointIribarren)
                self.datapointsSteepness.append(datapointSteepness)   
                self.datapointsWaterlineLatitudes.append(tangentLatitudes)
                self.datapointsWaterlineLongitudes.append(tangentLongitudes)   
                self.datapointsRunupLatitudes.append(runupLatitudes)
                self.datapointsRunupLongitudes.append(runupLongitudes)
                self.runupAverageSlopes.append(datapointAverageSlopes)
                self.datapointsRunupHolmanHigh.append(datapointHolmanHigh)
                self.datapointsRunupHolmanMid.append(datapointHolmanMid)
                self.datapointsRunupHolmanLow.append(datapointHolmanLow)
                self.datapointsSetupHolmanHigh.append(datapointHolmanHighSetup)
                self.datapointsSetupHolmanMid.append(datapointHolmanMidSetup)
                self.datapointsSetupHolmanLow.append(datapointHolmanLowSetup)
                self.datapointsSwashHolmanHigh.append(datapointHolmanHighSwash)
                self.datapointsSwashHolmanMid.append(datapointHolmanMidSwash)
                self.datapointsSwashHolmanLow.append(datapointHolmanLowSwash)
                self.datapointsSwashHolmanIncident.append(datapointHolmanSwashIncident)
                self.datapointsSwashHolmanInfragravity.append(datapointHolmanSwashInfragravity)
                self.datapointsSetupStockdon.append(datapointStockdonSetup)
                self.datapointsSetupStockdonLow.append(datapointStockdonSetupLow)
                self.datapointsSwashStockdonIncident.append(datapointStockdonSwashIncident)
                self.datapointsSwashStockdonInfragravity.append(datapointStockdonSwashInfragravity)
                self.datapointsSwashStockdonLow.append(datapointStockdonSwashLow)
                self.datapointsRunupStockdon.append(datapointStockdonRunup)
                self.datapointsRunupStockdonNoSetup.append(datapointStockdonRunupNoSetup)
                self.datapointsRunupStockdonLow.append(datapointStockdonRunupLow)
                self.datapointsSetupAdcirc.append(datapointAdcircSetup)
                self.datapointsRunupAdcirc.append(datapointAdcircRunup)
                self.datapointsDuneHeights.append(datapointDuneHeights)
                

    def generateGraphs(self):
        graph_directory = "graphs/"
        
        numberOfWindDatapoints = 0
        numberOfRainDatapoints = 0
        numberOfWaterDatapoints = 0
        numberOfEtaDatapoints = 0
        numberOfWaveDatapoints = 0
        numberOfElevationDatapoints = 0
        numberOfRunupDatapoints = 0
#         TODO: Currently, when graphing multiple products with obs on, OBS_STATIONS must contain the same number of station 
#           entries for each type of product
        if(self.windExists):
            numberOfWindDatapoints = len(self.windLabels)
        if(self.wavesExists):
            numberOfWaveDatapoints = len(self.waveLabels)
        if(self.rainExists):
            numberOfRainDatapoints = len(self.rainLabels)
        if(self.waterExists):
            numberOfWaterDatapoints = len(self.waterLabels)
        if(self.meshExists):
            numberOfElevationDatapoints = len(self.elevationLabels)
        if(self.etaExists):
            numberOfEtaDatapoints = len(self.etaLabels)
        if(self.buoyExists):
            numberOfWaveDatapoints = len(self.buoyDatapointsTimes)
        if(self.tideExists):
            numberOfWaterDatapoints = len(self.tideDatapointsTimes)
        if(self.gaugeExists):
            numberOfRainDatapoints = len(self.gaugeDatapointsTimes)
        if(self.assetExists):
            numberOfElevationDatapoints = len(self.assetDatapointsElevation)
        if(self.obsExists):
            numberOfWindDatapoints = len(self.obsDatapointsTimes)
        if(self.runupExists):
            numberOfRunupDatapoints = len(self.runupLabels)
        print("numberOfDatapoints Wind, Rain, Water, Wave, Eta, Elevation, Runup", numberOfWindDatapoints, numberOfRainDatapoints, numberOfWaterDatapoints, numberOfWaveDatapoints, numberOfEtaDatapoints, numberOfElevationDatapoints, numberOfRunupDatapoints, flush=True)
        fig, ax = plt.subplots()
        print("maxWind", self.maxWind, "maxRain", self.maxRain, "maxWave", self.maxSWH, "maxWater", self.maxWater, "maxEta", self.maxEta, "maxElevation", self.maxElevation, "maxRunup", self.maxRunup, flush=True)
        
        if(self.windExists):
            ax.scatter(self.obsLongitudes, self.obsLatitudes, label="Obs")
            ax.scatter(self.windLongitudes, self.windLatitudes, label="Wind")
        if(self.wavesExists):
            ax.scatter(self.tideLongitudes, self.tideLatitudes, label="Tide")
            ax.scatter(self.waveLongitudes, self.waveLatitudes, label="Waves")
        if(self.rainExists):
            ax.scatter(self.rainLongitudes, self.rainLatitudes, label="Rain")
            ax.scatter(self.gaugeLongitudes, self.gaugeLatitudes, label="Gauge")
        if(self.waterExists):
            ax.scatter(self.buoyLongitudes, self.buoyLatitudes, label="Buoy")
            ax.scatter(self.waterLongitudes, self.waterLatitudes, label="Water")
        if(self.meshExists):
            ax.scatter(self.assetLongitudes, self.assetLatitudes, label="Asset")
            ax.scatter(self.elevationLongitudes, self.elevationLatitudes, label="Mesh")
        if(self.etaExists):
            ax.scatter(self.etaLongitudes, self.etaLatitudes, label="Eta")
        if(self.runupExists):
            ax.scatter(self.runupLongitudes, self.runupLatitudes)
        ax.legend(loc="lower right")

        for index, label in enumerate(self.obsLabels):
            ax.annotate(label, (self.obsLongitudes[index], self.obsLatitudes[index]))
            if(self.windExists):
                ax.annotate(self.windLabels[index], (self.windLongitudes[index], self.windLatitudes[index]))
        for index, label in enumerate(self.buoyLabels):
            ax.annotate(label, (self.buoyLongitudes[index], self.buoyLatitudes[index]))
            if(self.wavesExists):
                ax.annotate(self.waveLabels[index], (self.waveLongitudes[index], self.waveLatitudes[index]))
        for index, label in enumerate(self.gaugeLabels):
            ax.annotate(label, (self.gaugeLongitudes[index], self.gaugeLatitudes[index]))
            if(self.rainExists):
                ax.annotate(self.rainLabels[index], (self.rainLongitudes[index], self.rainLatitudes[index]))
        for index, label in enumerate(self.tideLabels):
            ax.annotate(label, (self.tideLongitudes[index], self.tideLatitudes[index]))
            if(self.waterExists):
                ax.annotate(self.waterLabels[index], (self.waterLongitudes[index], self.waterLatitudes[index]))
            if(self.etaExists):
                ax.annotate(self.etaLabels[index], (self.etaLongitudes[index], self.etaLatitudes[index]))
        for index, label in enumerate(self.assetLabels):
            ax.annotate(label, (self.assetLongitudes[index], self.assetLatitudes[index]))
            if(self.meshExists):
                ax.annotate(self.elevationLabels[index], (self.elevationLongitudes[index], self.elevationLatitudes[index]))
            if(self.etaExists):
                ax.annotate(self.etaLabels[index], (self.etaLongitudes[index], self.etaLatitudes[index]))
        for index, label in enumerate(self.runupLabels):
            ax.annotate(label, (self.runupLongitudes[index], self.runupLatitudes[index]))
            
        plt.title("location of datapoints by data type")
        plt.xlabel("longitude")
        plt.ylabel("latitude")
        plt.savefig(graph_directory + 'closest_points.png')
        plt.close()
        
        img = mpimg.imread(self.backgroundMap)
        plotAxis = [self.backgroundAxis[0], self.backgroundAxis[1], self.backgroundAxis[3], self.backgroundAxis[2]]
        aspectRatio = (self.backgroundAxis[1] - self.backgroundAxis[0]) / (self.backgroundAxis[2] - self.backgroundAxis[3])
#         img = mpimg.imread('subsetFlipped.png')
#         img = mpimg.imread('NorthAtlanticBasin3.png')
        if(len(self.mapWindTimes) > 0):
            vmin = 0
#             vmax = math.ceil(self.maxWind)
            vmax = 20
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            if(self.windType == "FORT"):
                windTriangulation = Triangulation(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, triangles=self.mapWindTriangles, mask=self.mapWindMaskedTriangles)
            for index in range(len(self.mapWindTimes)):
                fig, ax = plt.subplots()
#                 plt.figure(figsize=(6, 6))
    #             print(self.endWindPointsLongitudes)
    #             print(self.endWindPointsLatitudes)
    #             print(self.endSpeeds)
                plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
#                 plt.imshow(img, alpha=0.5, extent=[-76.59179620444773, -63.41595750651321, 46.70943547053439, 36.92061410517965], zorder=2)
                if(self.windType == "FORT"):
#                     plt.scatter(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, c=self.mapSpeeds[index], alpha=0.5, label="Forecast", marker=".")
                    contourset = ax.tricontourf(windTriangulation, self.mapSpeeds[index], levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax, zorder=1)
                elif(self.windType == "POST"):
#                     plt.scatter(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, c=self.mapSpeeds[index], alpha=0.3, label="Forecast", marker=".", s=100)
#                     contourset = ax.tricontourf(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, self.mapSpeeds[index], levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax)
                    contourset = ax.pcolormesh(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, self.mapSpeeds[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
                elif(self.windType == "GFS"):
#                     plt.scatter(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, c=self.mapSpeeds[index], alpha=0.3, label="Forecast", marker=".", s=3600)
#                     contourset = ax.tricontourf(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, self.mapSpeeds[index], levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax)
#                     print(len(self.mapWindPointsLongitudes), len(self.mapWindPointsLatitudes), len(self.mapSpeeds[index]))
                    contourset = ax.pcolormesh(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, self.mapSpeeds[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
                plt.axis(plotAxis)
#                 plt.axis([-76.59179620444773, -63.41595750651321, 36.92061410517965, 46.70943547053439])
                plt.title("Wind Speed")
                plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#                 plt.xlabel(datetime.fromtimestamp(timestamp, timezone.utc))
    #             graphs up to 10 m/s, ~20 knots
                plt.colorbar(
                    ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                    ticks=range(vmin, vmax+5, 5),
                    boundaries=levelBoundaries,
                    values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                    label="Meters/Second",
                    ax=plt.gca()
                )
                plt.savefig(graph_directory + 'map_wind_' + str(index) + '.png')
                plt.close()
                gc.collect()
            with imageio.get_writer(graph_directory + 'wind.gif', mode='I') as writer:
                for index in range(len(self.mapWindTimes)):
                    filename = "map_wind_" + str(index) + ".png"
                    image = imageio.imread(graph_directory + filename)
                    writer.append_data(image)
                for index in range(len(self.mapWindTimes)):
                    filename = "map_wind_" + str(index) + ".png"
                    os.remove(graph_directory + filename)
            mapSpeedsNoNan = np.nan_to_num(self.mapSpeeds)
            swathWind = np.max(mapSpeedsNoNan, axis=0)
            fig, ax = plt.subplots(figsize=(9,9))
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            if(self.windType == "FORT"):
                contourset = ax.tricontourf(windTriangulation, self.mapSpeeds[index], levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax, zorder=1)
            else:
                contourset = ax.pcolormesh(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, swathWind, shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
            plt.axis(plotAxis)
            plt.title("Wind Swath")
#             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#             graphs up to 10 m/s, ~20 knots
            plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                ticks=range(vmin, vmax+5, 5),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                label="Meters/Second",
                ax=plt.gca()
            )
            plt.savefig(graph_directory + 'map_wind_swath.png')
            plt.close()
            gc.collect()
        if(len(self.mapRainTimes) > 0):
            vmin = 0
            vmax = math.ceil(self.maxRain)
            vmax = 25
            vmax = 5
            vmaxAccumulation = 500
#             vmaxAccumulation = 10
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            levelBoundariesAccumulation = np.linspace(vmin, vmaxAccumulation, levels + 1)
            for index in range(len(self.mapRainTimes)):
                fig, ax = plt.subplots()
    #             print(self.endWavePointsLongitudes)
    #             print(self.endWavePointsLatitudes)
    #             print(self.endSWH)
                plt.imshow(img, extent=self.backgroundAxis, alpha=0.6, aspect=aspectRatio, zorder=2)
#                 contourset = ax.tricontourf(self.mapRainPointsLongitudes, self.mapRainPointsLatitudes, self.mapRains[index], levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax)
                contourset = ax.pcolormesh(self.mapRainPointsLongitudes, self.mapRainPointsLatitudes, self.mapRains[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
                plt.axis(plotAxis)
                plt.title("Rain")
                plt.xlabel(datetime.fromtimestamp(int(self.mapRainTimes[index]), timezone.utc))
    #             plt.gca().invert_yaxis()
                plt.colorbar(
                    ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                    ticks=range(vmin, vmax+5, 5),
                    boundaries=levelBoundaries,
                    values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                    label="Millimeters/Hour",
                    ax=plt.gca()
                )
                plt.savefig(graph_directory + 'map_rain_' + str(index) + '.png')
                plt.close()
                gc.collect()
            with imageio.get_writer(graph_directory + 'rain.gif', mode='I') as writer:
                for index in range(len(self.mapRainTimes)):
                    filename = "map_rain_" + str(index) + ".png"
                    image = imageio.imread(graph_directory + filename)
                    writer.append_data(image)
                for index in range(len(self.mapRainTimes)):
                    filename = "map_rain_" + str(index) + ".png"
                    os.remove(graph_directory + filename)
            mapRainsNoNan = np.nan_to_num(self.mapRains)
            accumulatedRain = np.sum(mapRainsNoNan, axis=0)
            fig, ax = plt.subplots()
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.pcolormesh(self.mapRainPointsLongitudes, self.mapRainPointsLatitudes, accumulatedRain, shading='gouraud', cmap="jet", vmin=vmin, vmax=vmaxAccumulation, zorder=1)
            plt.axis(plotAxis)
            plt.title("Rain Accumulation")
#             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#             graphs up to 10 m/s, ~20 knots
            plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
#                 Increase vmax by factor of length of time to fit accumulation
                ticks=range(vmin, vmaxAccumulation+5, 50),
                boundaries=levelBoundariesAccumulation,
                values=(levelBoundariesAccumulation[:-1] + levelBoundariesAccumulation[1:]) / 2,
                label="Millimeters",
                ax=plt.gca()
            )
            plt.savefig(graph_directory + 'map_rain_accumulation.png')
            plt.close()
            gc.collect()
        if(len(self.mapElevation) > 0):
            vmin = -40
            vmax = 10
#             vmax = math.ceil(self.maxElevation)
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            # waveTriangulation = Triangulation(self.mapWavePointsLongitudes, self.mapWavePointsLatitudes, triangles=self.mapWaveTriangles, mask=self.mapWaveMaskedTriangles)
#             print("triangle len", self.mapElevationTriangles)
            elevationTriangulation = Triangulation(self.mapElevationPointsLongitudes, self.mapElevationPointsLatitudes, triangles=self.mapElevationTriangles, mask=self.mapElevationMaskedTriangles)
            fig, ax = plt.subplots(figsize=(9,9))
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.tripcolor(elevationTriangulation, self.mapElevation, shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
            ax.scatter(self.mapElevationPointsLongitudes, self.mapElevationPointsLatitudes, alpha=0.5, marker=".", s=5, zorder=4, color="purple")
#             if(self.assetExists):
            legendLabelInitialized = False
            transectLabelInitialized = False
            for assetIndex, assetLabel in enumerate(self.assetLabels):
                if("m" == assetLabel[-1]):
                    if("Waves" in assetLabel):
                        ax.scatter(self.assetLongitudes[assetIndex], self.assetLatitudes[assetIndex], zorder=3, alpha=0.7, marker=".", s=20, color="black", label="7m depth" if not legendLabelInitialized else None)
                        legendLabelInitialized = True
                        ax.annotate(assetLabel[:assetLabel.index(" ")], (self.assetLongitudes[assetIndex], self.assetLatitudes[assetIndex]))
                    else:
                        ax.scatter(self.assetLongitudes[assetIndex], self.assetLatitudes[assetIndex], zorder=3, alpha=0.7, marker="x", s=10, color="black", label="Transects" if not transectLabelInitialized else None)
                        transectLabelInitialized = True
#             ax.scatter(self.assetLongitudes, self.assetLatitudes, label="Obs Locations", zorder=3, alpha=0.7, marker=".", s=20, color="black")

#             Below line graphs mesh points
#             ax.scatter(self.mapElevationPointsLongitudes, self.mapElevationPointsLatitudes, label="Nodes", zorder=3, alpha=0.7, marker=".", s=1, color="black")
#           Below line graphs ASSET points without the need for observational asset data to have been generated
#             ax.scatter(self.elevationLongitudes, self.elevationLatitudes, label="Closest Node", zorder=3, alpha=0.7, marker=".", s=20, color="black")
#             for index in range(len(self.datapointsElevation)):
#                 ax.annotate(str(round(self.datapointsElevation[index], 2)), (self.elevationLongitudes[index], self.elevationLatitudes[index]))
            plt.axis(plotAxis)
            plt.title("Elevation Map")
#             plt.title("Map Elevation - " + "surf distance: " + self.runupSurfDistance[index] + " offshore distance: " + self.runupOffshoreDistance[index] + " slope: " + self.runupAverageSlope[index])
            ax.legend(loc="upper left")
#             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#             graphs up to 10 m/s, ~20 knots
            plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                ticks=range(vmin, vmax+5, 10),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                label="Meters",
                ax=plt.gca()
            )        
            plt.savefig(graph_directory + 'map_elevation.png')
            plt.close()
            gc.collect()
        if(len(self.mapEtaTimes) > 0):
            vmin = -1
            vmax = math.ceil(self.maxEta)
#             vmax = 20
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            for index in range(len(self.mapEtaTimes)):
                fig, ax = plt.subplots()
    #             print(self.endWavePointsLongitudes)
    #             print(self.endWavePointsLatitudes)
    #             print(self.endSWH)
                plt.imshow(img, extent=self.backgroundAxis, alpha=0.6, aspect=aspectRatio, zorder=2)
                contourset = ax.pcolormesh(self.mapEtaPointsLongitudes, self.mapEtaPointsLatitudes, self.mapEta[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
#               Todo: Fix triangulation errors
#                 contourset = ax.tripcolor(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, self.mapWaters[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
                plt.axis(plotAxis)
                plt.title("Eta Elevation")
                plt.xlabel(datetime.fromtimestamp(int(self.mapEtaTimes[index]),timezone.utc))
    #             plt.gca().invert_yaxis()
                plt.colorbar(
                    ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                    ticks=range(vmin, vmax+5, 2),
                    boundaries=levelBoundaries,
                    values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                    label="Meters",
                    ax=plt.gca()
                )
                plt.savefig(graph_directory + 'map_eta_' + str(index) + '.png')
                plt.close()
                gc.collect()
            with imageio.get_writer(graph_directory + 'eta.gif', mode='I') as writer:
                for index in range(len(self.mapEtaTimes)):
                    filename = "map_eta_" + str(index) + ".png"
                    image = imageio.imread(graph_directory + filename)
                    writer.append_data(image)
                for index in range(len(self.mapEtaTimes)):
                    filename = "map_eta_" + str(index) + ".png"
                    os.remove(graph_directory + filename)
            mapEtaNoNan = np.nan_to_num(self.mapEta)
            swathEta = np.max(self.mapEta, axis=0)
            fig, ax = plt.subplots()
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.pcolormesh(self.mapEtaPointsLongitudes, self.mapEtaPointsLatitudes, swathEta, shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
            plt.axis(plotAxis)
            plt.title("Eta Swath")
#             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#             graphs up to 10 m/s, ~20 knots
            plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                ticks=range(vmin, vmax+5, 2),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                label="Meters",
                ax=plt.gca()
            )
            plt.savefig(graph_directory + 'map_eta_swath.png')
            plt.close()
            gc.collect()
        if(len(self.mapWaterTimes) > 0):
            vmin = -1
            vminSwath = 0
#             vmax = math.ceil(self.maxWater)
            vmax = 2
#             vmax = 20
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            levelBoundariesSwath = np.linspace(vminSwath, vmax, levels + 1)
#             waterTriangulation = Triangulation(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, triangles=self.mapWaterTriangles, mask=self.mapWaterMaskedTriangles)
            for index in range(len(self.mapWaterTimes)):
                fig, ax = plt.subplots(figsize=(9,9))
    #             print(self.endWavePointsLongitudes)
    #             print(self.endWavePointsLatitudes)
    #             print(self.endSWH)
                plt.imshow(img, extent=self.backgroundAxis, alpha=0.6, aspect=aspectRatio, zorder=2)
                currentMaskedTriangles = self.mapWaterMaskedTriangles.copy()
                for triangleIndex, triangle in enumerate(self.mapWaterTriangles):
                    for pointIndex in triangle:
                        water = self.mapWaters[index][pointIndex]
    #                     Check for nan value
    #                     point = (self.mapWaterPointsLongitudes[pointIndex], self.mapWaterPointsLatitudes[pointIndex])
                        if(water == -99999.0):
    #                     if(point[0] < -72.1 and point[0] > -72.15 and point[1] > 41.4 and point[1] < 41.42):
    #                         print("point, water", point, water)
                            currentMaskedTriangles[triangleIndex] = True
                            break
                waterTriangulation = Triangulation(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, triangles=self.mapWaterTriangles, mask=currentMaskedTriangles)

                contourset = ax.tripcolor(waterTriangulation, self.mapWaters[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
                
#                 Plot points
                if(self.meshExists):
                    ax.scatter(self.assetLongitudes, self.assetLatitudes, label="Assets", zorder=3, alpha=0.7, marker=".", s=40, color="black")
                    
                if(self.obsExists):
                    ax.scatter(self.tideLongitudes, self.tideLatitudes, label="Obs", zorder=3, alpha=0.7, marker=".", s=40, color="black")
                    for tideIndex in range(len(self.tideLabels)):
                        ax.annotate(self.tideLabels[tideIndex], (self.tideLongitudes[tideIndex], self.tideLatitudes[tideIndex]))
                    
                if(self.runupExists):
                    for runupIndex, runupLabel in enumerate(self.runupLabels):
                        self.plotExtendedLines(ax, runupIndex, index, runupLabel)
#                         print("datapointsWaterlineLongitudes", type(self.datapointsWaterlineLongitudes[runupIndex][index]))
#                         ax.plot(self.datapointsWaterlineLongitudes[runupIndex][index], self.datapointsWaterlineLatitudes[runupIndex][index], label=runupLabel, zorder=3, alpha=0.7, marker=".", color="green")
#                         ax.plot(self.datapointsRunupLongitudes[runupIndex][index], self.datapointsRunupLatitudes[runupIndex][index], label=runupLabel, zorder=3, alpha=0.7, marker=".", color="red")
#               Todo: Fix triangulation errors
#                 contourset = ax.tripcolor(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, self.mapWaters[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
                plt.axis(plotAxis)
                plt.title(self.titlePrefix + "Water Elevation")
                plt.xlabel(datetime.fromtimestamp(self.mapWaterTimes[index], timezone.utc))
    #             plt.gca().invert_yaxis()
                plt.colorbar(
                    ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                    ticks=range(vmin, vmax+5, 2),
                    boundaries=levelBoundaries,
                    values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                    label="Meters",
                    ax=plt.gca()
                )
                plt.savefig(graph_directory + 'map_water_' + str(index) + '.png')
                plt.close()
                gc.collect()
            with imageio.get_writer(graph_directory + 'water.gif', mode='I') as writer:
                for index in range(len(self.mapWaterTimes)):
                    filename = "map_water_" + str(index) + ".png"
                    image = imageio.imread(graph_directory + filename)
                    writer.append_data(image)
                for index in range(len(self.mapWaterTimes)):
                    filename = "map_water_" + str(index) + ".png"
                    os.remove(graph_directory + filename)
            
            swathWaters = np.max(self.mapWaters, axis=0)
            print(len(swathWaters), len(self.mapWaterMaskedTriangles))
            for index, triangle in enumerate(self.mapWaterTriangles):
                for pointIndex in triangle:
                    water = swathWaters[pointIndex]
#                     Check for nan value
#                     point = (self.mapWaterPointsLongitudes[pointIndex], self.mapWaterPointsLatitudes[pointIndex])
                    if(water == -99999.0):
#                     if(point[0] < -72.1 and point[0] > -72.15 and point[1] > 41.4 and point[1] < 41.42):
#                         print("point, water", point, water)
                        self.mapWaterMaskedTriangles[index] = True
                        break
            waterTriangulation = Triangulation(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, triangles=self.mapWaterTriangles, mask=self.mapWaterMaskedTriangles)
#             print(self.mapWaterTriangles[0])
#             mapWatersNoNan = np.nan_to_num(self.mapWaters)
#             swathWaters = np.max(self.mapWaters, axis=0)
            fig, ax = plt.subplots(figsize=(9,9))
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.tripcolor(waterTriangulation, swathWaters, shading='gouraud', cmap="jet", vmin=vminSwath, vmax=vmax, zorder=1)
#             ax.scatter(self.waterLongitudes, self.waterLatitudes, label="Datapoints")
#             if(self.buoyExists):
#                     ax.scatter(self.buoyLongitudes, self.buoyLatitudes, label="Buoy", zorder=3)
#             if(self.meshExists):
#                 ax.scatter(self.assetLongitudes, self.assetLatitudes, label="Assets", zorder=4, alpha=0.7, marker=".", s=40, color="black")
            for waterIndex, tideLabel in enumerate(self.tideLabels):
                if("Waves" in tideLabel):
                    ax.scatter(self.waterLongitudes[waterIndex], self.waterLatitudes[waterIndex])
                    ax.annotate(tideLabel, (self.waterLongitudes[waterIndex], self.waterLatitudes[waterIndex]))
                    
            plt.axis(plotAxis)
            plt.title(self.titlePrefix + "Water Swath")
#             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#             graphs up to 10 m/s, ~20 knots
            plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                ticks=range(vminSwath, vmax+5, 1),
                boundaries=levelBoundariesSwath,
                values=(levelBoundariesSwath[:-1] + levelBoundariesSwath[1:]) / 2,
                label="Meters",
                ax=plt.gca()
            )
            plt.savefig(graph_directory + 'map_water_swath.png')
            plt.close()
            gc.collect()
        if(len(self.mapWaveTimes) > 0):
            vmin = 0
            vmax = math.ceil(self.maxSWH)
            vmax = 5
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            # waveTriangulation = Triangulation(self.mapWavePointsLongitudes, self.mapWavePointsLatitudes, triangles=self.mapWaveTriangles, mask=self.mapWaveMaskedTriangles)
            for index in range(len(self.mapWaveTimes)):
                fig, ax = plt.subplots()
    #             print(self.endWavePointsLongitudes)
    #             print(self.endWavePointsLatitudes)
    #             print(self.endSWH)
    
                currentMaskedTriangles = self.mapWaveMaskedTriangles.copy()
                for triangleIndex, triangle in enumerate(self.mapWaveTriangles):
                    for pointIndex in triangle:
                        swh = self.mapSWH[index][pointIndex]
    #                     Check for nan value
    #                     point = (self.mapWaterPointsLongitudes[pointIndex], self.mapWaterPointsLatitudes[pointIndex])
                        if(swh == -99999.0):
    #                     if(point[0] < -72.1 and point[0] > -72.15 and point[1] > 41.4 and point[1] < 41.42):
    #                         print("point, water", point, water)
                            currentMaskedTriangles[triangleIndex] = True
                            break
                waveTriangulation = Triangulation(self.mapWavePointsLongitudes, self.mapWavePointsLatitudes, triangles=self.mapWaveTriangles, mask=currentMaskedTriangles)

                plt.imshow(img, extent=self.backgroundAxis, aspect=aspectRatio)
                contourset = ax.tricontourf(waveTriangulation, self.mapSWH[index], levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax)
                plt.axis(plotAxis)
                plt.title("Significant Wave Height")
                plt.xlabel(datetime.fromtimestamp(int(self.mapWaveTimes[index]),timezone.utc))
    #             plt.gca().invert_yaxis()
                plt.colorbar(
                    ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                    ticks=range(vmin, vmax+5, 5),
                    boundaries=levelBoundaries,
                    values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                    label="Meters",
                    ax=plt.gca()
                )                
                plt.savefig(graph_directory + 'map_swh_' + str(index) + '.png')
                plt.close()
                gc.collect()
            with imageio.get_writer(graph_directory + 'wave.gif', mode='I') as writer:
                for index in range(len(self.mapWaveTimes)):
                    filename = "map_swh_" + str(index) + ".png"
                    image = imageio.imread(graph_directory + filename)
                    writer.append_data(image)
                for index in range(len(self.mapWaveTimes)):
                    filename = "map_swh_" + str(index) + ".png"
                    os.remove(graph_directory + filename)
            swathSWH = np.max(self.mapSWH, axis=0)
            for index, triangle in enumerate(self.mapWaveTriangles):
                for pointIndex in triangle:
                    swh = swathSWH[pointIndex]
#                     Check for nan value
#                     point = (self.mapWaterPointsLongitudes[pointIndex], self.mapWaterPointsLatitudes[pointIndex])
                    if(swh == -99999.0):
#                     if(point[0] < -72.1 and point[0] > -72.15 and point[1] > 41.4 and point[1] < 41.42):
#                         print("point, water", point, water)
                        self.mapWaveMaskedTriangles[index] = True
                        break
            waveTriangulation = Triangulation(self.mapWavePointsLongitudes, self.mapWavePointsLatitudes, triangles=self.mapWaveTriangles, mask=self.mapWaveMaskedTriangles)
            fig, ax = plt.subplots(figsize=(9,9))
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.tricontourf(waveTriangulation, swathSWH, levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax, zorder=1)
            ax.scatter(self.waveLongitudes, self.waveLatitudes, label="Datapoints")
            if(self.tideExists):
                    ax.scatter(self.tideLongitudes, self.tideLatitudes, label="Tide", zorder=3)
            plt.axis(plotAxis)
            plt.title("Significant Wave Height Swath")
#             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#             graphs up to 10 m/s, ~20 knots
            plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                ticks=range(vmin, vmax+5, 1),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                label="Meters",
                ax=plt.gca()
            )        
            plt.savefig(graph_directory + 'map_swh_swath.png')
            plt.close()
            gc.collect()
        # Plot wind speed over time
        for index in range(numberOfWindDatapoints):
            if(len(self.datapointsSpeeds) > 0):
                fig, ax = plt.subplots(figsize=(16,9))
                ax.scatter(self.windTimes, self.datapointsSpeeds[index], marker=".", label="Forecast")
                if(self.obsExists):
                    ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsSpeeds[index], marker=".", label="Obs")
                ax.legend(loc="lower right")
#                 ax.set_ylim([0, 50])
                stationName = self.obsLabels[index]
                plt.title(stationName + " station wind speed", fontsize=24)
#                 plt.xlabel("Hours since " + self.windStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("wind speed (m/s)")
                plt.savefig(graph_directory + stationName + '_wind_speed.png')
                plt.close()
            if(len(self.datapointsDirections) > 0):
                fig, ax = plt.subplots(figsize=(16,9))
                ax.scatter(self.windTimes, self.datapointsDirections[index], marker=".", label="Forecast")
                if(self.obsExists):
                    ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsDirections[index], marker=".", label="Obs")
                ax.legend(loc="lower right")
#                 ax.set_ylim([0, 50])
                stationName = self.obsLabels[index]
                plt.title(stationName + " station wind directions", fontsize=24)
                plt.ylabel("wind direction (degrees)")
                plt.savefig(graph_directory + stationName + '_wind_direction.png')
                plt.close()
        for index in range(numberOfRainDatapoints):
            if(len(self.datapointsRains) > 0):
                fig, ax = plt.subplots()
                ax.scatter(self.rainTimes, self.datapointsRains[index], marker=".", label="Forecast")
                if(self.gaugeExists):
                    ax.plot(self.gaugeDatapointsTimes[index], self.gaugeDatapointsRains[index], label="Gauge")
                    gaugeNoNan = np.nan_to_num(self.gaugeDatapointsRains[index])
                    accumulationGauge = str(round(np.sum(gaugeNoNan), 2))
                    accumulationSeriesGauge = []
                    for rainIndex, gaugeRain in enumerate(gaugeNoNan):
                        if(rainIndex == 0):
                            accumulationSeriesGauge.append(gaugeRain)
                        else:
                            accumulationSeriesGauge.append(gaugeRain + accumulationSeriesGauge[rainIndex - 1])

                else:
                    accumulationGauge = "NA"
                    accumulationSeriesGauge = []
                ax.legend(loc="lower right")
                stationName = self.gaugeLabels[index]
                

                rainNoNan = np.nan_to_num(self.datapointsRains[index])
                accumulationRain = str(round(np.sum(rainNoNan), 2))
                accumulationSeriesRain = []
                for rainIndex, rain in enumerate(rainNoNan):
                    if(rainIndex == 0):
                        accumulationSeriesRain.append(rain)
                    else:
                        accumulationSeriesRain.append(rain + accumulationSeriesRain[rainIndex - 1])
                plt.title(stationName + " rain-accumulation forecast/gauge:" + accumulationRain + "/" + accumulationGauge)
                plt.xlabel("Hours since " + self.rainStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("rain (mm/hr)")
                plt.savefig(graph_directory + stationName + '_rain.png')
                plt.close()
#                Plot accumulation series
                fig, ax = plt.subplots()
                ax.scatter(self.rainTimes, accumulationSeriesRain, marker=".", label="Forecast")
                if(self.gaugeExists):
                    ax.plot(self.gaugeDatapointsTimes[index], accumulationSeriesGauge, label="Gauge")
                ax.legend(loc="lower right")
                plt.title(stationName + " accumulated rain- forecast/gauge:" + accumulationRain + "/" + accumulationGauge)
                plt.xlabel("Hours since " + self.rainStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("rain (mm)")
                plt.savefig(graph_directory + stationName + '_rain_accumulation.png')
                plt.close()
        for index in range(numberOfWaterDatapoints):
            if(len(self.datapointsWaters) > 0):
                fig, ax = plt.subplots(figsize=(16,9))
                if(self.stillwaterExists):
                    ax.plot(self.stillwaterTimes, self.datapointsStillwaters[index], label=r"$\eta_{still}$", linestyle="--")
                if(self.tidewaterExists):
                    ax.plot(self.tidewaterTimes, self.datapointsTidewaters[index], label=r"$\eta_{tide}$", linestyle="--")
                ax.plot(self.waterTimes, self.datapointsWaters[index], label=r"$\eta$")
                if(self.tideExists):
                    ax.plot(self.tideDatapointsTimes[index], self.tideDatapointsWaters[index], label="Obs")
#                     ax.plot(self.tideDatapointsPredictionTimes[index], self.tideDatapointsPredictionWaters[index], label="Tides")
                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                stationName = self.tideLabels[index]
                maxElevation = str(round(max(self.datapointsWaters[index]), 2))
                plt.title(self.titlePrefix + stationName + " station water elevation", fontsize=24)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("elevation (meters)")
                plt.savefig(graph_directory + stationName + '_water.png')
                plt.close()
                

                if(self.tideExists):
                    fig, ax = plt.subplots(figsize=(16,9))
                    ax.plot(self.tideDatapointsTimes[index], self.tideDatapointsWaters[index], label="Station")
                    ax.legend(loc="upper left")
                    ax.format_xdata = mdates.DateFormatter('%d')
                    stationName = self.tideLabels[index]
                    plt.title(self.titlePrefix + stationName + " station water depth")
#                     plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("depth (meters)")
                    plt.savefig(graph_directory + stationName + '_station_water.png')
                    plt.close()
#         No loop because no timeseries
        if(len(self.datapointsElevation) > 0):
            fig, ax = plt.subplots(figsize=(16,13))
#             print(len(self.assetLabels), len(self.datapointsElevation))
            ax.scatter(self.assetLabels, self.datapointsElevation, label="Mesh")
            if(self.assetExists):
                ax.scatter(self.assetLabels, self.assetDatapointsElevation, label="Asset")
#                     ax.plot(self.tideDatapointsPredictionTimes[index], self.tideDatapointsPredictionWaters[index], label="Prediction")
            ax.legend(loc="upper left")
            plt.title("Asset Elevation vs. Mesh Elevation", fontsize=18)
            plt.xlabel("asset name")
            plt.xticks(fontsize=8, rotation=45, ha='right')
            plt.yticks(fontsize=14)
            plt.ylabel("elevation (meters)", fontsize=14)
            plt.savefig(graph_directory + "elevation.png")
            plt.close()
        for index in range(numberOfEtaDatapoints):
            if(len(self.datapointsEta) > 0):
                fig, ax = plt.subplots(figsize=(16,9))
                ax.plot(self.etaTimes, self.datapointsEta[index], label="Forecast")
                if(self.tideExists):
                    ax.plot(self.tideDatapointsTimes[index], self.tideDatapointsWaters[index], label="Station")
                    ax.plot(self.tideDatapointsPredictionTimes[index], self.tideDatapointsPredictionWaters[index], label="Prediction")
                ax.legend(loc="upper left")
                stationName = self.tideLabels[index]
                plt.title(stationName + " station eta elevation")
                plt.xlabel("Hours since " + self.etaStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("eta (meters)")
                plt.savefig(graph_directory + stationName + '_eta.png')
                plt.close()
        for index in range(numberOfWaveDatapoints):
            if(self.wavesExists):
                if(len(self.datapointsSWH[index]) > 0):
                    fig, ax = plt.subplots(figsize=(16,9))
                    ax.scatter(self.waveTimes, self.datapointsSWH[index], marker=".", label=r"$H_s$")
                    if(self.buoyExists):
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsSWH[index], label="Obs")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station significant wave height", fontsize=24)
                    plt.xlabel("Date")                    
                    ax.format_xdata = mdates.DateFormatter('%d')
                    plt.ylabel("SWH (meters)")
                    plt.savefig(graph_directory + stationName + '_wave_swh.png')
                    plt.close()
                if(len(self.datapointsMWD[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsMWD[index], marker=".", label="Forecast")
                    if(self.buoyExists):
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsMWD[index], label="Buoy")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station mean wave direction", fontsize=24)
#                     plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    ax.format_xdata = mdates.DateFormatter('%d')
                    plt.ylabel("MWD (degrees)")
                    plt.savefig(graph_directory + stationName + '_wave_mwd.png')
                    plt.close()
                if(len(self.datapointsMWP[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsMWP[index], marker=".", label="Forecast")
                    if(self.buoyExists):
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsMWP[index], label="Buoy")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station mean wave period", fontsize=24)
#                     plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    ax.format_xdata = mdates.DateFormatter('%d')
                    plt.ylabel("MWP (seconds)")
                    plt.savefig(graph_directory + stationName + '_wave_mwp.png')
                    plt.close()
                if(len(self.datapointsPWP[index]) > 0):
                    fig, ax = plt.subplots(figsize=(16,9))
                    ax.scatter(self.waveTimes, self.datapointsPWP[index], marker=".", label=r"$T_p$")
                    if(self.buoyExists):
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsPWP[index], label="Obs")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station peak wave period", fontsize=24)
                    plt.xlabel("Date")
                    ax.format_xdata = mdates.DateFormatter('%d')
                    plt.ylabel("PWP (seconds)")
                    plt.savefig(graph_directory + stationName + '_wave_pwp.png')
                    plt.close()
                if(len(self.datapointsRADMag[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADMag[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station radiation stress magnitude", fontsize=24)
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad Stress Magitude (1/m^2s^2)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_mag.png')
                    plt.close()
                if(len(self.datapointsRADDir[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADDir[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station radiation stress direction", fontsize=24)
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad stress direction (degrees)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_dir.png')
                    plt.close()
                    
# Graph wave parameters on the same graph for comparison
#     swh graph
        if self.wavesExists:
            fig_swh, ax_swh = plt.subplots(figsize=(12, 8))
            for index in range(numberOfWaveDatapoints):
                if len(self.datapointsSWH[index]) > 0:
                    if(not np.isnan(np.min(self.datapointsSWH[index]))):
                        ax_swh.scatter(self.waveTimes, self.datapointsSWH[index], 
                                       marker=".", label=f"Forecast {self.buoyLabels[index]}")
                        if self.buoyExists:
                            ax_swh.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsSWH[index], 
                                           label=f"Buoy {self.buoyLabels[index]}")
    
            ax_swh.legend(loc="lower right", ncol=2, bbox_to_anchor=(1, 0))
            ax_swh.set_title("Significant Wave Height Across All Stations")
            ax_swh.format_xdata = mdates.DateFormatter('%d')
            ax_swh.set_ylabel("SWH (meters)")
            ax_swh.set_xlabel("Date")
            plt.tight_layout()
            plt.savefig(graph_directory + 'all_stations_wave_swh.png')
            plt.close(fig_swh)
        # MWP Graph
        if self.wavesExists:
            fig_mwp, ax_mwp = plt.subplots(figsize=(12, 8))
            for index in range(numberOfWaveDatapoints):
                if len(self.datapointsMWP[index]) > 0:
                    if(not np.isnan(np.min(self.datapointsMWP[index]))):
                        ax_mwp.scatter(self.waveTimes, self.datapointsMWP[index], 
                                       marker=".", label=f"Forecast {self.buoyLabels[index]}")
                        if self.buoyExists:
                            ax_mwp.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsMWP[index], 
                                           label=f"Buoy {self.buoyLabels[index]}")
    
            ax_mwp.legend(loc="lower right", ncol=2, bbox_to_anchor=(1, 0))
            ax_mwp.set_title("Mean Wave Period Across All Stations")
            ax_mwp.format_xdata = mdates.DateFormatter('%d')
            ax_mwp.set_ylabel("MWP (seconds)")
            ax_mwp.set_xlabel("Date")
            plt.tight_layout()
            plt.savefig(graph_directory + 'all_stations_wave_mwp.png')
            plt.close(fig_mwp)

        # PWP Graph
        if self.wavesExists:
            fig_pwp, ax_pwp = plt.subplots(figsize=(12, 8))
            for index in range(numberOfWaveDatapoints):
                if len(self.datapointsPWP[index]) > 0:
                    if(not np.isnan(np.min(self.datapointsPWP[index]))):
                        ax_pwp.scatter(self.waveTimes, self.datapointsPWP[index], 
                                       marker=".", label=f"Forecast {self.buoyLabels[index]}")
                        if self.buoyExists:
                            ax_pwp.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsPWP[index], 
                                           label=f"Buoy {self.buoyLabels[index]}")
    
            ax_pwp.legend(loc="lower right", ncol=2, bbox_to_anchor=(1, 0))
            ax_pwp.set_title("Peak Wave Period Across All Stations")
            ax_pwp.format_xdata = mdates.DateFormatter('%d')
            ax_pwp.set_ylabel("PWP (seconds)")
            ax_pwp.set_xlabel("Date")
            plt.tight_layout()
            plt.savefig(graph_directory + 'all_stations_wave_pwp.png')
            plt.close(fig_pwp)
            
#           Plot mwp and pwp together
        if self.wavesExists:
            fig, ax = plt.subplots(figsize=(12, 8))
    
            for index in range(numberOfWaveDatapoints):
                if len(self.datapointsMWP[index]) > 0 and not np.isnan(np.min(self.datapointsMWP[index])):
                    ax.scatter(self.waveTimes, self.datapointsMWP[index], 
                               marker=".", color='b', label=f"MWP Forecast {self.buoyLabels[index]}")
                    if self.buoyExists:
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsMWP[index], 
                                   marker="x", color='b', label=f"MWP Buoy {self.buoyLabels[index]}")

                if len(self.datapointsPWP[index]) > 0 and not np.isnan(np.min(self.datapointsPWP[index])):
                    ax.scatter(self.waveTimes, self.datapointsPWP[index], 
                               marker=".", color='r', label=f"PWP Forecast {self.buoyLabels[index]}")
                    if self.buoyExists:
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsPWP[index], 
                                   marker="x", color='r', label=f"PWP Buoy {self.buoyLabels[index]}")

            ax.legend(loc="upper left", ncol=2, bbox_to_anchor=(1, 1))
            ax.set_title("MWP and PWP Across All Stations")
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.set_ylabel("Wave Period (seconds)")
            ax.set_xlabel("Date")
    
            fig.tight_layout()
            fig.savefig(graph_directory + 'all_stations_wave_mwp_pwp.png')
            plt.close(fig)
            
#         Graph water values on top of each other
#         if len(self.datapointsWaters) > 0:
#             fig, ax = plt.subplots(figsize=(16, 9))
#     
#             for index in range(numberOfWaterDatapoints):
#                 if(not np.isnan(np.min(self.datapointsWaters[index]))):
#                     stationName = self.tideLabels[index]
#                     # Plot forecast data for each station
#                     ax.plot(self.waterTimes, self.datapointsWaters[index], label=f"Forecast {stationName}")
#                     
#                     if(self.stillwaterExists):
#                         ax.plot(self.stillwaterTimes, self.datapointsStillwaters[index], label="Forecast")
#                         
#                     if(self.tidewaterExists):
#                         ax.plot(self.tidewaterTimes, self.datapointsTidewaters[index], label="Forecast")
#                     # Plot tide data if available
#                     if self.tideExists:
#                         ax.plot(self.tideDatapointsTimes[index], self.tideDatapointsWaters[index], label=f"Station {stationName}")
#                     
#                     # Note: Prediction data plotting is commented out in the original code, so it remains commented here:
#                     # ax.plot(self.tideDatapointsPredictionTimes[index], self.tideDatapointsPredictionWaters[index], label=f"Prediction {stationName}")
# 
#             # Configure the plot
#             ax.legend(loc="upper left", ncol=2, bbox_to_anchor=(1, 1))
#             ax.format_xdata = mdates.DateFormatter('%d')
#             plt.xticks(fontsize=12)
#             plt.yticks(fontsize=12)
#     
#             # Since we're plotting multiple stations, we'll use a more general title
#             plt.title(self.titlePrefix + "Water Elevation for All Stations", fontsize=18)
#             plt.xlabel("Date", fontsize=14)
#             plt.ylabel("Elevation (meters)", fontsize=14)
#     
#             plt.tight_layout()
#             plt.savefig(graph_directory + 'all_stations_water.png')
#             plt.close()

        
# Graph multipanel all stations water

        # Create a multi-panel figure with one subplot per station
        if(numberOfWaterDatapoints > 0):
            fig, axes = plt.subplots(numberOfWaterDatapoints, 1, figsize=(16, 4 * numberOfWaterDatapoints), sharex=True, constrained_layout=True)
            
            # Ensure axes is a 1D array for consistent indexing
            if numberOfWaterDatapoints == 1:
                axes = [axes]
            else:
                axes = axes.flatten()
            
            # Find global min and max elevation for shared y-axis limits
            all_elevations = []
            for index in range(numberOfWaterDatapoints):
                if len(self.datapointsWaters) > 0:
                    all_elevations.extend(self.datapointsWaters[index])
                    if self.stillwaterExists:
                        all_elevations.extend(self.datapointsStillwaters[index])
                    if self.tidewaterExists:
                        all_elevations.extend(self.datapointsTidewaters[index])
                    if self.tideExists:
                        all_elevations.extend(self.tideDatapointsWaters[index])
            
            global_min = min(all_elevations) if all_elevations else -1.0
            global_max = max(all_elevations) if all_elevations else 1.0
            # Add padding to y-limits for better visualization
            y_padding = (global_max - global_min) * 0.1
            y_min = global_min - y_padding
            y_max = global_max + y_padding
            
            # Plot data for each station
            for index in range(numberOfWaterDatapoints):
                ax = axes[index]
                if len(self.datapointsWaters) > 0:
                    # Plot stillwater, tidewater, water, and observed tide data
                    if self.tidewaterExists:
                        ax.plot(self.tidewaterTimes, self.datapointsTidewaters[index], label=r"$\eta_{tide}$", linestyle="--")
                    if self.stillwaterExists:
                        ax.plot(self.stillwaterTimes, self.datapointsStillwaters[index], label=r"$\eta_{still}$", linestyle="--")
                    ax.plot(self.waterTimes, self.datapointsWaters[index], label=r"$\eta$")
                    if self.tideExists:
                        ax.plot(self.tideDatapointsTimes[index], self.tideDatapointsWaters[index], label="Obs")
                    
                    # Add legend
                    ax.legend(loc="upper left")
                    
                    # Format x-axis for dates
    #                 ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
                    
                    # Set title and labels
                    stationName = self.tideLabels[index]
                    maxElevation = str(round(max(self.datapointsWaters[index]), 2))
                    ax.set_title(f"{self.titlePrefix}{stationName} station water elevation (Max: {maxElevation} m)", fontsize=16)
                    ax.set_ylabel("Elevation (meters)", fontsize=12)
                    
                    # Set shared y-axis limits
                    ax.set_ylim(y_min, y_max)
                
                if index == numberOfWaterDatapoints - 1:
                    # Add x-label only to the bottom subplot
                    ax.set_xlabel("Date", fontsize=12)
            
            # Save the figure
            plt.savefig(graph_directory + 'all_stations_water.png', dpi=300, bbox_inches='tight')
            plt.close()
            
        
# Graph multipanel wind

# Collect all time data for shared x-axis limits
        if(numberOfWindDatapoints > 0):
            all_times = []
            for index in range(numberOfWindDatapoints):
                if len(self.datapointsSpeeds) > 0 or len(self.datapointsDirections) > 0:
                    all_times.extend(self.windTimes)
                    if self.obsExists:
                        all_times.extend(self.obsDatapointsTimes[index])
            
            x_min = min(all_times) if all_times else self.windStartDate
            x_max = max(all_times) if all_times else self.windStartDate
            # Add padding to x-limits (e.g., 5% of the time range)
            if x_min != x_max:
                x_padding = (x_max - x_min) * 0.05
                x_min -= x_padding
                x_max += x_padding
            
            # --- Wind Speed Figure ---
            # Collect all speed data for shared y-axis limits
            all_speeds = []
            for index in range(numberOfWindDatapoints):
                if len(self.datapointsSpeeds) > 0:
                    all_speeds.extend(self.datapointsSpeeds[index])
                    if self.obsExists:
                        all_speeds.extend(self.obsDatapointsSpeeds[index])
            
            speed_min = min(all_speeds) if all_speeds else 0.0
            speed_max = max(all_speeds) if all_speeds else 50.0
            # Add padding to y-limits
            speed_padding = (speed_max - speed_min) * 0.1 if speed_max != speed_min else 1.0
            speed_y_min = max(0.0, speed_min - speed_padding)  # Ensure non-negative for wind speed
            speed_y_max = speed_max + speed_padding
            
            # Create figure for wind speed
            fig_speed, axes_speed = plt.subplots(numberOfWindDatapoints, 1, figsize=(16, 4 * numberOfWindDatapoints), sharex=True, constrained_layout=True)
            if numberOfWindDatapoints == 1:
                axes_speed = [axes_speed]
            else:
                axes_speed = axes_speed.flatten()
            
            # Plot wind speed data
            for index in range(numberOfWindDatapoints):
                ax = axes_speed[index]
                if len(self.datapointsSpeeds) > 0:
                    ax.scatter(self.windTimes, self.datapointsSpeeds[index], marker=".", label="Forecast")
                    if self.obsExists:
                        ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsSpeeds[index], marker=".", label="Obs")
                    
                    ax.legend(loc="lower right")
#                     ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
                    
                    stationName = self.obsLabels[index]
                    maxSpeed = str(round(max(self.datapointsSpeeds[index]), 2)) if self.datapointsSpeeds[index] else "N/A"
                    ax.set_title(f"{stationName} station wind speed (Max: {maxSpeed} m/s)", fontsize=16)
                    ax.set_ylabel("Wind speed (m/s)", fontsize=12)
                    
                    ax.set_ylim(speed_y_min, speed_y_max)
                    ax.set_xlim(x_min, x_max)
                
                if index == numberOfWindDatapoints - 1:
                    ax.set_xlabel("Date", fontsize=12)
            
            # Save wind speed figure
            plt.savefig(graph_directory + 'all_stations_wind_speed.png', dpi=300, bbox_inches='tight')
            plt.close(fig_speed)
            
            # --- Wind Direction Figure ---
            # Collect all direction data for shared y-axis limits
            all_directions = []
            for index in range(numberOfWindDatapoints):
                if len(self.datapointsDirections) > 0:
                    all_directions.extend(self.datapointsDirections[index])
                    if self.obsExists:
                        all_directions.extend(self.obsDatapointsDirections[index])
            
            direction_min = min(all_directions) if all_directions else 0.0
            direction_max = max(all_directions) if all_directions else 360.0
            direction_min = 0
            direction_max = 360
            # Add padding to y-limits, respecting 0-360 degree range
            direction_padding = (direction_max - direction_min) * 0.1 if direction_max != direction_min else 10.0
            direction_y_min = max(0.0, direction_min - direction_padding)
            direction_y_max = min(360.0, direction_max + direction_padding)
            
            # Create figure for wind direction
            fig_direction, axes_direction = plt.subplots(numberOfWindDatapoints, 1, figsize=(16, 4 * numberOfWindDatapoints), sharex=True, constrained_layout=True)
            if numberOfWindDatapoints == 1:
                axes_direction = [axes_direction]
            else:
                axes_direction = axes_direction.flatten()
            
            # Plot wind direction data
            for index in range(numberOfWindDatapoints):
                ax = axes_direction[index]
                if len(self.datapointsDirections) > 0:
                    ax.scatter(self.windTimes, self.datapointsDirections[index], marker=".", label="Forecast")
                    if self.obsExists:
                        ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsDirections[index], marker=".", label="Obs")
                    
                    ax.legend(loc="lower right")
#                     ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))
                    
                    stationName = self.obsLabels[index]
                    ax.set_title(f"{stationName} station wind direction", fontsize=16)
                    ax.set_ylabel("Wind direction (degrees)", fontsize=12)
                    
                    ax.set_ylim(direction_y_min, direction_y_max)
                    ax.set_xlim(x_min, x_max)
                
                if index == numberOfWindDatapoints - 1:
                    ax.set_xlabel("Date", fontsize=12)
            
            # Save wind direction figure
            plt.savefig(graph_directory + 'all_stations_wind_direction.png', dpi=300, bbox_inches='tight')
            plt.close(fig_direction)

#         Graph values generated by GetRunup step
        if(len(self.datapointsRunup) > 0):
            for index in range(numberOfRunupDatapoints):
            
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
                ax.plot(self.runupTimes, self.datapointsRunup[index], label="Stockdon Runup Distance")
#                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon No Setup 1.1(S/2)")
#                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")

                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxRunupDistance = str(round(max(self.datapointsRunup[index]), 2))
                plt.title(self.titlePrefix + stationName + " station runup distance max: " + maxRunupDistance, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("runup distance along shore (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_runup_distance.png')
                plt.close()
#             Iterate through runup times to graph a map of the waterline
            
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanHigh[index], label="1.1(setup + S)")
                ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label="1.1([setup + storm surge] + S/2) + [SWL]")
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanHigh[index], label="Holman High Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label="Holman Mid Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label="Holman Low Tide ξ")
                ax.plot(self.runupTimes, self.datapointsRunupStockdon[index], label="1.1(<η> + S/2) + [SWL]")
#                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon Swash (S/2)")
#                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")
#                 ax.plot(self.runupTimes, self.datapointsRunupAdcirc[index], label="[SWL + setup] + 1.1(S/2)")


                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxRunup = str(round(max(self.datapointsRunupHolmanMid[index]), 2)) + ", " + str(round(max(self.datapointsRunupStockdon[index]), 2))
                plt.title(self.titlePrefix + stationName + " station runup (adcirc, stockdon): " + maxRunup, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("runup (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_runup.png')
                plt.close()
            
#               graph deepwater wave height
                fig, ax = plt.subplots(figsize=(16,9))

                ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label="Deepwater SWH")
#                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon Swash (S/2)")
#                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")
#                 ax.plot(self.runupTimes, self.datapointsRunupAdcirc[index], label="[SWL + setup] + 1.1(S/2)")


                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxSwh = str(round(max(self.datapointsRunupHolmanLow[index]), 2))
                plt.title(self.titlePrefix + stationName + " station deepwater SWH max: " + maxSwh, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("Deepwater SWH (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_deepwater_swh.png')
                plt.close()
                
#                 Graph setup
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
#                 ax.plot(self.runupTimes, self.datapointsSetupHolmanHigh[index], label="Holman High Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSetupHolmanMid[index], label="Holman Mid Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSetupHolmanLow[index], label="Holman Low Tide ξ")
                ax.plot(self.runupTimes, self.datapointsSetupStockdon[index], label=r"Stockdon $\langle\eta\rangle$")
#                 ax.plot(self.runupTimes, self.datapointsSetupAdcirc[index], label="ADCIRC+SWAN setup+storm surge")
                ax.plot(self.runupTimes, self.datapointsSetupStockdonLow[index], label=r"SWAN $\eta_{setup}$")
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanHigh[index], label="ADCIRC+SWAN storm surge")


                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                stationName = self.runupLabels[index]
                maxSetup = str(round(max(self.datapointsSetupStockdonLow[index]), 2)) + ", " + str(round(max(self.datapointsSetupStockdon[index]), 2))
                plt.title(self.titlePrefix + stationName + " station setup max (SWAN, Stockdon): " + maxSetup, fontsize=24)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("setup (meters)")
                plt.savefig(graph_directory + stationName + '_setup.png')
                plt.close()
                
#                 Graph swash
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanHigh[index], label="Holman High Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanMid[index], label="Holman Mid Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanLow[index], label="Holman Low Tide ξ")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonIncident[index], label="Stockdon Incident βf√(HₒLₒ)")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonInfragravity[index], label="Stockdon Infragravity √(HₒLₒ)")
#                 ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label="Stockdon Low")
                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxSwash = str(round(max(self.datapointsSwashStockdonIncident[index]), 2)) + ", " + str(round(max(self.datapointsSwashStockdonInfragravity[index]), 2))
                plt.title(self.titlePrefix + stationName + " station swash max (inc, ig): " + maxSwash, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("swash (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_swash.png')
                plt.close()
                        
#                 Graph incident swash
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
                ax.plot(self.runupTimes, self.datapointsSwashHolmanIncident[index], label="Holman Incident ξ")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonIncident[index], label="Stockdon Incident βf√(HₒLₒ)")
#                 ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label="Stockdon Low")
                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxIncidentSwash = str(round(max(self.datapointsSwashStockdonIncident[index]), 2))
                plt.title(self.titlePrefix + stationName + " station incident (<3min) swash max: " + maxIncidentSwash, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("swash (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_incident_swash.png')
                plt.close()
                
#                 Graph infragravity swash
                fig, ax = plt.subplots(figsize=(16,9))
                ax.plot(self.runupTimes, self.datapointsSwashHolmanInfragravity[index], label="Holman Infragravity ξ")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonInfragravity[index], label="Stockdon Infragravity √(HₒLₒ)")
#                 ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label="Stockdon Low")
                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxInfragravitySwash = str(round(max(self.datapointsSwashStockdonInfragravity[index]), 2))
                plt.title(self.titlePrefix + stationName + " station infragravity (>3 min) swash max: " + maxInfragravitySwash, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("swash (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_infragravity_swash.png')
                plt.close()
            
                
#                 Graph water_swash
                if(len(self.datapointsWaters) > 0 and False):
                    # Assuming self.findMatchingIndices is defined as per your earlier request
                    datapointsWaterRunupIndices = self.findMatchingIndices(self.tideLabels, self.runupLabels[index][0:9])
#                     print("Finding Water stations corresponding to runup station")
#                     print("Searching for water labels with string: ", self.runupLabels[index][0:9])
#                     print("Found indices count:", len(datapointsWaterRunupIndices))
                    for datapointsWaterRunupIndex in datapointsWaterRunupIndices:
                        
                        fig, ax = plt.subplots(figsize=(16, 9))
                        
                        # Plot the water elevation time series
                        ax.plot(self.waterTimes, self.datapointsWaters[datapointsWaterRunupIndex], label=r"$\eta$", color='blue', linewidth=2)
                        
                        # Calculate total swash: sqrt(S_incident^2 + S_infragravity^2)
                        total_swash = np.sqrt(np.array(self.datapointsSwashStockdonIncident[index])**2 + 
                                              np.array(self.datapointsSwashStockdonInfragravity[index])**2)
                        
                        # Define the upper and lower bounds for the swash area
                        lower_bound = self.datapointsWaters[datapointsWaterRunupIndex] - 0.5 * total_swash
                        upper_bound = self.datapointsWaters[datapointsWaterRunupIndex] + 0.5 * total_swash
                        
                        # Fill the area between upper and lower bounds to highlight swash extent
                        ax.fill_between(self.waterTimes, lower_bound, upper_bound, color='lightblue', alpha=0.4, label="Swash Extent")
                        
                        # Add dotted lines for maximum and minimum extents
                        ax.plot(self.waterTimes, upper_bound, '--', color='red', label="+S/2", linewidth=1.5)
                        ax.plot(self.waterTimes, lower_bound, '--', color='green', label="-S/2", linewidth=1.5)
                        
                        # Calculate the maximum elevation including the swash
                        max_water_elevation = max(self.datapointsWaters[datapointsWaterRunupIndex])
                        max_swash_upper = max(upper_bound)
                        maxElevation = str(round(max_water_elevation, 2)) + ", " + str(round(max_swash_upper, 2))
                        
                        # Customize the plot
                        ax.legend(loc="upper left")
                        ax.format_xdata = mdates.DateFormatter('%d')
                        stationName = self.tideLabels[datapointsWaterRunupIndex]
#                         print("stationName of corresponding water station: ", stationName)
                        plt.title(self.titlePrefix + stationName + " station elevation max (water, swash): " + maxElevation, fontsize=18)
                        plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT))
                        plt.ylabel("elevation (meters)")
                        
                        # Adjust layout to prevent label cutoff
                        plt.tight_layout()
                        
                        # Save and close the plot
                        plt.savefig(graph_directory + stationName + '_water_swash.png', dpi=300)
                        plt.close()
           
       
#               Graph wavelength
                fig, ax = plt.subplots(figsize=(16,9))
                ax.plot(self.runupTimes, self.datapointsWavelength[index])
#                 ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxWavelength = str(round(max(self.datapointsWavelength[index]), 2))
                plt.title(self.titlePrefix + stationName + " station wavelength max: " + maxWavelength, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("wavelength (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_wavelength.png')
                plt.close()
                
#                 Graph steepness
                fig, ax = plt.subplots(figsize=(16,9))
                ax.plot(self.runupTimes, self.datapointsSteepness[index])
#                 ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxSteepness = str(round(max(self.datapointsSteepness[index]), 2))
                plt.title(self.titlePrefix + stationName + " station steepness max: " + maxSteepness, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("wave steepness (H₀/L₀)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_steepness.png')
                plt.close()
                
#                 Graph iribarren number
                fig, ax = plt.subplots(figsize=(16,9))
                ax.plot(self.runupTimes, self.datapointsIribarren[index])
                ax.set_ylim([0, 2])
#                 ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxIribarren = str(round(max(self.datapointsIribarren[index]), 2))
                plt.title(self.titlePrefix + stationName + " station iribarren max: " + maxIribarren, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("iribarren number", fontsize=14)
                plt.savefig(graph_directory + stationName + '_iribarren.png')
                plt.close()
                
#                 Graph average slope
                fig, ax = plt.subplots(figsize=(16,9))
                ax.plot(self.runupTimes, self.runupAverageSlopes[index])
                ax.set_ylim([0, 0.1])
#                 ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxAverageSlope = str(round(max(self.runupAverageSlopes[index]), 2))
                plt.title(self.titlePrefix + stationName + " station average slope (waterline to surf) max: " + maxAverageSlope, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("average slope", fontsize=14)
                plt.savefig(graph_directory + stationName + '_slope.png')
                plt.close()


            # Combined runup plots for all transects
            fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
            for transect in range(1, 6):
                ax = axes[transect - 1]
                dune_heights = []
                unique_heights = set()
    
                for index in range(numberOfRunupDatapoints):
                    stationName = self.runupLabels[index]
                    if str(transect) in stationName[0:stationName.index(" ")]:
    #                     print("found label", self.runupLabels[index])
    #                     print("runup values", self.datapointsRunupHolmanMid[index])
                        dune_heights = self.datapointsDuneHeights[index]
                        ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label=stationName)
                        unique_heights.update(dune_heights)
    
                # Plot horizontal lines for each unique dune height
                for height in unique_heights:
                    if(transect >= 5):
                        ax.axhline(y=height, linestyle='--', color='red', label=f'Runup Height {height:.2f}m' if height == list(unique_heights)[0] else None)
                    else:
                        ax.axhline(y=height, linestyle='--', color='grey', label=f'Runup Height {height:.2f}m' if height == list(unique_heights)[0] else None)
    
                ax.legend(loc="upper left", fontsize=10)
                ax.format_xdata = mdates.DateFormatter('%d')
                ax.tick_params(axis='both', labelsize=12)
                ax.set_ylabel("Runup (meters)", fontsize=12)
                ax.set_title(f"{self.titlePrefix}Napatree{transect} Runup", fontsize=14)
    
            plt.tight_layout()
            plt.savefig(graph_directory + 'Napatree_all_runup.png')
            plt.close()
    
            # Combined deepwater significant wave height (H_0) plots for all transects
            fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
            for transect in range(1, 6):
                ax = axes[transect - 1]
    
                for index in range(numberOfRunupDatapoints):
                    stationName = self.runupLabels[index]
                    if str(transect) in stationName[0:stationName.index(" ")]:
                        ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label=stationName)
    
                ax.legend(loc="upper left", fontsize=10)
                ax.format_xdata = mdates.DateFormatter('%d')
                ax.tick_params(axis='both', labelsize=12)
                ax.set_ylabel(r"$H_0$ (meters)", fontsize=12)
                ax.set_title(f"{self.titlePrefix}Napatree{transect} Deepwater SWH", fontsize=16)
    
    #         plt.xlabel("Day", fontsize=14)
            plt.tight_layout()
            plt.savefig(graph_directory + 'Napatree_all_deepwater_swh.png')
            plt.close()
    
            # Combined significant wave height (H_s) plots for all transects
            fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
            for transect in range(1, 6):
                ax = axes[transect - 1]
    
                for index in range(numberOfRunupDatapoints):
                    stationName = self.runupLabels[index]
                    if str(transect) in stationName[0:stationName.index(" ")]:  # Match deepline indices
                        swhIndex = self.buoyLabels.index(stationName)
                        ax.plot(self.runupTimes, self.datapointsSWH[swhIndex], label=stationName)
    
                ax.legend(loc="upper left", fontsize=10)
                ax.format_xdata = mdates.DateFormatter('%d')
                ax.tick_params(axis='both', labelsize=12)
                ax.set_ylabel(r"$H_s$ (meters)", fontsize=12)
                ax.set_title(f"{self.titlePrefix}Napatree{transect} SWH", fontsize=16)
    
    #         plt.xlabel("Day", fontsize=14)
            plt.tight_layout()
            plt.savefig(graph_directory + 'Napatree_all_swh.png')
            plt.close()
    
            # Combined elevation, max SWH, and max deepwater SWH plots for all transects
            fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
            for transect in range(1, 6):
                ax = axes[transect - 1]
                ax2 = ax.twinx()  # Second y-axis for elevation
            
                deeplineDistances = []
                deeplineElevations = []
                deeplineSWH = []
                deeplineDeepwaterSWH = []
            
                for index in range(numberOfRunupDatapoints):
                    stationName = self.runupLabels[index]
                    if str(transect) in stationName[0:stationName.index(" ")]:
                        swhIndex = self.buoyLabels.index(stationName)
                        deeplineSWH.append(np.max(self.datapointsSWH[swhIndex]))
                        elevationIndex = self.assetLabels.index(stationName)
                        deeplineElevations.append(self.datapointsElevation[elevationIndex])
                        deeplineDeepwaterSWH.append(np.max(self.datapointsRunupHolmanLow[index]))
                        # Extract distance from name (e.g., "1000m" -> 1000)
                        distance_str = stationName[stationName.rindex(" ") + 1:-1]
                        deeplineDistances.append(int(distance_str))
            
                # Plot SWH and deepwater SWH on primary y-axis
                ax.plot(deeplineDistances, deeplineSWH, label="Max SWH", color='blue')
                ax.plot(deeplineDistances, deeplineDeepwaterSWH, label="Max Deepwater SWH", color='green')
                # Plot elevation on secondary y-axis
                ax2.plot(deeplineDistances, deeplineElevations, label="Elevation", color='red', linestyle="--")
            
                # Find distances for depth lines (-7m, -20m) using interpolation or nearest match
                deeplineElevations = np.array(deeplineElevations)
                deeplineDistances = np.array(deeplineDistances)
                
                # Distance for -7m depth
                if np.any((deeplineElevations <= DEPTH_LINE_7M + 0.1) & (deeplineElevations >= DEPTH_LINE_7M - 0.1)):
                    # Find nearest elevation to -7m
                    idx_7m = np.argmin(np.abs(deeplineElevations - DEPTH_LINE_7M))
                    distance_7m = deeplineDistances[idx_7m]
                else:
                    # Interpolate if exact match not found
                    try:
                        distance_7m = np.interp(DEPTH_LINE_7M, deeplineElevations[::-1], deeplineDistances[::-1])
                    except:
                        distance_7m = None
                        print(f"Warning: Could not find or interpolate distance for depth {DEPTH_LINE_7M}m in transect {transect}")
            
                # Distance for -20m depth
                if np.any((deeplineElevations <= DEPTH_LINE_20M + 0.1) & (deeplineElevations >= DEPTH_LINE_20M - 0.1)):
                    # Find nearest elevation to -20m
                    idx_20m = np.argmin(np.abs(deeplineElevations - DEPTH_LINE_20M))
                    distance_20m = deeplineDistances[idx_20m]
                else:
                    # Interpolate if exact match not found
                    try:
                        distance_20m = np.interp(DEPTH_LINE_20M, deeplineElevations[::-1], deeplineDistances[::-1])
                    except:
                        distance_20m = None
                        print(f"Warning: Could not find or interpolate distance for depth {DEPTH_LINE_20M}m in transect {transect}")
            
                # Plot vertical lines
                if distance_7m is not None:
                    ax.axvline(x=distance_7m, color='purple', linestyle='--', label='Depth -7m', alpha=0.7)
                if distance_20m is not None:
                    ax.axvline(x=distance_20m, color='orange', linestyle='--', label='Depth -20m', alpha=0.7)
                ax.axvline(x=DISTANCE_LINE_9000M, color='black', linestyle='--', label='9000m', alpha=0.7)
            
                # Customize axes
                ax.set_ylabel("SWH (meters)", fontsize=12, color='blue')
                ax2.set_ylabel("Elevation (meters)", fontsize=12, color='red')
                ax.tick_params(axis='y', labelcolor='blue', labelsize=12)
                ax2.tick_params(axis='y', labelcolor='red', labelsize=12)
                ax.tick_params(axis='x', labelsize=12)
                ax.set_title(f"{self.titlePrefix}Napatree{transect} Deepline Metrics", fontsize=16)
            
                # Combine legends (only for first transect)
                if transect == 1:
                    lines1, labels1 = ax.get_legend_handles_labels()
                    lines2, labels2 = ax2.get_legend_handles_labels()
                    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=10)
            
            plt.xlabel("Distance (meters)", fontsize=14)
            plt.tight_layout()
            plt.savefig(graph_directory + 'Napatree_all_deepline_metrics.png')
            plt.close()

# 
# # Graph all runup
# 
#         fig, ax = plt.subplots(figsize=(16,9))
#         duneHeights = []
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("1" in stationName[0:stationName.index(" ")]):
#                 duneHeights = self.datapointsDuneHeights[index]
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label=stationName)
# 
#         ax.plot(self.runupTimes, duneHeights, label="Dune Height")
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree1 all runup: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Runup (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree1_all_runup.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         duneHeights = []
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("2" in stationName[0:stationName.index(" ")]):
#                 duneHeights = self.datapointsDuneHeights[index]
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label=stationName)
# 
#         ax.plot(self.runupTimes, duneHeights, label="Dune Height")
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree2 all runup: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Runup (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree2_all_runup.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         duneHeights = []
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("3" in stationName[0:stationName.index(" ")]):
#                 duneHeights = self.datapointsDuneHeights[index]
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label=stationName)
# 
#         ax.plot(self.runupTimes, duneHeights, label="Dune Height")
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree3 all runup: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Runup (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree3_all_runup.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         duneHeights = []
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("4" in stationName[0:stationName.index(" ")]):
#                 duneHeights = self.datapointsDuneHeights[index]
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label=stationName)
# 
#         ax.plot(self.runupTimes, duneHeights, label="Dune Height")
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree4 all runup: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Runup (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree4_all_runup.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         duneHeights = []
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("5" in stationName[0:stationName.index(" ")]):
#                 duneHeights = self.datapointsDuneHeights[index]
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label=stationName)
# 
#         ax.plot(self.runupTimes, duneHeights, label="Dune Height")
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree5 all runup: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Runup (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree5_all_runup.png')
#         plt.close()
# #         
#     #               graph all deepwater swh                
#         fig, ax = plt.subplots(figsize=(16,9))
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("1" in stationName[0:stationName.index(" ")]):
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label=stationName)
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon Swash (S/2)")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupAdcirc[index], label="[SWL + setup] + 1.1(S/2)")
# 
# 
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + r"Napatree1 deepwater significant wave height $H_0$: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel(r"$H_0$ (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree1_all_deepwater_swh.png')
#         plt.close()
# # #         
#         fig, ax = plt.subplots(figsize=(16,9))
#         for index in range(numberOfRunupDatapoints):
#             stationName = self.runupLabels[index]
#             if("1" in stationName[0:stationName.index(" ")] and stationName[-1] == "m"):
#                 swhIndex = self.buoyLabels.index(stationName)
#                 ax.plot(self.runupTimes, self.datapointsSWH[swhIndex], label=stationName)
#                 
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + r"Napatree1 significant wave height $H_s$: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel(r"$H_s$ (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree1_all_swh.png')
#         plt.close()
# 
#         deeplineDistances = []
#         deeplineElevations = []
#         deeplineSWH = []
#         deeplineDeepwaterSWH = []
#         for index in range(numberOfRunupDatapoints):
#             stationName = self.runupLabels[index]
#             if("1" in stationName[0:stationName.index(" ")]):
#                 swhIndex = self.buoyLabels.index(stationName)
#                 deeplineSWH.append(np.max(self.datapointsSWH[swhIndex]))
#                 elevationIndex = self.assetLabels.index(stationName)
#                 deeplineElevations.append(self.datapointsElevation[elevationIndex])
#                 deeplineDeepwaterSWH.append(np.max(self.datapointsRunupHolmanLow[index]))
#                 
#                 deeplineDistances.append(int(stationName[stationName.rindex(" ") + 1:len(stationName) - 1]))
# 
# 
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree1 Deepline Elevation: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineElevations)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Elevation (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree1_all_elevations.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree1 Deepline SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree1_max_swh.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree1 Deepline Deepwater SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineDeepwaterSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree1_max_deepwater_swh.png')
#         plt.close()

                
    #               graph all deepwater swh                
#         fig, ax = plt.subplots(figsize=(16,9))
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("2" in stationName[0:stationName.index(" ")]):
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label=stationName)
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon Swash (S/2)")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupAdcirc[index], label="[SWL + setup] + 1.1(S/2)")
# 
# 
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree2 all deepwater SWH: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree2_all_deepwater_swh.png')
#         plt.close()
        
#         deeplineDistances = []
#         deeplineElevations = []
#         deeplineSWH = []
#         deeplineDeepwaterSWH = []
#         for index in range(numberOfRunupDatapoints):
#             stationName = self.runupLabels[index]
#             if("2" in stationName[0:stationName.index(" ")] and stationName[-1] == "m"):
#                 swhIndex = self.buoyLabels.index(stationName)
#                 deeplineSWH.append(np.max(self.datapointsSWH[swhIndex]))
#                 elevationIndex = self.assetLabels.index(stationName)
#                 deeplineElevations.append(self.datapointsElevation[elevationIndex])
#                 deeplineDeepwaterSWH.append(np.max(self.datapointsRunupHolmanLow[index]))
#                 
#                 deeplineDistances.append(int(stationName[stationName.rindex(" ") + 1:len(stationName) - 1]))
# 
# 
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree2 Deepline Elevation: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineElevations)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Elevation (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree2_all_elevations.png')
#         plt.close()
        
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree2 Deepline SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree2_max_swh.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree2 Deepline Deepwater SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineDeepwaterSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree2_max_deepwater_swh.png')
#         plt.close()

    #               graph all deepwater swh                
#         fig, ax = plt.subplots(figsize=(16,9))
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("3" in stationName[0:stationName.index(" ")]):
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label=stationName)
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon Swash (S/2)")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupAdcirc[index], label="[SWL + setup] + 1.1(S/2)")
# 
# 
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree3 all deepwater SWH: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree3_all_deepwater_swh.png')
#         plt.close()
#         
#         deeplineDistances = []
#         deeplineElevations = []
#         deeplineSWH = []
#         deeplineDeepwaterSWH = []
#         for index in range(numberOfRunupDatapoints):
#             stationName = self.runupLabels[index]
#             if("3" in stationName[0:stationName.index(" ")] and stationName[-1] == "m"):
#                 swhIndex = self.buoyLabels.index(stationName)
#                 deeplineSWH.append(np.max(self.datapointsSWH[swhIndex]))
#                 elevationIndex = self.assetLabels.index(stationName)
#                 deeplineElevations.append(self.datapointsElevation[elevationIndex])
#                 deeplineDeepwaterSWH.append(np.max(self.datapointsRunupHolmanLow[index]))
#                 
#                 deeplineDistances.append(int(stationName[stationName.rindex(" ") + 1:len(stationName) - 1]))
# 
# 
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree3 Deepline Elevation: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineElevations)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Elevation (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree3_all_elevations.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree3 Deepline SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree3_max_swh.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree3 Deepline Deepwater SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineDeepwaterSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree3_max_deepwater_swh.png')
#         plt.close()


    #               graph all deepwater swh                
#         fig, ax = plt.subplots(figsize=(16,9))
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("4" in stationName[0:stationName.index(" ")]):
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label=stationName)
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon Swash (S/2)")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupAdcirc[index], label="[SWL + setup] + 1.1(S/2)")
# 
# 
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree4 all deepwater SWH: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree4_all_deepwater_swh.png')
#         plt.close()
        
#         deeplineDistances = []
#         deeplineElevations = []
#         deeplineSWH = []
#         deeplineDeepwaterSWH = []
#         for index in range(numberOfRunupDatapoints):
#             stationName = self.runupLabels[index]
#             if("4" in stationName[0:stationName.index(" ")] and stationName[-1] == "m"):
#                 swhIndex = self.buoyLabels.index(stationName)
#                 deeplineSWH.append(np.max(self.datapointsSWH[swhIndex]))
#                 elevationIndex = self.assetLabels.index(stationName)
#                 deeplineElevations.append(self.datapointsElevation[elevationIndex])
#                 deeplineDeepwaterSWH.append(np.max(self.datapointsRunupHolmanLow[index]))
#                 
#                 deeplineDistances.append(int(stationName[stationName.rindex(" ") + 1:len(stationName) - 1]))
# 
# 
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree4 Deepline Elevation: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineElevations)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Elevation (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree4_all_elevations.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree4 Deepline SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree4_max_swh.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree4 Deepline Deepwater SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineDeepwaterSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree4_max_deepwater_swh.png')
#         plt.close()

    #               graph all deepwater swh                
#         fig, ax = plt.subplots(figsize=(16,9))
#         for index in range(numberOfRunupDatapoints):
# 
#             stationName = self.runupLabels[index]
#             if("5" in stationName[0:stationName.index(" ")]):
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label=stationName)
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonNoSetup[index], label="Stockdon Swash (S/2)")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupStockdonLow[index], label="Stockdon Low")
#         #                 ax.plot(self.runupTimes, self.datapointsRunupAdcirc[index], label="[SWL + setup] + 1.1(S/2)")
# 
# 
#         ax.legend(loc="upper left")
#         ax.format_xdata = mdates.DateFormatter('%d')
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree5 all deepwater SWH: ", fontsize=18)
# #                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
#         plt.tight_layout()
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.savefig(graph_directory + 'Napatree5_all_deepwater_swh.png')
#         plt.close()
#         
#         deeplineDistances = []
#         deeplineElevations = []
#         deeplineSWH = []
#         deeplineDeepwaterSWH = []
#         for index in range(numberOfRunupDatapoints):
#             stationName = self.runupLabels[index]
#             if("5" in stationName[0:stationName.index(" ")] and stationName[-1] == "m"):
#                 swhIndex = self.buoyLabels.index(stationName)
#                 deeplineSWH.append(np.max(self.datapointsSWH[swhIndex]))
#                 elevationIndex = self.assetLabels.index(stationName)
#                 deeplineElevations.append(self.datapointsElevation[elevationIndex])
#                 deeplineDeepwaterSWH.append(np.max(self.datapointsRunupHolmanLow[index]))
#                 
#                 deeplineDistances.append(int(stationName[stationName.rindex(" ") + 1:len(stationName) - 1]))
# 
# 
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree5 Deepline Elevation: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineElevations)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Elevation (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree5_all_elevations.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree5 Deepline SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree5_max_swh.png')
#         plt.close()
#         
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree5 Deepline Deepwater SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineDeepwaterSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("Deepwater SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree5_max_deepwater_swh.png')
#         plt.close()

                
#         if(len(self.runupTimes) > 0):
#             vmin = -1
#             vminSwath = 0
# #             vmax = math.ceil(self.maxWater)
#             vmax = 5
# #             vmax = 20
#             levels = 100
#             levelBoundaries = np.linspace(vmin, vmax, levels + 1)
#             levelBoundariesSwath = np.linspace(vminSwath, vmax, levels + 1)
# #             waterTriangulation = Triangulation(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, triangles=self.mapWaterTriangles, mask=self.mapWaterMaskedTriangles)
#             for index in range(len(self.runupTimes)):
#                 fig, ax = plt.subplots(figsize=(9,9))
#     #             print(self.endWavePointsLongitudes)
#     #             print(self.endWavePointsLatitudes)
#     #             print(self.endSWH)
#                 plt.imshow(img, extent=self.backgroundAxis, alpha=0.6, aspect=aspectRatio, zorder=2)
#                 
# #                 Plot points
#                 if(self.meshExists):
#                     ax.scatter(self.assetLongitudes, self.assetLatitudes, label="Assets", zorder=3, alpha=0.7, marker=".", s=40, color="black")
#                     
#                 if(self.runupExists):
#                     for runupIndex, runupLabel in enumerate(self.runupLabels):
#                         self.plotExtendedLines(ax, runupIndex, index, runupLabel)
# #                         print("datapointsWaterlineLongitudes", type(self.datapointsWaterlineLongitudes[runupIndex][index]))
# #                         ax.plot(self.datapointsWaterlineLongitudes[runupIndex][index], self.datapointsWaterlineLatitudes[runupIndex][index], label=runupLabel, zorder=3, alpha=0.7, marker=".", color="green")
# #                         ax.plot(self.datapointsRunupLongitudes[runupIndex][index], self.datapointsRunupLatitudes[runupIndex][index], label=runupLabel, zorder=3, alpha=0.7, marker=".", color="red")
# 
# #               Todo: Fix triangulation errors
# #                 contourset = ax.tripcolor(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, self.mapWaters[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
#                 plt.axis(plotAxis)
#                 plt.title(self.titlePrefix + "Runup Waterline")
#                 plt.xlabel(self.runupTimes[index])
#     #             plt.gca().invert_yaxis()
# 
#                 plt.savefig(graph_directory + 'map_runup_' + str(index) + '.png')
#                 plt.close()
#                 gc.collect()
#             with imageio.get_writer(graph_directory + 'runup.gif', mode='I') as writer:
#                 for index in range(len(self.runupTimes)):
#                     filename = "map_runup_" + str(index) + ".png"
#                     image = imageio.imread(graph_directory + filename)
#                     writer.append_data(image)
#                 for index in range(len(self.runupTimes)):
#                     filename = "map_runup_" + str(index) + ".png"
#                     os.remove(graph_directory + filename)
#             plt.close()
#             gc.collect()

