# Queries NOAA NOS buoys and saves the data
# Pranav 9/25/2023
# Fuck matlab

import scipy.io
from urllib.request import urlretrieve
from urllib.error import HTTPError
from datetime import datetime, timedelta, timezone
import json
from Encoders import NumpyEncoder
        
        
# parse this (raintest)
# <table border="1" cellpadding="2">
#  <caption nowrap="nowrap"><strong>Daily Sum Precipitation, total, inches, Met station, [Daily sum for preceding day]</strong></caption>
# <tr><th>DATE</th><th>Jul<br />2024</th><th>Aug<br />2024</th></tr>
# <tr align="center"><th>1</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>2</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>3</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.06<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>4</th><td nowrap="nowrap">0.13<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.27<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>5</th><td nowrap="nowrap">0.21<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>6</th><td nowrap="nowrap">0.27<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">1.02<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>7</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.09<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>8</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.09<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>9</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.25<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>10</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.32<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>11</th><td nowrap="nowrap">0.02<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>12</th><td nowrap="nowrap">0.14<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.36<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>13</th><td nowrap="nowrap">0.39<sup>P&nbsp;&nbsp;</sup></td><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td></tr>
# <tr align="center"><th>14</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>15</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>16</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>17</th><td nowrap="nowrap">0.67<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>18</th><td nowrap="nowrap">0.16<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>19</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>20</th><td nowrap="nowrap">0.02<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>21</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>22</th><td nowrap="nowrap">0.01<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>23</th><td nowrap="nowrap">0.15<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>24</th><td nowrap="nowrap">0.01<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>25</th><td nowrap="nowrap">0.53<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>26</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>27</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>28</th><td nowrap="nowrap">0.11<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>29</th><td nowrap="nowrap">1.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>30</th><td nowrap="nowrap">0.00<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr align="center"><th>31</th><td nowrap="nowrap">0.12<sup>P&nbsp;&nbsp;</sup></td><td>&nbsp;</td></tr>
# <tr><th></th><td></td></tr><tr><th>COUNT</th><th>31</th><th>13</th></tr>
# <tr><th>MAX</th><th>1.00</th><th>1.02</th></tr>
class GetObsRain:
    def __init__(self, STATIONS_FILE="", OBS_RAIN_DATA_FILE="", startDateObject="", endDateObject=""):
        temp_directory = OBS_RAIN_DATA_FILE[0:OBS_RAIN_DATA_FILE.rfind("/") + 1]
        print(type(startDateObject), flush=True)
        print(startDateObject, flush=True)
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)

        startDate = startDateObject.strftime("%Y-%m-%d")
        endDate = endDateObject.strftime("%Y-%m-%d")
#         quit()
        dateStartFormat = startDateObject.strftime("%Y-%m-%d")

        # Noreaster 12/23 festivus  storm 22, 23
        # startDate = "20221220"
        # endDate = "20221224"
        # dateStartFormat = "2022-12-20"
        # 
        # heightStartDate = "2022-12-20T00:00:00Z"
        # heightEndDate = "2022-12-24T23:59:59Z"
    
        badStations = []
        rainDict = {}
        for key in stationsDict["USGS"].keys():
            stationDict = stationsDict["USGS"][key]
            stationId = stationDict["id"]
            stationName = stationDict["name"]
            url = "https://waterdata.usgs.gov/nwis/dv?cb_00045=on&format=html&site_no=" + stationId + "&legacy=&referred_module=sw&period=&begin_date=" + startDate + "&end_date=" + endDate
        #     sensorURL = 'https://ioos-dif-sos-prod.co-ops-aws-east1.net/ioos-dif-sos/SOS?service=SOS&request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&procedure=urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
            filename = "raintest"
        #     sensorFilename = stationDict["id"] + "_sensor"
            try:
        #     Once mat files are downloaded once, comment out this line to stop querying the API
                urlretrieve(url, filename)
        
                beginRainData = False
                months = []
                deltaDaysForMonths = []
                maxrowRains = []
                minrowRains = []
                rowRains = []
                rowDays = []
                
                dates = []
                rains = []
                with open(filename) as file:
                    lines = file.readlines()
                    for line in lines:
                        if("Daily Sum Precipitation, total, inches, Met station, [Daily sum for preceding day]" in line):
                            beginRainData = True
                        elif(beginRainData and ("</table></td></tr></table></td></tr></table>" in line)):
                            beginRainData = False
                            break
                        if(beginRainData):
                            if("DATE" in line):
                                data = line.split("<th>")
                                for monthData in data[2::]:
                                    month = monthData[0:3]
                                    year = monthData[9:13]
                                    months.append((month, year))
