import os
import json
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.cm import ScalarMappable
from matplotlib.tri import Triangulation
from datetime import datetime, timezone
import imageio
import gc

class DiffGrapher:
    DATE_FORMAT = "%m/%d/%y-%HZ"
    
        
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
        delta = datetime.fromtimestamp(timestamp, timezone.utc) - startDate
        return delta.total_seconds()/3600
    
    def extrapolateWindToTenMeterHeight(self, windVelocity, altitude):
        return windVelocity
    #     WIND_PROFILE_EXPONENT = 0.11
    #     return windVelocity * ((10.0/altitude)**WIND_PROFILE_EXPONENT)

    def __init__(self, dataToGraph={}, STATIONS_FILE="", backgroundMap="", backgroundAxis=[]):
        print("Initializing grapher", flush=True)
        self.obsExists = False
        self.gaugeExists = False
        self.tideExists = False
        self.windExists = False
        self.wavesExists = False
        self.rainExists = False
        self.waterExists = False
        
        self.windStartDate = None
        self.waveStartDate = None
        self.rainStartDate = None
        self.waterStartDate = None
        
        self.windType = ""
        
        self.backgroundMap = backgroundMap
        self.backgroundAxis = backgroundAxis
        
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
        if("RAIN" in dataToGraph):
            self.rainExists = True
        if("WATER" in dataToGraph):
            self.waterExists = True
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
        self.waterDiffTimes = []
        
        self.maxWater = 5
        self.mapWaterPoints = []
        self.mapWaterTimes = []
        self.mapWaterPointsLatitudes = []
        self.mapWaterPointsLongitudes = []
        self.mapWaterTriangles = []
        self.mapWaterMaskedTriangles = []
        self.mapWaters = []
        
        self.datapointsWaters = []
        self.datapointsDiffWaters = []
        
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
        
        self.maxSWH = 3
        self.mapWavePoints = []
        self.mapWavePointsLatitude = []
        self.mapWavePointsLongitude = []
        self.mapWaveTriangles = []
        self.mapWaveMaskedTriangles = []
        self.mapWaveTimes = []
        self.mapSWH = []

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
            
        if(self.waterExists):
            with open(dataToGraph["WATER"]) as outfile:
                waterDataset = json.load(outfile)
            with open(dataToGraph["DIFF"]) as outfile:
                waterDiffDataset = json.load(outfile)
                
            waterTimestampsInitialized = False
            waterDiffTimestampsInitialized = False
            for stationKey in waterDataset.keys():
                if(stationKey == "map_data"):
                    self.mapWaterTriangles = waterDataset["map_data"]["map_triangles"]
                    self.mapWaterMaskedTriangles = waterDataset["map_data"]["map_maskedTriangles"]
                    self.mapWaterTimes = waterDataset["map_data"]["map_times"]
                    self.mapWaterPoints = waterDataset["map_data"]["map_points"]
                    self.mapWaterPointsLatitudes = waterDataset["map_data"]["map_pointsLatitudes"]
                    self.mapWaterPointsLongitudes = waterDataset["map_data"]["map_pointsLongitude"]
                    self.mapWaters = waterDataset["map_data"]["map_water"]
                    self.diffWaters = waterDiffDataset["map_data"]["map_water"]
                    for index in range(len(self.mapWaterTimes)):
                        for nodeIndex in range(len(self.mapWaters[index])):
                            pointWater = self.mapWaters[index][nodeIndex]
#                             pointWater = self.mapWaters[index][nodeIndex] - self.diffWaters[index][nodeIndex]
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
                        datapointDiffWaters = []
                        for index in range(len(waterDataset[stationKey]["times"])):
                            if(self.waterStartDate == None):
                                self.waterStartDate = datetime.fromtimestamp(int(waterDataset[stationKey]["times"][index]), timezone.utc)
                            if(not waterTimestampsInitialized):
                                self.waterTimes.append(self.unixTimeToDeltaHours(waterDataset[stationKey]["times"][index], self.waterStartDate))
