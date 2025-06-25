# Queries NOAA NOS buoys and saves the data
# Pranav 9/25/2023
# Fuck matlab

import scipy.io
from urllib.request import urlretrieve
from urllib.error import HTTPError
from datetime import datetime, timedelta, timezone
import json
from Encoders import NumpyEncoder
import pandas as pd
import numpy as np
import signal
import os
import time 

MOORING_LENGTH = 1

# Add logic to pull loaded data from txt file depending on source in station
def alarm_handler(signum, frame):
    raise TimeoutError("URL retrieval timed out")

def safe_urlretrieve(url, filename, timeout=10, max_retries=3):
    for attempt in range(max_retries):
        try:
            # Set the alarm for the timeout
            signal.signal(signal.SIGALRM, alarm_handler)
            signal.alarm(timeout)
            
            urlretrieve(url, filename)
            
            # Cancel the alarm if the retrieval was successful
            signal.alarm(0)
            return True  # Indicate success
        except TimeoutError:
            print(f"Attempt {attempt + 1} timed out. Retrying...")
            if os.path.exists(filename):
                os.remove(filename)  # Remove partially downloaded file if exists
        except Exception as e:
            print(f"Attempt {attempt + 1} failed with error: {e}. Retrying...")
            if os.path.exists(filename):
                os.remove(filename)  # Clean up if there's an error
        finally:
            signal.alarm(0)  # Cancel the alarm in case it wasn't cancelled yet

    return False  # If all retries fail
        
class GetBuoyWater:
    def __init__(self, STATIONS_FILE="", OBS_WATER_DATA_FILE="", startDateObject="", endDateObject=""):
        temp_directory = OBS_WATER_DATA_FILE[0:OBS_WATER_DATA_FILE.rfind("/") + 1]
        print(type(startDateObject), flush=True)
        print(startDateObject, flush=True)
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
#         with open(ADCIRC_MESH_DATA_FILE) as datafile:
#             meshDict = json.load(datafile)

        # stationIds = [8413320, 8443970, 8447435, 8449130, 8447930, 8452660, 8510560, 8418150, 8419870, 8454049, 8454000, 8461490, 8411060, 8531680, 8534720, 8452944]
        # stationNames = ['Bar Harbor', 'Boston', 'Chatham', 'Nantucket', 'Woods Hole', 'Newport', 'Montauk', 'Portland', 'Seavey Island, ME', 'Quonset Point', 'Providence', 'New London', 'Cutler Faris Wharf', 'Sandy Hook', 'Altlantic City', 'Conimicut Light'] 
        stationIds = [8413320, 8447435, 8449130, 8452660, 8418150, 8454049, 8454000, 8411060, 8531680, 8452944]
        stationNames = ['Bar Harbor', 'Chatham', 'Nantucket', 'Newport', 'Portland', 'Quonset Point', 'Providence', 'Cutler Faris Wharf', 'Sandy Hook', 'Conimicut Light'] 

        startDate = startDateObject.strftime("%Y%m%d")
        endDate = endDateObject.strftime("%Y%m%d")
        startDateFormat = startDateObject.strftime("%Y%m%d")
        endDateFormat = endDateObject.strftime("%Y%m%d")

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
        
        predictionYears = []
        year = startDateObject.year
        endYear = endDateObject.year
        while(year <= endYear):
