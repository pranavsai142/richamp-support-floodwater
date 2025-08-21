import os
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable
from matplotlib.tri import Triangulation
from datetime import datetime, timezone
import imageio
import gc
from geographiclib.geodesic import Geodesic
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

import requests
from scipy.interpolate import RegularGridInterpolator
import time
import threading
import sys
import itertools
from pyproj import Transformer
import pandas as pd


SMALL_SIZE = 14
MEDIUM_SIZE = 18
BIGGER_SIZE = 22

DEPTH_LINE_7M = -7.0
DEPTH_LINE_20M = -20.0
DISTANCE_LINE_9000M = 9000.0

GRAPH_SWASH = True
GRAPH_MULTIPANEL = True

BYPASS_WATER_TIMESERIES_PLOTS = False
BYPASS_WATER_MAP_PLOTS = True

MHW_ELEVATION_RELATIVE_TO_NAVD88 = 0.646

FORESHORE_BEACH_SLOPE_OBS = [0.13, 0.11, 0.08, 0.07, 0.07]  

GRAPH_2022 = False 

MHWL_TRANSECTS = []
DUNE_TOE_TRANSECTS = []
DUNE_CREST_TRANSECTS = []  
BEACH_SLOPES_TRANSECTS = []  
ALL_LONGITUDES_TRANSECTS = []
ALL_LATITUDES_TRANSECTS = []
ALL_DUNE_CREST_TRANSECTS = []
ALL_SHORELINE_LONGITUDES_TRANSECTS = []
ALL_SHORELINE_LATITUDES_TRANSECTS = []
ALL_BEACH_SLOPES_TRANSECTS = []

TWLCC_FORECAST_POINTS_IDENTIFIERS = [[17, 3, 3], [17, 3, 47]]
TWLCC_FORECAST_POINTS_LATITUDES = []
TWLCC_FORECAST_POINTS_LONGITUDES = []



# Search for below to find where to make changes when running runup graphs for 2022 vs 2023
#             CHANGE HERE WHEN DOING 2022 VS 2023 NOREASTER

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

    def __init__(self, dataToGraph={}, STATIONS_FILE="", backgroundMap="", backgroundAxis=[], titlePrefix="", GRAPH_DIRECTORY="graphs/"):
        self.GRAPH_DIRECTORY = GRAPH_DIRECTORY
        
        self.USGS_BEACH_PROFILE_FILE = "usgs_beach_profile_file.csv"
        
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
        self.datapointsRunupObs = []
        self.datapointsRunupObsSwash = []
        self.datapointsRunupObsIncidentSwash = []
        self.datapointsRunupObsInfragravitySwash = []
        self.datapointsRunupObsSwh = []
        self.datapointsRunupObsPwp = []
        self.datapointsRunupObsImpact = []
        self.datapointsRunupObsBeachSlope = []

        
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
            
        if(self.waterExists or False):
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
                datapointRunupObs = []
                datapointRunupObsSwash = []
                datapointRunupObsIncidentSwash = []
                datapointRunupObsInfragravitySwash = []
                datapointRunupObsSwh = []
                datapointRunupObsPwp = []
                datapointRunupObsImpact = []
                datapointRunupObsBeachSlope = []
                

                
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
                    datapointHolmanLowSwash.append(runupDataset[stationKey]["swashHolmanLow"][index])
                    datapointStockdonSetup.append(runupDataset[stationKey]["setupStockdon"][index])
                    datapointStockdonSetupLow.append(runupDataset[stationKey]["setupStockdonLow"][index])
                    datapointStockdonSwashLow.append(runupDataset[stationKey]["swashStockdonLow"][index])
                    datapointStockdonSwashIncident.append(runupDataset[stationKey]["swashStockdonIncident"][index])
                    datapointStockdonSwashInfragravity.append(runupDataset[stationKey]["swashStockdonInfragravity"][index])
                    datapointStockdonRunup.append(runupDataset[stationKey]["runupStockdon"][index])
                    datapointStockdonRunupNoSetup.append(runupDataset[stationKey]["runupStockdonNoSetup"][index])
                    datapointAdcircSetup.append(runupDataset[stationKey]["setupAdcirc"][index])
                    datapointAdcircRunup.append(runupDataset[stationKey]["runupAdcirc"][index])
                    datapointDuneHeights.append(runupDataset[stationKey]["duneHeights"][index])

                    
                for index in range(len(runupDataset[stationKey]["swashHolmanHigh"])):
                    if(runupDataset[stationKey]["setupHolmanHigh"][index] <= runupDataset[stationKey]["times"][-1]):
                        datapointHolmanHighSetup.append(self.unixTimeToDeltaHours(runupDataset[stationKey]["setupHolmanHigh"][index], self.runupStartDate))
                        datapointHolmanMidSetup.append(runupDataset[stationKey]["setupHolmanMid"][index])
                        datapointHolmanLowSetup.append(runupDataset[stationKey]["setupHolmanLow"][index])
                        datapointHolmanHighSwash.append(runupDataset[stationKey]["swashHolmanHigh"][index])
                        datapointHolmanMidSwash.append(runupDataset[stationKey]["swashHolmanMid"][index])
                        datapointHolmanSwashIncident.append(runupDataset[stationKey]["swashHolmanIncident"][index])
                        datapointHolmanSwashInfragravity.append(runupDataset[stationKey]["swashHolmanInfragravity"][index])
                        datapointStockdonRunupLow.append(runupDataset[stationKey]["runupStockdonLow"][index])
                        datapointRunupObs.append(runupDataset[stationKey]["obsRunup"][index])
                        datapointRunupObsSwash.append(runupDataset[stationKey]["obsSwash"][index])
                        datapointRunupObsIncidentSwash.append(runupDataset[stationKey]["obsIncidentSwash"][index])
                        datapointRunupObsInfragravitySwash.append(runupDataset[stationKey]["obsInfragravitySwash"][index])
                        datapointRunupObsSwh.append(runupDataset[stationKey]["obsSwh"][index])
                        datapointRunupObsPwp.append(runupDataset[stationKey]["obsPwp"][index])
                        datapointRunupObsImpact.append(runupDataset[stationKey]["obsImpact"][index])
                        datapointRunupObsBeachSlope.append(runupDataset[stationKey]["obsBeachSlope"][index])
                        
                    
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
                self.datapointsRunupObs.append(datapointRunupObs)
                self.datapointsRunupObsSwash.append(datapointRunupObsSwash)
                self.datapointsRunupObsIncidentSwash.append(datapointRunupObsIncidentSwash)
                self.datapointsRunupObsInfragravitySwash.append(datapointRunupObsInfragravitySwash)
                self.datapointsRunupObsSwh.append(datapointRunupObsSwh)
                self.datapointsRunupObsPwp.append(datapointRunupObsPwp)
                self.datapointsRunupObsImpact.append(datapointRunupObsImpact)
                self.datapointsRunupObsBeachSlope.append(datapointRunupObsBeachSlope)
                

                

    def generateGraphs(self):
        graph_directory = self.GRAPH_DIRECTORY
        if not os.path.exists(graph_directory):
            os.makedirs(graph_directory)
        
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
        plt.savefig(graph_directory + 'closest_points.png', dpi=300)
        plt.close()
        
        img = mpimg.imread(self.backgroundMap)
        plotAxis = [self.backgroundAxis[0], self.backgroundAxis[1], self.backgroundAxis[3], self.backgroundAxis[2]]
        aspectRatio = (self.backgroundAxis[1] - self.backgroundAxis[0]) / (self.backgroundAxis[2] - self.backgroundAxis[3])