#                             print(len(waterDataset[stationKey]["water"]), len(waterDiffDataset[stationKey]["water"]))
                            datapointWater = waterDataset[stationKey]["water"][index]
                            datapointWaters.append(datapointWater)
                        waterTimestampsInitialized = True
                        for index in range(len(waterDiffDataset[stationKey]["times"])):
                            if(not waterDiffTimestampsInitialized):
                                self.waterDiffTimes.append(self.unixTimeToDeltaHours(waterDiffDataset[stationKey]["times"][index], self.waterStartDate))
#                             print(len(waterDataset[stationKey]["water"]), len(waterDiffDataset[stationKey]["water"]))
                            datapointDiffWaters.append(waterDiffDataset[stationKey]["water"][index])
#                             datapointWaters.append(waterDataset[stationKey]["water"][index])
                        waterDiffTimestampsInitialized = True
                        self.datapointsWaters.append(datapointWaters)
                        self.datapointsDiffWaters.append(datapointDiffWaters)
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
                    self.waveLabels.append(nodeIndex)
                    self.waveLatitudes.append(iteratorDataset[stationKey]["latitude"])
                    self.waveLongitudes.append(iteratorDataset[stationKey]["longitude"])
                    if(not obsLabelsInitialized):
                        self.obsLabels.append(self.obsMetadata["NOS"][stationKey]["name"])
                        self.obsLatitudes.append(float(self.obsMetadata["NOS"][stationKey]["latitude"]))
                        self.obsLongitudes.append(float(self.obsMetadata["NOS"][stationKey]["longitude"]))

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
            obsLabelsInitialized = True              

    def generateGraphs(self):
        graph_directory = "graphs/"
        
        numberOfDatapoints = 0
