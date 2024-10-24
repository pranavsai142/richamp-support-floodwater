import os
import json
import math
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

class Grapher:
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
        delta = datetime.fromtimestamp(timestamp) - startDate
        return delta.total_seconds()/3600
    
    def extrapolateWindToTenMeterHeight(self, windVelocity, altitude):
        return windVelocity
    #     WIND_PROFILE_EXPONENT = 0.11
    #     return windVelocity * ((10.0/altitude)**WIND_PROFILE_EXPONENT)
    
    def __init__(self, dataToGraph={}, STATIONS_FILE=""):
        print("hi")
        self.obsExists = False
        self.windExists = False
        self.wavesExists = False
        self.rainExists = False
        
        self.windStartDate = None
        self.waveStartDate = None
        self.rainStartDate = None
        if("OBS" in dataToGraph):
            self.obsExists = True
        if("POST" in dataToGraph or "GFS" in dataToGraph or "FORT" in dataToGraph):
            self.windExists = True
        if("SWH" in dataToGraph or "MWD" in dataToGraph or "MWP" in dataToGraph or "PWP" in dataToGraph or "RAD" in dataToGraph):
            self.wavesExists = True
        if("RAIN" in dataToGraph):
            self.rainExists = True
        with open(STATIONS_FILE) as outfile:
            self.obsMetadata = json.load(outfile)["NOS"]
            
                
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
        
        self.windLongitudes = []
        self.windLatitudes = []
        self.windLabels = []
        self.windTimes = []
        
        self.datapointsDirections = []
        self.datapointsSpeeds = []
        
        self.rainLongitudes = []
        self.rainLatitudes = []
        self.rainLabels = []
        self.rainTimes = []
        
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

#        So loading obs, wind, and waves should be able to cover and set all available data

        windType = ""
        if("OBS" in dataToGraph):
            with open(dataToGraph["OBS"]) as outfile:
                obsDataset = json.load(outfile)
        if("POST" in dataToGraph):  
            windType = "POST"
            with open(dataToGraph["POST"]) as outfile:
                windDataset = json.load(outfile)
        if("GFS" in dataToGraph):
            windType = "GFS"
            with open(dataToGraph["GFS"]) as outfile:
                windDataset = json.load(outfile)
        if("FORT" in dataToGraph):
            windType = "FORT"
            with open(dataToGraph["FORT"]) as outfile:
                windDataset = json.load(outfile)
                  
        if(self.windExists):
            windTimestampsInitialized = False
            for nodeIndex in windDataset.keys():
                stationKey = windDataset[nodeIndex]["stationKey"]
                if(stationKey in self.obsWindData.keys()):
                    self.windLabels.append(nodeIndex)
                    self.windLatitudes.append(windDataset[nodeIndex]["latitude"])
                    self.windLongitudes.append(windDataset[nodeIndex]["longitude"])
                    
                    if(not obsLabelsInitialized):
                        self.obsLabels.append(self.obsMetadata[stationKey]["name"])
                        self.obsLatitudes.append(float(self.obsMetadata[stationKey]["latitude"]))
                        self.obsLongitudes.append(float(self.obsMetadata[stationKey]["longitude"]))
                    
                    datapointDirections = []
                    datapointSpeeds = []
                    for index in range(len(windDataset[nodeIndex]["times"])):
                        if(self.windstartDate == None):
                            self.windStartDate = datetime.fromtimestamp(int(windDataset[nodeIndex]["times"][index]))
                        if(not windTimestampsInitialized):
                            windTimes.append(self.unixTimeToDeltaHours(windDataset[nodeIndex]["times"][index], self.windStartDate))
                        if(windType == "GFS" or windType == "FORT"):
                            windX = windDataset[nodeIndex]["windsX"][index]
                            windY = windDataset[nodeIndex]["windsY"][index]
                            windSpeed = self.vectorSpeed(windX, windY)
                            windDirection = self.vectorDirection(windX, windY)
                        elif(windType == "POST"):
                            windSpeed = windDataset[nodeIndex]["speeds"][index]
                            windDirection = windDataset[nodeIndex]["directions"][index]
                        datapointDirections.append(windDirection)
                        datapointSpeeds.append(windSpeed)
                    self.datapointsDirections.append(datapointDirections)
                    self.datapointsSpeeds.append(datapointSpeeds)
                    if(self.obsExists):
                        obsTimes = []
                        obsSpeeds = []
                        obsDirections = []