#         img = mpimg.imread('subsetFlipped.png', dpi=300)
#         img = mpimg.imread('NorthAtlanticBasin3.png', dpi=300)

        # Create a new colormap with alpha-blended colors
        def create_blended_cmap(cmap, alpha=0.5):
            # Get the colors from the original colormap
            colors = cmap(np.linspace(0, 1, 256))
            # Blend each color with white (alpha blending)
            white = np.array([1, 1, 1, 1])
            blended_colors = alpha * colors + (1 - alpha) * white
            # Ensure alpha channel is 1 for the colormap
            blended_colors[:, 3] = 1
            # Create a new colormap
            return mcolors.ListedColormap(blended_colors)
            
        if(len(self.mapWindTimes) > 0):
            vmin = 0
            vmax = 20
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            
            # Get the original colormap
            original_cmap = plt.cm.get_cmap('jet')
            
            
            # Create the blended colormap for the colorbar
            blended_cmap = create_blended_cmap(original_cmap, alpha=0.5)
            
            if(self.windType == "FORT"):
                windTriangulation = Triangulation(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, triangles=self.mapWindTriangles, mask=self.mapWindMaskedTriangles)
            
            for index in range(len(self.mapWindTimes)):
                fig, ax = plt.subplots()
                plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
                
                if(self.windType == "FORT"):
                    contourset = ax.tricontourf(windTriangulation, self.mapSpeeds[index], levelBoundaries, cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)
                elif(self.windType == "POST"):
                    contourset = ax.pcolormesh(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, self.mapSpeeds[index], shading='gouraud', cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)
                elif(self.windType == "GFS"):
                    contourset = ax.pcolormesh(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, self.mapSpeeds[index], shading='gouraud', cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)
                
                plt.axis(plotAxis)
                plt.title("Wind Speed")
                plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
                
                # Use the blended colormap for the colorbar
                plt.colorbar(
                    ScalarMappable(norm=contourset.norm, cmap=blended_cmap),  # Use blended_cmap here
                    ticks=range(vmin, vmax+5, 5),
                    boundaries=levelBoundaries,
                    values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                    label="Meters/Second",
                    ax=plt.gca()
                )
                
                plt.savefig(graph_directory + 'map_wind_' + str(index) + '.png', dpi=300)
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
            fig, ax = plt.subplots(figsize=(18,18))

            # Create the blended colormap for the colorbar
            blended_cmap = create_blended_cmap(original_cmap, alpha=0.5)

            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            if(self.windType == "FORT"):
                contourset = ax.tricontourf(windTriangulation, self.mapSpeeds[index], levelBoundaries, cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)
            else:
                contourset = ax.pcolormesh(self.mapWindPointsLongitudes, self.mapWindPointsLatitudes, swathWind, shading='gouraud', cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)

            plt.axis(plotAxis)
            plt.title("Wind Swath", fontsize=30)

            # Create the colorbar and set font properties
            cbar = plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=blended_cmap),
                ticks=range(vmin, vmax+5, 5),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                ax=plt.gca()
            )
            cbar.ax.tick_params(labelsize=28)  # Set colorbar tick label font size
            cbar.set_label("Meters/Second", fontsize=28)  # Set colorbar label font size

            # Set axis tick label font sizes
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)  # Corrected from duplicate xticks

            plt.savefig(graph_directory + 'map_wind_swath.png', dpi=300)
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
                plt.savefig(graph_directory + 'map_rain_' + str(index) + '.png', dpi=300)
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
            plt.savefig(graph_directory + 'map_rain_accumulation.png', dpi=300)
            plt.close()
            gc.collect()
        if(len(self.mapElevation) > 0):
            
            # Assuming this is part of a larger class with existing attributes
            # USGS_BEACH_PROFILE_FILE, graph_directory, plotAxis, img, aspectRatio are defined
            
            def create_blended_cmap(original_cmap, alpha=0.5):
                # Create a blended colormap with specified alpha
                colors = original_cmap(np.linspace(0, 1, 256))
                colors[:, -1] = alpha  # Set alpha for all colors
                return plt.cm.colors.ListedColormap(colors)

            vmin = -15
            vmax = 10
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            elevationTriangulation = Triangulation(
                self.mapElevationPointsLongitudes,
                self.mapElevationPointsLatitudes,
                triangles=self.mapElevationTriangles,
                mask=self.mapElevationMaskedTriangles
            )
        
            fig, ax = plt.subplots(figsize=(18, 18))
        
            # Get the original colormap
            original_cmap = plt.cm.get_cmap('jet')
        
            # Create the blended colormap for the colorbar
            blended_cmap = create_blended_cmap(original_cmap, alpha=0.5)
        
            # Plot background image and elevation triangulation
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.tripcolor(
                elevationTriangulation,
                self.mapElevation,
                shading='gouraud',
                cmap=original_cmap,
                vmin=vmin,
                vmax=vmax,
                zorder=1
            )
            ax.scatter(
                self.mapElevationPointsLongitudes,
                self.mapElevationPointsLatitudes,
                alpha=0.5,
                marker=".",
                s=15,
                zorder=4,
                color="purple"
            )
        
            # Query and plot transects from USGS_BEACH_PROFILE_FILE
            try:
                df = pd.read_csv(self.USGS_BEACH_PROFILE_FILE)
            except Exception as e:
                print(f"Error reading {self.USGS_BEACH_PROFILE_FILE}: {e}")
                return
        
            # Filter valid transects with all SL, DT, DC points
            valid_transects = []
            # Group by state, segment, profile
            grouped = df.groupby(['state', 'segment', 'profile'])
            for (state, segment, profile), group in grouped:
                group_valid = group[(group['lon'] != 999) & (group['lat'] != 999)]
                dc_data = group_valid[group_valid['feature_type'] == 'DC']
                dt_data = group_valid[group_valid['feature_type'] == 'DT']
                sl_data = group_valid[group_valid['feature_type'] == 'SL']
                # Check for exactly one SL, DT, DC and at least one point in plotAxis
                if (len(dc_data) == 1 and len(dt_data) == 1 and len(sl_data) == 1):
                    group_lons = group_valid['lon']
                    group_lats = group_valid['lat']
                    if any(
                        (group_lons.between(plotAxis[0], plotAxis[1])) &
                        (group_lats.between(plotAxis[2], plotAxis[3]))
                    ):
                        valid_transects.append((state, segment, profile))
                        ALL_DUNE_CREST_TRANSECTS.append(float(dc_data['z'].iloc[0]))
                        ALL_LONGITUDES_TRANSECTS.append(float(dc_data['lon'].iloc[0]))
                        ALL_LATITUDES_TRANSECTS.append(float(dc_data['lat'].iloc[0]))
                        ALL_SHORELINE_LONGITUDES_TRANSECTS.append(float(sl_data['lon'].iloc[0]))
                        ALL_SHORELINE_LATITUDES_TRANSECTS.append(float(sl_data['lat'].iloc[0]))
                        ALL_BEACH_SLOPES_TRANSECTS.append(float(sl_data['slope'].iloc[0]))
                        for twlccPoint in TWLCC_FORECAST_POINTS_IDENTIFIERS:
                            if state == twlccPoint[0] and segment == twlccPoint[1] and profile == twlccPoint[2]:
                                TWLCC_FORECAST_POINTS_LATITUDES.append(float(dc_data['lat'].iloc[0]))
                                TWLCC_FORECAST_POINTS_LONGITUDES.append(float(dc_data['lon'].iloc[0]))
                    else:
                        print(f"Transect {state}-{segment}-{profile} excluded: No points within plotAxis {plotAxis}")
                else:
                    print(f"Transect {state}-{segment}-{profile} excluded: Missing SL, DT, or DC (DC: {len(dc_data)}, DT: {len(dt_data)}, SL: {len(sl_data)})")
            print(f"Valid transects with SL, DT, DC: {valid_transects}")
            
            with open("usgs_dune_crest_coordinates.txt", "w") as f:
                for index in range(len(ALL_LONGITUDES_TRANSECTS)):
                    f.write(str(ALL_LATITUDES_TRANSECTS[index]) + "," +  str(ALL_LONGITUDES_TRANSECTS[index]) + "," + str(ALL_SHORELINE_LATITUDES_TRANSECTS[index]) + "," + str(ALL_SHORELINE_LONGITUDES_TRANSECTS[index]) + "," + str(ALL_BEACH_SLOPES_TRANSECTS[index]) + "\n")
            # Initialize transect lists
            MHWL_TRANSECTS = [None] * 5  # Shoreline (SL)
            DUNE_TOE_TRANSECTS = [None] * 5  # Dune Toe (DT)
            DUNE_CREST_TRANSECTS = [None] * 5  # Dune Crest (DC)
            BEACH_SLOPES_TRANSECTS = [None] * 5
        
            # Get transect numbers from assetLabels (using your modified logic)
            transect_numbers = []
            asset_lons = []
            asset_lats = []
            for assetIndex, assetLabel in enumerate(self.assetLabels):  # Limit to 5 transects
                if "m" == assetLabel[-1]:
                    if assetLabel[assetLabel.index(" ") + 1] == "0" and int(assetLabel[8:assetLabel.index(" ")]) <= 5:
                        try:
                            transect_num = int(assetLabel[assetLabel.index(" ") - 1])
                            transect_numbers.append(transect_num)
                            asset_lons.append(self.assetLongitudes[assetIndex])
                            asset_lats.append(self.assetLatitudes[assetIndex])
                        except (ValueError, IndexError):
                            print(f"Warning: Could not parse transect number from {assetLabel}")
                            continue
            print(f"Transect numbers from assetLabels: {transect_numbers}")
        
            # Find closest transects
            closest_transects = []
            for i, (asset_lon, asset_lat, transect_num) in enumerate(zip(asset_lons, asset_lats, transect_numbers)):
                # Filter transects with matching profile and valid SL, DT, DC points
                candidates = [(s, seg, p) for (s, seg, p) in valid_transects]
                if not candidates:
                    print(f"No valid transect for profile {transect_num}")
                    continue
        
                # Find closest transect by minimum distance
                min_distance = float('inf')
                closest_transect = None
                for (state, segment, profile) in candidates:
                    group = df[(df['state'] == state) & (df['segment'] == segment) & (df['profile'] == profile) & (df['lon'] != 999) & (df['lat'] != 999)]
                    distances = np.sqrt(
                        (group['lon'] - asset_lon)**2 +
                        (group['lat'] - asset_lat)**2
                    )
                    if distances.min() < min_distance:
                        min_distance = distances.min()
                        closest_transect = (state, segment, profile)
        
                if min_distance > 0.1:  # Threshold to avoid far matches
                    print(f"No close match for transect {transect_num} (min distance: {min_distance})")
                    continue
        
                closest_transects.append(closest_transect)
        
                # Save z values for DC, DT, SL
                group = df[(df['state'] == closest_transect[0]) & (df['segment'] == closest_transect[1]) & (df['profile'] == closest_transect[2])]
                dc_data = group[group['feature_type'] == 'DC']
                dt_data = group[group['feature_type'] == 'DT']
                sl_data = group[group['feature_type'] == 'SL']
                DUNE_CREST_TRANSECTS[i] = float(dc_data['z'].iloc[0])
                DUNE_TOE_TRANSECTS[i] = float(dt_data['z'].iloc[0])
                MHWL_TRANSECTS[i] = float(sl_data['z'].iloc[0])
                BEACH_SLOPES_TRANSECTS[i] = float(sl_data['slope'].iloc[0])
        
            print(f"Closest transects: {closest_transects}")
        
            # Plot asset points
            for assetIndex, assetLabel in enumerate(self.assetLabels):
                if "m" == assetLabel[-1]:
                    if "Waves" in assetLabel:
                        ax.scatter(
                            self.assetLongitudes[assetIndex],
                            self.assetLatitudes[assetIndex],
                            zorder=3,
                            alpha=0.7,
                            marker="x",
                            s=60,
                            color="black"
                        )
                        ax.annotate(
                            assetLabel[:assetLabel.index(" ")],
                            (self.assetLongitudes[assetIndex], self.assetLatitudes[assetIndex]),
                            fontsize=22
                        )
                    else:
                        ax.scatter(
                            self.assetLongitudes[assetIndex],
                            self.assetLatitudes[assetIndex],
                            zorder=3,
                            alpha=0.7,
                            marker=".",
                            s=30,
                            color="red"
                        )
                        
            # Plot all valid transects
            for (state, segment, profile) in valid_transects:
                group = df[(df['state'] == state) & (df['segment'] == segment) & (df['profile'] == profile) & (df['lon'] != 999) & (df['lat'] != 999)]
                dc_data = group[group['feature_type'] == 'DC']
                dt_data = group[group['feature_type'] == 'DT']
                sl_data = group[group['feature_type'] == 'SL']
        
                # Ensure all three points exist
                if len(dc_data) != 1 or len(dt_data) != 1 or len(sl_data) != 1:
                    continue
        
                # Collect points in order: DC -> DT -> SL
                points = [
                    (dc_data['lon'].iloc[0], dc_data['lat'].iloc[0]),
                    (dt_data['lon'].iloc[0], dt_data['lat'].iloc[0]),
                    (sl_data['lon'].iloc[0], sl_data['lat'].iloc[0])
                ]
                lons, lats = zip(*points)
        
                # Plot transect line
                is_highlighted = (state, segment, profile) in closest_transects
                line_color = 'k' if is_highlighted else 'gray'
                line_width = 2.5 if is_highlighted else 1.5
                line_alpha = 0.9 if is_highlighted else 0.5
                ax.plot(lons, lats, color=line_color, linewidth=line_width, alpha=line_alpha, zorder=3)
        
                # Add arrow at SL, extending slightly beyond
                x1, y1 = points[-2]  # DT
                x2, y2 = points[-1]  # SL
                dx = x2 - x1
                dy = y2 - y1
                arrow_length = 2.0  # Extend 2x the DT -> SL segment
                segment_length = np.sqrt(dx**2 + dy**2)
                if segment_length > 0:
                    dx_scaled = dx / segment_length * 0.001  # Base length in degrees
                    dy_scaled = dy / segment_length * 0.001
                    ax.arrow(
                        x2, y2,  # Start at SL
                        dx_scaled * arrow_length, dy_scaled * arrow_length,  # Extend beyond SL
                        color=line_color,
                        alpha=line_alpha,
                        width=0.0001,
                        head_width=0.0003,
                        head_length=0.0003,
                        zorder=3
                    )
        
                        
            for twlccIndex in range(len(TWLCC_FORECAST_POINTS_IDENTIFIERS)):
                ax.scatter(
                    TWLCC_FORECAST_POINTS_LONGITUDES[twlccIndex],
                    TWLCC_FORECAST_POINTS_LATITUDES[twlccIndex],
                    zorder=3,
                    alpha=0.7,
                    marker="v",
                    s=30,
                    color="green"
                )
                ax.annotate(
                    "TWL&CC Site",
                    (TWLCC_FORECAST_POINTS_LONGITUDES[twlccIndex], TWLCC_FORECAST_POINTS_LATITUDES[twlccIndex]),
                    fontsize=16
                )
        
            plt.axis(plotAxis)
            plt.title("Elevation Map", fontsize=30)
        
            # Create the colorbar and set font properties
            cbar = plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=blended_cmap),
                ticks=range(vmin, vmax + 5, 10),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                ax=plt.gca()
            )
            cbar.ax.tick_params(labelsize=28)
            cbar.set_label("Meters", fontsize=28)
        
            # Set axis tick label font sizes
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)
        
            plt.savefig(os.path.join(graph_directory, 'map_elevation.png'), dpi=300)
            plt.close()
            gc.collect()
        
            # Save transect data
            with open(os.path.join(graph_directory, 'transect_data.json'), 'w') as f:
                json.dump({
                    'MHWL_TRANSECTS': MHWL_TRANSECTS,
                    'DUNE_TOE_TRANSECTS': DUNE_TOE_TRANSECTS,
                    'DUNE_CREST_TRANSECTS': DUNE_CREST_TRANSECTS
                }, f, indent=4)
#             vmin = -15
#             vmax = 10
#             levels = 100
#             levelBoundaries = np.linspace(vmin, vmax, levels + 1)
#             elevationTriangulation = Triangulation(self.mapElevationPointsLongitudes, self.mapElevationPointsLatitudes, triangles=self.mapElevationTriangles, mask=self.mapElevationMaskedTriangles)
#     
#             fig, ax = plt.subplots(figsize=(18,18))
#     
#             # Get the original colormap
#             original_cmap = plt.cm.get_cmap('jet')
#     
#             # Create the blended colormap for the colorbar
#             blended_cmap = create_blended_cmap(original_cmap, alpha=0.5)
#     
#             plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
#             contourset = ax.tripcolor(elevationTriangulation, self.mapElevation, shading='gouraud', cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)
#             ax.scatter(self.mapElevationPointsLongitudes, self.mapElevationPointsLatitudes, alpha=0.5, marker=".", s=15, zorder=4, color="purple")  # Increased s=5 to s=15
#     
#             legendLabelInitialized = False
#             transectLabelInitialized = False
#             for assetIndex, assetLabel in enumerate(self.assetLabels):
#                 if("m" == assetLabel[-1]):
#                     if("Waves" in assetLabel):
#                         ax.scatter(self.assetLongitudes[assetIndex], self.assetLatitudes[assetIndex], zorder=3, alpha=0.7, marker="x", s=60, color="black", label="7m depth" if not legendLabelInitialized else None)  # Increased s=20 to s=60
#                         legendLabelInitialized = True
#                         ax.annotate(assetLabel[:assetLabel.index(" ")], (self.assetLongitudes[assetIndex], self.assetLatitudes[assetIndex]), fontsize=22)  # Set annotation fontsize
#                     else:
#                         ax.scatter(self.assetLongitudes[assetIndex], self.assetLatitudes[assetIndex], zorder=3, alpha=0.7, marker=".", s=30, color="black", label="Transects" if not transectLabelInitialized else None)  # Increased s=10 to s=30
#                         transectLabelInitialized = True
#     
#             plt.axis(plotAxis)
#             plt.title("Elevation Map", fontsize=30)
#     
#             # Create the colorbar and set font properties
#             cbar = plt.colorbar(
#                 ScalarMappable(norm=contourset.norm, cmap=blended_cmap),
#                 ticks=range(vmin, vmax+5, 10),
#                 boundaries=levelBoundaries,
#                 values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
#                 ax=plt.gca()
#             )
#             cbar.ax.tick_params(labelsize=28)  # Set colorbar tick label font size
#             cbar.set_label("Meters", fontsize=28)  # Set colorbar label font size
#     
#             # Set axis tick label font sizes
#             plt.xticks(fontsize=22)
#             plt.yticks(fontsize=22)
#     
#             # Set legend font size
#             if ax.get_legend():
#                 ax.legend(loc="upper left", fontsize=22)
#     
#             plt.savefig(graph_directory + 'map_elevation.png', dpi=300)
#             plt.close()
#             gc.collect()




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
                plt.savefig(graph_directory + 'map_eta_' + str(index) + '.png', dpi=300)
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
            plt.savefig(graph_directory + 'map_eta_swath.png', dpi=300)
            plt.close()
            gc.collect()
        if(len(self.mapWaterTimes) > 0):
            vmin = -1
            vminSwath = 0.6
            vmax = 1
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            levelBoundariesSwath = np.linspace(vminSwath, vmax, levels + 1)
        
            # Get the original colormap
            original_cmap = plt.cm.get_cmap('jet')
        
            # Create blended colormaps for the colorbars
            blended_cmap_elevation = create_blended_cmap(original_cmap, alpha=0.6)  # For water elevation plots
            blended_cmap_swath = create_blended_cmap(original_cmap, alpha=0.5)      # For swath plot
        
            if(not BYPASS_WATER_MAP_PLOTS):
                for index in range(len(self.mapWaterTimes)):
    #             for index in range(0):
                    fig, ax = plt.subplots(figsize=(18,18))
                    plt.imshow(img, extent=self.backgroundAxis, alpha=0.6, aspect=aspectRatio, zorder=2)
                    currentMaskedTriangles = self.mapWaterMaskedTriangles.copy()
                    for triangleIndex, triangle in enumerate(self.mapWaterTriangles):
                        for pointIndex in triangle:
                            water = self.mapWaters[index][pointIndex]
                            if(water == -99999.0):
                                currentMaskedTriangles[triangleIndex] = True
                                break
                    waterTriangulation = Triangulation(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, triangles=self.mapWaterTriangles, mask=currentMaskedTriangles)
            
                    contourset = ax.tripcolor(waterTriangulation, self.mapWaters[index], shading='gouraud', cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)
            
                    # Plot points
                    if(self.meshExists):
                        ax.scatter(self.assetLongitudes, self.assetLatitudes, label="Assets", zorder=3, alpha=0.7, marker=".", s=40, color="black")
            
                    if(self.obsExists):
                        ax.scatter(self.tideLongitudes, self.tideLatitudes, label="Obs", zorder=3, alpha=0.7, marker=".", s=40, color="black")
                        for tideIndex in range(len(self.tideLabels)):
                            ax.annotate(self.tideLabels[tideIndex], (self.tideLongitudes[tideIndex], self.tideLatitudes[tideIndex]))
            
                    if(self.runupExists):
                        for runupIndex, runupLabel in enumerate(self.runupLabels):
                            self.plotExtendedLines(ax, runupIndex, index, runupLabel)
            
                    plt.axis(plotAxis)
                    plt.title(self.titlePrefix + "Water Elevation")
                    plt.xlabel(datetime.fromtimestamp(self.mapWaterTimes[index], timezone.utc))
            
                    # Use the blended colormap for the colorbar (alpha=0.6)
                    plt.colorbar(
                        ScalarMappable(norm=contourset.norm, cmap=blended_cmap_elevation),
                        ticks=range(vmin, vmax+5, 2),
                        boundaries=levelBoundaries,
                        values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                        label="Meters",
                        ax=plt.gca()
                    )
                    # Set axis tick label font sizes
                    plt.xticks(fontsize=22)
                    plt.yticks(fontsize=22)  # Corrected from duplicate xticks
            
                    plt.savefig(graph_directory + 'map_water_' + str(index) + '.png', dpi=300)
                    plt.close()
                    gc.collect()
        
            # Create GIF
                with imageio.get_writer(graph_directory + 'water.gif', mode='I') as writer:
                    for index in range(len(self.mapWaterTimes)):
                        filename = "map_water_" + str(index) + ".png"
                        image = imageio.imread(graph_directory + filename)
                        writer.append_data(image)
                    for index in range(len(self.mapWaterTimes)):
                        filename = "map_water_" + str(index) + ".png"
                        os.remove(graph_directory + filename)
        
            # Water Swath Plot
            swathWaters = np.max(self.mapWaters, axis=0)
            print(len(swathWaters), len(self.mapWaterMaskedTriangles))
            for index, triangle in enumerate(self.mapWaterTriangles):
                for pointIndex in triangle:
                    water = swathWaters[pointIndex]
                    if(water == -99999.0):
                        self.mapWaterMaskedTriangles[index] = True
                        break
            waterTriangulation = Triangulation(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, triangles=self.mapWaterTriangles, mask=self.mapWaterMaskedTriangles)
        
            fig, ax = plt.subplots(figsize=(18,18))
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.tripcolor(waterTriangulation, swathWaters, shading='gouraud', cmap=original_cmap, vmin=vminSwath, vmax=vmax, zorder=1)
        
            for waterIndex, tideLabel in enumerate(self.tideLabels):
                if("Waves" in tideLabel):
                    ax.scatter(self.waterLongitudes[waterIndex], self.waterLatitudes[waterIndex])
                    ax.annotate(tideLabel, (self.waterLongitudes[waterIndex], self.waterLatitudes[waterIndex]))
        
            plt.axis(plotAxis)
            plt.title(self.titlePrefix + "Water Swath", fontsize=30)
        
            # Use the blended colormap for the colorbar (alpha=0.5)
            cbar = plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=blended_cmap_swath),
                ticks=np.arange(vminSwath, vmax + 0.2, 0.2),
                boundaries=levelBoundariesSwath,
                values=(levelBoundariesSwath[:-1] + levelBoundariesSwath[1:]) / 2,
                ax=plt.gca()
            )
            cbar.ax.tick_params(labelsize=28)  # Set colorbar tick label font size
            cbar.set_label("Meters", fontsize=28)  # Set colorbar label font size

    

            # Set axis tick label font sizes
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)  # Corrected from duplicate xticks
            plt.savefig(graph_directory + 'map_water_swath.png', dpi=300)
            plt.close()
            gc.collect()
        if(len(self.mapWaveTimes) > 0):
            vmin = 0
            vmax = math.ceil(self.maxSWH)
            vmax = 17
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
        
            # Get the original colormap
            original_cmap = plt.cm.get_cmap('jet')
        
            # Create blended colormap for the colorbars
            blended_cmap = create_blended_cmap(original_cmap, alpha=0.5)  # For both wave height and swath plots
        
