# Queries NOAA NOS buoys and saves the data
# Pranav 9/25/2023
# Fuck matlab

import scipy.io
from urllib.request import urlretrieve
from urllib.error import HTTPError
from datetime import datetime, timedelta, timezone
import json
from Encoders import NumpyEncoder
import gzip
import shutil
        
class GetBuoyWaves:
    def __init__(self, STATIONS_FILE="", OBS_WAVE_DATA_FILE="", startDateObject="", endDateObject=""):
        temp_directory = OBS_WAVE_DATA_FILE[0:OBS_WAVE_DATA_FILE.rfind("/") + 1]
        print(type(startDateObject), flush=True)
        print(startDateObject, flush=True)
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)

        # stationIds = [8413320, 8443970, 8447435, 8449130, 8447930, 8452660, 8510560, 8418150, 8419870, 8454049, 8454000, 8461490, 8411060, 8531680, 8534720, 8452944]
        # stationNames = ['Bar Harbor', 'Boston', 'Chatham', 'Nantucket', 'Woods Hole', 'Newport', 'Montauk', 'Portland', 'Seavey Island, ME', 'Quonset Point', 'Providence', 'New London', 'Cutler Faris Wharf', 'Sandy Hook', 'Altlantic City', 'Conimicut Light'] 
        stationIds = [8413320, 8447435, 8449130, 8452660, 8418150, 8454049, 8454000, 8411060, 8531680, 8452944]
        stationNames = ['Bar Harbor', 'Chatham', 'Nantucket', 'Newport', 'Portland', 'Quonset Point', 'Providence', 'Cutler Faris Wharf', 'Sandy Hook', 'Conimicut Light'] 
        
#         if(startDateObject < datetime.now() - timedelta(days=45)) {
#             if()
#         }
#         else {
#             
#         }
        
        startDate = startDateObject.strftime("%Y%m%d")
        endDate = endDateObject.strftime("%Y%m%d")
        startDateFormat = startDateObject.strftime("%Y-%m-%d")
        endDateFormat = endDateObject.strftime("%Y-%m-%d")

        heightStartDate = startDateObject.strftime("%Y-%m-%dT%H:%M:%SZ")
        heightEndDate = endDateObject.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        startYear = int(startDateObject.strftime("%Y"))
        endYear = int(endDateObject.strftime("%Y"))
        currentDate = datetime.now(timezone.utc)
        currentYear = currentDate.year
        year = startYear
        historicalYears = []
        while(year < currentYear and year <= endYear):
#             print("Historical Data!")
            historicalYears.append(year)
            year += 1
#         print(historicalYears)
        historicalDataEndDate = datetime(year=year, month=1, day=1, tzinfo=timezone.utc)
#         print(historicalDataEndDate)
        pastYearDataStartMonth = 1;
        pastYearDataEndMonth = 1;
        if(historicalDataEndDate < startDateObject):
            pastYearDataStartMonth = startDateObject.month
        if(pastYearDataEndMonth < endDateObject.month):
            if(endDateObject > (currentDate - timedelta(days=45))):
                pastYearDataEndMonth = (currentDate - timedelta(days=45)).month
            elif(endDateObject > historicalDataEndDate):
                pastYearDataEndMonth = endDateObject.month
#         print("start end months", pastYearDataStartMonth, pastYearDataEndMonth)
        realtimeDataStartDate = (currentDate - timedelta(days=45))
        realtimeDataEndDate = (currentDate - timedelta(days=45))
        if(realtimeDataStartDate < startDateObject):
            realtimeDataStartDate = startDateObject
#         else:
#             realtimeDataStartDate = startDateObject
        if(realtimeDataStartDate < endDateObject):
            realtimeDataEndDate = endDateObject
#         else:
#             realtimeDataEndDate = endDateObject
        print("historical query:", historicalYears)
        print("past year query:", pastYearDataStartMonth, pastYearDataEndMonth)
        print("realtime query:", realtimeDataStartDate, realtimeDataEndDate)
#         pastYearStartDate = 
#         if(startDateObject < datetime.now() - timedelta(days=45)) {
#             if()
#         }
        