#         TODO: Currently, when graphing multiple products with obs on, OBS_STATIONS must contain the same number of station 
#           entries for each type of product
        if(self.tideExists):
            numberOfDatapoints = len(self.tideDatapointsTimes)
        if(self.gaugeExists):
            numberOfDatapoints = len(self.gaugeDatapointsTimes)
        if(self.obsExists):
            numberOfDatapoints = len(self.obsDatapointsTimes)
        elif(self.windExists):
            numberOfDatapoints = len(self.windLabels)
        elif(self.wavesExists):
            numberOfDatapoints = len(self.waveLabels)
        elif(self.rainExists):
            numberOfDatapoints = len(self.rainLabels)
        elif(self.waterExists):
            numberOfDatapoints = len(self.waterLabels)
        print("numberOfDatapoints", numberOfDatapoints, flush=True)
        fig, ax = plt.subplots()
        print("maxWind", self.maxWind, "maxRain", self.maxRain, "maxWave", self.maxSWH, "maxWater", self.maxWater, flush=True)
        
        ax.scatter(self.obsLongitudes, self.obsLatitudes, label="Obs")
        if(self.windExists):
            ax.scatter(self.windLongitudes, self.windLatitudes, label="Wind")
        if(self.wavesExists):
            ax.scatter(self.waveLongitudes, self.waveLatitudes, label="Waves")
        if(self.gaugeExists):
                ax.scatter(self.gaugeLongitudes, self.gaugeLatitudes, label="Gauge")
        if(self.rainExists):
            ax.scatter(self.rainLongitudes, self.rainLatitudes, label="Rain")
        if(self.tideExists):
                ax.scatter(self.tideLongitudes, self.tideLatitudes, label="Tide")
        if(self.waterExists):
            ax.scatter(self.waterLongitudes, self.waterLatitudes, label="Water")
        ax.legend(loc="lower right")

        for index, label in enumerate(self.obsLabels):
            ax.annotate(label, (self.obsLongitudes[index], self.obsLatitudes[index]))
            if(self.windExists):
                ax.annotate(self.windLabels[index], (self.windLongitudes[index], self.windLatitudes[index]))
            if(self.wavesExists):
                ax.annotate(self.waveLabels[index], (self.waveLongitudes[index], self.waveLatitudes[index]))
            if(self.waterExists):
                ax.annotate(self.waterLabels[index], (self.waterLongitudes[index], self.waterLatitudes[index]))
        for index, label in enumerate(self.gaugeLabels):
            ax.annotate(label, (self.gaugeLongitudes[index], self.gaugeLatitudes[index]))
            if(self.rainExists):
                ax.annotate(self.rainLabels[index], (self.rainLongitudes[index], self.rainLatitudes[index]))
        for index, label in enumerate(self.tideLabels):
            ax.annotate(label, (self.tideLongitudes[index], self.tideLatitudes[index]))
            if(self.waterExists):
                ax.annotate(self.waterLabels[index], (self.waterLongitudes[index], self.waterLatitudes[index]))
            
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
            vmax = 50
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
            fig, ax = plt.subplots()
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
#             vmax = math.ceil(self.maxRain)
            vmax = 25
            vmaxAccumulation = 500
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
#         if(len(self.mapWaterTimes) > 0):
#             vmin = -1
#             vmax = math.ceil(self.maxWater)
# #             vmax = 20
#             levels = 100
#             levelBoundaries = np.linspace(vmin, vmax, levels + 1)
#             waterTriangulation = Triangulation(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, triangles=self.mapWaterTriangles, mask=self.mapWaterMaskedTriangles)
#             for index in range(len(self.mapWaterTimes)):
#                 fig, ax = plt.subplots()
#     #             print(self.endWavePointsLongitudes)
#     #             print(self.endWavePointsLatitudes)
#     #             print(self.endSWH)
#                 plt.imshow(img, extent=self.backgroundAxis, alpha=0.6, aspect=aspectRatio, zorder=2)
#                 contourset = ax.tripcolor(waterTriangulation, self.mapWaters[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
# #               Todo: Fix triangulation errors
# #                 contourset = ax.tripcolor(self.mapWaterPointsLongitudes, self.mapWaterPointsLatitudes, self.mapWaters[index], shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
#                 plt.axis(plotAxis)
#                 plt.title("Water Elevation")
#                 plt.xlabel(datetime.fromtimestamp(int(self.mapWaterTimes[index]),timezone.utc))
#     #             plt.gca().invert_yaxis()
#                 plt.colorbar(
#                     ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
#                     ticks=range(vmin, vmax+5, 2),
#                     boundaries=levelBoundaries,
#                     values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
#                     label="Meters",
#                     ax=plt.gca()
#                 )
#                 plt.savefig(graph_directory + 'map_water_' + str(index) + '.png')
#                 plt.close()
#                 gc.collect()
#             with imageio.get_writer(graph_directory + 'water.gif', mode='I') as writer:
#                 for index in range(len(self.mapWaterTimes)):
#                     filename = "map_water_" + str(index) + ".png"
#                     image = imageio.imread(graph_directory + filename)
#                     writer.append_data(image)
#                 for index in range(len(self.mapWaterTimes)):
#                     filename = "map_water_" + str(index) + ".png"
#                     os.remove(graph_directory + filename)
#             mapWatersNoNan = np.nan_to_num(self.mapWaters)
#             swathWaters = np.max(self.mapWaters, axis=0)
#             fig, ax = plt.subplots()
#             plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
#             contourset = ax.tripcolor(waterTriangulation, swathWaters, shading='gouraud', cmap="jet", vmin=vmin, vmax=vmax, zorder=1)
#             plt.axis(plotAxis)
#             plt.title("Water Swath")
# #             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
# #             graphs up to 10 m/s, ~20 knots
#             plt.colorbar(
#                 ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
#                 ticks=range(vmin, vmax+5, 2),
#                 boundaries=levelBoundaries,
#                 values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
#                 label="Meters",
#                 ax=plt.gca()
#             )
#             plt.savefig(graph_directory + 'map_water_swath.png')
#             plt.close()
#             gc.collect()
        if(len(self.mapWaveTimes) > 0):
            vmin = 0
            vmax = math.ceil(self.maxWave)
            levels = 100
            levelBoundaries = np.linspace(vmin, vmax, levels + 1)
            waveTriangulation = Triangulation(self.mapWavePointsLongitudes, self.mapWavePointsLatitudes, triangles=self.mapWaveTriangles, mask=self.mapWaveMaskedTriangles)
            for index in range(len(self.mapWaveTimes)):
                fig, ax = plt.subplots()
    #             print(self.endWavePointsLongitudes)
    #             print(self.endWavePointsLatitudes)
    #             print(self.endSWH)
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
            mapSWHNoNan = np.nan_to_num(self.mapSWH)
            swathSWH = np.max(mapSWHNoNan, axis=0)
            fig, ax = plt.subplots()
            plt.imshow(img, alpha=0.5, extent=self.backgroundAxis, aspect=aspectRatio, zorder=2)
            contourset = ax.tricontourf(waveTriangulation, swathSWH, levelBoundaries, alpha=0.5, vmin=vmin, vmax=vmax)
            plt.axis(plotAxis)
            plt.title("Wave Significant Wave Height Swath")