#             for index in range(len(self.mapWaveTimes)):
#                 fig, ax = plt.subplots()
#                 currentMaskedTriangles = self.mapWaveMaskedTriangles.copy()
#                 for triangleIndex, triangle in enumerate(self.mapWaveTriangles):
#                     for pointIndex in triangle:
#                         swh = self.mapSWH[index][pointIndex]
#                         if(swh == -99999.0):
#                             currentMaskedTriangles[triangleIndex] = True
#                             break
#                 waveTriangulation = Triangulation(self.mapWavePointsLongitudes, self.mapWavePointsLatitudes, triangles=self.mapWaveTriangles, mask=currentMaskedTriangles)
#         
#                 plt.imshow(img, extent=self.backgroundAxis, alpha=0.5, aspect=aspectRatio, zorder=2)
#                 contourset = ax.tricontourf(waveTriangulation, self.mapSWH[index], levelBoundaries, cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1)
#         
#                 plt.axis(plotAxis)
#                 plt.title("Significant Wave Height")
#                 plt.xlabel(datetime.fromtimestamp(int(self.mapWaveTimes[index]), timezone.utc))
#         
#                 # Use the blended colormap for the colorbar
#                 plt.colorbar(
#                     ScalarMappable(norm=contourset.norm, cmap=blended_cmap),
#                     ticks=range(vmin, vmax+5, 5),
#                     boundaries=levelBoundaries,
#                     values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
#                     label="Meters",
#                     ax=plt.gca()
#                 )
#         
#                 plt.savefig(graph_directory + 'map_swh_' + str(index) + '.png', dpi=300)
#                 plt.close()
#                 gc.collect()
#         
#             # Create GIF
#             with imageio.get_writer(graph_directory + 'wave.gif', mode='I') as writer:
#                 for index in range(len(self.mapWaveTimes)):
#                     filename = "map_swh_" + str(index) + ".png"
#                     image = imageio.imread(graph_directory + filename)
#                     writer.append_data(image)
#                 for index in range(len(self.mapWaveTimes)):
#                     filename = "map_swh_" + str(index) + ".png"
#                     os.remove(graph_directory + filename)
        
            # Wave Swath Plot
            swathSWH = np.max(self.mapSWH, axis=0)
            for index, triangle in enumerate(self.mapWaveTriangles):
                for pointIndex in triangle:
                    swh = swathSWH[pointIndex]
                    if(swh == -99999.0):
                        self.mapWaveMaskedTriangles[index] = True
                        break
            waveTriangulation = Triangulation(self.mapWavePointsLongitudes, self.mapWavePointsLatitudes, triangles=self.mapWaveTriangles, mask=self.mapWaveMaskedTriangles)
        
            fig, ax = plt.subplots(figsize=(18,18))
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.tricontourf(waveTriangulation, swathSWH, levelBoundaries, cmap=original_cmap, vmin=vmin, vmax=vmax, zorder=1, alpha=0.5)
            ax.tricontour(waveTriangulation, swathSWH, levels=np.arange(vmin, vmax + 1, 0.5), colors='black', linewidths=3, zorder=1)
            ax.scatter(self.waveLongitudes, self.waveLatitudes, label="Datapoints")
            if(self.tideExists):
                ax.scatter(self.tideLongitudes, self.tideLatitudes, label="Tide", zorder=3)
        
            plt.axis(plotAxis)
            plt.title("Significant Wave Height Swath", fontsize=28)
        
            # Use the blended colormap for the colorbar
            # Use the blended colormap for the colorbar (alpha=0.5)
            cbar = plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=blended_cmap),
                ticks=range(vmin, vmax+5, 1),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                ax=plt.gca()
            )
            cbar.ax.tick_params(labelsize=28)  # Set colorbar tick label font size
            cbar.set_label("Meters", fontsize=28)  # Set colorbar label font size
        
            plt.xticks(fontsize=22)
            plt.yticks(fontsize=22)  # Corrected from duplicate xticks
            
            plt.savefig(graph_directory + 'map_swh_swath.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_wind_speed.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_wind_direction.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_rain.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_rain_accumulation.png', dpi=300)
                plt.close()
        for index in range(numberOfWaterDatapoints):
            if(BYPASS_WATER_TIMESERIES_PLOTS):
                break
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
                plt.savefig(graph_directory + stationName + '_water.png', dpi=300)
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
                    plt.savefig(graph_directory + stationName + '_station_water.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_eta.png', dpi=300)
                plt.close()
        for index in range(numberOfWaveDatapoints):
            if(self.wavesExists):
                if(len(self.datapointsSWH[index]) > 0):
                    fig, ax = plt.subplots(figsize=(16,9))
                    ax.scatter(self.waveTimes, self.datapointsSWH[index], marker=".", label=r"$H_s$")
                    stationTitle = str(round(max(self.datapointsSWH[index]), 2))
                    if(self.buoyExists):
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsSWH[index], label="Obs")
                        stationTitle = str(round(max(self.datapointsSWH[index]), 2)) + ", " + str(round(max(self.buoyDatapointsSWH[index]), 2)) 
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + r" Significant Wave Height (Max $H_s$, Obs: " + stationTitle + " m)")
                    plt.xlabel("Date")                    
                    ax.format_xdata = mdates.DateFormatter('%d')
                    plt.ylabel("SWH (meters)")
                    plt.savefig(graph_directory + stationName + '_wave_swh.png', dpi=300)
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
                    plt.savefig(graph_directory + stationName + '_wave_mwd.png', dpi=300)
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
                    plt.savefig(graph_directory + stationName + '_wave_mwp.png', dpi=300)
                    plt.close()
                if(len(self.datapointsPWP[index]) > 0):
                    fig, ax = plt.subplots(figsize=(16,9))
                    ax.scatter(self.waveTimes, self.datapointsPWP[index], marker=".", label=r"$T_p$")
                    stationTitle = str(round(max(self.datapointsPWP[index]), 2))
                    if(self.buoyExists):
                        ax.scatter(self.buoyDatapointsTimes[index], self.buoyDatapointsPWP[index], label="Obs")
                        stationTitle = str(round(max(self.datapointsPWP[index]), 2)) + ", " + str(round(max(self.buoyDatapointsPWP[index]), 2)) 
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + r" Peak Wave Period (Max $T_p$, Obs: " + stationTitle + " sec)")
                    plt.xlabel("Date")
                    ax.format_xdata = mdates.DateFormatter('%d')
                    plt.ylabel("PWP (seconds)")
                    plt.savefig(graph_directory + stationName + '_wave_pwp.png', dpi=300)
                    plt.close()
                if(len(self.datapointsRADMag[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADMag[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station radiation stress magnitude", fontsize=24)
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad Stress Magitude (1/m^2s^2)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_mag.png', dpi=300)
                    plt.close()
                if(len(self.datapointsRADDir[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADDir[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.buoyLabels[index]
                    plt.title(stationName + " station radiation stress direction", fontsize=24)
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad stress direction (degrees)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_dir.png', dpi=300)
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
    
            ax_swh.legend(loc="lower right", ncol=2, prop={'size': 11})
            ax_swh.set_title("Significant Wave Height Across All Stations")
            ax_swh.format_xdata = mdates.DateFormatter('%d')
            ax_swh.set_ylabel("SWH (meters)")
            ax_swh.set_xlabel("Date")
            plt.tight_layout()
            plt.savefig(graph_directory + 'all_stations_wave_swh.png', dpi=300)
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
            plt.savefig(graph_directory + 'all_stations_wave_mwp.png', dpi=300)
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
            plt.savefig(graph_directory + 'all_stations_wave_pwp.png', dpi=300)
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
            fig.savefig(graph_directory + 'all_stations_wave_mwp_pwp.png', dpi=300)
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
#             plt.savefig(graph_directory + 'all_stations_water.png', dpi=300)
#             plt.close()

        
# Graph multipanel all stations water

        # --- Multipanel Water Plot ---
        if(numberOfWaterDatapoints > 0 and GRAPH_MULTIPANEL):  # Removed 'and False' to enable the plot
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
                    all_elevations.extend([x for x in self.datapointsWaters[index] if not np.isnan(x)])
                    if self.stillwaterExists:
                        all_elevations.extend([x for x in self.datapointsStillwaters[index] if not np.isnan(x)])
                    if self.tidewaterExists:
                        all_elevations.extend([x for x in self.datapointsTidewaters[index] if not np.isnan(x)])
                    if self.tideExists:
                        all_elevations.extend([x for x in self.tideDatapointsWaters[index] if not np.isnan(x)])
            
            global_min = min(all_elevations) if all_elevations else -1.0
            global_max = max(all_elevations) if all_elevations else 1.0
            y_padding = (global_max - global_min) * 0.1
            y_min = global_min - y_padding
            y_max = global_max + y_padding
            
            # Plot data for each station
            for index in range(numberOfWaterDatapoints):
                ax = axes[index]
                if len(self.datapointsWaters) > 0:
                    # Compute max values for title
                    max_eta = round(np.nanmax(self.datapointsWaters[index]), 2) if len(self.datapointsWaters[index]) > 0 else "-"
                    max_obs = round(np.nanmax(self.tideDatapointsWaters[index]), 2) if self.tideExists and len(self.tideDatapointsWaters[index]) > 0 else "-"
                    
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
                    ax.format_xdata = mdates.DateFormatter('%d')
                    
                    # Set title and labels
                    stationName = self.tideLabels[index]
                    ax.set_title(f"{self.titlePrefix}{stationName} Water Level (Max η, Obs: {max_eta}, {max_obs} m)", fontsize=16)
                    ax.set_ylabel("Elevation (meters)", fontsize=12)
                    
                    # Set shared y-axis limits
                    ax.set_ylim(y_min, y_max)
                
                if index == numberOfWaterDatapoints - 1:
                    ax.set_xlabel("Date", fontsize=12)
            
            # Save the figure
            plt.savefig(graph_directory + 'all_stations_water.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # --- Multipanel Wind Plots ---
        if(numberOfWindDatapoints > 0 and GRAPH_MULTIPANEL):  # Removed 'and False' to ensure consistency
            all_times = []
            for index in range(numberOfWindDatapoints):
                if len(self.datapointsSpeeds) > 0 or len(self.datapointsDirections) > 0:
                    all_times.extend(self.windTimes)
                    if self.obsExists:
                        all_times.extend(self.obsDatapointsTimes[index])
            
            x_min = min(all_times) if all_times else self.windStartDate
            x_max = max(all_times) if all_times else self.windStartDate
            if x_min != x_max:
                x_padding = (x_max - x_min) * 0.05
                x_min -= x_padding
                x_max += x_padding
            
            # --- Wind Speed Figure ---
            all_speeds = []
            for index in range(numberOfWindDatapoints):
                if len(self.datapointsSpeeds) > 0:
                    all_speeds.extend([x for x in self.datapointsSpeeds[index] if not np.isnan(x)])
                    if self.obsExists:
                        all_speeds.extend([x for x in self.obsDatapointsSpeeds[index] if not np.isnan(x)])
            
            speed_min = min(all_speeds) if all_speeds else 0.0
            speed_max = max(all_speeds) if all_speeds else 50.0
            speed_padding = (speed_max - speed_min) * 0.1 if speed_max != speed_min else 1.0
            speed_y_min = max(0.0, speed_min - speed_padding)
            speed_y_max = speed_max + speed_padding
            
            fig_speed, axes_speed = plt.subplots(numberOfWindDatapoints, 1, figsize=(16, 4 * numberOfWindDatapoints), sharex=True, constrained_layout=True)
            if numberOfWindDatapoints == 1:
                axes_speed = [axes_speed]
            else:
                axes_speed = axes_speed.flatten()
            
            # Plot wind speed data
            for index in range(numberOfWindDatapoints):
                ax = axes_speed[index]
                if len(self.datapointsSpeeds) > 0:
                    # Compute max values for title
                    max_gfs = round(np.nanmax(self.datapointsSpeeds[index]), 2) if len(self.datapointsSpeeds[index]) > 0 else "-"
                    max_obs = round(np.nanmax(self.obsDatapointsSpeeds[index]), 2) if self.obsExists and len(self.obsDatapointsSpeeds[index]) > 0 else "-"
                    
                    ax.scatter(self.windTimes, self.datapointsSpeeds[index], marker=".", label="GFS")
                    if self.obsExists:
                        ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsSpeeds[index], marker=".", label="Obs")
                    
                    ax.legend(loc="lower right")
                    ax.format_xdata = mdates.DateFormatter('%d')
                    
                    stationName = self.obsLabels[index]
                    ax.set_title(f"{self.titlePrefix}{stationName} Wind Speed (Max GFS, Obs: {max_gfs}, {max_obs} m/s)", fontsize=16)
                    ax.set_ylabel("Wind speed (m/s)", fontsize=12)
                    
                    ax.set_ylim(speed_y_min, speed_y_max)
                    ax.set_xlim(x_min, x_max)
                
                if index == numberOfWindDatapoints - 1:
                    ax.set_xlabel("Date", fontsize=12)
            
            plt.savefig(graph_directory + 'all_stations_wind_speed.png', dpi=300, bbox_inches='tight')
            plt.close(fig_speed)
            
            # --- Wind Direction Figure ---
            all_directions = []
            for index in range(numberOfWindDatapoints):
                if len(self.datapointsDirections) > 0:
                    all_directions.extend([x for x in self.datapointsDirections[index] if not np.isnan(x)])
                    if self.obsExists:
                        all_directions.extend([x for x in self.obsDatapointsDirections[index] if not np.isnan(x)])
            
            direction_min = 0
            direction_max = 360
            direction_padding = (direction_max - direction_min) * 0.1
            direction_y_min = max(0.0, direction_min - direction_padding)
            direction_y_max = min(360.0, direction_max + direction_padding)
            
            fig_direction, axes_direction = plt.subplots(numberOfWindDatapoints, 1, figsize=(16, 4 * numberOfWindDatapoints), sharex=True, constrained_layout=True)
            if numberOfWaterDatapoints == 1:
                axes_direction = [axes_direction]
            else:
                axes_direction = axes_direction.flatten()
            
            # Plot wind direction data
            for index in range(numberOfWindDatapoints):
                ax = axes_direction[index]
                if len(self.datapointsDirections) > 0:
                    ax.scatter(self.windTimes, self.datapointsDirections[index], marker=".", label="GFS")
                    if self.obsExists:
                        ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsDirections[index], marker=".", label="Obs")
                    
                    ax.legend(loc="lower right")
                    ax.format_xdata = mdates.DateFormatter('%d')
                    
                    stationName = self.obsLabels[index]
                    ax.set_title(f"{self.titlePrefix}{stationName} Wind Direction", fontsize=16)
                    ax.set_ylabel("Wind direction (degrees)", fontsize=12)
                    
                    ax.set_ylim(direction_y_min, direction_y_max)
                    ax.set_xlim(x_min, x_max)
                
                if index == numberOfWindDatapoints - 1:
                    ax.set_xlabel("Date", fontsize=12)
            
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
                plt.savefig(graph_directory + stationName + '_runup_distance.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_runup.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_deepwater_swh.png', dpi=300)
                plt.close()
                
#                 print("runup obs times: ", self.datapointsSetupHolmanHigh[index][0:20])
#                 quit()
#                 Graph setup
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
#                 ax.plot(self.runupTimes, self.datapointsSetupHolmanHigh[index], label="Holman High Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSetupHolmanMid[index], label="Holman Mid Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSetupHolmanLow[index], label="Holman Low Tide ξ")
                ax.plot(self.runupTimes, self.datapointsSetupStockdon[index], label=r"Stockdon $\langle\eta\rangle$")
#                 ax.plot(self.runupTimes, self.datapointsSetupAdcirc[index], label="ADCIRC+SWAN setup+storm surge")
                ax.plot(self.runupTimes, self.datapointsSetupStockdonLow[index], label=r"SWAN $\eta_{setup}$")
                
                
                ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsSwashHolmanInfragravity[index], label=r"TWL&CC $\langle \eta \rangle$")
#                 ax.plot(self.runupTimes, self.datapointsRunupHolmanHigh[index], label="ADCIRC+SWAN storm surge")


                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                stationName = self.runupLabels[index]
                maxSetup = str(round(max(self.datapointsSetupStockdonLow[index]), 2)) + ", " + str(round(max(self.datapointsSetupStockdon[index]), 2))
                plt.title(self.titlePrefix + stationName[0:stationName.index(" ")] + " Setup (Max SWAN, Stockdon: " + maxSetup + " m)", fontsize=24)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("Setup (meters)")
                plt.xlabel("Date")
                plt.savefig(graph_directory + stationName + '_setup.png', dpi=300)
                plt.close()
                
#                 Graph swash
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanHigh[index], label="Holman High Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanMid[index], label="Holman Mid Tide ξ")
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanLow[index], label="Holman Low Tide ξ")
                datapointsSwashStockdon = np.sqrt((np.array(self.datapointsSwashStockdonIncident[index])**2 + np.array(self.datapointsSwashStockdonInfragravity[index])**2))
                ax.plot(self.runupTimes, datapointsSwashStockdon, color = "green", label=r"Stockdon Swash $\sqrt{S_{inc}^2 + S_{ig}^2}$")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonIncident[index], color = "blue", label="Stockdon Incident βf√(HₒLₒ)")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonInfragravity[index], color = "orange", label="Stockdon Infragravity √(HₒLₒ)")
                
                ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsSwash[index], linestyle="--", color = "green", label=r"TWL&CC Swash")
                ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsIncidentSwash[index], linestyle="--", color = "blue", label=r"TWL&CC Incident Swash")
                ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsInfragravitySwash[index], linestyle="--", color = "orange", label=r"TWL&CC Infragravity Swash")