#         print(startYear)
#         print(endYear)

        # Noreaster 12/23 festivus  storm 22, 23
        # startDate = "20221220"
        # endDate = "20221224"
        # dateStartFormat = "2022-12-20"
        # 
        # heightStartDate = "2022-12-20T00:00:00Z"
        # heightEndDate = "2022-12-24T23:59:59Z"
    
        badStations = []
        waveDict = {}
        for key in stationsDict["NDBC"].keys():
            stationDict = stationsDict["NDBC"][key]
            stationId = stationDict["id"]
            stationName = stationDict["name"]
            
#             Collect all the data from each of the three queries into one centralized array
            data = []
            for year in historicalYears:
                print(year)
# https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Hourly_Height_Verified_Water_Level.htmlTable?STATION_ID%2CDATUM%2CBEGIN_DATE%2CEND_DATE%2Ctime%2CWL_VALUE%2CSIGMA&STATION_ID=%228452660%22&DATUM%3E=%22MSL%22&BEGIN_DATE%3E=%222024-07-29%22&END_DATE%3E=%222024-08-10%22
#             url = "https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Hourly_Height_Verified_Water_Level.mat?STATION_ID%2CDATUM%2CBEGIN_DATE%2CEND_DATE%2Ctime%2CWL_VALUE%2CSIGMA&STATION_ID=%22"  + stationId + "%22&DATUM%3E=%22NAVD%22&BEGIN_DATE%3E=%22" + startDateFormat + "%22&END_DATE%3E=%22" + endDateFormat + "%22"
#             WVHT = Significant Wave Height, APD = mean wave period, SwD = mean wave direction
#               There is also wind wave information, swell height, period, and wave steepness quality descriptor available
#                 url = "https://www.ndbc.noaa.gov/histsearch.php?station=" + stationId + "&year=" + str(year) + "&f1=wvht&t1a=lt&v1a=999&t1b=&v1b=&c1=&f2=&t2a=&v2a=&t2b=&v2b=&c2=&f3=&t3a=&v3a=&t3b=&v3b=&mode=data"
#               Compile data from 3 different potential data sources, historical waves, past year waves, and realtime waves.
                historicalUrl = "https://www.ndbc.noaa.gov/view_text_file.php?filename=" + stationId + "h" + str(year) + ".txt.gz&dir=data/historical/stdmet/"
#                 Similar to how year range for historical data was found, get month range for pastYear data, creating an array of months to query data from. 
#               Latest data available from past year url is currentDate - 45 days

                print(historicalUrl)
#             print(url)
        #     sensorURL = 'https://ioos-dif-sos-prod.co-ops-aws-east1.net/ioos-dif-sos/SOS?service=SOS&request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&procedure=urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
                filename = temp_directory + stationDict["id"] + "_Historical.txt"
        #     sensorFilename = stationDict["id"] + "_sensor"
                try:
        #     Once mat files are downloaded once, comment out this line to stop querying the API
                    urlretrieve(historicalUrl, filename)
                    with open(filename) as file:
                        lines = file.readlines()
                        for line in lines[2::]:
                            data.append(line.split(" "))
#                             print(data)
#                             Time is in UTC
#                             year = data[0]
#                             month = data[1]
#                             day = data[2]
#                             hour = data[3]
#                             minute = data[4]
                except (HTTPError, FileNotFoundError):
        #         print("oops bad url")
                    badStations.append(badStations.append(stationDict))
            for month in range(pastYearDataStartMonth, pastYearDataEndMonth + 1):
                monthStr = datetime(year=1900, month=month, day=1).strftime('%b')
                print(monthStr)
                if((currentDate - timedelta(days=45)).month <= month):
                    filename = temp_directory + stationId + "_PastYear.txt"
                    pastYearUrl = "https://www.ndbc.noaa.gov/data/stdmet/" + monthStr + "/" + stationId + ".txt"
                else:
                    filename = temp_directory + stationId + "_PastYear.txt.gz"
                    pastYearUrl = "https://www.ndbc.noaa.gov/data/stdmet/" + monthStr + "/" + stationId + str(month) + str(currentDate.year) + ".txt.gz"

                print(pastYearUrl)
#                 filename = temp_directory + stationDict["id"] + ".txt.gz"
        #     sensorFilename = stationDict["id"] + "_sensor"
                try:
        #     Once mat files are downloaded once, comment out this line to stop querying the API
                    urlretrieve(pastYearUrl, filename)
                    if(".gz" in filename):
                        with gzip.open(filename, 'rb') as f_in:
                            with open(filename[:-3], 'wb') as f_out:
                                shutil.copyfileobj(f_in, f_out)
                        filename = temp_directory + stationId + "_PastYear.txt"
                    with open(filename) as file:
                        lines = file.readlines()
                        for line in lines[2::]:
                            data.append(line.split(" "))
