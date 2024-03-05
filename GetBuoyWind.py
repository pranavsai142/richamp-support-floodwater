# Queries NOAA NOS buoys and saves the data
# Pranav 9/25/2023
# Fuck matlab

import scipy.io
from urllib.request import urlretrieve
from urllib.error import HTTPError
from datetime import datetime, timedelta
import json
from Encoders import NumpyEncoder
        
NOS_STATIONS_FILE_NAME = "NOS_Stations.json"
# NOS_WIND_FILE_NAME = "NOS_DEB_Wind.json"
NOS_WIND_FILE_NAME = "NOS_Wind.json"

class GetBuoyWind:
	def __init__(self, NOS_STATIONS_FILE_NAME=NOS_STATIONS_FILE_NAME, NOS_WIND_FILE_NAME=NOS_WIND_FILE_NAME, startDateObject="", endDateObject=""):
		print(type(startDateObject))
		print(startDateObject)
		with open(NOS_STATIONS_FILE_NAME) as stations_file:
			stationsDict = json.load(stations_file)

		# stationIds = [8413320, 8443970, 8447435, 8449130, 8447930, 8452660, 8510560, 8418150, 8419870, 8454049, 8454000, 8461490, 8411060, 8531680, 8534720, 8452944]
		# stationNames = ['Bar Harbor', 'Boston', 'Chatham', 'Nantucket', 'Woods Hole', 'Newport', 'Montauk', 'Portland', 'Seavey Island, ME', 'Quonset Point', 'Providence', 'New London', 'Cutler Faris Wharf', 'Sandy Hook', 'Altlantic City', 'Conimicut Light'] 
		stationIds = [8413320, 8447435, 8449130, 8452660, 8418150, 8454049, 8454000, 8411060, 8531680, 8452944]
		stationNames = ['Bar Harbor', 'Chatham', 'Nantucket', 'Newport', 'Portland', 'Quonset Point', 'Providence', 'Cutler Faris Wharf', 'Sandy Hook', 'Conimicut Light'] 

		startDate = startDateObject.strftime("%Y%m%d")
		endDate = endDateObject.strftime("%Y%m%d")
		dateStartFormat = startDateObject.strftime("%Y-%m-%d")

		heightStartDate = startDateObject.strftime("%Y-%m-%dT%H:%M:%SZ")
		heightEndDate = endDateObject.strftime("%Y-%m-%dT%H:%M:%SZ")

		# Noreaster 12/23 festivus  storm 22, 23
		# startDate = "20221220"
		# endDate = "20221224"
		# dateStartFormat = "2022-12-20"
		# 
		# heightStartDate = "2022-12-20T00:00:00Z"
		# heightEndDate = "2022-12-24T23:59:59Z"
	
		badStations = []
		windDict = {}
		for key in stationsDict["NOS"].keys():
			stationDict = stationsDict["NOS"][key]
			stationId = stationDict["id"]
			stationName = stationDict["name"]
			url = "https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Wind.mat?STATION_ID%2Ctime%2CWind_Speed%2CWind_Direction%2CWind_Gust&STATION_ID%3E=%22" + stationId + "%22&BEGIN_DATE%3E=%22" + startDate + "%22&END_DATE%3E=%22" + endDate + "%22&time%3E=" + dateStartFormat + "T00%3A00%3A00Z"
			heightURL = "https://opendap.co-ops.nos.noaa.gov/ioos-dif-sos/SOS?service=SOS&request=GetObservation&version=1.0.0&observedProperty=water_surface_height_above_reference_datum&offering=urn:ioos:station:NOAA.NOS.CO-OPS:" + stationId + "&responseFormat=text/csv&eventTime=" + heightStartDate + "/" + heightEndDate + "&unit=Meters"
		#     sensorURL = 'https://ioos-dif-sos-prod.co-ops-aws-east1.net/ioos-dif-sos/SOS?service=SOS&request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&procedure=urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
			matFilename = stationDict["id"] + ".mat"
			heightFilename = stationDict["id"] + "_height.csv"
		#     sensorFilename = stationDict["id"] + "_sensor"
			try:
		#     Once mat files are downloaded once, comment out this line to stop querying the API
				urlretrieve(url, matFilename)
				urlretrieve(heightURL, heightFilename)
		#     	urlretrieve(sensorURL, sensorFilename)
				data = scipy.io.loadmat(matFilename)
				unixTimes = data["IOOS_Wind"]["time"][0][0].flatten()
				windDirections = data["IOOS_Wind"]["Wind_Direction"][0][0].flatten()
				windSpeeds = data["IOOS_Wind"]["Wind_Speed"][0][0].flatten()
				windGusts = data["IOOS_Wind"]["Wind_Gust"][0][0].flatten()
				windDict[key] = {}
				windDict[key]["times"] = unixTimes
				windDict[key]["directions"] = windDirections
				windDict[key]["speeds"] = windSpeeds
				windDict[key]["gusts"] = windGusts
		
		
				file = open(heightFilename)
				csvHeightTimes = []
				csvHeightValues = []
				skipHeader = True
				for line in file:
					if(skipHeader):
						skipHeader = False
					else:
						data = line.split(",")
		#     			print(data)
						heightFormattedTime = data[4]
						year = int(heightFormattedTime[0:4])
						month = int(heightFormattedTime[5:7])
						day = int(heightFormattedTime[8:10])
						hour = int(heightFormattedTime[11:13])
						minute = int(heightFormattedTime[14:16])
						second = int(heightFormattedTime[17:19])
				
						heightTime = datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)
				
						heightValue = float(data[5])
						csvHeightTimes.append(datetime.timestamp(heightTime))
						csvHeightValues.append(heightValue)
				print("CSV and .mat same length? " + stationName, len(csvHeightTimes) == len(unixTimes))
				print("CSV height Times vs unixTimes len", len(csvHeightTimes), len(unixTimes))
				heightTime = datetime.timestamp(datetime(year=3000, month=1, day=1))
				csvHeightTimes.append(heightTime)
				heightIndex = 0
				heightValues = []
				for unixTime in unixTimes:
					if(unixTime > csvHeightTimes[heightIndex + 1]):
						heightIndex += 1
					heightValues.append(csvHeightValues[heightIndex])
				windDict[key]["heights"] = heightValues
			except (HTTPError, FileNotFoundError):
		#     	print("oops bad url")
				badStations.append(badStations.append(stationDict))
		
		# print(windDict)
		with open(NOS_WIND_FILE_NAME, "w") as outfile:
			json.dump(windDict, outfile, cls=NumpyEncoder)