#                 ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label="Stockdon Low")
                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxSwash = str(round(max(datapointsSwashStockdon), 2)) + ", " + str(round(max(self.datapointsRunupObsSwash[index]), 2))
                plt.title(self.titlePrefix + stationName[0:stationName.index(" ")] + r" Swash (Max $\sqrt{S_{inc}^2 + S_{ig}^2}$, TWL&CC): " + maxSwash, fontsize=24)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("Swash (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_swash.png', dpi=300)
                plt.close()
                        
#                 Graph incident swash
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsRunup[index], label="runup")
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanIncident[index], label="Holman Incident ξ")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonIncident[index], label="Stockdon Incident βf√(HₒLₒ)")
                ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsIncidentSwash[index], label=r"TWL&CC Incident")
#                 ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label="Stockdon Low")
                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxIncidentSwash = str(round(max(self.datapointsSwashStockdonIncident[index]), 2))
                plt.title(self.titlePrefix + stationName[0:stationName.index(" ")] + " station incident (<3min) swash max: " + maxIncidentSwash, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("swash (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_incident_swash.png', dpi=300)
                plt.close()
                
#                 Graph infragravity swash
                fig, ax = plt.subplots(figsize=(16,9))
#                 ax.plot(self.runupTimes, self.datapointsSwashHolmanInfragravity[index], label="Holman Infragravity ξ")
                ax.plot(self.runupTimes, self.datapointsSwashStockdonInfragravity[index], label="Stockdon Infragravity √(HₒLₒ)")
                ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsInfragravitySwash[index], label=r"TWL&CC Infragravity")
#                 ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label="Stockdon Low")
                ax.legend(loc="upper left")
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                stationName = self.runupLabels[index]
                maxInfragravitySwash = str(round(max(self.datapointsSwashStockdonInfragravity[index]), 2))
                plt.title(self.titlePrefix + stationName[0:stationName.index(" ")] + " station infragravity (>3 min) swash max: " + maxInfragravitySwash, fontsize=18)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("swash (meters)", fontsize=14)
                plt.savefig(graph_directory + stationName + '_infragravity_swash.png', dpi=300)
                plt.close()
            
                
#                 if(len(self.datapointsWaters) > 0 and GRAPH_SWASH):
#                     # Assuming self.findMatchingIndices is defined as per your earlier request
#                     datapointsWaterRunupIndices = self.findMatchingIndices(self.tideLabels, self.runupLabels[index][0:9])
#                     for datapointsWaterRunupIndex in datapointsWaterRunupIndices:
#                         fig, ax = plt.subplots(figsize=(16, 9))
#                 
#                         # Plot the water elevation time series
#                         ax.plot(self.waterTimes, self.datapointsWaters[datapointsWaterRunupIndex], label=r"$\eta$", color='blue', linewidth=2)
#                 
#                         # Calculate total swash: sqrt(S_incident^2 + S_infragravity^2)
#                         total_swash = np.sqrt(np.array(self.datapointsSwashStockdonIncident[index])**2 + 
#                                               np.array(self.datapointsSwashStockdonInfragravity[index])**2)
#                 
#                         # Define the upper and lower bounds for the swash area
#                         lower_bound = self.datapointsWaters[datapointsWaterRunupIndex] - 0.5 * total_swash
#                         upper_bound = self.datapointsWaters[datapointsWaterRunupIndex] + 0.5 * total_swash
#                         upper_bound_1_1 = 1.1 * upper_bound  # New 1.1 * upper_bound line
#                 
#                         # Fill the area between lower_bound and upper_bound_1_1 to highlight swash extent
#                         ax.fill_between(self.waterTimes, lower_bound, upper_bound_1_1, color='lightblue', alpha=0.4, label="Swash Extent")
#                 
#                         # Add dotted lines for original and new extents
#                         ax.plot(self.waterTimes, upper_bound, '--', color='red', label=r"$\frac{S}{2}$", linewidth=1.5)
#                         ax.plot(self.waterTimes, lower_bound, '--', color='green', label=r"$-\frac{S}{2}$", linewidth=1.5)
#                         ax.plot(self.waterTimes, upper_bound_1_1, '--', color='purple', label=r"$1.1\frac{S}{2}$", linewidth=1.5)  # New 1.1 * S/2 line
#                 
#                         # Calculate the maximum elevation including the swash
#                         max_water_elevation = max(self.datapointsWaters[datapointsWaterRunupIndex])
#                         max_swash_upper = max(upper_bound)
#                         max_swash_upper_1_1 = max(upper_bound_1_1)  # Max of new 1.1 * upper_bound
#                         maxElevation = f"{round(max_water_elevation, 2)}, {round(max_swash_upper, 2)}, {round(max_swash_upper_1_1, 2)}"
#                 
#                         # Customize the plot
#                         ax.legend(loc="upper left")
#                         ax.format_xdata = mdates.DateFormatter('%d')
#                         stationName = self.tideLabels[datapointsWaterRunupIndex]
#                         plt.title(self.titlePrefix + stationName[0:stationName.index(" ")] + 
#                                   r" Water Level (Max $\eta$, $\frac{S}{2} + \eta$, $1.1\frac{S}{2} + \eta$: " + maxElevation + " m)", fontsize=24)
#                         plt.xlabel("Date")
#                         plt.ylabel("Elevation (meters)")
#                 
#                         # Adjust layout to prevent label cutoff
#                         plt.tight_layout()
#                 
#                         # Save and close the plot
#                         plt.savefig(graph_directory + stationName + '_water_swash.png', dpi=300)
#                         plt.close()

                if(GRAPH_SWASH):
                    fig, ax = plt.subplots(figsize=(16, 9))
                
                    # Plot the water elevation time series using datapointsSwashStockdonLow
                    ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label=r"$\eta$", color='blue', linewidth=2)
                
                    # Calculate total swash: sqrt(S_incident^2 + S_infragravity^2)
#                     total_swash = np.sqrt(np.array(self.datapointsSwashStockdonIncident[index])**2 + 
#                                           np.array(self.datapointsSwashStockdonInfragravity[index])**2)
                    total_swash = (np.array(self.datapointsSwashHolmanLow[index]) * 2) * (1/1.1)
                
                    # Define the upper and lower bounds for the swash area
                    lower_bound = self.datapointsSwashStockdonLow[index] - 0.5 * total_swash
                    upper_bound = self.datapointsSwashStockdonLow[index] + 0.5 * total_swash
                    upper_bound_1_1 = self.datapointsSwashStockdonLow[index] + 0.5 * 1.1 * total_swash  # New 1.1 * upper_bound line
                
                    # Fill the area between lower_bound and upper_bound_1_1 to highlight swash extent
                    ax.fill_between(self.runupTimes, lower_bound, upper_bound_1_1, color='lightblue', alpha=0.4, label="Swash Extent")
                
                    # Add dotted lines for original and new extents
                    ax.plot(self.runupTimes, upper_bound, '--', color='red', label=r"$+\frac{S}{2}$", linewidth=1.5)
                    ax.plot(self.runupTimes, lower_bound, '--', color='green', label=r"$-\frac{S}{2}$", linewidth=1.5)
                    ax.plot(self.runupTimes, upper_bound_1_1, color='purple', label=r"+1.1$\frac{S}{2}$", linewidth=1.5)  # New 1.1 * S/2 line
                
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsSwashHolmanHigh[index], '--', color="purple", label=r"TWL TWL&CC", linewidth=1.5) 
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupStockdonLow[index], '--', color="blue", alpha=0.5, label=r"$\eta$ TWL&CC", linewidth=1.5) 

                    # Calculate the maximum elevation including the swash
                    max_water_elevation = max(self.datapointsSwashStockdonLow[index])
                    max_swash_upper = max(upper_bound)
                    max_swash_upper_1_1 = max(upper_bound_1_1)  # Max of new 1.1 * upper_bound
                    maxElevation = f"{round(max_water_elevation, 2)}, {round(max_swash_upper, 2)}, {round(max_swash_upper_1_1, 2)}"
                
                    # Customize the plot
                    ax.legend(loc="upper left")
                    ax.format_xdata = mdates.DateFormatter('%d')
                    stationName = self.runupLabels[index]  # Use runupLabels for station name
                    plt.title(self.titlePrefix + stationName[0:9] + 
                              r" Water Level (Max $\eta$, $+\frac{S}{2}$, $+1.1\frac{S}{2}$: " + maxElevation + " m)", fontsize=24)
                    plt.xlabel("Date")
                    plt.ylabel("Elevation (meters)")
                
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
                plt.savefig(graph_directory + stationName + '_wavelength.png', dpi=300)
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
                plt.savefig(graph_directory + stationName + '_steepness.png', dpi=300)
                plt.close()
                
                #                 Graph iribarren number

                
                # Assuming self.datapointsIribarren[index] contains the Iribarren numbers (ξ₀)
                fig, ax = plt.subplots(figsize=(16, 9))
                
                # Plot the Iribarren number over time
                ax.plot(self.runupTimes, self.datapointsIribarren[index], color='#FF9999', linewidth=2, marker='o', markersize=6, label='Iribarren Number')
                
                # Set y-axis limits
                ax.set_ylim([0, 2])
                
                # Define pastel colors and shaded regions for wave types based on ξ₀ ranges
                ax.axhspan(1.5, 2.0, color='#D3E0EA', alpha=0.7, label='Surging/Collapsing (ξ₀ > 1.5)')  # Light blue
                ax.axhspan(0.5, 1.5, color='#C1E1C6', alpha=0.7, label='Plunging (0.5 < ξ₀ ≤ 1.5)')    # Light green
                ax.axhspan(0.0, 0.5, color='#FADADD', alpha=0.7, label='Spilling (ξ₀ ≤ 0.5)')         # Light pink
                
                # Customize x-axis date format
                ax.format_xdata = mdates.DateFormatter('%d')
                plt.xticks(fontsize=12)
                plt.yticks(fontsize=12)
                
                # Station name and max Iribarren value
                stationName = self.runupLabels[index]
                maxIribarren = str(round(max(self.datapointsIribarren[index]), 2))
                plt.title(self.titlePrefix + stationName[0:stationName.index(" ")] + f' Iribarren (Max: {maxIribarren})', fontsize=18)
                
                # Y-axis label
                plt.ylabel('Iribarren Number', fontsize=14, fontweight='bold', color='#555555')
                
                # Add legend
                ax.legend(loc='upper left', fontsize=10, frameon=True, facecolor='white', edgecolor='#CCCCCC')
                
                # Simulate wave images with annotations (using simple shapes as placeholders)
                # Note: Replace with actual image paths or use custom patches
                def add_wave_annotation(x, y, wave_type):
                    if wave_type == 'Surging/Collapsing':
                        color, shape = '#D3E0EA', 's'  # Square for steep wave
                    elif wave_type == 'Plunging':
                        color, shape = '#C1E1C6', '^'  # Triangle for plunging wave
                    else:  # Spilling
                        color, shape = '#FADADD', 'o'  # Circle for gentle wave
                    ax.scatter(x, y, c=color, marker=shape, s=200, edgecolor='none', alpha=0.8)
                    ax.annotate(wave_type, xy=(x, y), xytext=(0, 10), textcoords='offset points',
                                ha='center', va='bottom', fontsize=10, color='#333333',
                                bbox=dict(boxstyle='round,pad=0.5', fc='white', alpha=0.8))
                
                # Add wave type annotations for each data point, skip annotating each thing