#                             print(line)
#                             print(data)
#                             Time is in UTC
#                             year = data[0]
#                             month = data[1]
#                             day = data[2]
#                             hour = data[3]
#                             minute = data[4]
                except (HTTPError, FileNotFoundError):
        #         print("oops bad url")
                    badStations.append(badStations.append(stationDict))
            if(realtimeDataStartDate != realtimeDataEndDate):
                realtimeUrl =  "https://www.ndbc.noaa.gov/data/realtime2/" + stationId + ".txt"
                print(realtimeUrl)
#             print(url)
        #     sensorURL = 'https://ioos-dif-sos-prod.co-ops-aws-east1.net/ioos-dif-sos/SOS?service=SOS&request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&procedure=urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
                filename = temp_directory + stationDict["id"] + "_Realtime.txt"
        #     sensorFilename = stationDict["id"] + "_sensor"
                try:
        #     Once mat files are downloaded once, comment out this line to stop querying the API
                    urlretrieve(realtimeUrl, filename)
                    with open(filename) as file:
                        lines = file.readlines()
                        for line in lines[2::]:
                            data.append(line.split(" "))
#                             print(data)
#                             Time is in UTC
#                             year = data[0]
#                             month = data[1]
#                             day = data[2]
#                             hour = data[3]
#                             minute = data[4]
                except (HTTPError, FileNotFoundError):
        #         print("oops bad url")
                    badStations.append(badStations.append(stationDict))
#                 pastYearUrl = "https://www.ndbc.noaa.gov/view_text_file.php?filename=" + stationId + "h" + str(year) + ".txt.gz&dir=data/stdmet/" + str(month)

#         There is one extra field in realtime data, PTDY that is the second to last field. 
#          The pastYear and historical does not contain this field
            times = []
            timestamps = []
            significantWaveHeights = []
            peakWavePeriods = []
            meanWavePeriods = []
            meanWaveDirections = []
            for dataLine in data:
                dataLine = ' '.join(dataLine).split()
#                 print(dataLine)
                year = int(dataLine[0])
                month = int(dataLine[1])
                day = int(dataLine[2])
                hour = int(dataLine[3])
                minute = int(dataLine[4])
                windDir = dataLine[5]
                windSpeed = dataLine[6]
                gust = dataLine[7]
                significantWaveHeight = float(dataLine[8])
                peakWavePeriod = float(dataLine[9])
                meanWavePeriod = float(dataLine[10])
                meanWaveDirection = float(dataLine[11])
                pressure = dataLine[12]
                airTemperature = dataLine[13]
                waterTemperature = dataLine[14]
                dewpoint = dataLine[15]
                visibility = dataLine[16]
#                 print(len(dataLine))
                if(len(dataLine) > 18):
                    pressureTendency = dataLine[17]
                    tide = dataLine[18][:-2]
                else:
                    tide = dataLine[17][:-2]
                
                time = datetime(year=year, month=month, day=day, hour=hour, minute=minute, tzinfo=timezone.utc)
    #             print(time)
                if(time >= startDateObject and time <= endDateObject):
                    times.append(time)
                    timestamps.append(datetime.timestamp(time))
                    significantWaveHeights.append(significantWaveHeight)
                    peakWavePeriods.append(peakWavePeriod)
                    meanWavePeriods.append(meanWavePeriod)
                    meanWaveDirections.append(meanWaveDirection)
    #         print(times)
    #             quit()
            #         urlretrieve(sensorURL, sensorFilename)
    #                 data = scipy.io.loadmat(matFilename)
                waveDict[key] = {}
                waveDict[key]["times"] = timestamps
                waveDict[key]["swh"] = significantWaveHeights
                waveDict[key]["pwp"] = peakWavePeriods
                waveDict[key]["mwp"] = meanWavePeriods
                waveDict[key]["mwd"] = meanWaveDirections
        
        
#         print(waveDict)
        with open(OBS_WAVE_DATA_FILE, "w") as outfile:
            json.dump(waveDict, outfile, cls=NumpyEncoder)
