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
    
    def unixTimeToDeltaHours(self, timestamp):
        delta = datetime.fromtimestamp(timestamp) - self.startDate
        return delta.total_seconds()/3600
    
    def extrapolateWindToTenMeterHeight(self, windVelocity, altitude):
        return windVelocity
    #     WIND_PROFILE_EXPONENT = 0.11
    #     return windVelocity * ((10.0/altitude)**WIND_PROFILE_EXPONENT)
    
    def __init__(self, graphObs=False, graphRain=False, WIND_TYPE="", WIND_DATA_FILE="", RAIN_DATA_FILE="", OBS_WIND_FILE="", STATIONS_FILE=""):
        with open(WIND_DATA_FILE) as outfile:
            floodwaterStationsWindData = json.load(outfile)
        
        with open(STATIONS_FILE) as outfile:
            self.obsStationsData = json.load(outfile)["NOS"]
        
        self.graphObs=graphObs
        self.graphRain=graphRain
        self.WIND_TYPE = WIND_TYPE
        
        if(self.graphObs):
            with open(OBS_WIND_FILE) as outfile:
                self.obsWindData = json.load(outfile)
                
        if(self.graphRain):
            with open(RAIN_DATA_FILE) as outfile:
                floodwaterStationsRainData = json.load(outfile)
            
        self.floodwaterStationsLatitudes = []
        self.floodwaterStationsLongitudes = []
        self.floodwaterStationsNodeLabels = []
        self.floodwaterStationsTimes = []
        self.floodwaterStationsWindDirections = []
        self.floodwaterStationsWindSpeeds = []
        self.floodwaterStationsRains = []
        self.nosLatitudes = []
        self.nosLongitudes = []
        self.stationLabels = []
        self.nosTimes = []
        self.nosWindDirections = []
        self.nosWindSpeeds = []
        self.nosStationsHeights = []
        self.startDate = None
        for nodeIndex in floodwaterStationsWindData.keys():
            stationKey = floodwaterStationsWindData[nodeIndex]["stationKey"]
            if((self.graphObs and stationKey in self.obsWindData.keys()) or (not self.graphObs)):
                self.floodwaterStationsNodeLabels.append(nodeIndex)
                self.floodwaterStationsLatitudes.append(floodwaterStationsWindData[nodeIndex]["latitude"])
                self.floodwaterStationsLongitudes.append(floodwaterStationsWindData[nodeIndex]["longitude"])