#                         Height is not station altitude, it is sea surface height
                        obsHeights = []
                        for index in range(len(self.obsWindData[stationKey]["times"])):
                            obsTimes.append(self.unixTimeToDeltaHours(obsDataset[stationKey]["times"][index], self.windStartDate))
                            obsSpeed = self.obsWindData[stationKey]["speeds"][index]
                            obsDirection = self.obsWindData[stationKey]["directions"][index]
                            obsHeight = self.obsWindData[stationKey]["heights"][index]
                            nosStationWindSpeeds.append(self.extrapolateWindToTenMeterHeight(nosStationWindSpeed, nosStationAltitude))
                            nosStationHeights.append(nosStationHeight)
                        self.obsDatapointsTimes.append(obsTimes)
                        self.obsDatapointsSpeeds.append(obsSpeeds)
                        self.obsDatapointsDirections.append(obsDataset[stationKey]["directions"])
                        self.obsDatapointsHeights.append(obsHeights)
            obsLabelsInitialized = True
                        
        if(self.rainExists):
            with open(dataToGraph["RAIN"]) as outfile:
                rainDataset = json.load(outfile)
                
            rainTimestampsInitialized = False
            for nodeIndex in rainDataset.keys():
                stationKey = windDataset[nodeIndex]["stationKey"]
                self.rainLabels.append(nodeIndex)
                self.windLatitudes.append(rainDataset[nodeIndex]["latitude"])
                self.windLongitudes.append(rainDataset[nodeIndex]["longitude"])
                
                if(not obsLabelsInitialized):
                    self.obsLabels.append(self.obsMetadata[stationKey]["name"])
                    self.obsLatitudes.append(float(self.obsMetadata[stationKey]["latitude"]))
                    self.obsLongitudes.append(float(self.obsMetadata[stationKey]["longitude"]))

                datapointRains = []
                for index in range(len(rainDataset[nodeIndex]["times"])):
                    if(self.rainStartDate == None):
                        self.rainStartDate = datetime.fromtimestamp(int(rainDataset[nodeIndex]["times"][index]))
                    if(not rainTimestampsInitialized):
                        rainTimes.append(self.unixTimeToDeltaHours(rainDataset[nodeIndex]["times"][index], self.rainStartDate))
                    datapointRains.append(rainDataset[nodeIndex]["rains"][index])
                self.datapointsRains.append(datapointRains)
            obsLabelsInitialized = True
                        
        if(self.wavesExists):
            swhExists = False
            mwdExists = False
            mwpExists = False
            pwdExists = False
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
            for nodeIndex in iteratorDataset.keys():
                stationKey = iteratorDataset[nodeIndex]["stationKey"]
                self.waveLabels.append(nodeIndex)
                self.waveLatitudes.append(iteratorDataset[nodeIndex]["latitude"])
                self.waveLongitudes.append(iteratorDataset[nodeIndex]["longitude"])
                if(not obsLabelsInitialized):
                    self.obsLabels.append(self.obsMetadata[stationKey]["name"])
                    self.obsLatitudes.append(float(self.obsMetadata[stationKey]["latitude"]))
                    self.obsLongitudes.append(float(self.obsMetadata[stationKey]["longitude"]))

                datapointSWH = []
                datapointMWD = []
                datapointMWP = []
                datapointPWP = []
                datapointRADMag = []
                datapointRADDir = []
                for index in range(len(iteratorDataset[nodeIndex]["times"])):
                    if(self.waveStartDate == None):
                        self.waveStartDate = datetime.fromtimestamp(int(iteratorDataset[nodeIndex]["times"][index]))
                    if(not waveTimestampsInitialized):
                        self.waveTimes.append(self.unixTimeToDeltaHours(iteratorDataset[nodeIndex]["times"][index], self.waveStartDate))
                    if(swhExists):
                        datapointSWH.append(swhDataset[nodeIndex]["swh"][index])
                    if(mwdExists):
                        datapointMWD.append(mwdDataset[nodeIndex]["mwd"][index])
                    if(mwpExists):
                        datapointMWP.append(mwpDataset[nodeIndex]["mwp"][index])
                    if(pwpExists):
                        datapointPWP.append(pwpDataset[nodeIndex]["pwp"][index])
                    if(radExists):
                        radX = radDataset[nodeIndex]["radstressX"][index]
                        radY = radDataset[nodeIndex]["radstressY"][index]
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
        if(self.obsExists):
            numberOfDatapoints = len(self.nosTimes)
        elif(self.windExists):
            numberOfDatapoints = len(self.windLabels)
        elif(self.wavesExists):
            numberOfDatapoints = len(self.waveLabels)
        elif(self.rainExists):
            numberOfDatapoints = len(self.rainLabels)
        print("numberOfDatapoints", numberOfDatapoints)
        fig, ax = plt.subplots()
        
        ax.scatter(self.obsLongitudes, self.obsLatitudes, label="Obs")
        if(self.windExists):
            ax.scatter(self.windLongitudes, self.windLatitudes, label="Wind")
        if(self.wavesExists):
            ax.scatter(self.waveLongitudes, self.waveLatitudes, label="Waves")
        if(self.rainExists):
            ax.scatter(self.rainLongitudes, self.rainLatitudes, label="Rain")
        ax.legend(loc="lower right")

        for index, label in enumerate(self.obsLabels):
            ax.annotate(label, (self.obsLongitudes[index], self.obsLatitudes[index]))
            if(self.windExists):
                ax.annotate(self.windLabels[index], (self.windLongitudes[index], self.windLatitudes[index]))
            if(self.wavesExists):
                ax.annotate(self.waveLabels[index], (self.waveLongitudes[index], self.waveLatitudes[index]))
            if(self.rainExists):
                ax.annotate(self.rainLabels[index], (self.rainLongitudes[index], self.rainLatitudes[index]))
            
        plt.title("location of datapoints by data type")
        plt.xlabel("longitude")
        plt.ylabel("latitude")
        plt.savefig(graph_directory + 'closest_points.png')
        # Plot wind speed over time
        for index in range(numberOfDatapoints):
            if(len(self.datapointsSpeeds) > 0):
                fig, ax = plt.subplots()
                ax.scatter(self.windTimes, self.datapointsSpeeds[index], marker=".", label="Forecast")
                if(self.obsExists):
                    ax.scatter(self.obsTimes[index], self.obsDatapointsSpeeds[index], marker=".", label="Obs")
                ax.legend(loc="lower right")
                stationName = self.obsLabels[index]
                plt.title(stationName + " station wind speed")
                plt.xlabel("Hours since " + self.windStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("wind speed (m/s)")
                plt.savefig(graph_directory + stationName + '_wind_speed.png')
            if(len(self.datapointsDirections) > 0):
                fig, ax = plt.subplots()
                ax.scatter(self.windTimes, self.datapointsDirections[index], marker=".", label="Forecast")
                if(self.obsExists):
                    ax.scatter(self.obsTimes[index], self.obsDatapointsDirections[index], marker=".", label="Obs")
                ax.legend(loc="lower right")
                stationName = self.obsLabels[index]
                plt.title(stationName + " station wind directions")
                plt.xlabel("Hours since " + self.windStartDate.strftime(self.DATE_FORMAT))
                plt.ylabel("wind direction (degrees)")
                plt.savefig(graph_directory + stationName + '_wind_direction.png')
                
            if(self.wavesExists):
                if(len(self.datapointsSWH) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsSWH[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station significant wave height")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("SWH (meters)")
                    plt.savefig(graph_directory + stationName + '_wave_swh.png')
                    
                if(len(self.datapointsMWD) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsMWD[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station mean wave direction")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("MWD (degrees)")
                    plt.savefig(graph_directory + stationName + '_wave_mwd.png')
                    
                if(len(self.datapointsMWP) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsMWP[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station mean wave period")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("MWP (seconds)")
                    plt.savefig(graph_directory + stationName + '_wave_mwp.png')
                
                if(len(self.datapointsPWP) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsPWP[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station peak wave period")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("PWP (seconds)")
                    plt.savefig(graph_directory + stationName + '_wave_pwp.png')
                    
                if(len(self.datapointsRADMag) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADMag[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station radiation stress magnitude")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad Stress Magitude (1/m^2s^2)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_mag.png')
            
                if(len(self.datapointsRADDir) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.waveTimes, self.datapointsRADDir[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station radiation stress direction")
                    plt.xlabel("Hours since " + self.waveStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad stress direction (degrees)")
                    plt.savefig(graph_directory + stationName + '_wave_radstress_dir.png')
                
                if(len(self.datapointsRains) > 0):
                    fig, ax = plt.subplots()
                    ax.scatter(self.rainTimes, self.datapointsRains[index], marker=".", label="Forecast")
                    ax.legend(loc="lower right")
                    stationName = self.obsLabels[index]
                    plt.title(stationName + " station radiation stress direction")
                    plt.xlabel("Hours since " + self.rainStartDate.strftime(self.DATE_FORMAT))
                    plt.ylabel("Rad stress direction (degrees)")
                    plt.savefig(graph_directory + stationName + '_rain.png')
           
        quit()
