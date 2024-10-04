# Queries NOAA NOS buoys and saves the data
# Pranav 9/25/2023
# Fuck matlab

import scipy.io
from urllib.request import urlretrieve
from urllib.error import HTTPError
from datetime import datetime, timedelta, timezone
import json
        
class GetObsElevation:
    def __init__(self, STATIONS_FILE="", OBS_ASSET_DATA_FILE=""):
        temp_directory = OBS_ASSET_DATA_FILE[0:OBS_ASSET_DATA_FILE.rfind("/") + 1]
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
            


        # Noreaster 12/23 festivus  storm 22, 23
        # startDate = "20221220"
        # endDate = "20221224"
        # dateStartFormat = "2022-12-20"
        # 
        # heightStartDate = "2022-12-20T00:00:00Z"
        # heightEndDate = "2022-12-24T23:59:59Z"
    
        elevationDict = {}

        for key in stationsDict["ASSET"].keys():
            stationDict = stationsDict["ASSET"][key]
            stationId = stationDict["id"]
            stationName = stationDict["name"]
            elevation = stationDict["elevation"]
            elevationDict[key] = {}
#             Convert to meters
            elevationDict[key]["elevation"] = float(elevation) * 0.3
        
        
        # print(windDict)
        with open(OBS_ASSET_DATA_FILE, "w") as outfile:
            json.dump(elevationDict, outfile)
