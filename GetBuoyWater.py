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
        # ERDDAP BEGIN_DATE/END_DATE expect YYYY-MM-DD
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
                
                
            if ".csv" in stationSource and os.path.isfile(stationSource):
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
                    # Step 7: Populate waterDict
                    waterDict[key] = {}
                    waterDict[key]["times"] = unixTimes
                    waterDict[key]["water"] = waters
                    waterDict[key]["prediction_times"] = []
                    waterDict[key]["prediction_water"] = []
                else:
                    # Local CSV exists but does not cover the run window — fall through to live CO-OPS API
                    print(f"Local CSV {file_path} has no data in window; falling back to CO-OPS API for {stationId}")
                    stationSource = "COOPS_API"

            if ".csv" in stationSource and not os.path.isfile(stationSource) and stationSource != "COOPS_API":
                # Listed as a CSV in OBS_STATIONS but file not on disk — live API instead of hard fail
                print(f"Local CSV missing ({stationSource}); falling back to CO-OPS API for {stationId}")
                stationSource = "COOPS_API"

            # Already filled from local txt/csv covering the window? skip live fetch
            if key in waterDict:
                continue

            if "USGS" in stationSource:
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
                # Live CO-OPS product API (preferred). Old ERDDAP .mat endpoint is dead/unreliable.
                # Docs: https://api.tidesandcurrents.noaa.gov/api/prod/
                try:
                    import urllib.request
                    begin = startDateObject.strftime("%Y%m%d")
                    end = endDateObject.strftime("%Y%m%d")
                    # water_level = verified 6-min; falls back to predictions if empty
                    base = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"
                    wl_url = (
                        f"{base}?product=water_level&application=richamp-support"
                        f"&begin_date={begin}&end_date={end}&station={stationId}"
                        f"&time_zone=gmt&units=metric&datum=MSL&format=json"
                    )
                    print(f"CO-OPS API water_level station={stationId}", flush=True)
                    with urllib.request.urlopen(wl_url, timeout=30) as resp:
                        payload = json.loads(resp.read().decode("utf-8"))
                    unixTimes = []
                    waters = []
                    for row in payload.get("data") or []:
                        try:
                            t = datetime.strptime(row["t"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                            if t < startDateObject or t > endDateObject:
                                continue
                            v = row.get("v")
                            if v is None or v == "":
                                continue
                            unixTimes.append(int(t.timestamp()))
                            waters.append(float(v))
                        except (KeyError, ValueError, TypeError):
                            continue

                    pred_times = []
                    pred_waters = []
                    pred_url = (
                        f"{base}?product=predictions&application=richamp-support"
                        f"&begin_date={begin}&end_date={end}&station={stationId}"
                        f"&time_zone=gmt&units=metric&datum=MSL&interval=h&format=json"
                    )
                    try:
                        with urllib.request.urlopen(pred_url, timeout=30) as resp:
                            pred_payload = json.loads(resp.read().decode("utf-8"))
                        for row in pred_payload.get("predictions") or []:
                            try:
                                t = datetime.strptime(row["t"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                                if t < startDateObject or t > endDateObject:
                                    continue
                                pred_times.append(int(t.timestamp()))
                                pred_waters.append(float(row["v"]))
                            except (KeyError, ValueError, TypeError):
                                continue
                    except Exception as pe:
                        print(f"CO-OPS predictions optional fail {stationId}: {pe}", flush=True)

                    if not unixTimes and pred_times:
                        # No verified water yet (e.g. future forecast window) — use tidal predictions as obs proxy
                        print(f"station {stationId}: no verified water_level; using predictions", flush=True)
                        unixTimes = pred_times
                        waters = pred_waters

                    waterDict[key] = {
                        "times": np.array(unixTimes, dtype=np.int64),
                        "water": np.array(waters, dtype=np.float64),
                        "prediction_times": pred_times,
                        "prediction_water": pred_waters,
                    }
                    print(f"station {stationId}: n_obs={len(unixTimes)} n_pred={len(pred_times)}", flush=True)
                    if not unixTimes and not pred_times:
                        badStations.append(stationDict)
                except Exception as e:
                    print(f"CO-OPS API fail station {stationId}: {e}", flush=True)
                    badStations.append(stationDict)
                    waterDict[key] = {
                        "times": np.array([], dtype=np.int64),
                        "water": np.array([], dtype=np.float64),
                        "prediction_times": [],
                        "prediction_water": [],
                    }
        
        # print(windDict)
        print(f"GetBuoyWater: wrote {len(waterDict)} stations; bad={len(badStations)}")
        with open(OBS_WATER_DATA_FILE, "w") as outfile:
            json.dump(waterDict, outfile, cls=NumpyEncoder)