#             plt.xlabel(datetime.fromtimestamp(int(self.mapWindTimes[index]), timezone.utc))
#             graphs up to 10 m/s, ~20 knots
            plt.colorbar(
                ScalarMappable(norm=contourset.norm, cmap=contourset.cmap),
                ticks=range(vmin, vmax+5, 5),
                boundaries=levelBoundaries,
                values=(levelBoundaries[:-1] + levelBoundaries[1:]) / 2,
                label="Meters",
                ax=plt.gca()
            )        
            plt.savefig(graph_directory + 'map_swh_swath.png')
            plt.close()
            gc.collect()
        # Plot wind speed over time
        for index in range(numberOfDatapoints):
            if(len(self.datapointsSpeeds) > 0):
                fig, ax = plt.subplots()
                ax.scatter(self.windTimes, self.datapointsSpeeds[index], marker=".", label="Forecast")
                if(self.obsExists):
                    ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsSpeeds[index], marker=".", label="Obs")
                ax.legend(loc="lower right")
                stationName = self.obsLabels[index]
                plt.title(stationName + " station wind speed")
                plt.xlabel("Hours since " + self.windStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("wind speed (m/s)")
                plt.savefig(graph_directory + stationName + '_wind_speed.png')
                plt.close()
            if(len(self.datapointsDirections) > 0):
                fig, ax = plt.subplots()
                ax.scatter(self.windTimes, self.datapointsDirections[index], marker=".", label="Forecast")
                if(self.obsExists):
                    ax.scatter(self.obsDatapointsTimes[index], self.obsDatapointsDirections[index], marker=".", label="Obs")
                ax.legend(loc="lower right")
                stationName = self.obsLabels[index]
                plt.title(stationName + " station wind directions")
                plt.xlabel("Hours since " + self.windStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("wind direction (degrees)")
                plt.savefig(graph_directory + stationName + '_wind_direction.png')
                plt.close()
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
            if(len(self.datapointsWaters) > 0):
                fig, ax = plt.subplots()
                ax.plot(self.waterTimes, self.datapointsWaters[index], label="Forecast")
                ax.plot(self.waterDiffTimes, self.datapointsDiffWaters[index], label="Diff")
                if(self.tideExists):
                    ax.plot(self.tideDatapointsTimes[index], self.tideDatapointsWaters[index], label="Tide Station")
                ax.legend(loc="upper left")
                stationName = self.tideLabels[index]
                plt.title(stationName + " station water elevation")
                plt.xlabel("Hours since " + self.waterStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("elevation (meters)")
                plt.savefig(graph_directory + stationName + '_water.png')
                plt.close()
            if(self.wavesExists):
                if(len(self.datapointsSWH[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsSWH[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station significant wave height")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("SWH (meters)")
                    plt.savefig(graph_directory + stationName + '_wave_swh.png')
                    plt.close()
                if(len(self.datapointsMWD[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsMWD[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station mean wave direction")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("MWD (degrees)")
                    plt.savefig(graph_directory + stationName + '_wave_mwd.png')
                    plt.close()
                if(len(self.datapointsMWP[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsMWP[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station mean wave period")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("MWP (seconds)")
                    plt.savefig(graph_directory + stationName + '_wave_mwp.png')
                    plt.close()
                if(len(self.datapointsPWP[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsPWP[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station peak wave period")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("PWP (seconds)")
                    plt.savefig(graph_directory + stationName + '_wave_pwp.png')
                    plt.close()
                if(len(self.datapointsRADMag[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADMag[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station radiation stress magnitude")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad Stress Magitude (1/m^2s^2)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_mag.png')
                    plt.close()
                if(len(self.datapointsRADDir[index]) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADDir[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station radiation stress direction")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad stress direction (degrees)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_dir.png')
                    plt.close()
                
           