#             print("Historical Data!")
            predictionYears.append(year)
            year += 1
            
        for key in stationsDict["NOS"].keys():
            stationDict = stationsDict["NOS"][key]
            stationId = stationDict["id"]
            stationName = stationDict["name"]
            stationSource = stationDict["source"]
            if(".txt" in stationSource):
                print("Pulling Data from Station File")
                                # Path to the text file
                file_path = stationSource
                
                # Step 1: Load the data
                # The file is tab-separated, and the first column is datetime
                # We specify the column names manually since the file doesn't have a header
                column_names = [
                    "datetime", "salinity", "temperature", "DO_umol_kg", 
                    "Depth_m", "pressure_decibars", "col6", "col7", "col8", "col9"
                ]
                data = pd.read_csv(file_path, sep="\t", names=column_names, parse_dates=["datetime"])

                # Step 2: Convert datetime from EST to GMT
                # Localize the datetime to EST (UTC-5)
                data["datetime"] = data["datetime"].dt.tz_localize("EST")

                # Convert from EST to GMT (UTC)
                data["datetime"] = data["datetime"].dt.tz_convert("GMT")

                # Step 3: Filter data based on the time range (startDateObject to endDateObject)
                # Ensure startDateObject and endDateObject are timezone-aware (GMT)
                # If they are naive, you would need to localize them to GMT, but we assume they are already in GMT
                filtered_data = data[
                    (data["datetime"] >= startDateObject) & (data["datetime"] <= endDateObject)
                ]

                # Step 4: Convert filtered datetime to Unix timestamps
                # If no data falls within the range, filtered_data will be empty
                if not filtered_data.empty:
                    unixTimes = (filtered_data["datetime"].astype("int64") // 10**9).to_numpy()
                    waters = filtered_data["Depth_m"].to_numpy()
                else:
                    # Handle the case where no data falls within the range
                    unixTimes = np.array([], dtype=np.int64)
                    waters = np.array([], dtype=np.float64)
                
                stationElevation = meshDict[key]["elevation"]
                print("station elevation", key, stationElevation)
                waters = waters + MOORING_LENGTH
#                 waters = waters + stationElevation
#                 
                waterDict[key] = {}
                waterDict[key]["times"] = unixTimes
                waterDict[key]["water"] = waters
                waterDict[key]["prediction_times"] = []
                waterDict[key]["prediction_water"] = []
                
                
            if ".csv" in stationSource:
                print("Pulling Data from Tides and Currents Station File")
    
                # Path to the CSV file
                file_path = stationSource
    
                # Step 1: Load the data
                # The file is comma-separated with headers
                column_names = ["Date", "Time (GMT)", "Predicted (m)", "Preliminary (m)", "Verified (m)"]
                data = pd.read_csv(file_path, sep=",", names=column_names, header=0, parse_dates=False)
    
                # Step 2: Combine Date and Time (GMT) into a single datetime column
                data["datetime"] = pd.to_datetime(data["Date"] + " " + data["Time (GMT)"], format="%Y/%m/%d %H:%M")
    
                # Step 3: Localize datetime to GMT
                data["datetime"] = data["datetime"].dt.tz_localize("GMT")
    
                # Step 4: Filter data based on the time range (startDateObject to endDateObject)
                filtered_data = data[
                    (data["datetime"] >= startDateObject) & (data["datetime"] <= endDateObject)
                ]
    
                # Step 5: Convert filtered datetime to Unix timestamps and extract water levels
                if not filtered_data.empty:
                    unixTimes = (filtered_data["datetime"].astype("int64") // 10**9).to_numpy()
        
                    # Use Verified (m) if available, otherwise fall back to Preliminary (m)
                    waters = filtered_data["Verified (m)"].replace("-", np.nan).astype(float)
                    waters = waters.fillna(filtered_data["Preliminary (m)"].replace("-", np.nan).astype(float)).to_numpy()
        
                    # Extract predicted water levels
                    prediction_waters = filtered_data["Predicted (m)"].replace("-", np.nan).astype(float).to_numpy()
        
#                     # Add MOORING_LENGTH to waters
#                     waters = waters + MOORING_LENGTH
                else:
                    # Handle empty filtered data
                    unixTimes = np.array([], dtype=np.int64)
                    waters = np.array([], dtype=np.float64)
                    prediction_waters = np.array([], dtype=np.float64)
    
                # Step 6: Get station elevation
#                 stationElevation = meshDict[key]["elevation"]
#                 print("station elevation", key, stationElevation)
    
                # Step 7: Populate waterDict
                waterDict[key] = {}
                waterDict[key]["times"] = unixTimes
                waterDict[key]["water"] = waters
                waterDict[key]["prediction_times"] = []  # Same timestamps for predictions
                waterDict[key]["prediction_water"] = []

            elif "USGS" in stationSource:
                print("Pulling Data from USGS Station")
            
                # Step 1: Construct the USGS URL dynamically
                # Ensure startDT is at the beginning of the start date (00:00:00.000)
                usgs_start_date = startDateObject.strftime("%Y-%m-%dT00:00:00.000-05:00")
                # Ensure endDT is at the end of the end date (23:59:59.999)
                usgs_end_date = endDateObject.strftime("%Y-%m-%dT23:59:59.999-05:00")
                url = f"https://nwis.waterservices.usgs.gov/nwis/iv/?sites={stationId}&agencyCd=USGS&startDT={usgs_start_date}&endDT={usgs_end_date}&parameterCd=00065&format=rdb"
                print(f"Generated USGS URL: {url}")
            
                # Step 2: Download and load the data
                filename = temp_directory + stationDict["id"] + "_usgs.txt"
                try:
                    # Download the data
                    safe_urlretrieve(url, filename)
            
                    # Read the tab-delimited USGS data, skipping header lines (starting with '#') and the metadata row
                    # The metadata row ('5s 15s 20d 6s 14n 10s') is typically the line after the header names
                    data = pd.read_csv(
                        filename,
                        sep="\t",
                        comment="#",
                        skiprows=[0],  # Skip the metadata row after the header
                        parse_dates=["datetime"],
                        date_format="%Y-%m-%d %H:%M"
                    )
            
                    # Step 3: Verify datetime column exists and is in datetime format
                    if "datetime" not in data.columns:
                        raise ValueError("Expected 'datetime' column not found in USGS data")
            
                    # Ensure the datetime column is in datetime64 format
                    data["datetime"] = pd.to_datetime(data["datetime"], errors="coerce")
                    if data["datetime"].isna().all():
                        raise ValueError("Failed to parse 'datetime' column as valid datetime values")
            
                    # Step 4: Convert datetime from EST to GMT
                    data["datetime"] = data["datetime"].dt.tz_localize("EST").dt.tz_convert("GMT")
            
                    # Step 5: Filter data based on the time range
                    filtered_data = data[(data["datetime"] >= startDateObject) & (data["datetime"] <= endDateObject)]
            
                    # Step 6: Process water levels (convert to NAVD88 and meters)
                    if not filtered_data.empty:
                        # Find the water level column (e.g., 67433_00065)
                        water_column = [col for col in filtered_data.columns if col.endswith("_00065")]
                        if not water_column:
                            raise ValueError("No water level column (ending with '_00065') found in USGS data")
                        water_column = water_column[0]
            
                        # Convert to NAVD88 by subtracting 0.15 ft
                        waters_ft_navd88 = filtered_data[water_column].astype(float) - 0.15
                        # Convert feet to meters (1 ft = 0.3048 meters)
                        waters_m = waters_ft_navd88 * 0.3048
                        # Convert datetime to Unix timestamps
                        unixTimes = (filtered_data["datetime"].astype("int64") // 10**9).to_numpy()
                        waters = waters_m.to_numpy()
                    else:
                        # Handle empty filtered data
                        unixTimes = np.array([], dtype=np.int64)
                        waters = np.array([], dtype=np.float64)
            
                    # Step 7: Populate waterDict
                    waterDict[key] = {}
                    waterDict[key]["times"] = unixTimes
                    waterDict[key]["water"] = waters
                    waterDict[key]["prediction_times"] = []  # USGS does not provide predictions in this data
                    waterDict[key]["prediction_water"] = []
            
                except (HTTPError, FileNotFoundError, pd.errors.EmptyDataError, ValueError) as e:
                    print(f"Error processing USGS data for URL {url}: {str(e)}")
                    badStations.append(stationDict)
            else:
    # https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Hourly_Height_Verified_Water_Level.htmlTable?STATION_ID%2CDATUM%2CBEGIN_DATE%2CEND_DATE%2Ctime%2CWL_VALUE%2CSIGMA&STATION_ID=%228452660%22&DATUM%3E=%22MSL%22&BEGIN_DATE%3E=%222024-07-29%22&END_DATE%3E=%222024-08-10%22
                url = "https://opendap.co-ops.nos.noaa.gov/erddap/tabledap/IOOS_Hourly_Height_Verified_Water_Level.mat?STATION_ID%2CDATUM%2CBEGIN_DATE%2CEND_DATE%2Ctime%2CWL_VALUE%2CSIGMA&STATION_ID=%22"  + stationId + "%22&DATUM%3E=%22MSL%22&BEGIN_DATE%3E=%22" + startDateFormat + "%22&END_DATE%3E=%22" + endDateFormat + "%22"
                
                predictionTimes = []
                predictionWaters = []
                for year in predictionYears:
                    try:
                        predictionUrl = "https://tidesandcurrents.noaa.gov/cgi-bin/predictiondownload.cgi?&stnid=" + stationId +  "&threshold=&thresholdDirection=greaterThan&bdate=" + str(year) + "&timezone=GMT&datum=NAVD&clock=24hour&type=txt&annual=true"
                        print("predictionUrl", predictionUrl)
                        predictionFilename = temp_directory + stationDict["id"] + str(year) + "_TidePrediction.mat"
                        safe_urlretrieve(predictionUrl, predictionFilename)
                        with open(predictionFilename) as file:
                            lines = file.readlines()
                            if(len(lines) > 0):
                                for line in lines[14::]:
                                    data = line.split("\t")
    #                                 https://www.digitalocean.com/community/tutorials/python-string-to-datetime-strptime
                                    time = datetime.strptime(data[0] + data[2] + "GMT", "%Y/%m/%d%H:%M%Z")
                                    time = time.replace(tzinfo=timezone.utc)
                                    if(time >= startDateObject and time <= endDateObject):
                                        print(time)
                                        predictionTimes.append(datetime.timestamp(time))
                                        predictionWater = float(data[5]) / 100.0
                                        predictionWaters.append(predictionWater)
    #                             predictionLines.append(lines[15::])
                    except (HTTPError, FileNotFoundError):
                        print("Bad prdiction url: ", predictionUrl)
                        badStations.append(badStations.append(stationDict))
    #             print(predictionLines)
    
    #             print(url)
            #     sensorURL = 'https://ioos-dif-sos-prod.co-ops-aws-east1.net/ioos-dif-sos/SOS?service=SOS&request=DescribeSensor&version=1.0.0&outputFormat=text/xml;subtype="sensorML/1.0.1/profiles/ioos_sos/1.0"&procedure=urn:ioos:station:NOAA.NOS.CO-OPS:8454000'
                matFilename = temp_directory + stationDict["id"] + ".mat"
            #     sensorFilename = stationDict["id"] + "_sensor"
                try:
                    print("mat url", url)
            #     Once mat files are downloaded once, comment out this line to stop querying the API
                    safe_urlretrieve(url, matFilename)
            #         urlretrieve(sensorURL, sensorFilename)
                    data = scipy.io.loadmat(matFilename)
                    unixTimes = data["IOOS_Hourly_Height_Verified_Wat"]["time"][0][0].flatten()
                    waters = data["IOOS_Hourly_Height_Verified_Wat"]["WL_VALUE"][0][0].flatten()
                    waterDict[key] = {}
                    waterDict[key]["times"] = unixTimes
                    waterDict[key]["water"] = waters
                    waterDict[key]["prediction_times"] = predictionTimes
                    waterDict[key]["prediction_water"] = predictionWaters
            
                except (HTTPError, FileNotFoundError):
                    print("bad mat url: ", url)
                    badStations.append(badStations.append(stationDict))
        
        # print(windDict)
        with open(OBS_WATER_DATA_FILE, "w") as outfile:
            json.dump(waterDict, outfile, cls=NumpyEncoder)
