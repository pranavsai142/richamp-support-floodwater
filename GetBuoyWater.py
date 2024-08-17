# Queries NOAA NOS buoys and saves the data
# Pranav 9/25/2023
# Fuck matlab

import scipy.io
from urllib.request import urlretrieve
from urllib.error import HTTPError
from datetime import datetime, timedelta
import json
from Encoders import NumpyEncoder
        
class GetBuoyWater:
    def __init__(self, STATIONS_FILE="", OBS_WATER_DATA_FILE="", startDateObject="", endDateObject=""):
        temp_directory = OBS_WATER_DATA_FILE[0:OBS_WATER_DATA_FILE.rfind("/") + 1]
        print(type(startDateObject), flush=True)
        print(startDateObject, flush=True)
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)

        # stationIds = [8413320, 8443970, 8447435, 8449130, 8447930, 8452660, 8510560, 8418150, 8419870, 8454049, 8454000, 8461490, 8411060, 8531680, 8534720, 8452944]
        # stationNames = ['Bar Harbor', 'Boston', 'Chatham', 'Nantucket', 'Woods Hole', 'Newport', 'Montauk', 'Portland', 'Seavey Island, ME', 'Quonset Point', 'Providence', 'New London', 'Cutler Faris Wharf', 'Sandy Hook', 'Altlantic City', 'Conimicut Light'] 
        stationIds = [8413320, 8447435, 8449130, 8452660, 8418150, 8454049, 8454000, 8411060, 8531680, 8452944]
        stationNames = ['Bar Harbor', 'Chatham', 'Nantucket', 'Newport', 'Portland', 'Quonset Point', 'Providence', 'Cutler Faris Wharf', 'Sandy Hook', 'Conimicut Light'] 

        startDate = startDateObject.strftime("%Y%m%d")
        endDate = endDateObject.strftime("%Y%m%d")
        startDateFormat = startDateObject.strftime("%Y-%m-%d")
        endDateFormat = endDateObject.strftime("%Y-%m-%d")

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
        waterDict = {}
        for key in stationsDict["NOS"].keys():
            stationDict = stationsDict["NOS"][key]
            stationId = stationDict["id"]
            stationName = stationDict["name"]
# https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Hourly_Height_Verified_Water_Level.htmlTable?STATION_ID%2CDATUM%2CBEGIN_DATE%2CEND_DATE%2Ctime%2CWL_VALUE%2CSIGMA&STATION_ID=%228452660%22&DATUM%3E=%22MSL%22&BEGIN_DATE%3E=%222024-07-29%22&END_DATE%3E=%222024-08-10%22
            url = "https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Hourly_Height_Verified_Water_Level.mat?STATION_ID%2CDATUM%2CBEGIN_DATE%2CEND_DATE%2Ctime%2CWL_VALUE%2CSIGMA&STATION_ID=%22"  + stationId + "%22&DATUM%3E=%22MSL%22&BEGIN_DATE%3E=%22" + startDateFormat + "%22&END_DATE%3E=%22" + endDateFormat + "%22"
        #     sensorURL = 'https://ioos-dif-sos-prod.co-ops-aws-east1.net/ioos-dif-sos/SOS?service=SOS&request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&procedure=urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
            matFilename = temp_directory + stationDict["id"] + ".mat"
        #     sensorFilename = stationDict["id"] + "_sensor"
            try:
        #     Once mat files are downloaded once, comment out this line to stop querying the API
                urlretrieve(url, matFilename)
        #         urlretrieve(sensorURL, sensorFilename)
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
        
            except (HTTPError, FileNotFoundError):
        #         print("oops bad url")
                badStations.append(badStations.append(stationDict))
        
        # print(windDict)
        with open(OBS_WATER_DATA_FILE, "w") as outfile:
            json.dump(waterDict, outfile, cls=NumpyEncoder)