#                 for x, y in zip(self.runupTimes, self.datapointsIribarren[index]):
#                     if y > 1.5:
#                         add_wave_annotation(x, y, 'Surging/Collapsing')
#                     elif 0.5 < y <= 1.5:
#                         add_wave_annotation(x, y, 'Plunging')
#                     else:  # y <= 0.5
#                         add_wave_annotation(x, y, 'Spilling')
                
                # Customize the plot's appearance
                ax.grid(False)
                ax.set_facecolor('#F5F5F5')  # Light gray background
                for spine in ax.spines.values():
                    spine.set_visible(False)
                ax.tick_params(axis='both', colors='#555555')
                fig.patch.set_facecolor('#F5F5F5')
                
                # Save the figure
                plt.savefig(graph_directory + stationName + '_iribarren.png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
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
                plt.title(self.titlePrefix + stationName[0:stationName.index(" ")] + r" instant $\beta_f$", fontsize=24)
#                 plt.xlabel("Start: " + self.waterStartDate.strftime(self.DATE_FORMAT), fontsize=14)
                plt.ylabel("Slope")
                plt.xlabel("Date")
                plt.savefig(graph_directory + stationName + '_slope.png', dpi=300)
                plt.close()


        # Function to parse depth and distance from station label
        def parse_station_label(stationName):
            # Example: "Napatree1 7m Depth Waves 75m"
            depth_match = re.search(r'(\d+\.?\d*m)\s+Depth', stationName)
            distance_match = re.search(r'Waves\s+(\d+\.?\d*m)', stationName)
            depth = depth_match.group(1) if depth_match else None
            distance = distance_match.group(1) if distance_match else None
            return depth, distance
        
        
        # Collect all y-values for dynamic y-limits
        all_y_values = []
        for index in range(len(self.runupLabels)):
            all_y_values.extend([x for x in self.runupAverageSlopes[index] if not np.isnan(x)])
            all_y_values.extend([x for x in self.datapointsRunupObsBeachSlope[index] if not np.isnan(x)])
        all_y_values.extend(FORESHORE_BEACH_SLOPE_OBS)
        
        y_min = min(all_y_values) if all_y_values else -0.1
        y_max = max(all_y_values) if all_y_values else 0.1
        y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 0.01
        y_min = y_min - y_padding
        y_max = y_max + y_padding
        
        # Create 5x1 subplots
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        
        for transect in range(1, 6):
            ax = axes[transect - 1]
            
            # Find one station per transect (7m depth)
            slopes_by_name = {}
            for index, station_name in enumerate(self.runupLabels):
                if str(transect) != station_name[8:station_name.index(" ")]:
                    continue
                if '7m Depth Waves' in station_name:
                    ax.plot(self.runupTimes, self.runupAverageSlopes[index], label=r"$\beta_{{f}}$", color='blue', linestyle='-')
                    ax.axhline(y=BEACH_SLOPES_TRANSECTS[transect - 1], color='green', linestyle='--', label=r"$\beta_{{f}}$ TWL&CC")
                    ax.axhline(y=FORESHORE_BEACH_SLOPE_OBS[transect - 1], color='red', linestyle='--', label=r"$\beta_{{f}}$ Obs")
                    base_name = ' '.join(station_name.split()[:-1]) if station_name.endswith(('_true', '_false')) else station_name
                    if base_name not in slopes_by_name:
                        slopes_by_name[base_name] = {'true': None, 'false': None}
                    if station_name.endswith('_true'):
                        slopes_by_name[base_name]['true'] = self.runupAverageSlopes[index]
                    elif station_name.endswith('_false'):
                        slopes_by_name[base_name]['false'] = self.runupAverageSlopes[index]
            
            # Plot slopes for the selected station
            for base_name, slopes in slopes_by_name.items():
                if slopes['true'] is not None:
                    ax.plot(self.runupTimes, slopes['true'], label=r"Daily Average $\beta_f$", color='blue', linestyle='-')
                if slopes['false'] is not None:
                    ax.plot(self.runupTimes, slopes['false'], label=r"Instantaneous $\beta_f$", color='red', linestyle='--')
                break  # Plot only one station per transect 
            
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylabel("Slope", fontsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Foreshore Beach Slope", fontsize=16)
            ax.set_ylim(y_min, y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(f"{graph_directory}/Napatree_all_slope.png")
        plt.close()
    
    
# napatree_all_setup
        # Collect all y-values for dynamic y-limits
        all_y_values = []
        for index in range(len(self.runupLabels)):
            if '7m Depth Waves' in self.runupLabels[index]:
                all_y_values.extend([x for x in self.datapointsSetupStockdon[index] if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsSetupStockdonLow[index] if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsSwashHolmanInfragravity[index] if not np.isnan(x)])
        
        y_min = min(all_y_values) if all_y_values else -0.1
        y_max = max(all_y_values) if all_y_values else 0.1
        y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 0.01
        y_min = y_min - y_padding
        y_max = y_max + y_padding
        
        # Create 5x1 subplots
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        
        for transect in range(1, 6):
            ax = axes[transect - 1]
            
            # Find one station per transect (7m depth)
            for index, station_name in enumerate(self.runupLabels):
                if str(transect) != station_name[8:station_name.index(" ")]:
                    continue
                if '7m Depth Waves' in station_name:
                    # Plot setup time series
                    ax.plot(self.runupTimes, self.datapointsSetupStockdon[index], label=r"$\langle\eta\rangle$ Stockdon", color='blue')
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsSwashHolmanInfragravity[index], label=r"$\langle \eta \rangle$ TWL&CC", color='green')
                    ax.plot(self.runupTimes, self.datapointsSetupStockdonLow[index], label=r"$\eta_{setup}$ SWAN", color='orange')
                    
                    # Calculate max values for title
                    max_swan = round(max(self.datapointsSetupStockdonLow[index]), 2)
                    max_stockdon = round(max(self.datapointsSetupStockdon[index]), 2)
                    maxSetup = f"{max_swan}, {max_stockdon}"
                    
                    # Set title and labels
                    ax.set_title(f"{self.titlePrefix}Napatree{transect} Setup (Max SWAN, Stockdon: {maxSetup} m)", fontsize=16)
                    ax.set_ylabel("Setup (meters)", fontsize=12)
                    break  # Plot only one station per transect
            
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylim(y_min, y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(f"{graph_directory}/Napatree_all_setup.png")
        plt.close()
        
#         napatree all swash

        # Collect all y-values for dynamic y-limits
        all_y_values = []
        for index in range(len(self.runupLabels)):
            if '7m Depth Waves' in self.runupLabels[index]:
                datapointsSwashStockdon = np.sqrt(np.array(self.datapointsSwashStockdonIncident[index])**2 + np.array(self.datapointsSwashStockdonInfragravity[index])**2)
                all_y_values.extend([x for x in datapointsSwashStockdon if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsSwashStockdonIncident[index] if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsSwashStockdonInfragravity[index] if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsRunupObsSwash[index] if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsRunupObsIncidentSwash[index] if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsRunupObsInfragravitySwash[index] if not np.isnan(x)])
        
        y_min = min(all_y_values) if all_y_values else -0.1
        y_max = max(all_y_values) if all_y_values else 0.1
        y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 0.01
        y_min = y_min - y_padding
        y_max = y_max + y_padding
        
        # Create 5x1 subplots
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        
        for transect in range(1, 6):
            ax = axes[transect - 1]
            
            # Find one station per transect (7m depth)
            for index, station_name in enumerate(self.runupLabels):
                if str(transect) != station_name[8:station_name.index(" ")]:
                    continue
                if '7m Depth Waves' in station_name:
                    # Calculate total swash
                    datapointsSwashStockdon = np.sqrt(np.array(self.datapointsSwashStockdonIncident[index])**2 + np.array(self.datapointsSwashStockdonInfragravity[index])**2)
                    
                    # Plot swash time series
                    ax.plot(self.runupTimes, datapointsSwashStockdon, color="green", label=r"Stockdon Swash $\sqrt{{S_{{inc}}^2 + S_{{ig}}^2}}$")
                    ax.plot(self.runupTimes, self.datapointsSwashStockdonIncident[index], color="blue", label=r"Stockdon Incident $S_{inc}$")
                    ax.plot(self.runupTimes, self.datapointsSwashStockdonInfragravity[index], color="orange", label=r"Stockdon Infragravity $S_{ig}$")
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsSwash[index], linestyle="--", color="green", label=r"Swash TWL&CC", alpha=0.5)
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsIncidentSwash[index], linestyle="--", color="blue", label=r"Incident Swash TWL&CC", alpha=0.5)
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsInfragravitySwash[index], linestyle="--", color="orange", label=r"Infragravity Swash TWL&CC", alpha=0.5)
                    
                    # Calculate max values for title
                    max_swash_stockdon = round(max(datapointsSwashStockdon), 2)
                    max_swash_usgs = round(max(self.datapointsRunupObsSwash[index]), 2)
                    maxSwash = f"{max_swash_stockdon}, {max_swash_usgs}"
                    
                    # Set title and labels
                    ax.set_title(f"{self.titlePrefix}Napatree{transect} Swash " + r"(Max $S$, TWL&CC: " +  f"{maxSwash})", fontsize=14)
                    ax.set_ylabel("Swash (meters)", fontsize=12)
                    break  # Plot only one station per transect
            
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylim(y_min, y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(f"{graph_directory}/Napatree_all_swash.png")
        plt.close()
        
#     napatree all water swash

        # Collect all y-values for dynamic y-limits
        all_y_values = []
        for index in range(len(self.runupLabels)):
            if '7m Depth Waves' in self.runupLabels[index]:
                total_swash = (np.array(self.datapointsSwashHolmanLow[index]) * 2) * (1/1.1)
                lower_bound = self.datapointsSwashStockdonLow[index] - 0.5 * total_swash
                upper_bound = self.datapointsSwashStockdonLow[index] + 0.5 * total_swash
                upper_bound_1_1 = self.datapointsSwashStockdonLow[index] + 0.5 * 1.1 * total_swash
                all_y_values.extend([x for x in self.datapointsSwashStockdonLow[index] if not np.isnan(x)])
                all_y_values.extend([x for x in lower_bound if not np.isnan(x)])
                all_y_values.extend([x for x in upper_bound if not np.isnan(x)])
                all_y_values.extend([x for x in upper_bound_1_1 if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsSwashHolmanHigh[index] if not np.isnan(x)])
                all_y_values.extend([x for x in self.datapointsRunupStockdonLow[index] if not np.isnan(x)])
        
        y_min = min(all_y_values) if all_y_values else -0.1
        y_max = max(all_y_values) if all_y_values else 0.1
        y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 0.01
        y_min = y_min - y_padding
        y_max = y_max + y_padding
        
        # Create 5x1 subplots
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        
        for transect in range(1, 6):
            ax = axes[transect - 1]
            
            # Find one station per transect (7m depth)
            for index, station_name in enumerate(self.runupLabels):
                if str(transect) != station_name[8:station_name.index(" ")]:
                    continue
                if '7m Depth Waves' in station_name:
                    # Plot water elevation
                    ax.plot(self.runupTimes, self.datapointsSwashStockdonLow[index], label=r"$\eta$", color='blue', linewidth=2)
                    
                    # Calculate total swash and bounds
                    total_swash = (np.array(self.datapointsSwashHolmanLow[index]) * 2) * (1/1.1)
                    lower_bound = self.datapointsSwashStockdonLow[index] - 0.5 * total_swash
                    upper_bound = self.datapointsSwashStockdonLow[index] + 0.5 * total_swash
                    upper_bound_1_1 = self.datapointsSwashStockdonLow[index] + 0.5 * 1.1 * total_swash
                    
                    # Fill swash extent
                    ax.fill_between(self.runupTimes, lower_bound, upper_bound_1_1, color='lightblue', alpha=0.4, label="Swash Extent")
                    
                    # Plot bounds
                    ax.plot(self.runupTimes, upper_bound, '--', color='red', label=r"$+\frac{S}{2}$", linewidth=1.5)
                    ax.plot(self.runupTimes, lower_bound, '--', color='green', label=r"$-\frac{S}{2}$", linewidth=1.5)
                    ax.plot(self.runupTimes, upper_bound_1_1, color='purple', label=r"+1.1$\frac{S}{2}$", linewidth=1.5)
                    
                    # Plot USGS data
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsSwashHolmanHigh[index], '--', color="purple", alpha=0.5, label=r"TWL TWL&CC", linewidth=1.5)
                    ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupStockdonLow[index], '--', color="blue", alpha=0.5, label=r"$\eta$ TWL&CC", linewidth=1.5)
                    
                    # Calculate max values for title
                    max_water_elevation = round(max(self.datapointsSwashStockdonLow[index]), 2)
                    max_swash_upper = round(max(upper_bound), 2)
                    max_swash_upper_1_1 = round(max(upper_bound_1_1), 2)
                    maxElevation = f"{max_water_elevation}, {max_swash_upper}, {max_swash_upper_1_1}"
                    
                    # Set title and labels
                    ax.set_title(f"{self.titlePrefix}Napatree{transect} Water Level " + r"(Max $\eta$, $+\frac{{S}}{{2}}$, $+1.1\frac{{S}}{{2}}$: " + f"{maxElevation} m)", fontsize=14)
                    ax.set_ylabel("Elevation (meters)", fontsize=12)
                    break  # Plot only one station per transect
            
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylim(y_min, y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(f"{graph_directory}/Napatree_all_water_swash.png")
        plt.close()
        
#         napatree all iribarren
        
        # Collect all y-values for dynamic y-limits (though fixed to [0, 2] as in single plot)
        all_y_values = []
        for index in range(len(self.runupLabels)):
            if '7m Depth Waves' in self.runupLabels[index]:
                all_y_values.extend([x for x in self.datapointsIribarren[index] if not np.isnan(x)])
        
        y_min = 0  # Fixed as in single plot
        y_max = 2
        y_padding = 0  # No padding needed for fixed limits
        # y_min = y_min - y_padding
        # y_max = y_max + y_padding
        
        # Create 5x1 subplots
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        
        for transect in range(1, 6):
            ax = axes[transect - 1]
            
            # Find one station per transect (7m depth)
            for index, station_name in enumerate(self.runupLabels):
                if str(transect) != station_name[8:station_name.index(" ")]:
                    continue
                if '7m Depth Waves' in station_name:
                    # Plot Iribarren number
                    ax.plot(self.runupTimes, self.datapointsIribarren[index], linewidth=2, marker='o', markersize=6, label='Iribarren Number')
                    
                    # Add shaded regions for wave types
                    ax.axhspan(1.5, 2.0, color='#D3E0EA', alpha=0.7, label='Surging/Collapsing (ξ₀ > 1.5)')
                    ax.axhspan(0.5, 1.5, color='#C1E1C6', alpha=0.7, label='Plunging (0.5 < ξ₀ ≤ 1.5)')
                    ax.axhspan(0.0, 0.5, color='#FADADD', alpha=0.7, label='Spilling (ξ₀ ≤ 0.5)')
                    
                    # Calculate max value for title
                    maxIribarren = round(max(self.datapointsIribarren[index]), 2)
                    
                    # Set title and labels
                    ax.set_title(f"{self.titlePrefix}Napatree{transect} Iribarren (Max: {maxIribarren})", fontsize=16)
                    ax.set_ylabel("Iribarren Number", fontsize=12)
                    
                    # Customize appearance
                    ax.grid(False)
                    ax.set_facecolor('#F5F5F5')
                    for spine in ax.spines.values():
                        spine.set_visible(False)
                    ax.tick_params(axis='both', colors='#555555')
                    break  # Plot only one station per transect
            
            ax.legend(loc="upper left", fontsize=10, frameon=True, facecolor='white', edgecolor='#CCCCCC')
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylim(y_min, y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        fig.patch.set_facecolor('#F5F5F5')
        plt.tight_layout()
        plt.savefig(f"{graph_directory}/Napatree_all_iribarren.png", bbox_inches='tight', facecolor=fig.get_facecolor())
        plt.close()
    

        # --- Combined Runup Plots for All Transects --- 
        
        all_y_values = []
        eta_values = None  # Store the first valid η dataset
        for transect in range(1, 6):
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    all_y_values.extend([x for x in self.datapointsRunupHolmanMid[index] if not np.isnan(x)])
                    all_y_values.extend([x for x in self.datapointsDuneHeights[index] if not np.isnan(x)])
                    # Capture the first valid η dataset
                    if eta_values is None and len(self.datapointsSwashStockdonLow[index]) > 0:
                        eta_values = self.datapointsSwashStockdonLow[index]
        
        y_min = min(all_y_values) if all_y_values else -10.0
        y_max = max(all_y_values) if all_y_values else 10.0
        y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 0.5
        y_min = y_min - y_padding
        y_max = y_max + y_padding
        
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        for transect in range(1, 6):
            ax = axes[transect - 1]
            dune_heights = []
            unique_heights = set()
        
            # Collect max values for 7m, 20m, 9km
            max_7m = max_20m = max_9km = "-"
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    depth, distance = parse_station_label(stationName)
                    if depth == "7m":
                        max_7m = round(np.nanmax(self.datapointsRunupHolmanMid[index]), 2) if len(self.datapointsRunupHolmanMid[index]) > 0 else "-"
                    elif depth == "20m":
                        max_20m = round(np.nanmax(self.datapointsRunupHolmanMid[index]), 2) if len(self.datapointsRunupHolmanMid[index]) > 0 else "-"
                    if distance == "9000m":
                        max_9km = round(np.nanmax(self.datapointsRunupHolmanMid[index]), 2) if len(self.datapointsRunupHolmanMid[index]) > 0 else "-"
        
                    dune_heights = self.datapointsDuneHeights[index]
                    ax.plot(self.runupTimes, self.datapointsRunupHolmanMid[index], label=stationName[stationName.index(" ") + 1:])
                    unique_heights.update([x for x in dune_heights if not np.isnan(x)])
        
            #https://x.com/i/grok/share/h5PUOM8iQLOEEh3QJ8g2xPJtK
            ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsSwashHolmanHigh[index], '--', color="blue", alpha = 0.3, label=r"TWL TWL&CC")
            
            # Calculate the error distances for asymmetric error bars
            yerr_lower = np.array(self.datapointsSwashHolmanHigh[index]) - np.array(self.datapointsSwashHolmanMid[index])  # Distance from central to 5% (lower bound)
            yerr_upper = np.array(self.datapointsSwashHolmanIncident[index]) - np.array(self.datapointsSwashHolmanHigh[index])  # Distance from central to 95% (upper bound)
            
            # Combine into asymmetric error array
            yerr = [yerr_lower, yerr_upper]
            
            # Add error bars
            ax.errorbar(self.datapointsSetupHolmanHigh[index], self.datapointsSwashHolmanHigh[index], yerr=yerr, fmt='none', ecolor='blue', alpha = 0.2, capsize=3)
            # Plot η line if available
            if eta_values is not None:
                ax.plot(self.runupTimes, eta_values, linestyle='-', color='black', label='η')
                ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupStockdonLow[index], '--', color="black", label=r"$\eta$ TWL&CC", alpha = 0.5) 
        
            # Plot horizontal lines for dune heights