#                                     Initialize rowRains array with empty arrays with number of months
                                    rowRains.append([])
                            if("COUNT" in line):
                                data = line.split("<th>")
                                for daysData in data[3::]:
                                    deltaDaysForMonths.append(int(daysData[0:daysData.find('<')]))
                            if("MAX" in line):
                                data = line.split("<th>")
                                for maxData in data[2::]:
                                    maxrowRains.append(float(maxData[0:4]))
                            if("MIN" in line):
                                data = line.split("<th>")
                                for minData in data[2::]:
                                    minrowRains.append(float(minData[0:4]))
                            if('<tr align="center">' in line):
                                dayStr = line.split("<th>")[1]
                                day = int(dayStr[0:dayStr.find('<')])
                                rowDays.append(day)
#                                 print(day)
                                rainData = dayStr[dayStr.find("</th>") + 5::]
                                rainData = rainData.split("<td")[1::]
#                                 print(rainData)
                                for index, rain in enumerate(rainData):
                                    if(">&nbsp;</td>" in rain):
#                                         print("In 0")
                                        rowRains[index].append(float(-1))
                                    else:
#                                         print(rain)
#                                         print("RAIN", rain[17:rain.find("<")])
#                                         Convert from inches per day to mm per hour
                                        rowRains[index].append(float(rain[17:rain.find("<")]) * 1.0583333153333347)
#                                     print(rowRains)
#                                     if(index == 2):
#                                         quit()
#                 print(months, deltaDaysForMonths, maxrowRains, minrowRains, rowRains)
                
#                 Moved                 BOOF

                for monthIndex, month in enumerate(months):
                    deltaDaysForMonth = deltaDaysForMonths[monthIndex]
#                     print(deltaDaysForMonth)
                    startDay = None
                    endDay = None
                    foundStart = False
#                     print(rowRains[monthIndex])
                    rowRainsLength = len(rowRains[monthIndex])
#                     quit()
                    for index, rain in enumerate(rowRains[monthIndex]):
                        if(rain == -1):
                            if(foundStart):
                                foundStart = False
                                endDay = index + 1
                                break
                        elif(index == (rowRainsLength - 1)):
                            foundStart = False
                            endDay = index + 1
                            break
                        else:
#                             print("found number", rain, index)
#                             quit()
                            if(not foundStart):
                                foundStart = True
                                startDay = index + 1
#                     print("rowRains for month, deltaDaysForMonth", month, startDay, endDay)
                    dayIndex = startDay
#                     print(dayIndex)
#                     quit()
                    for index, rowDay in enumerate(rowDays):
                        dateStr = (month[0] + month[1] + str(rowDay).zfill(2)) + "12"
                        date = datetime.strptime(dateStr, "%b%Y%d%H").replace(tzinfo=timezone.utc)
                        dates.append(date)
#                         print(date)
                        rains.append(rowRains[monthIndex][dayIndex - 1])
                        dayIndex = dayIndex + 1
#                     while dayIndex < (startDay + deltaDaysForMonth):
#                         print(dayIndex)
#                         dateStr = (month[0] + month[1] + str(dayIndex).zfill(2))
#                         date = datetime.strptime(dateStr, "%b%Y%d").replace(tzinfo=timezone.utc)
#                         dates.append(date)
#                         print(date)
#                         rains.append(rowRains[monthIndex][dayIndex - 1])
#                         dayIndex = dayIndex + 1
                
                    
#                     unixTimes = data["IOOS_Wind"]["time"][0][0].flatten()
#                     windDirections = data["IOOS_Wind"]["Wind_Direction"][0][0].flatten()
#                     windSpeeds = data["IOOS_Wind"]["Wind_Speed"][0][0].flatten()
#                 windGusts = data["IOOS_Wind"]["Wind_Gust"][0][0].flatten()
#                 rainDict[key] = {}
#                 rainDict[key]["times"] = unixTimes
#                 windDict[key]["directions"] = windDirections
#                 windDict[key]["speeds"] = windSpeeds
#                 windDict[key]["gusts"] = windGusts
#                 print(len(dates), len(rains))
                timestamps = []
                for date in dates:
                    timestamps.append(date.timestamp())
                rainDict[key] = {}
                rainDict[key]["times"] = timestamps
                rainDict[key]["rain"] = rains
            except (HTTPError, FileNotFoundError):  
                print("oops bad url")
#                 badStations.append(badStations.append(stationDict))
        
        # print(windDict)
        with open(OBS_RAIN_DATA_FILE, "w") as outfile:
            json.dump(rainDict, outfile, cls=NumpyEncoder)
#         quit()