#                 self.floodwaterStationWindsX = floodwaterStationsWindData[nodeIndex]["windsX"]
#                 self.floodwaterStationWindsY = floodwaterStationsWindData[nodeIndex]["windsY"]
                floodwaterStationTimes = []
                floodwaterStationWindDirections = []
                floodwaterStationWindSpeeds = []
                floodwaterStationRains = []
                for index in range(len(floodwaterStationsWindData[nodeIndex]["times"])):
                    if(self.startDate == None):
                        self.startDate = datetime.fromtimestamp(int(floodwaterStationsWindData[nodeIndex]["times"][index]))
                    floodwaterStationTimes.append(self.unixTimeToDeltaHours(floodwaterStationsWindData[nodeIndex]["times"][index]))
                    if(self.WIND_TYPE == "GFS" or self.WIND_TYPE == "FORT"):
                        floodwaterWindX = floodwaterStationsWindData[nodeIndex]["windsX"][index]
                        floodwaterWindY = floodwaterStationsWindData[nodeIndex]["windsY"][index]
                        floodwaterWindSpeed = self.vectorSpeed(floodwaterWindX, floodwaterWindY)
                        floodwaterWindDirection = self.vectorDirection(floodwaterWindX, floodwaterWindY)
                    elif(self.WIND_TYPE == "POST"):
                        floodwaterWindSpeed = floodwaterStationsWindData[nodeIndex]["speeds"][index]
                        floodwaterWindDirection = floodwaterStationsWindData[nodeIndex]["directions"][index]
                    floodwaterStationWindDirections.append(floodwaterWindDirection)
                    floodwaterStationWindSpeeds.append(floodwaterWindSpeed)
                    if(self.graphRain):
                        floodwaterStationRains.append(floodwaterStationsRainData[nodeIndex]["rains"][index])
        
                self.floodwaterStationsTimes.append(floodwaterStationTimes)
                self.floodwaterStationsWindDirections.append(floodwaterStationWindDirections)
                self.floodwaterStationsWindSpeeds.append(floodwaterStationWindSpeeds)
                self.floodwaterStationsRains.append(floodwaterStationRains)
                if(self.graphObs):
                    self.stationLabels.append(self.obsStationsData[stationKey]["name"])
                    self.nosLatitudes.append(float(self.obsStationsData[stationKey]["latitude"]))
                    self.nosLongitudes.append(float(self.obsStationsData[stationKey]["longitude"]))
                    nosStationTimes = []
                    nosStationWindSpeeds = []
                    nosStationHeights = []
                    for index in range(len(self.obsWindData[stationKey]["times"])):
                        nosStationTimes.append(self.unixTimeToDeltaHours(self.obsWindData[stationKey]["times"][index]))
                        nosStationWindSpeed = self.obsWindData[stationKey]["speeds"][index]
                        nosStationHeight = self.obsWindData[stationKey]["heights"][index]
                        nosStationAltitude = None
                        nosStationWindSpeeds.append(self.extrapolateWindToTenMeterHeight(nosStationWindSpeed, nosStationAltitude))
                        nosStationHeights.append(nosStationHeight)
                    self.nosTimes.append(nosStationTimes)
                    self.nosWindSpeeds.append(nosStationWindSpeeds)
                    self.nosWindDirections.append(self.obsWindData[stationKey]["directions"])
                    self.nosStationsHeights.append(nosStationHeights)
        

    def generateGraphs(self):
        graph_directory = "graphs/"
        
        if(self.graphObs):
            numberOfStations = len(self.nosTimes)
        else:
            numberOfStations = len(self.floodwaterStationsTimes)
        print("numberOfStations", numberOfStations)
        fig, ax = plt.subplots()
        ax.scatter(self.floodwaterStationsLongitudes, self.floodwaterStationsLatitudes, label="ricv1")
        ax.scatter(self.nosLongitudes, self.nosLatitudes, label="Buoy")
        ax.legend(loc="lower right")

        for index, stationLabel in enumerate(self.stationLabels):
            ax.annotate(stationLabel, (self.nosLongitudes[index], self.nosLatitudes[index]))
            ax.annotate(self.floodwaterStationsNodeLabels[index], (self.floodwaterStationsLongitudes[index], self.floodwaterStationsLatitudes[index]))
            
        plt.title("nos station points and closest gfs, adcirc (asgs, floodwater) in mesh plotted")
        plt.xlabel("longitude")
        plt.ylabel("latitude")
        plt.savefig(graph_directory + 'closest_points.png')
        # Plot wind speed over time
        for index in range(numberOfStations):
            fig, ax = plt.subplots()
            ax.scatter(self.floodwaterStationsTimes[index], self.floodwaterStationsWindSpeeds[index], marker=".", label="Floodwater")
            if(self.graphObs):
                ax.scatter(self.nosTimes[index], self.nosWindSpeeds[index], marker=".", label="Buoy")
            ax.legend(loc="lower right")
            if(self.graphObs):
                stationName = self.stationLabels[index]
            else:
                stationName = self.floodwaterStationsNodeLabels[index]
            plt.title(stationName + " station observational vs forecast wind speed")
            plt.xlabel("Hours since " + self.startDate.strftime(self.DATE_FORMAT))
            plt.ylabel("wind speed (m/s)")
            plt.savefig(graph_directory + stationName + '_wind.png')
            
        if(self.graphRain):
            for index in range(numberOfStations):
                fig, ax = plt.subplots()
                ax.scatter(self.floodwaterStationsTimes[index], self.floodwaterStationsRains[index], marker=".", label="GFS")
                ax.legend(loc="upper right")
                if(self.graphObs):
                    stationName = self.stationLabels[index]
                else:
                    stationName = self.floodwaterStationsNodeLabels[index]
                plt.title(stationName + " station forecasted rain")
                plt.xlabel("Hours since " + self.startDate.strftime(self.DATE_FORMAT))
                plt.ylabel("rain accumlation over 1 hr (mm)")
                plt.savefig(graph_directory + stationName + '_rain.png')
        quit()