#             CHANGE HERE WHEN DOING 2022 VS 2023 NOREASTER
            for height in unique_heights:
                if GRAPH_2022:
                    if (transect >= 5):  # 2 For 2023, 5 for 2022, also change below from Dune Height to Runup Height depending on data
                        ax.axhline(y=height, linestyle='--', color='red', label=f'Runup Height {height:.2f}m' if height == list(unique_heights)[0] else None)
                    else:
                        ax.axhline(y=height, linestyle='--', color='grey', label=f'Runup Height {height:.2f}m' if height == list(unique_heights)[0] else None)
                else:
                    if (transect >= 2):  # 2 For 2023, 5 for 2022, also change below from Dune Height to Runup Height depending on data
                        ax.axhline(y=height, linestyle='--', color='red', label=f'Dune Height {height:.2f}m' if height == list(unique_heights)[0] else None)
                    else:
                        ax.axhline(y=height, linestyle='--', color='grey', label=f'Dune Height {height:.2f}m' if height == list(unique_heights)[0] else None)
        
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylabel("Runup (meters)", fontsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Runup (Max 7m, 20m, 9km: {max_7m}, {max_20m}, {max_9km} m)", fontsize=14)
            ax.set_ylim(y_min, y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_all_runup.png', dpi=300)
        plt.close()
        
        # --- Figure 1: Combined Deepwater Significant Wave Height ---
        all_deepwater_swh = []
        for index in range(numberOfRunupDatapoints):
            all_deepwater_swh.extend([x for x in self.datapointsRunupHolmanLow[index] if not np.isnan(x)])
        
        deepwater_swh_min = min(all_deepwater_swh) if all_deepwater_swh else 0.0
        deepwater_swh_max = max(all_deepwater_swh) if all_deepwater_swh else 10.0
        deepwater_swh_padding = (deepwater_swh_max - deepwater_swh_min) * 0.1 if deepwater_swh_max != deepwater_swh_min else 0.5
        deepwater_swh_y_min = max(0.0, deepwater_swh_min - deepwater_swh_padding)
        deepwater_swh_y_max = deepwater_swh_max + deepwater_swh_padding
        
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        for transect in range(1, 6):
            ax = axes[transect - 1]
        
            # Collect max values for 7m, 20m, 9km
            max_7m = max_20m = max_9km = "-"
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    depth, distance = parse_station_label(stationName)
                    if depth == "7m":
                        max_7m = round(np.nanmax(self.datapointsRunupHolmanLow[index]), 2) if len(self.datapointsRunupHolmanLow[index]) > 0 else "-"
                    elif depth == "20m":
                        max_20m = round(np.nanmax(self.datapointsRunupHolmanLow[index]), 2) if len(self.datapointsRunupHolmanLow[index]) > 0 else "-"
                    if distance == "9000m":
                        max_9km = round(np.nanmax(self.datapointsRunupHolmanLow[index]), 2) if len(self.datapointsRunupHolmanLow[index]) > 0 else "-"
        
                    ax.plot(self.runupTimes, self.datapointsRunupHolmanLow[index], label=stationName[stationName.index(" ") + 1:])
        
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylabel("Deepwater Significant Wave Height (meters)", fontsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Deepwater Significant Wave Height (Max 7m, 20m, 9km: {max_7m}, {max_20m}, {max_9km} m)", fontsize=16)
            ax.set_ylim(deepwater_swh_y_min, deepwater_swh_y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_all_deepwater_swh.png', dpi=300)
        plt.close()
        
        # --- Figure 2: Combined Significant Wave Height ---
        all_swh = []
        for index in range(numberOfRunupDatapoints):
            if self.runupLabels[index] in self.buoyLabels:
                swhIndex = self.buoyLabels.index(self.runupLabels[index])
                all_swh.extend([x for x in self.datapointsSWH[swhIndex] if not np.isnan(x)])
        
        swh_min = min(all_swh) if all_swh else 0.0
        swh_max = max(all_swh) if all_swh else 10.0
        swh_padding = (swh_max - swh_min) * 0.1 if swh_max != swh_min else 0.5
        swh_y_min = max(0.0, swh_min - swh_padding)
        swh_y_max = swh_max + swh_padding
        
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        for transect in range(1, 6):
            obsPlotted = False
            ax = axes[transect - 1]
        
            # Collect max values for 7m, 20m, 9km
            max_7m = max_20m = max_9km = "-"
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    if stationName in self.buoyLabels:
                        swhIndex = self.buoyLabels.index(stationName)
                        depth, distance = parse_station_label(stationName)
                        if depth == "7m":
                            max_7m = round(np.nanmax(self.datapointsSWH[swhIndex]), 2) if len(self.datapointsSWH[swhIndex]) > 0 else "-"
                            color = "blue"
                        elif depth == "20m":
                            max_20m = round(np.nanmax(self.datapointsSWH[swhIndex]), 2) if len(self.datapointsSWH[swhIndex]) > 0 else "-"
                            color = "orange"
                        if distance == "9000m":
                            max_9km = round(np.nanmax(self.datapointsSWH[swhIndex]), 2) if len(self.datapointsSWH[swhIndex]) > 0 else "-"
                            color = "green"
        
                        if(not obsPlotted):
                            ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsSwh[index], '--', label=r"$H_s$ TWL&CC", color="blue")
                            obsPlotted = True
                        ax.plot(self.runupTimes, self.datapointsSWH[swhIndex], label=stationName[stationName.index(" ") + 1:], color=color)

        
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylabel("Significant Wave Height (meters)", fontsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Significant Wave Height (Max 7m, 20m, 9km: {max_7m}, {max_20m}, {max_9km} m)", fontsize=16)
            ax.set_ylim(swh_y_min, swh_y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_all_swh.png', dpi=300)
        plt.close()
        
        # --- Combined Peak Wave Period ---
        all_pwp = []
        for index in range(numberOfRunupDatapoints):
            if self.runupLabels[index] in self.buoyLabels:
                pwpIndex = self.buoyLabels.index(self.runupLabels[index])
                all_pwp.extend([x for x in self.datapointsPWP[pwpIndex] if not np.isnan(x)])
        
        pwp_min = min(all_pwp) if all_pwp else 0.0
        pwp_max = max(all_pwp) if all_pwp else 20.0
        pwp_padding = (pwp_max - pwp_min) * 0.1 if pwp_max != pwp_min else 0.5
        pwp_y_min = max(0.0, pwp_min - pwp_padding)
        pwp_y_max = pwp_max + pwp_padding
        
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        for transect in range(1, 6):
            obsPlotted = False
            ax = axes[transect - 1]
        
            # Collect max values for 7m, 20m, 9km
            max_7m = max_20m = max_9km = "-"
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    if stationName in self.buoyLabels:
                        pwpIndex = self.buoyLabels.index(stationName)
                        depth, distance = parse_station_label(stationName)
                        if depth == "7m":
                            color = "blue"
                            max_7m = round(np.nanmax(self.datapointsPWP[pwpIndex]), 2) if len(self.datapointsPWP[pwpIndex]) > 0 else "-"
                        elif depth == "20m":
                            color = "orange"
                            max_20m = round(np.nanmax(self.datapointsPWP[pwpIndex]), 2) if len(self.datapointsPWP[pwpIndex]) > 0 else "-"
                        if distance == "9000m":
                            color = "green"
                            max_9km = round(np.nanmax(self.datapointsPWP[pwpIndex]), 2) if len(self.datapointsPWP[pwpIndex]) > 0 else "-"
        
                        if(not obsPlotted):
                            ax.plot(self.datapointsSetupHolmanHigh[index], self.datapointsRunupObsPwp[index], '--', label=r"$T_p$ TWL&CC", color="blue") 
                            obsPlotted = True 
                        ax.plot(self.runupTimes, self.datapointsPWP[pwpIndex], label=stationName[stationName.index(" ") + 1:], color=color)
            
        
            ax.legend(loc="upper left", fontsize=10)
            ax.format_xdata = mdates.DateFormatter('%d')
            ax.tick_params(axis='both', labelsize=12)
            ax.set_ylabel("Peak Wave Period (seconds)", fontsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Peak Wave Period (Max 7m, 20m, 9km: {max_7m}, {max_20m}, {max_9km} sec)", fontsize=16)
            ax.set_ylim(pwp_y_min, pwp_y_max)
        
        axes[-1].set_xlabel("Date", fontsize=14)
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_all_pwp.png', dpi=300)
        plt.close()
        
        # --- Figure 3: Combined Elevation, Max SWH, and Max Deepwater SWH ---
        # Collect all data for consistent y-axes
        all_swh_metrics = []
        all_deepwater_swh_metrics = []
        all_elevations = []
        for transect in range(1, 6):
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    if stationName in self.buoyLabels:
                        swhIndex = self.buoyLabels.index(stationName)
                        all_swh_metrics.append(np.max(self.datapointsSWH[swhIndex]))
                    if stationName in self.assetLabels:
                        elevationIndex = self.assetLabels.index(stationName)
                        all_elevations.append(self.datapointsElevation[elevationIndex])
                    all_deepwater_swh_metrics.append(np.max(self.datapointsRunupHolmanLow[index]))
        
        swh_metrics_min = min(all_swh_metrics + all_deepwater_swh_metrics) if all_swh_metrics or all_deepwater_swh_metrics else 0.0
        swh_metrics_max = max(all_swh_metrics + all_deepwater_swh_metrics) if all_swh_metrics or all_deepwater_swh_metrics else 10.0
        swh_metrics_padding = (swh_metrics_max - swh_metrics_min) * 0.1 if swh_metrics_max != swh_metrics_min else 0.5
        swh_metrics_y_min = max(0.0, swh_metrics_min - swh_metrics_padding)
        swh_metrics_y_max = swh_metrics_max + swh_metrics_padding
        
        elevation_min = min(all_elevations) if all_elevations else -30.0
        elevation_max = max(all_elevations) if all_elevations else 10.0
        elevation_padding = (elevation_max - elevation_min) * 0.1 if elevation_max != elevation_min else 1.0
        elevation_y_min = elevation_min - elevation_padding
        elevation_y_max = elevation_max + elevation_padding
        
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        for transect in range(1, 6):
            ax = axes[transect - 1]
            ax2 = ax.twinx()
        
            deeplineDistances = []
            deeplineElevations = []
            deeplineSWH = []
            deeplineDeepwaterSWH = []
        
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    if stationName in self.buoyLabels:
                        swhIndex = self.buoyLabels.index(stationName)
                        deeplineSWH.append(np.max(self.datapointsSWH[swhIndex]))
                    if stationName in self.assetLabels:
                        elevationIndex = self.assetLabels.index(stationName)
                        deeplineElevations.append(self.datapointsElevation[elevationIndex])
                    deeplineDeepwaterSWH.append(np.max(self.datapointsRunupHolmanLow[index]))
                    distance_str = stationName[stationName.rindex(" ") + 1:-1]
                    deeplineDistances.append(int(distance_str))
        
            # Sort by distance to ensure processing from closest to farthest
            sorted_indices = np.argsort(deeplineDistances)
            deeplineDistances = np.array(deeplineDistances)[sorted_indices]
            deeplineElevations = np.array(deeplineElevations)[sorted_indices]
            deeplineSWH = np.array(deeplineSWH)[sorted_indices]
            deeplineDeepwaterSWH = np.array(deeplineDeepwaterSWH)[sorted_indices]
        
            ax.plot(deeplineDistances, deeplineSWH, label="Max SWH", color='blue')
            ax.plot(deeplineDistances, deeplineDeepwaterSWH, label="Max Deepwater SWH", color='green')
            ax2.plot(deeplineDistances, deeplineElevations, label="Elevation", color='red', linestyle="--")
        
            # Find first crossing for -7m depth
            distance_7m = None
            for i in range(len(deeplineElevations) - 1):
                y1, y2 = deeplineElevations[i], deeplineElevations[i + 1]
                x1, x2 = deeplineDistances[i], deeplineDistances[i + 1]
                # Check if -7m is crossed (y1 > -7 > y2 or y1 < -7 < y2)
                if (y1 > DEPTH_LINE_7M and y2 <= DEPTH_LINE_7M) or (y1 < DEPTH_LINE_7M and y2 >= DEPTH_LINE_7M):
                    # Linear interpolation: x = x1 + (x2 - x1) * (target - y1) / (y2 - y1)
                    distance_7m = x1 + (x2 - x1) * (DEPTH_LINE_7M - y1) / (y2 - y1)
                    break
            if distance_7m is None:
                print(f"Warning: No -7m depth crossing found in transect {transect}")
        
            # Find first crossing for -20m depth
            distance_20m = None
            for i in range(len(deeplineElevations) - 1):
                y1, y2 = deeplineElevations[i], deeplineElevations[i + 1]
                x1, x2 = deeplineDistances[i], deeplineDistances[i + 1]
                # Check if -20m is crossed (y1 > -20 > y2 or y1 < -20 < y2)
                if (y1 > DEPTH_LINE_20M and y2 <= DEPTH_LINE_20M) or (y1 < DEPTH_LINE_20M and y2 >= DEPTH_LINE_20M):
                    # Linear interpolation
                    distance_20m = x1 + (x2 - x1) * (DEPTH_LINE_20M - y1) / (y2 - y1)
                    break
            if distance_20m is None:
                print(f"Warning: No -20m depth crossing found in transect {transect}")
        
            # Plot vertical lines
            if distance_7m is not None:
                ax.axvline(x=distance_7m, color='purple', linestyle='--', label='Depth -7m', alpha=0.7)
            if distance_20m is not None:
                ax.axvline(x=distance_20m, color='orange', linestyle='--', label='Depth -20m', alpha=0.7)
            ax.axvline(x=DISTANCE_LINE_9000M, color='black', linestyle='--', label='9000m', alpha=0.7)
        
            ax.set_ylabel("SWH (meters)", fontsize=12, color='blue')
            ax2.set_ylabel("Elevation (meters)", fontsize=12, color='red')
            ax.tick_params(axis='y', labelcolor='blue', labelsize=12)
            ax2.tick_params(axis='y', labelcolor='red', labelsize=12)
            ax.tick_params(axis='x', labelsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Profile", fontsize=16)
        
            ax.set_ylim(swh_metrics_y_min, swh_metrics_y_max)
            ax2.set_ylim(elevation_y_min, elevation_y_max)
        
            if transect == 1:
                lines1, labels1 = ax.get_legend_handles_labels()
                lines2, labels2 = ax2.get_legend_handles_labels()
                ax.legend(lines1 + lines2, labels1 + labels2, loc="upper right", fontsize=10)
        
            # Set x-axis label on the bottom subplot
            if transect == 5:
                ax.set_xlabel("Distance (meters)", fontsize=14)
        
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_all_deepline_metrics.png', dpi=300)
        plt.close()
        
        # --- Combined Elevation Profiles for All Transects ---
        # Collect all elevation data for consistent y-axis, excluding NaN
        all_elevations = []
        all_dem_elevations = []
        for transect in range(1, 6):
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    if stationName in self.assetLabels:
                        elevationIndex = self.assetLabels.index(stationName)
                        elev = self.datapointsElevation[elevationIndex]
                        dem_elev = self.assetDatapointsElevation[elevationIndex]
                        if not np.isnan(elev):
                            all_elevations.append(elev)
                        if not np.isnan(dem_elev):
                            all_dem_elevations.append(dem_elev)
        
        # Compute global y-axis limits, handling empty lists
        elevation_min = min(all_elevations + all_dem_elevations) if all_elevations or all_dem_elevations else -30.0
        elevation_max = max(all_elevations + all_dem_elevations) if all_elevations or all_dem_elevations else 10.0
        elevation_padding = (elevation_max - elevation_min) * 0.1 if elevation_max != elevation_min else 1.0
        elevation_y_min = elevation_min - elevation_padding
        elevation_y_max = elevation_max + elevation_padding
        
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        for transect in range(1, 6):
            ax = axes[transect - 1]
        
            deeplineDistances = []
            deeplineElevations = []
            deeplineDemElevations = []
        
            # Collect data for the transect
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    if stationName in self.assetLabels:
                        elevationIndex = self.assetLabels.index(stationName)
                        deeplineElevations.append(self.datapointsElevation[elevationIndex])
                        deeplineDemElevations.append(self.assetDatapointsElevation[elevationIndex])
                        distance_str = stationName[stationName.rindex(" ") + 1:-1]
                        deeplineDistances.append(int(distance_str))
        
            # Convert to numpy arrays and sort by distance
            deeplineDistances = np.array(deeplineDistances)
            deeplineElevations = np.array(deeplineElevations)
            deeplineDemElevations = np.array(deeplineDemElevations)
            sorted_indices = np.argsort(deeplineDistances)
            deeplineDistances = deeplineDistances[sorted_indices]
            deeplineElevations = deeplineElevations[sorted_indices]
            deeplineDemElevations = deeplineDemElevations[sorted_indices]
        
            # Interpolate NaN values in deeplineDemElevations
            if np.any(np.isnan(deeplineDemElevations)):
                valid_mask = ~np.isnan(deeplineDemElevations)
                if np.sum(valid_mask) >= 2:  # Need at least 2 valid points for interpolation
                    deeplineDemElevations = np.interp(
                        deeplineDistances,
                        deeplineDistances[valid_mask],
                        deeplineDemElevations[valid_mask]
                    )
                else:
                    print(f"Warning: Insufficient valid DEM elevation data for interpolation in transect {transect}")
                    deeplineDemElevations[np.isnan(deeplineDemElevations)] = 0.0  # Fallback: replace NaN with 0
        
            # Plot elevation lines
            ax.plot(deeplineDistances, deeplineElevations, label="Mesh", color='red', linestyle="--")
            ax.plot(deeplineDistances, deeplineDemElevations, label="GEBCO DEM", color='black', linestyle="-")
        
            # Customize axes
            ax.set_ylabel("Elevation (meters)", fontsize=12)
            ax.tick_params(axis='both', labelsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Elevation Profile", fontsize=16)
            ax.set_ylim(elevation_y_min, elevation_y_max)  # Consistent y-axis limits
        
            # Add legend
            ax.legend(loc="upper right", fontsize=10)
        
            # Set x-axis label on the bottom subplot
            if transect == 5:
                ax.set_xlabel("Distance (meters)", fontsize=14)
        
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_all_elevation_profiles.png', dpi=300)
        plt.close()
        
        
        
# alongshore innundation plot

        # --- Combined Elevation Profiles for All Transects ---
        # Collect all elevation data for consistent y-axis, excluding NaN
        all_elevations = []
        all_dem_elevations = []
        for transect in range(1, 6):
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    if stationName in self.assetLabels:
                        elevationIndex = self.assetLabels.index(stationName)
                        elev = self.datapointsElevation[elevationIndex]
                        dem_elev = self.assetDatapointsElevation[elevationIndex]
                        if not np.isnan(elev):
                            all_elevations.append(elev)
                        if not np.isnan(dem_elev):
                            all_dem_elevations.append(dem_elev)
        
        # Compute global y-axis limits, handling empty lists
        elevation_min = min(all_elevations + all_dem_elevations) if all_elevations or all_dem_elevations else -30.0
        elevation_max = max(all_elevations + all_dem_elevations) if all_elevations or all_dem_elevations else 10.0
        elevation_padding = (elevation_max - elevation_min) * 0.1 if elevation_max != elevation_min else 1.0
        elevation_y_min = elevation_min - elevation_padding
        elevation_y_max = elevation_max + elevation_padding
        
        fig, ax = plt.subplots(figsize=(16,9))
    
        alongshoreLongitudes = []
        alongshoreElevations = []
        alongshoreDemElevations = []
        alongshoreTwlccElevations = []
    
        transectsIndex = 0
        for elevationIndex, assetLabel in enumerate(self.assetLabels):
            if (assetLabel[assetLabel.index(" ") + 1] == "A"):
                elev = self.datapointsElevation[elevationIndex]
                dem_elev = self.assetDatapointsElevation[elevationIndex]
                longitude = self.assetLongitudes[elevationIndex]
                twlcc_elev = ALL_DUNE_CREST_TRANSECTS[transectsIndex]
                transectsIndex = transectsIndex + 1
                if not np.isnan(elev):
                    alongshoreElevations.append(elev)
                if not np.isnan(dem_elev):
                    alongshoreDemElevations.append(dem_elev)
                alongshoreLongitudes.append(longitude)
                alongshoreTwlccElevations.append(twlcc_elev)

        # Convert to numpy arrays and sort by distance
        alongshoreLongitudes = np.array(alongshoreLongitudes)
        alongshoreElevations = np.array(alongshoreElevations)
        alongshoreDemElevations = np.array(alongshoreDemElevations)
        sorted_indices = np.argsort(alongshoreLongitudes)
        alongshoreLongitudes = alongshoreLongitudes[sorted_indices]
        alongshoreElevations = alongshoreElevations[sorted_indices]
        alongshoreDemElevations = alongshoreDemElevations[sorted_indices]
    
        # Interpolate NaN values in deeplineDemElevations
        if np.any(np.isnan(alongshoreDemElevations)):
            valid_mask = ~np.isnan(alongshoreDemElevations)
            if np.sum(valid_mask) >= 2:  # Need at least 2 valid points for interpolation
                alongshoreDemElevations = np.interp(
                    alongshoreLongitudes,
                    alongshoreLongitudes[valid_mask],
                    alongshoreDemElevations[valid_mask]
                )
            else:
                print(f"Warning: Insufficient valid DEM elevation data for interpolation in transect {transect}")
                alongshoreDemElevations[np.isnan(alongshoreDemElevations)] = 0.0  # Fallback: replace NaN with 0
    
        # Plot elevation lines
#             Change to plotting latitude x axis elevation y axis
        ax.plot(alongshoreLongitudes, alongshoreElevations, label="Mesh", color='red', linestyle="--")
        ax.plot(alongshoreLongitudes, alongshoreDemElevations, label="USGS DEM", color='black', linestyle="-")
        ax.plot(alongshoreLongitudes, alongshoreTwlccElevations, label="TWL&CC Profiles", color='green', linestyle="-")
    
        # Customize axes
        ax.set_ylabel("Elevation (meters)", fontsize=12)
        ax.tick_params(axis='both', labelsize=12)
        ax.set_title(f"{self.titlePrefix}Napatree Alongshore Profile", fontsize=16)
        ax.set_ylim(0, 10)  # Consistent y-axis limits
    
        # Add legend
        ax.legend(loc="upper right", fontsize=10)
    
        # Set x-axis label on the bottom subplot
        ax.set_xlabel("Longitude", fontsize=14)
        
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_alongshore_elevation_profiles.png', dpi=300)
        plt.close()


        # --- Combined Elevation Profiles for All Transects ---
        # Collect all elevation data for consistent y-axis, excluding NaN
        all_elevations = []
        all_dem_elevations = []
        for transect in range(1, 6):
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                    for elevationIndex, assetLabel in enumerate(self.assetLabels):
                        if (assetLabel[assetLabel.index(" ") + 1] == "P" and 
                            assetLabel[8:assetLabel.index(" ")] == str(transect)):
                            elev = self.datapointsElevation[elevationIndex]
                            dem_elev = self.assetDatapointsElevation[elevationIndex]
                            if not np.isnan(elev):
                                all_elevations.append(elev)
                            if not np.isnan(dem_elev):
                                all_dem_elevations.append(dem_elev)
        
        # Compute global y-axis limits
        elevation_min = min(all_elevations + all_dem_elevations) if all_elevations or all_dem_elevations else -30.0
        elevation_max = max(all_elevations + all_dem_elevations) if all_elevations or all_dem_elevations else 10.0
        elevation_padding = (elevation_max - elevation_min) * 0.1 if elevation_max != elevation_min else 1.0
        elevation_y_min = elevation_min - elevation_padding
        elevation_y_max = elevation_max + elevation_padding
        
        fig, axes = plt.subplots(5, 1, figsize=(16, 20), sharex=True)
        for transect in range(1, 6):
            ax = axes[transect - 1]
        
            profileDistances = []
            profileElevations = []
            profileDemElevations = []
        
            # Collect data for the transect
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")]:
                
                    dune_toe_elev_ref = self.datapointsSetupHolmanMid[index][-1]  # Reference elevation
                    dune_crest_elev_ref = self.datapointsSetupHolmanLow[index][-1]  # Reference elevation
                    obs_dune_elev_ref = self.datapointsDuneHeights[index][-1]
                    average_slopes = self.runupAverageSlopes[index]
#                     average_obs_slope = -self.datapointsRunupObsBeachSlope[index][-1]
                    average_obs_slope = BEACH_SLOPES_TRANSECTS[transect - 1]
                    print("BEACH PROFILE DATA", MHWL_TRANSECTS, DUNE_TOE_TRANSECTS, DUNE_CREST_TRANSECTS)
                    mhwl_elev = MHWL_TRANSECTS[transect-1]
                    dune_toe_elev_ref = DUNE_TOE_TRANSECTS[transect-1]
                    dune_crest_elev_ref = DUNE_CREST_TRANSECTS[transect-1]

                    for elevationIndex, assetLabel in enumerate(self.assetLabels):
                        if (assetLabel[assetLabel.index(" ") + 1] == "P" and 
                            assetLabel[8:assetLabel.index(" ")] == str(transect)):
                            profileElevations.append(self.datapointsElevation[elevationIndex])
                            profileDemElevations.append(self.assetDatapointsElevation[elevationIndex])
                            distance_str = assetLabel[assetLabel.rindex(" ") + 1:-1]
                            profileDistances.append(float(distance_str))
        
            # Convert to numpy arrays and sort by distance to fix connection issue
            sort_indices = np.argsort(profileDistances)
            profileDistances = np.array(profileDistances)[sort_indices]
            profileElevations = np.array(profileElevations)[sort_indices]
            profileDemElevations = np.array(profileDemElevations)[sort_indices]
        
            # Interpolate NaN values in profileDemElevations
            if np.any(np.isnan(profileDemElevations)):
                valid_mask = ~np.isnan(profileDemElevations)
                if np.sum(valid_mask) >= 2:
                    profileDemElevations = np.interp(
                        profileDistances,
                        profileDistances[valid_mask],
                        profileDemElevations[valid_mask]
                    )
                else:
                    print(f"Warning: Insufficient valid DEM elevation data for interpolation in transect {transect}")
                    profileDemElevations[np.isnan(profileDemElevations)] = 0.0
        
            # Plot elevation lines
            ax.plot(profileDistances, profileElevations, label="Mesh", color='black')
            ax.plot(profileDistances, profileDemElevations, label="USGS 1m DEM", color='brown', linestyle="-")
        
            # Define reference elevations
#             mhwl_elev = MHW_ELEVATION_RELATIVE_TO_NAVD88  # Hardcoded MHWL elevation
        
            # Find intersection for MHWL
            def find_intersection(distances, elevations, target_elev):
                if len(distances) < 2 or np.all(elevations == elevations[0]):
                    return None
                for i in range(len(distances) - 1, 0, -1):
                    diff1 = float(elevations[i] - target_elev)
                    diff2 = float(elevations[i - 1] - target_elev)
                    if diff1 * diff2 <= 0:
                        x1, x2 = distances[i], distances[i - 1]
                        y1, y2 = elevations[i], elevations[i - 1]
                        if y2 != y1:
                            intersect_x = x1 + (target_elev - y1) * (x2 - x1) / (y2 - y1)
                            return intersect_x
                        return x1
                return None
        
            mhwl_intersect = find_intersection(profileDistances, profileElevations, mhwl_elev)
            
        
            # Plot MHWL intersection
            if mhwl_intersect is not None:
                ax.scatter(mhwl_intersect, mhwl_elev, color='blue', s=100, edgecolor='white', zorder=5)
                ax.annotate('MHWL', xy=(mhwl_intersect, mhwl_elev), xytext=(5, 5), textcoords='offset points',
                            ha='left', va='bottom', fontsize=10, color='blue', bbox=dict(facecolor='white', alpha=0.8, edgecolor='none'))
        
            # Draw subtle horizontal lines for dune crest and dune toe
            ax.axhline(y=dune_crest_elev_ref, linewidth=1, alpha=0.7, color='green', label='Dune Height TWL&CC')
#             ax.axhline(y=dune_toe_elev_ref, linewidth=1, alpha=0.7, color='green', label='Dune Toe TWL&CC')
            if(GRAPH_2022):
                ax.axhline(y=obs_dune_elev_ref, linewidth=1, alpha=0.7, color="orange", label='Runup Height Obs')
            else:
                ax.axhline(y=obs_dune_elev_ref, linewidth=1, alpha=0.7, color="orange", label='Dune Height Obs')

        
            # Plot additional horizontal lines using unique non-NaN values from self.datapointsDuneHeights
#             duneHeightPlotted = False
#             print(self.datapointsDuneHeights[index])
#             quit()
#             unique_dune_heights = [x for x in self.datapointsDuneHeights[index] if not np.isnan(x)]
#             unique_dune_heights = sorted(list(set(unique_dune_heights)))
#             for dune_height in unique_dune_heights:
#                 ax.axhline(y=dune_height, linestyle='--', linewidth=1, alpha=0.7, color='red', label='Dune Height' if not duneHeightPlotted else "")
#                 duneHeightPlotted = True
#         
            # Draw slope lines through MHWL with correct direction (inward/downward)
            if mhwl_intersect is not None:
                # β_f,USGS from self.datapointsRunupObsBeachSlope
                beta_usgs = -average_obs_slope  # Negative slope for inward direction
                x_range = ax.get_xlim()
                x_start = mhwl_intersect
                x_end = x_start - 100  # Inward direction
                y_start_usgs = mhwl_elev
                y_end_usgs = y_start_usgs + beta_usgs * (x_end - x_start)
                ax.plot([x_start, x_end], [y_start_usgs, y_end_usgs], color='cyan', linestyle='--', linewidth=1, alpha=0.6)
                ax.plot([], [], color='cyan', linestyle='--', linewidth=1, alpha=0.5, label=r'$\beta_{{f,TWL&CC}} = {:.2f}$'.format(abs(beta_usgs)))
        
                # β_f,obs hardcoded per transect
                beta_obs = -FORESHORE_BEACH_SLOPE_OBS[transect - 1]  # Negative slope for inward direction
                y_start_obs = mhwl_elev
                y_end_obs = y_start_obs + beta_obs * (x_end - x_start)
                ax.plot([x_start, x_end], [y_start_obs, y_end_obs], color='purple', linestyle='--', linewidth=1, alpha=0.6)
                ax.plot([], [], color='purple', linestyle='--', linewidth=1, alpha=0.5, label=r'$\beta_{{f,obs}} = {:.2f}$'.format(abs(beta_obs)))
        
                # β_f,avg from mean of runupAverageSlopes
                beta_avg = -np.max(average_slopes)  # Negative slope for inward direction
                y_start_avg = mhwl_elev
                y_end_avg = y_start_avg + beta_avg * (x_end - x_start)
                ax.plot([x_start, x_end], [y_start_avg, y_end_avg], color='magenta', linestyle='--', linewidth=1, alpha=0.6)
                ax.plot([], [], color='magenta', linestyle='--', linewidth=1, alpha=0.5, label=r'$\beta_{{f,avg}} = {:.2f}$'.format(abs(beta_avg)))
        
            # Water lines and total water lines
            for index in range(numberOfRunupDatapoints):
                stationName = self.runupLabels[index]
                if str(transect) == stationName[8:stationName.index(" ")] and "Waves" in stationName and "4" in stationName[stationName.index(" ") + 1]:
                    # Plot η line (maximum value as horizontal line)
                    if len(self.datapointsSwashStockdonLow[index]) > 0:
                        eta = np.array(self.datapointsSwashStockdonLow[index])
                        max_eta_value = np.nanmax(eta)
                        ax.axhline(y=max_eta_value, color='blue', linestyle='-', label='η' if transect == 1 else "")
                        # Shade underneath η with pastel blue, avoiding terrain
                        ax.fill_between(profileDistances, np.full_like(profileDistances, max_eta_value), elevation_y_min, 
                                        where=(max_eta_value > profileElevations) & (max_eta_value < elevation_y_max), 
                                        color='#CCE5FF', alpha=0.5, label='η Shade' if transect == 0 else "")
        
                    # Plot total water level (maximum value as horizontal line)
                    total_water = np.array(self.datapointsRunupHolmanMid[index])
                    max_total_value = np.nanmax(total_water)
                    ax.axhline(y=max_total_value, color='purple', linestyle='-', label='TWL' if transect == 1 else "")
                    # Shade underneath total water with pastel red, avoiding terrain
                    ax.fill_between(profileDistances, np.full_like(profileDistances, max_total_value), elevation_y_min, 
                                    where=(max_total_value > profileElevations) & (max_total_value < elevation_y_max), 
                                    color='#FFCCCC', alpha=0.5, label='Total Water Shade' if transect == 0 else "")
                                  

#                     ax.axhline(y=np.nanmax(np.array(self.datapointsSwashHolmanHigh[index])), linestyle='--', color='orange', alpha=0.5, label='TWL&CC TWL' if transect == 1 else "")

                    ax.axhline(y=np.nanmax(np.array(self.datapointsRunupStockdonLow[index])), linestyle='--', color='blue', alpha=0.7, label='η TWL&CC' if transect == 1 else "")

                    # Plot the horizontal line at the maximum value
                    max_value = np.nanmax(np.array(self.datapointsSwashHolmanHigh[index]))
                    ax.axhline(y=max_value, linestyle='--', color='purple', alpha=0.7, label='TWL TWL&CC' if transect == 1 else "")
                    
                    # Calculate the error distances for asymmetric error bars
                    yerr_lower = np.array(self.datapointsSwashHolmanHigh[index]) - np.array(self.datapointsSwashHolmanMid[index])  # Distance from central to 5% (lower bound)
                    yerr_upper = np.array(self.datapointsSwashHolmanIncident[index]) - np.array(self.datapointsSwashHolmanHigh[index])  # Distance from central to 95% (upper bound)
                    
                    # Since it's a horizontal line, use the maximum value's error bounds
                    # Find the index of the maximum value to get the corresponding error bounds
                    max_idx = np.nanargmax(np.array(self.datapointsSwashHolmanHigh[index]))
                    yerr_lower_max = yerr_lower[max_idx]
                    yerr_upper_max = yerr_upper[max_idx]
                    
                    # Choose an x-coordinate for the error bar (e.g., middle of the time series)
                    # Replace x_mid with your time series x-values if available, or a reasonable point
                    
                    # Plot the error bar as a single point
                    ax.errorbar(0, max_value, yerr=[[yerr_lower_max], [yerr_upper_max]], fmt='none', ecolor='purple', alpha=0.7, capsize=5)


            # Shade terrain underneath elevation curve
            ax.fill_between(profileDistances, profileElevations, elevation_y_min, where=(profileElevations > elevation_y_min), 
                            color='#D2B48C', alpha=0.5, label='Terrain' if transect == 0 else "")
        
            # Customize axes
            ax.set_ylabel("Elevation (meters)", fontsize=12)
            ax.tick_params(axis='both', labelsize=12)
            ax.set_title(f"{self.titlePrefix}Napatree{transect} Elevation Profile", fontsize=16)
            ax.set_ylim(-2, 6.15)
#             ax.set_xlim(min(profileDistances), max(profileDistances))
            ax.set_xlim(-170, 50)
            ax.grid(False)
        
            # Update legend
            handles, labels = ax.get_legend_handles_labels()
            unique_labels = dict(zip(labels, handles))
            handles = list(unique_labels.values())
            labels = list(unique_labels.keys())
            ax.legend(handles=handles, loc="upper right", fontsize=10)
        
            # Set x-axis label on the bottom subplot
            if transect == 5:
                ax.set_xlabel("Distance (meters)", fontsize=14)
        
        plt.tight_layout()
        plt.savefig(graph_directory + 'Napatree_beach_elevation_profiles.png', dpi=300)
        plt.close()
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
#         plt.savefig(graph_directory + 'Napatree1_all_runup.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree2_all_runup.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree3_all_runup.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree4_all_runup.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree5_all_runup.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree1_all_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree1_all_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree1_all_elevations.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree1_max_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree1_max_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree2_all_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree2_all_elevations.png', dpi=300)
#         plt.close()
        
#         fig, ax = plt.subplots(figsize=(16,9))
#         plt.xticks(fontsize=12)
#         plt.yticks(fontsize=12)
#         plt.title(self.titlePrefix + "Napatree2 Deepline SWH: ", fontsize=18)
#         ax.plot(deeplineDistances, deeplineSWH)
#         plt.xlabel("Distance", fontsize=14)
#         plt.ylabel("SWH (meters)", fontsize=14)
#         plt.tight_layout()
#         plt.savefig(graph_directory + 'Napatree2_max_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree2_max_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree3_all_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree3_all_elevations.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree3_max_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree3_max_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree4_all_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree4_all_elevations.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree4_max_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree4_max_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree5_all_deepwater_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree5_all_elevations.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree5_max_swh.png', dpi=300)
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
#         plt.savefig(graph_directory + 'Napatree5_max_deepwater_swh.png', dpi=300)
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
#                 fig, ax = plt.subplots(figsize=(18,18))
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
#                 plt.savefig(graph_directory + 'map_runup_' + str(index) + '.png', dpi=300)
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

