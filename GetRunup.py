import json
import os
from typing import List, Dict, Optional
from datetime import datetime

fields = [
    "dateTime", "twl", "twl05", "twl95", "setup", "runup", "runup05", "runup95",
    "tideWindSetup", "swash", "incSwash", "infragSwash", "hs", "pp", "predictedImpact"
]
    

def datetime_to_unix_time(datetime_str: str) -> int:
    """Convert datetime string (YYYY-MM-DD HH:MM:SS) to Unix timestamp."""
    try:
        return int(datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S").timestamp())
    except ValueError as e:
        print(f"Error parsing datetime {datetime_str}: {e}")
        raise

def read_site_json(file_path: str) -> Optional[Dict]:
    """
    Read site JSON file and return a dictionary with site-specific data.
    Returns None if the file cannot be read or lacks required fields.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Handle both single object and list with one object
        site_data = data[0] if isinstance(data, list) and len(data) > 0 else data
        required_fields = ["siteLatitude", "siteLongitude", "toeHeight", "crestHeight"]
        if not all(field in site_data for field in required_fields):
            print(f"Site JSON missing required fields: {file_path}")
            return None
        # Convert numeric fields to float
        return {
            "siteLatitude": float(site_data["siteLatitude"]),
            "siteLongitude": float(site_data["siteLongitude"]),
            "toeHeight": float(site_data["toeHeight"]),
            "crestHeight": float(site_data["crestHeight"]),
            "beachSlope": float(site_data["beachSlope"])
        }
    except FileNotFoundError:
        print(f"Site file not found: {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in site file: {file_path}")
        return None
    except Exception as e:
        print(f"Error reading site file {file_path}: {e}")
        return None

def read_water_levels_json(file_path: str, fields: List[str]) -> List[Dict]:
    """
    Read water levels JSON file and return a list of dictionaries with specified fields.
    Always includes 'id' and 'unixTime'. Converts numeric fields to float and dateTime to unixTime.
    """
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        # Ensure data is a list
        if not isinstance(data, list):
            print(f"Water levels JSON is not a list: {file_path}")
            return []
        
        results = []
        required_fields = ["id", "dateTime"] + [f for f in fields if f not in ["id", "dateTime"]]
        numeric_fields = [
            "twl", "twl05", "twl95", "setup", "runup", "runup05", "runup95",
            "tideWindSetup", "swash", "incSwash", "infragSwash", "hs", "pp"
        ]
        
        for item in data:
            # Check if all required fields are present
            if not all(field in item for field in required_fields):
                print(f"Skipping record in {file_path} due to missing fields: {item}")
                continue
            # Create new record with requested fields
            record = {"id": str(item["id"])}  # Ensure id is string
            for field in fields:
                if field == "dateTime":
                    record["unixTime"] = datetime_to_unix_time(item["dateTime"])
                elif field == "predictedImpact":
                    record[field] = str(item[field])  # Ensure predictedImpact is string
                elif field in numeric_fields:
                    try:
                        record[field] = float(item[field])  # Convert to float
                    except (ValueError, TypeError):
                        print(f"Invalid numeric value for {field} in {file_path}: {item[field]}")
                        continue
                else:
                    record[field] = item[field]
            results.append(record)
        return results
    except FileNotFoundError:
        print(f"Water levels file not found: {file_path}")
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON in water levels file: {file_path}")
        return []
    except Exception as e:
        print(f"Error reading water levels file {file_path}: {e}")
        return []

def fetch_water_levels(
    site_ids: List[int] = [1401, 1402, 1403],
    forecast_dates: List[str] = ["2022-12-20", "2023-12-15"],
    fields: List[str] = [
        "dateTime", "twl", "twl05", "twl95", "setup", "runup", "runup05", "runup95",
        "tideWindSetup", "swash", "incSwash", "infragSwash", "hs", "pp", "predictedImpact"
    ],
    base_dir: str = "."
) -> List[Dict]:
    """
    Fetch all water level data from JSON files for specified sites and forecast dates.
    Includes site-specific data (latitude, longitude, toeHeight, crestHeight).
    Returns a list of dictionaries with water level and site data, using unixTime instead of dateTime.
    """
    results = []
    
    for site_id in site_ids:
        for forecast_date in forecast_dates:
            # Construct paths to water levels and site JSON files
            folder = f"twlForecast_OKX_{site_id}_{forecast_date} 00-00-00_json"
            water_levels_path = os.path.join(base_dir, folder, f"twlForecast_OKX_{site_id}_{forecast_date} 00-00-00_waterLevels.json")
            site_path = os.path.join(base_dir, folder, f"twlForecast_OKX_{site_id}_{forecast_date} 00-00-00_site.json")
            
            # Read site data
            site_data = read_site_json(site_path)
            if not site_data:
                continue
            
            # Read water levels data
            water_levels = read_water_levels_json(water_levels_path, fields)
            
            # Combine water level and site data
            for wl in water_levels:
                result = wl.copy()
                result["siteId"] = str(site_id)  # Ensure siteId is string
                result.update(site_data)
                results.append(result)
    
    return results

# Example usage
# if __name__ == "__main__":
#     water_level_data = fetch_water_levels(
#         site_ids=[1401, 1402, 1403],
#         forecast_dates=["2022-12-20", "2023-12-15"],
#         fields=fields,
#         base_dir="."
#     )
#     
#     # Print a sample of results (first few records for brevity)
#     for item in water_level_data[:5]:  # Limit to first 5 for demonstration
#         print(f"Site {item['siteId']} (Timestamp: {item['unixTime']}):")
#         print(f"  Latitude: {item['siteLatitude']}, Longitude: {item['siteLongitude']}")
#         print(f"  Dune Toe Height: {item['toeHeight']}, Dune Crest Height: {item['crestHeight']}")
#         print(f"  TWL: {item['twl']}, TWL05: {item['twl05']}, TWL95: {item['twl95']}")
#         print(f"  Setup: {item['setup']}, Runup: {item['runup']}")
#         print(f"  Runup05: {item['runup05']}, Runup95: {item['runup95']}")
#         print(f"  Tide+Wind Setup: {item['tideWindSetup']}, Swash: {item['swash']}")
#         print(f"  Incident Swash: {item['incSwash']}, Infragravity Swash: {item['infragSwash']}")
#         print(f"  Hs: {item['hs']}, Pp: {item['pp']}")
#         print(f"  Predicted Impact: {item['predictedImpact']}")
#         print()
#     
#     print(f"Total records retrieved: {len(water_level_data)}")










# Calculates runup with a set of json data files, then writes the runup to a json file
# Running the postprocessing takes >2 hr
# The majority of the time spent finding the closest nodes to all the points on the tangent
# Interpolating the water data to each point, to find the waterline point
# *Wet dry nodes are binary* *The wet dry algorithim is crucial*
# Also, generating both water and wave maps takes alot of time, as well as runup distance map
# pranav 1/16/2024

from datetime import datetime, timedelta, timezone
import json
import haversine
import math
import numpy as np
from Encoders import NumpyEncoder
from geographiclib.geodesic import Geodesic
from scipy.optimize import fsolve  # For solving the dispersion relation
       
       
DAY_IN_UNIX_TIME = 86400
CALCULATE_DAILY_AVERAGE_SLOPE = False
 
class GetRunup:

# 3/12/25
# Its not a great situation
# The problem is, trying to add just the swash component to produce a runup elevation prediction
# The runup elevation prediction is relative to the still water level in the paper
# the still water level changes with tides and storm surge
# The still water level can be offset from the geoid, either above or below.
# Each point on the geoid has an elevation, in the fort.14 file. This gives a relative elevation of the geoid. (NAVD88)
# Near the shoreline, the elevation is basically 0. It can vary though.
# The elevation of the geoid has to be added to the still water level from adcirc
# This gives an elevation of the still water level relative to NAVD88
# The still water level from adcirc also includes the setup
# Then the swash elevation has to be added to this
# The problem is that the stoll water level goes between 0.4 and -0.4 above the geoid
# The geoid elevation in most cases will be negative, thus bringing the still water elevation down to around 0 relative to NAVD88
# Adding the swash elevation to this will not be significant at all. It probbably wont be above 0.5
# The target value is ~4-5
# 

#     The holmann runup formula defines runup excent
#   as Atotalof 154runuptimeseriesarediscusseidn thispaper.Afterdigiti- zation of a runup time seriesand transformationto the verti- cal component,the mean (r/) and the standard deviation a arefound.From thisthesetup¥ iscalculatedas((r/)-tide) and the significantswashheightRsvas4a.
#   4 times the standard deviation of mean runup from the observations
# Also, iribarren number under 0.3 is parameterized differencly
# Also, setup is parameterized independent of swash.
# Even though the parameterization of swash depends on setup, a single coeficcient is used to model the process
# Unlike stockdon which includes a parameterization for setup seperatley.
# In practice, the stockdon swash can just be not included to the empirical formula
# However, holman doesn't allow for that because they calculated the constant including swasg

# Holman also provides formula for the incident and infragravity swash height
#  He mentions that the incident swash will cap because of saturation, but the infragravity will keep growing.
# Maybe can see this by plotting the incident band swash ontop of the infragravity band swash.
# This isin't runup nessesarily, beacuse runup is incident and infragravity combined, like how stickdon does it.
# What I should see in the swash bands graph is that infragravity swash keeps growing, while incident swash stops growing as the magnitude of the runup increases.

# Pi Day Update
# I did a forecast using padcirc
# The setup, the water - still water, is pretty low
# Whaat are the concequences of this?
# Using stockdon's parameterization of 1.1(setup  + S/2) results in low values

    def calculateHolmanHighRunup(self, iribarrenNumber, waveHeight):
        slope = 0.80
        intercept = 0.11
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanMidRunup(self, iribarrenNumber, waveHeight):
        slope = 0.93
        intercept = 0.04
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanLowRunup(self, iribarrenNumber, waveHeight):
        slope = 0.24
        intercept = 0.65
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanHighSetup(self, iribarrenNumber, waveHeight):
        slope = 0.35
        intercept = 0.14
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanMidSetup(self, iribarrenNumber, waveHeight):
        slope = 0.46
        intercept = 0.06
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanLowSetup(self, iribarrenNumber, waveHeight):
        slope = -0.20
        intercept = 0.73
        return ((iribarrenNumber * slope) + intercept) * waveHeight
        
    def calculateHolmanHighSwash(self, iribarrenNumber, waveHeight):
        slope = 0.88
        intercept = -0.06
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanMidSwash(self, iribarrenNumber, waveHeight):
        slope = 0.92
        intercept = -0.03
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanLowSwash(self, iribarrenNumber, waveHeight):
        slope = 0.87
        intercept = -0.15
        return ((iribarrenNumber * slope) + intercept) * waveHeight
               
    def calculateHolmanIncidentSwash(self, iribarrenNumber, waveHeight):
        slope = 0.69
        intercept = -0.19
        return ((iribarrenNumber * slope) + intercept) * waveHeight

    def calculateHolmanInfragravitySwash(self, iribarrenNumber, waveHeight):
        slope = 0.53
        intercept = 0.09
        return ((iribarrenNumber * slope) + intercept) * waveHeight
        
# Stockdon parameterizations
    def calculateStockdonSetup(self, averageSlope, waveHeight, deepwaterWavelength):
        slope = 0.35
        return slope * (np.sqrt(waveHeight * deepwaterWavelength)) * averageSlope
        
    def calculateStockdonIncidentSwash(self, averageSlope, waveHeight, deepwaterWavelength):
        slope = 0.75
        return slope * (np.sqrt(waveHeight * deepwaterWavelength)) * averageSlope
    def calculateStockdonInfragravitySwash(self, waveHeight, deepwaterWavelength):
        slope = 0.06
        return slope * (np.sqrt(waveHeight * deepwaterWavelength))
    def calculateStockdonLowSetup(self, waveHeight, deepwaterWavelength):
        slope = 0.016
        return slope * (np.sqrt(waveHeight * deepwaterWavelength))
    def calculateStockdonLowSwash(self, waveHeight, deepwaterWavelength):
        slope = 0.046
        return slope * (np.sqrt(waveHeight * deepwaterWavelength))
        

    def calculateStockdonRunup(self, averageSlope, waveHeight, deepwaterWavelength, stillwaterLevel):
        setup = self.calculateStockdonSetup(averageSlope, waveHeight, deepwaterWavelength)
        swash = np.sqrt(waveHeight * deepwaterWavelength * (((averageSlope**2) * 0.563) + 0.004))
        return (1.1 * (setup + (swash/2.0))) + stillwaterLevel
        
    def findDuneHeight(self, time, duneHeights):
        """
        Find the dune height for a given Unix timestamp from the duneHeights list.
        Returns the height of the closest timestamp that is less than or equal to the given time.
        If no such timestamp exists, returns the earliest height.
        """
        if not duneHeights:
            return 0.0  # Default if no heights are defined
        
        # Sort by timestamp to ensure correct order
        sorted_heights = sorted(duneHeights, key=lambda x: x['timestamp'])
        
        # Find the closest timestamp <= time
        for entry in reversed(sorted_heights):
            if time >= entry['timestamp']:
                return entry['height']
        
        # If no timestamp is <= time, return the latest height
        return sorted_heights[-1]['height']
        
    def calculateStockdonRunupNoSetup(self, averageSlope, waveHeight, deepwaterWavelength):
        swash = np.sqrt(waveHeight * deepwaterWavelength * (((averageSlope**2) * 0.563) + 0.004))
        return 1.1 * (swash/2.0)
        
#     Adds the swash (S) to the "adcircSetup", in this case is just the stil;l
    def calculateAdcircRunup(self, adcircWaterLevel, stockdonSwash):
        return adcircWaterLevel + stockdonSwash
#         stockdonCorrectedSwash = (stockdonSwash / 1.1) * 2.0
#         return 1.1 * (adcircSetup + stockdonCorrectedSwash)
#         return adcircWaterLevel  + stockdonCorrectedSwash
        
    def calculateAdcircRunupUsingSetup(self, adcircSetup, stockdonSwash, stillwaterLevel):
        stockdonCorrectedSwash = (stockdonSwash / 1.1)
        return (1.1 * (adcircSetup + stockdonCorrectedSwash)) + stillwaterLevel
    
    def calculateAdcircRunupUsingSetupFullSwash(self, adcircSetup, stockdonSwash, stillwaterLevel):
        stockdonCorrectedSwash = (stockdonSwash / 1.1) * 2
        return 1.1 * (adcircSetup + stockdonCorrectedSwash) + stillwaterLevel
        
    def calculateStockdonLowRunup(self, waveHeight, deepwaterWavelength):
        slope = 0.043
        return slope * (np.sqrt(waveHeight * deepwaterWavelength))

        
    def calculateRunupDistance(self, runupHeight, averageSlope):
        return runupHeight * np.sqrt((1/(averageSlope**2)) + 1)
        
    def calculateRunupWaterline(self, waterlineCoordinates, tangentCoordinates, runup):
        # Extract coordinates (latitude, longitude)
        lat1, lon1 = waterlineCoordinates
        lat2, lon2 = tangentCoordinates
    
        # Calculate the geodesic between the points
        geod = Geodesic.WGS84
        g = geod.Inverse(lat1, lon1, lat2, lon2)
    
        # Get the azimuth (bearing) at the first point
        azi = g['azi1']
    
        # Calculate perpendicular bearing (90 degrees clockwise)
        perp_azi = (azi - 90) % 360
    
        # Calculate new positions by moving perpendicular to the line
        # Move waterline point
        r1 = geod.Direct(lat1, lon1, perp_azi, runup)
        runupWaterlineLat = r1['lat2']
        runupWaterlineLon = r1['lon2']
    
        # Move tangent point
        r2 = geod.Direct(lat2, lon2, perp_azi, runup)
        runupTangentLat = r2['lat2']
        runupTangentLon = r2['lon2']
    
        # Return translated coordinates as tuples
        runupWaterlineCoordinates = (runupWaterlineLat, runupWaterlineLon)
        runupTangentCoordinates = (runupTangentLat, runupTangentLon)
    
        return runupWaterlineCoordinates, runupTangentCoordinates

    def __init__(self, 
        STATIONS_FILE="",
        ADCIRC_WATER_DATA_FILE="", 
        WAVE_SWH_DATA_FILE="", 
        WAVE_MWD_DATA_FILE="",
        WAVE_PWP_DATA_FILE="",
        ADCIRC_MESH_DATA_FILE="",
        ADCIRC_STILLWATER_DATA_FILE="",
        ADCIRC_TIDEWATER_DATA_FILE="",
        RUNUP_DATA_FILE=""):
        print("Generating Runup!", flush=True)
        temp_directory = RUNUP_DATA_FILE[0:RUNUP_DATA_FILE.rfind("/") + 1]
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
        with open(ADCIRC_WATER_DATA_FILE) as datafile:
            waterDict = json.load(datafile)
        with open(WAVE_SWH_DATA_FILE) as datafile:
            swhDict = json.load(datafile)
#         with open(WAVE_MWD_DATA_FILE) as datafile:
#             mwdDict = json.load(datafile)
        with open(WAVE_PWP_DATA_FILE) as datafile:
            pwpDict = json.load(datafile)
        with open(ADCIRC_MESH_DATA_FILE) as datafile:
            meshDict = json.load(datafile)
        with open(ADCIRC_STILLWATER_DATA_FILE) as datafile:
            stillwaterDict = json.load(datafile)
        with open(ADCIRC_TIDEWATER_DATA_FILE) as datafile:
            tidewaterDict = json.load(datafile)
            


        # Noreaster 12/23 festivus  storm 22, 23
        # startDate = "20221220"
        # endDate = "20221224"
        # dateStartFormat = "2022-12-20"
        # 
        # heightStartDate = "2022-12-20T00:00:00Z"
        # heightEndDate = "2022-12-24T23:59:59Z"
    
        runupDict = {}

        for key in stationsDict["RUNUP"].keys():
#             The RUNUP stations should correspond to a node on the ADCIRC mesh
#               The RUNUP stations can also include an offshore node in the json, bypassing the need to find the offshore node index.
            stationDict = stationsDict["RUNUP"][key]
            if("d" in key):
                generalKey = key[0:key.index("d")]
            elif(len(key) == 3):
                generalKey = key[0:-1]
            else:
                generalKey = key
            CALCULATE_DAILY_AVERAGE_SLOPE = False
            normalDict = stationsDict["NORMAL"][generalKey]
            tangentDict = stationsDict["TANGENT"][generalKey]
            stationId = stationDict["id"]
            stationName = stationDict["name"]
            shorelineCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
            offshoreKey = stationDict["offshoreKey"]
            offshoreCoordinates = (float(stationDict["offshoreLatitude"]), float(stationDict["offshoreLongitude"]))
            surfKey = stationDict["surfKey"]
            surfCoordinates = (float(stationDict["surfLatitude"]), float(stationDict["surfLongitude"]))
            deeplineKey = stationDict["deeplineKey"]
            slopelineKey = stationDict["slopelineKey"]
            slopelineCoordinates = (float(stationDict["slopelineLatitude"]), float(stationDict["slopelineLongitude"]))
            
            runupTimes = waterDict[offshoreKey]["times"]
#             runupTimes = swhDict[offshoreKey]["times"]
            offshoreWater = waterDict[offshoreKey]["water"]
            
            
#             waterTimestampsInitialized = False
#             for stationKey in waterDict.keys():
#                 if(stationKey != "map_data"):
#                     nodeIndex = waterDict[stationKey]["nodeIndex"]
#                     if(not self.tideExists or (stationKey in tideDataset.keys())):
#                         self.waterLabels.append(nodeIndex)
#                         self.waterLatitudes.append(waterDataset[stationKey]["latitude"])
#                         self.waterLongitudes.append(waterDataset[stationKey]["longitude"])
#                 
#                         if(not tideLabelsInitialized):
#                             self.tideLabels.append(self.obsMetadata["NOS"][stationKey]["name"])
#                             self.tideLatitudes.append(float(self.obsMetadata["NOS"][stationKey]["latitude"]))
#                             self.tideLongitudes.append(float(self.obsMetadata["NOS"][stationKey]["longitude"]))
# 
#                         datapointWaters = []
#                         for index in range(len(waterDataset[stationKey]["times"])):
#                             if(self.waterStartDate == None):
#                                 self.waterStartDate = datetime.fromtimestamp(int(waterDataset[stationKey]["times"][index]), timezone.utc)
#                             if(not waterTimestampsInitialized):
#                                 self.waterTimes.append(self.unixTimeToDeltaHours(waterDataset[stationKey]["times"][index], self.waterStartDate))
#                             datapointWaters.append(waterDataset[stationKey]["water"][index])
#                         waterTimestampsInitialized = True
#                         self.datapointsWaters.append(datapointWaters)
#                         if(self.tideExists):
#                             tideTimes = []
#                             tideWaters = []
#                 #                         Height is not station altitude, it is sea surface height
#                             for index in range(len(tideDataset[stationKey]["times"])):
#                                 tideTimes.append(self.unixTimeToDeltaHours(tideDataset[stationKey]["times"][index], self.waterStartDate))
#                                 tideWater = tideDataset[stationKey]["water"][index]
#                                 tideWaters.append(tideWater)
#                             self.tideDatapointsTimes.append(tideTimes)
#                             self.tideDatapointsWaters.append(tideWaters)
#                             tidePredictionTimes = []
#                             tidePredictionWaters = []
#                 #                         Height is not station altitude, it is sea surface height
#                             for index in range(len(tideDataset[stationKey]["prediction_times"])):
#                                 tidePredictionTimes.append(self.unixTimeToDeltaHours(tideDataset[stationKey]["prediction_times"][index], self.waterStartDate))
#                                 tidePredictionWater = tideDataset[stationKey]["prediction_water"][index]
#                                 tidePredictionWaters.append(tidePredictionWater)
#                             self.tideDatapointsPredictionTimes.append(tidePredictionTimes)
#                             self.tideDatapointsPredictionWaters.append(tidePredictionWaters)
#             tideLabelsInitialized = True
            
            
            # Your existing code
#             offshoreSwh = swhDict[offshoreKey]["swh"]
#             offshoreMwd = mwdDict[offshoreKey]["mwd"]
#             offshorePwp = pwpDict[offshoreKey]["pwp"]
            
            offshoreSwh = swhDict[deeplineKey]["swh"]
#             offshoreMwd = mwdDict[deeplineKey]["mwd"]
            offshorePwp = pwpDict[deeplineKey]["pwp"]

#             meshDict[slopelineKey]["elevation"]
            duneHeights = []
            for index, time in enumerate(runupTimes):
                duneHeights.append(self.findDuneHeight(time, stationDict["duneHeights"]))
#                 print("time", time, stationDict["duneHeights"])
#             print("duneHeights", duneHeights)
#             quit()
            print("deepline SWH Max: ", np.max(offshoreSwh))
            print("deepline PWP Max: ", np.max(offshorePwp))

#             shorelineElevation = float(meshDict[generalKey]["elevation"])
#             surfElevation = float(meshDict[surfKey]["elevation"])
            
#             offshoreElevation = float(meshDict[offshoreKey]["elevation"])
            offshoreElevation = float(meshDict[deeplineKey]["elevation"])

            print("deeplineElevation: ", offshoreElevation)
            # Calculating wave parameters preserved in arrays
            g = 9.81
            offshoreWavelength = (g * np.array(offshorePwp)**2) / (2 * math.pi)  # Deepwater wavelength (L_0)
            offshoreSteepness = np.array(offshoreSwh) / offshoreWavelength  # Initial steepness (will update later)

            # New code for reverse shoaling
            # Step 1: Deepwater group velocity
            T = np.array(offshorePwp)  # Wave period
            c_g0 = g * T / (4 * math.pi)  # Deepwater group velocity

            # Step 2: Solve dispersion relation for k at offshore depth
            h = offshoreElevation * -1.0  # Assuming this is the depth (positive)
            omega = 2 * math.pi / T  # Angular frequency

            # Function to solve dispersion relation: omega^2 = gk * tanh(kh)
            def dispersion(k, omega, h):
                return omega**2 - g * k * np.tanh(k * h)

            # Initial guess for k (using deepwater approximation)
            k0 = omega**2 / g
            k = np.zeros_like(T, dtype=float)
            for i in range(len(T)):
                k[i] = fsolve(dispersion, k0[i], args=(omega[i], h))[0]

            # Step 3: Calculate local wavelength, phase speed, and group velocity
            L = 2 * math.pi / k  # Local wavelength at offshore depth
            c = omega / k  # Phase speed
            n = 0.5 * (1 + (2 * k * h) / np.sinh(2 * k * h))  # Group velocity factor
            c_g = n * c  # Local group velocity

            # Step 4: Reverse shoal to get deepwaterSwh
            deepwaterSwh = offshoreSwh * np.sqrt(c_g / c_g0)

            # Step 5: Update offshoreSwh and recalculate steepness
            offshoreSwh = deepwaterSwh  # As requested
            offshoreSteepness = offshoreSwh / offshoreWavelength  # Updated steepness using deepwater values

#             slopelineElevation = float(meshDict[slopelineKey]["elevation"])

            # Now offshoreSwh represents the deepwater significant wave height
            waterlineKeys = []
            averageSlopes = []
            iribarrenNumbers = []
            runupValues = []
            runupValuesHolmanHigh = []
            runupValuesHolmanMid = []
            runupValuesHolmanLow = []
            swashValuesHolmanHigh = []
            swashValuesHolmanMid = []
            swashValuesHolmanLow = []
            setupValuesHolmanHigh = []
            setupValuesHolmanMid = []
            setupValuesHolmanLow = []
            swashValuesHolmanIncident = []
            swashValuesHolmanInfragravity = []
            setupValuesStockdon = []
            swashValuesStockdonIncident = []
            swashValuesStockdonInfragravity = []
            setupValuesStockdonLow = []
            swashValuesStockdonLow = []
            runupValuesStockdon = []
            runupValuesStockdonNoSetup = []
            runupValuesStockdonLow = []
            runupValuesAdcirc = []
            setupValuesAdcirc = []
            runupWaterlineLatitudes = [] 
            runupWaterlineLongitudes = [] 
            runupTangentLatitudes = [] 
            runupTangentLongitudes = []
            
            runupValuesObs = []
            runupValuesObsSwash = []
            runupValuesObsIncidentSwash = []
            runupValuesObsInfragravitySwash = []
            runupValuesObsSwh = []
            runupValuesObsPwp = []
            runupValuesObsImpact = []
            runupValuesObsBeachSlope = []
            
            for index, waterValue in enumerate(offshoreWater):
                waterlineKey = None
                stillwaterLineKey = None
                tidewaterLineKey = None
#                Find the waterline key
                for normalKey in normalDict:
                    normalStationWaterValue = waterDict[normalKey]["water"][index]
#                     normalStationStillwaterValue = stillwaterDict[normalKey]["water"][index]
#                     print("normalStationWaterValue, index", index, normalStationWaterValue)
#                     if(not np.isnan(normalStationStillwaterValue)):
#                         stillwaterLineKey = normalKey
                    if(not np.isnan(normalStationWaterValue)):
                        waterlineKey = normalKey
                        break
                if(waterlineKey != None):
#                     print("Found waterline", waterlineKey, " for index", index)
                    waterlineKeys.append(waterlineKey)
                else:
                    print("DID NOT FIND WATERLINE! Appending previous waterline key.")
                    print("If no previous key exists, will error out.")
                    waterlineKeys.append(waterlineKey[-1])
                    
#                 Find the stillwater line, so we can pull SWL data without any gaps
                for normalKey in normalDict:
                    normalStationStillwaterValue = stillwaterDict[normalKey]["water"][index]
#                     print("normalStationWaterValue, index", index, normalStationWaterValue)
                    if(not np.isnan(normalStationStillwaterValue)):
                        stillwaterLineKey = normalKey
                        break
                        
                for normalKey in normalDict:
                    normalStationTidewaterValue = tidewaterDict[normalKey]["water"][index]
#                     print("normalStationWaterValue, index", index, normalStationWaterValue)
                    if(not np.isnan(normalStationTidewaterValue)):
                        tidewaterLineKey = normalKey
                        break
#                 Now I have the waterline key
                


#                   The corresponding tangent key
                tangentStation = tangentDict[waterlineKey]
                tangentCoordinates = (float(tangentStation["latitude"]), float(tangentStation["longitude"]))
                
                waterlineStation = normalDict[waterlineKey]
                waterlineCoordinates = (float(waterlineStation["latitude"]), float(waterlineStation["longitude"]))
                waterlineElevation = float(meshDict[waterlineKey]["elevation"])
                
                adjacentWaterlineKey = str(int(waterlineKey) + 1)
                adjacentWaterlineStation = normalDict[adjacentWaterlineKey]
                adjacentWaterlineCoordinates = (float(adjacentWaterlineStation["latitude"]), float(adjacentWaterlineStation["longitude"]))
                adjacentWaterlineElevation = meshDict[adjacentWaterlineKey]["elevation"]
                
#                 Now I need to calculate the averageSlope using the waterlineKey point


#                 waterlineDistance = haversine.haversine(waterlineCoordinates, adjacentWaterlineCoordinates) * 1000
#                 averageSlope = math.atan((waterlineElevation - adjacentWaterlineElevation) / waterlineDistance)
#                 averageSlopes.append(averageSlope)
                
            if(CALCULATE_DAILY_AVERAGE_SLOPE):
                startOfDayTime = None
                maxWaterlineKey = None
                minWaterlineKey = None
                numIndexes = 0
                for index, time in enumerate(runupTimes):
                    numIndexes += 1
                    if(startOfDayTime == None):
                        startOfDayTime = time
                    waterlineKey = waterlineKeys[index]
                    if(maxWaterlineKey == None or waterlineKey > maxWaterlineKey):
                        maxWaterlineKey = waterlineKey
                    if(minWaterlineKey == None or waterlineKey < minWaterlineKey):
                        minWaterlineKey = waterlineKey
                    if((time - startOfDayTime) == DAY_IN_UNIX_TIME or index == (len(runupTimes) - 1)):
                        waterlineStation = normalDict[minWaterlineKey]
                        waterlineCoordinates = (float(waterlineStation["latitude"]), float(waterlineStation["longitude"]))
                        waterlineElevation = float(meshDict[minWaterlineKey]["elevation"])
                    
                        if(minWaterlineKey != maxWaterlineKey):
                            adjacentWaterlineKey = str(int(maxWaterlineKey))
                        else:
                            adjacentWaterlineKey = str(int(minWaterlineKey) + 1)
                        adjacentWaterlineStation = normalDict[adjacentWaterlineKey]
                        adjacentWaterlineCoordinates = (float(adjacentWaterlineStation["latitude"]), float(adjacentWaterlineStation["longitude"]))
                        adjacentWaterlineElevation = meshDict[adjacentWaterlineKey]["elevation"]
                    
        #                 Now I need to calculate the averageSlope using the waterlineKey point
    
    
                        waterlineDistance = haversine.haversine(waterlineCoordinates, adjacentWaterlineCoordinates) * 1000
                        averageSlope = math.atan((waterlineElevation - adjacentWaterlineElevation) / waterlineDistance)
                        print("END DAY, Slope", time, startOfDayTime, averageSlope)
                        for averageSlopeIndex in range(numIndexes):
                            averageSlopes.append(averageSlope)
    #                         print("APPENDING AVERAGE SLOPE", averageSlope)
                        numIndexes = 0
                        startOfDayTime = None
                        minWaterlineKey = None
                        maxWaterlineKey = None
                    
#             print("AVERAGE SLOPES", averageSlopes)
#             quit()
#             From this point, iterate through each timestep in the wave file.
            for index, waterValue in enumerate(offshoreWater):
                waterlineKey = None
                stillwaterLineKey = None
                tidewaterLineKey = None
#                Find the waterline key
                waterlineKey = waterlineKeys[index]
                    
#                 Find the stillwater line, so we can pull SWL data without any gaps
                for normalKey in normalDict:
                    normalStationStillwaterValue = stillwaterDict[normalKey]["water"][index]
#                     print("normalStationWaterValue, index", index, normalStationWaterValue)
                    if(not np.isnan(normalStationStillwaterValue)):
                        stillwaterLineKey = normalKey
                        break
                        
                for normalKey in normalDict:
                    normalStationTidewaterValue = tidewaterDict[normalKey]["water"][index]
#                     print("normalStationWaterValue, index", index, normalStationWaterValue)
                    if(not np.isnan(normalStationTidewaterValue)):
                        tidewaterLineKey = normalKey
                        break
#                 Now I have the waterline key
                


#                   The corresponding tangent key
                tangentStation = tangentDict[waterlineKey]
                tangentCoordinates = (float(tangentStation["latitude"]), float(tangentStation["longitude"]))
                
                waterlineStation = normalDict[waterlineKey]
                waterlineCoordinates = (float(waterlineStation["latitude"]), float(waterlineStation["longitude"]))
                waterlineElevation = float(meshDict[waterlineKey]["elevation"])
                
                adjacentWaterlineKey = str(int(waterlineKey) + 1)
                adjacentWaterlineStation = normalDict[adjacentWaterlineKey]
                adjacentWaterlineCoordinates = (float(adjacentWaterlineStation["latitude"]), float(adjacentWaterlineStation["longitude"]))
                adjacentWaterlineElevation = meshDict[adjacentWaterlineKey]["elevation"]
                
#                 Now I need to calculate the averageSlope using the waterlineKey point

                if(CALCULATE_DAILY_AVERAGE_SLOPE):
                    averageSlope = averageSlopes[index]
                else:
                    waterlineDistance = haversine.haversine(waterlineCoordinates, adjacentWaterlineCoordinates) * 1000
                    averageSlope = math.atan((waterlineElevation - adjacentWaterlineElevation) / waterlineDistance)
                    averageSlopes.append(averageSlope)
#                 Hardcode foreshore beach slope
#                 if("1" in generalKey):
#                     averageSlope = 0.13
#                 elif("2" in generalKey):
#                     averageSlope = 0.11
#                 elif("3" in generalKey):
#                     averageSlope = 0.08
#                 elif("4" in generalKey):
#                     averageSlope = 0.07
#                 elif("5" in generalKey):
#                     averageSlope = 0.07
#                 Use first calculate average slope
                
#                 slopelineDistance = haversine.haversine(slopelineCoordinates, waterlineCoordinates) * 1000
#                 slopelineDistance = slopelineDistance
#                 averageSlope = math.atan((slopelineElevation - waterlineElevation) / slopelineDistance)
#                 averageSlopes.append(averageSlope)
#                 print("slopelineElevation, distance, averageSlope, waterlineElevation: ", slopelineElevation, slopelineDistance, averageSlope, waterlineElevation)
                
#                 Get the water elevation at the waterline point.
#                  The minimum of this should just be the elevation of the point itself
#                   The wet dry algorithim is also important here
# #                 Because I am having issues with the waterline key advancing in the SWAN vs the padcirc run,
#                   I can't get SWL values for the timestamps where there is no data at that node for padcirc, but is for SWAN
#               So, just going to hardcode to use waterlineKey to be the first waterline key it finds.
# Doing this everywhere messes up the lines, so just to pull the SWL and the SWL + setup water levels,
#           I will always use the same node, which is the first waterline node in the timeseries.
#           Doing this wont change the generated values that much, as the water elevation is very similar for all nodes along the normal of the beach.
#                 waterlineKey = waterlineKeys[0]
                waterlineWaterValue = waterDict[waterlineKey]["water"][index]
                waterlineStillwaterValue = stillwaterDict[stillwaterLineKey]["water"][index]
                waterlineTidewaterValue = tidewaterDict[tidewaterLineKey]["water"][index]
#                 print("waterlineWaterValue, waterlineStillWaterValue", waterlineWaterValue, waterlineStillwaterValue)
#                 print("waterlineDistance, averageSlope, coordinates", waterlineDistance, averageSlope, waterlineCoordinates, adjacentWaterlineCoordinates)
                #           Then I need to calculate the wave parameters
#           That can happen outside of the loop

#           Then calculate the irribarren number
                iribarren = (averageSlope / (np.sqrt(offshoreSteepness[index])))
                iribarrenNumbers.append(iribarren)
                
                
                runupHolmanHigh = self.calculateHolmanHighRunup(iribarren, offshoreSwh[index])
                runupHolmanMid = self.calculateHolmanMidRunup(iribarren, offshoreSwh[index])
                runupHolmanLow = self.calculateHolmanLowRunup(iribarren, offshoreSwh[index])

                swashHolmanLow = self.calculateHolmanLowSwash(iribarren, offshoreSwh[index])
                swashHolmanIncident = self.calculateHolmanIncidentSwash(iribarren, offshoreSwh[index])
                swashHolmanInfragravity = self.calculateHolmanInfragravitySwash(iribarren, offshoreSwh[index])
                
                stockdonSetup = self.calculateStockdonSetup(averageSlope, offshoreSwh[index], offshoreWavelength[index])
                
                stockdonSwashIncident = self.calculateStockdonIncidentSwash(averageSlope, offshoreSwh[index], offshoreWavelength[index])
                stockdonSwashInfragravity = self.calculateStockdonInfragravitySwash(offshoreSwh[index], offshoreWavelength[index])
                    
                stockdonSetupLow = self.calculateStockdonLowSetup(offshoreSwh[index], offshoreWavelength[index])                
                stockdonSwashLow = self.calculateStockdonLowSwash(offshoreSwh[index], offshoreWavelength[index])
                stockdonRunup = self.calculateStockdonRunup(averageSlope, offshoreSwh[index], offshoreWavelength[index], waterlineStillwaterValue)
#                 stockdonRunup = self.calculateStockdonRunup(averageSlope, offshoreSwh[index], offshoreWavelength[index], waterlineTidewaterValue)
                stockdonRunupNoSetup = self.calculateStockdonRunupNoSetup(averageSlope, offshoreSwh[index], offshoreWavelength[index])
                
#                 Add the waterline water value
#                 The "adrircSetup" is a value that is the still water level 
#                  Assumed to be 0 in stockdon because the data is time averaged
#                   But is usually nonzero in adcirc runs, because of 1. sea level offset 2. tidal forcing 3. Wind induced storm surge 4. The motions of the GWCE
#               Basically the still water level is the level at equilibrium
#               The setup is what SWAN adds, and the adcircSetup is the value after adding the still water level + setup
#               So stockdon has the still water level as 0, so its doing its runup calculation relative to the still water level
#               My runup calculation is relative to the geoid NAVD88. 
#               You cant seperate the setup from the still water level offset yet, that is what I am trying to compile
#               padcswan for.
#               Theres a slight problem though. In the stockdon formula, there is a factor of 1.1. This factor should 
#               only be applied to the setup! not the still water level also. The still water level should be added without the 
#               1.1 factor. this is a meme level situation.
                adcircSetup = waterlineWaterValue - waterlineStillwaterValue
                adcircStormSurge = waterlineStillwaterValue - waterlineTidewaterValue
                adcircRunup = self.calculateAdcircRunup(waterlineWaterValue, stockdonRunupNoSetup)
#                 adcircRunup = self.calculateAdcircRunup(waterlineTidewaterValue, stockdonRunupNoSetup)

#                 Hijack some existing variables
                stockdonSetupLow = adcircSetup
                runupHolmanHigh = adcircStormSurge
#                 adcircSetup = adcircSetup + adcircStormSurge
                adcircSetup = adcircSetup
                runupHolmanMid = self.calculateAdcircRunupUsingSetup(adcircSetup, stockdonRunupNoSetup, waterlineStillwaterValue)
#                 runupHolmanMid = self.calculateAdcircRunupUsingSetup(adcircSetup, stockdonRunupNoSetup, waterlineTidewaterValue)
                runupHolmanLow = offshoreSwh[index]
                
#                 Define runupHolmanMid as 1.1(S/2) + eta
                runupHolmanMid = adcircRunup
                stockdonSwashLow = waterlineWaterValue
                swashHolmanLow = stockdonRunupNoSetup
#                 runupHolmanMid = stockdonRunup


                
#                 runupValues.append(stockdonRunup)
                runupValuesHolmanHigh.append(runupHolmanHigh)
                runupValuesHolmanMid.append(runupHolmanMid)
                runupValuesHolmanLow.append(runupHolmanLow)
                swashValuesHolmanLow.append(swashHolmanLow)
                
                setupValuesStockdon.append(stockdonSetup)
                swashValuesStockdonIncident.append(stockdonSwashIncident)
                swashValuesStockdonInfragravity.append(stockdonSwashInfragravity)
                setupValuesStockdonLow.append(stockdonSetupLow)
                swashValuesStockdonLow.append(stockdonSwashLow)
                runupValuesStockdon.append(stockdonRunup)
                runupValuesStockdonNoSetup.append(stockdonRunupNoSetup)
                
                setupValuesAdcirc.append(adcircSetup)
                runupValuesAdcirc.append(adcircRunup)
                
                runupDistance = self.calculateRunupDistance(stockdonRunupNoSetup, averageSlope)
                runupValues.append(runupDistance)
                runupWaterlineCoordinates, runupTangentCoordinates = self.calculateRunupWaterline(waterlineCoordinates, tangentCoordinates, runupDistance)
                runupWaterlineLatitudes.append(runupWaterlineCoordinates[0])
                runupWaterlineLongitudes.append(runupWaterlineCoordinates[1])
                runupTangentLatitudes.append(runupTangentCoordinates[0])
                runupTangentLongitudes.append(runupTangentCoordinates[1])
                

                
# Get obs runup
            if("1" in generalKey):
                site_ids=[1402]
            elif("2" in generalKey):
                site_ids=[1402]
            elif("3" in generalKey):
                site_ids=[1402]
            elif("4" in generalKey):
                site_ids=[1403]
            elif("5" in generalKey):
                site_ids=[1403]
#                 This isint working                     

# forecast_dates: List[str] = ["2022-12-20", "2023-12-15"],
#                 print("site_ids", site_ids)
            water_level_data = fetch_water_levels(
                site_ids=site_ids,
                forecast_dates = ["2023-12-15"],
                fields=fields,
                base_dir="."
            )
            
            for item in water_level_data:
                obsRunupTimes = item["unixTime"]
#                     print("obsRunupTimes converted", datetime.fromtimestamp(obsRunupTimes, timezone.utc))
#                     obsLatitude = item["siteLatitude"]
#                     obsLongitude = item["siteLongitude"]
                obsToeHeight = item["toeHeight"] - 0.069
                obsCrestHeight = item["crestHeight"] - 0.069
                obsTwl = item["twl"] - 0.069
                obsTwl05 = item["twl05"] - 0.069
                obsTwl95 = item["twl95"] - 0.069
                obsSetup = item["setup"]
                obsRunup = item["runup"]
                obsWaterLevel = item["tideWindSetup"] - 0.069
                obsSwash = item["swash"]
                obsIncidentSwash = item["incSwash"]
                obsInfragravitySwash = item["infragSwash"]
                obsSwh = item["hs"]
                obsPwp = item["pp"]
                obsImpact = item["predictedImpact"]
                obsBeachSlope = item["beachSlope"]
#                     print("IMPACT:", obsImpact)
                
                setupHolmanHigh = obsRunupTimes
                setupHolmanMid = obsToeHeight
                setupHolmanLow = obsCrestHeight
                swashHolmanHigh = obsTwl
                swashHolmanMid = obsTwl05
                swashHolmanIncident = obsTwl95
                swashHolmanInfragravity = obsSetup
                stockdonRunupLow = obsWaterLevel
            

            
                setupValuesHolmanHigh.append(setupHolmanHigh)
                setupValuesHolmanMid.append(setupHolmanMid)
                setupValuesHolmanLow.append(setupHolmanLow)
                swashValuesHolmanHigh.append(swashHolmanHigh)
                swashValuesHolmanMid.append(swashHolmanMid)
                swashValuesHolmanIncident.append(swashHolmanIncident)
                swashValuesHolmanInfragravity.append(swashHolmanInfragravity)
                runupValuesStockdonLow.append(stockdonRunupLow)
                runupValuesObs.append(obsRunup)
                runupValuesObsSwash.append(obsSwash)
                runupValuesObsIncidentSwash.append(obsIncidentSwash)
                runupValuesObsInfragravitySwash.append(obsInfragravitySwash)
                runupValuesObsSwh.append(obsSwh)
                runupValuesObsPwp.append(obsPwp)
                runupValuesObsImpact.append(obsImpact)
                runupValuesObsBeachSlope.append(obsBeachSlope)

#             scrapped variables
#             setupHolmanHigh = self.calculateHolmanHighSetup(iribarren, offshoreSwh[index])
#             setupHolmanMid = self.calculateHolmanMidSetup(iribarren, offshoreSwh[index])
#             setupHolmanLow = self.calculateHolmanLowSetup(iribarren, offshoreSwh[index])
#             
#                 swashHolmanHigh = self.calculateHolmanHighSwash(iribarren, offshoreSwh[index])
#                 swashHolmanMid = self.calculateHolmanMidSwash(iribarren, offshoreSwh[index])
#                 swashHolmanIncident = self.calculateHolmanIncidentSwash(iribarren, offshoreSwh[index])
#                 swashHolmanInfragravity = self.calculateHolmanInfragravitySwash(iribarren, offshoreSwh[index])
#                 stockdonRunupLow = self.calculateStockdonLowRunup(offshoreSwh[index], offshoreWavelength[index]) 

            
#                 runupValuesStockdonLow = obsSwash
#                 runupValuesStockdonNoSetup = obsIncidentSwash
#                 runupValuesStockdon = obsIngragravitySwash
            
            
            
            
            
            
#             
#             # Print a sample of results (first few records for brevity)
#             for item in water_level_data[:5]:  # Limit to first 5 for demonstration
#                 print(f"Site {item['siteId']} (Timestamp: {item['unixTime']}):")
#                 print(f"  Latitude: {item['siteLatitude']}, Longitude: {item['siteLongitude']}")
#                 print(f"  Dune Toe Height: {item['toeHeight']}, Dune Crest Height: {item['crestHeight']}")
#                 print(f"  TWL: {item['twl']}, TWL05: {item['twl05']}, TWL95: {item['twl95']}")
#                 print(f"  Setup: {item['setup']}, Runup: {item['runup']}")
#                 print(f"  Runup05: {item['runup05']}, Runup95: {item['runup95']}")
#                 print(f"  Tide+Wind Setup: {item['tideWindSetup']}, Swash: {item['swash']}")
#                 print(f"  Incident Swash: {item['incSwash']}, Infragravity Swash: {item['infragSwash']}")
#                 print(f"  Hs: {item['hs']}, Pp: {item['pp']}")
#                 print(f"  Predicted Impact: {item['predictedImpact']}")
#                 print()
#     

#           Then calculate the runup value 2% exceedence

#           Then calculate the runupLine and runupTangentLine
#           
#           Save these. Will end up having two arrays called runupWaterlineLatitudes[] runupWaterlineLogitudes runupTangentLatitudes runupTangentLongitudes

#           These will get graphed alongside the waterlineKey generated line with the tangent point


#                     print("waterValue at ", normalKey, waterDict[normalKey]["water"][index])
#                     print("closest Nodes to normalkey", normalKey, waterDict[normalKey]["nodeIndex"])
#                     closestNode = waterDict[normalKey]["nodeIndex"]
#                     closestNodeWaterIndex = waterDict["map_data"]["map_points"].index(closestNode)
#                     print(closestNodeWaterIndex)
#                     print(len(waterDict["map_data"]["map_water"]))
#                     print(waterDict["map_data"]["map_water"][index][closestNodeWaterIndex])
#                     normalWaterValue = waterDict[normalKey]["water"][index]
#                     if not np.isnan(normalWaterValue):
#                         waterlineKey = normalKey
#                         break
#                 normalStation = normalDict[waterlineKey]
#                 tangentStation = tangentDict[waterlineKey]
#                 print("Normal, tangent stations", normalStation, tangentStation)
#             print(offshoreWater, offshoreSwh, offshoreMwd, offshoreMwp, shorelineElevation, offshoreElevation)
#             print("max time, water, swg, mwd, mwp, and elevation shoreline offshore", max(offshoreWater), max(offshoreSwh), max(offshoreMwd), max(offshoreMwp), shorelineElevation, offshoreElevation)
    #                             distance and threshold in kilometers
#             print("shorelineElevation, surfElevation, offshoreElevation", shorelineElevation, surfElevation, offshoreElevation)
#             surfDistance = haversine.haversine(surfCoordinates, shorelineCoordinates) * 1000
#             offshoreDistance = haversine.haversine(offshoreCoordinates, shorelineCoordinates) * 1000
#             print("surfDistance, offshoreDistance", surfDistance, offshoreDistance)
#             print("distance between offshore and shoreline", distance)
#             Calculate average slope in radians
#              hardcode the average slope
#             distance = 50
#             offshoreElevation = 5


#             surfDistance = haversine.haversine(surfCoordinates, shorelineCoordinates) * 1000
#             offshoreDistance = haversine.haversine(offshoreCoordinates, shorelineCoordinates) * 1000
#             averageSlope = math.atan((shorelineElevation - surfElevation) / surfDistance)
            averageSlope = 0
            surfDistance = 0
            offshoreDistance = 0
#             print("shore to surf average slope", averageSlope)
#             averageSlope = 0.025
#             averageSlope = 

#             Convert mean wave period to deepwater wavelength
#             print("offshoreWavelength", offshoreWavelength)
            
#             Iribarren number
#             swh200 = offshoreSwh[200]
#             wavelength200 = offshoreWavelength[200]
#             iribarren200 = averageSlope / (np.sqrt(swh200 / wavelength200))
#             print("swh200", swh200, "wavelength200", wavelength200)
#             print("IRIBARREN NUMBER AT INDEX 200:", iribarren200)
#             First, calculate offshore node index from given runup station location (Can be hardcoded to a specific v18 node index)
#               A way to find the shoreline and offshore point elevation, water level, and wave parameters,
#               Observational stations can be set for the shoreline and offshore point. Then the values will be interpolated onto the points as
#               a timeseries
#               Next, generate cross shore transect from station to offshore
#               Next, extract depth profile along transect from mesh data file
#               Next, extract wave data for offshore point
#               Finally, loop through each time and calculate the runup using the extracted values and a selected formula


#           Revised 1/29/25
#             Key steps to calculating the wave runup
#              Find the deep water wavelength. This is a dispeersion problem that should be calculated with account to the water depth.
#                     -I tink done
#             Find the significant wave height, shoaled to the appropriate offshore distance
#                 Vosdoukas uses SWH and wavelength at 93 meter depth
#                     Stockdon "reverse shoaled the data to deep water using linear wave theory". They assimilated data from a bunch of places
#                         Holman used wave data 3km away at 20 m depth
#              Calculate the iribarren number, validate its validity
#             Figure out how to convert the mean wave direction into meaningful values
#                 Created additional points at NJ and Katama Airfield. Running to see what the min max values of MWD are

#              -Also running on local for the purpose of working out the calculations for SWH and Deepwater wavelength

#             1/30/25 Midnight update.. well folks, thats all! Tried a whole numch of things, iribarren calculation is off. I dont know if its a problem with the average slope or the wavelength calculaton, or the iribarren
#               formula itself. Poop. Should I just quit?

#              1/30/25 11PM, tried tweaking. Added graphing for wavelength and iribarren, as well as debugs showing calculation of iribarren.
#                 No luck, iribarren is stll way too low. Do I have to use peak wave period?

#             1/31/25 I fixed it. Was multiplying instead of dividing in the iribarren formula. 
#                 The iribarren number calculations look correct, I can now calculate runup?
#                     Adding graphing for shoreline, surf, and offshore points to visualize where they are in space and their elevation

#           2/1/25 program in the runup formulas and compare in graphs

#           2/3/25 Define offshore points with normal vector starting from shoreline.
#           Graph swh as a function of distance from shoreline
#           Graph mwp vp pwp to compare
#           Create script to convert GFS oceanweather wind to 306 type wind for ManRuns

#           2/5 The convert script isint working. Debug by converting oceanweather to 306, then to nc, then graphing until it is right.
#           Ask mr. g to write it starting at max lat and min lon, row by row. And ask him to make a Wind_Inp file so its easy to convert to NetCDF

#           Finished OceanwatherTo306 script. Got runs. Now need to calculate runup.
#            First step is to get a series of points x distance from the 0 water level point on the shpreline.
#             The first question, how to find the 0 water level point for a given time?
#           One idea is to interpolate to where there is 0 water. 
#               Another idea is to pick where the water level is at a minimum.
#             
#             What has to be given is a general location of the shoreline. 
#             What can be given is a set of two points. A general coastline point and a general surfzone point.
#             The goal is, from the genral location of the shoreline point, can a precise location of the 0 water level point be generated?
#              Given the shoreline point, a search can ensue around a set radius. A subset of the water data is taken in the search area
#              The water level of the search area is scanned to try and produce a waterline line segment.



#              Scratch the above.
#                 Define a line along the beach connecting the shoreline point to the surfzone point.
#                  To find the location of runup prediction, traverse the line. Find for which position of the line the water level reaches 0.

#           I created a script to generate normal line obs stations. Detirmining the prediction location for runup for a given timestep
#              i.e finding the location of 0 water level for a given timestep
#           Is another challenge
#           The adcirc mesh might have even better resolution or atlesat on par with the normal line
#           
#           GetBuoyWater stopped working. NAVD datum isint working. Thinking I have to switch to MSL datum, then add in MSL offset to convert to navd after pulling the obs data

#           Thought of a way to get runup prediction location
#              Discretize and generate stations close to shoreline point at a fine resolution
#           For each time, Iterate through the stations, starting at the offshore side. 
#             Check the water level for each station, if the water level is equal to 0, break. The found point
#               Is the location of runup prediction.
#                This method heavily depends on the coarseness of the station locations in order to get an accurate runup prediction point.
#               Save the runup prediction points for each timestep to an array.
#               The next step is to use the runup prediction point as the shoreline point for any given timestep. This means that the beach slope and distance have
#               to be calculated from the runup prediction point, not the shoreline point.
#             It will probbably be easier to create the predictionLocations array first,
#               Then work on creating runup predictions using the predicitonLocation and surfline to generate iribarren number.

#           Water levels look wack. Don't match up with observation at all. Rerunning with fixed sea level offset.

#           I dont know whats wrong with water obs getBuoyWater program. 
#           The problem of telling what location the runup prediction is valid for is a seperate issue.
#           This problem is already solved by looking at the wet and dry nodes for a given timestamp
#             The prediction for how much runup is independent of the location? No its not. But its probbably defined as static.
#              I mean, what is being calculated is the average slope. So technically is the waterline moves inshore, then the average slope would
#               increase.

#           Basically, i thought of it.
#            A map of the beach, showing the waterline changing with each timestamp.
#              Then also a line parallel to the waterline. Showing the 2% exceddence of runup.

#           To accomplish this, the tangent of the waterline has to be calculated at each timestep.
#           Then, the tangent is translated in space by a distance of tue 2% exceedence of runup.
#           This runup tangent line is then visualized in the maps for each timestep.
#           Along with this, a timeseries of the runup value will also be produced.
#             Similar to other products. Map + timeseries

#              Whats the first problem? How can I calculate the tangent line? the current method is creating a set of interpolated stations
#               that is normal to the waterline. 
#               
#              The idea, probbably repeating myself, is to create a hyerresolution set of interpolated stations, all along the beach.
#             Then iterate through these hyperstations, and find the first one (starting from oceanside) that has a waterlevel of nan or 0.
#              This hyperstation is the waterline point.

#              Another stations can be defined alongside the waterline station.
#                 This station can be called the tangent station, and geometrically defines a waterline on the beach.
#               The tangent stations will be hyperresolutionized along with the normal stations, forming a pair of points
#               At each hyerresolution grid step.
    
#               Given the hyperresolution point, the corresponding hyperresolutions tangent point can be used to construct a waterline tangent.
#                  Implement this ASAP. this is what I will present for seminar.


#           Now, how to construct tangent line?
#            It would be easy to construct a tangent line by reading the water map directly. 
#              The hyperstation will have a closestNode attribute, signifying what node is the closest to it.

            predictionLocations = []

            runupDict[key] = {}
            runupDict[key]["surfDistance"] = surfDistance
            runupDict[key]["offshoreDistance"] = offshoreDistance
            runupDict[key]["waterlineKeys"] = waterlineKeys
            runupDict[key]["averageSlope"] = averageSlope
            runupDict[key]["averageSlopes"] = averageSlopes
            runupDict[key]["times"] = runupTimes
            runupDict[key]["runupWaterlineLatitudes"] = runupWaterlineLatitudes
            runupDict[key]["runupWaterlineLongitudes"] = runupWaterlineLongitudes
            runupDict[key]["runupTangentLatitudes"] = runupTangentLatitudes
            runupDict[key]["runupTangentLongitudes"] = runupTangentLongitudes
            runupDict[key]["runup"] = runupValues
            runupDict[key]["runupHolmanHigh"] = runupValuesHolmanHigh
            runupDict[key]["runupHolmanMid"] = runupValuesHolmanMid
            runupDict[key]["runupHolmanLow"] = runupValuesHolmanLow
            runupDict[key]["setupHolmanHigh"] = setupValuesHolmanHigh
            runupDict[key]["setupHolmanMid"] = setupValuesHolmanMid
            runupDict[key]["setupHolmanLow"] = setupValuesHolmanLow
            runupDict[key]["swashHolmanHigh"] = swashValuesHolmanHigh
            runupDict[key]["swashHolmanMid"] = swashValuesHolmanMid
            runupDict[key]["swashHolmanLow"] = swashValuesHolmanLow
            runupDict[key]["swashHolmanIncident"] = swashValuesHolmanIncident
            runupDict[key]["swashHolmanInfragravity"] = swashValuesHolmanInfragravity
            
            runupDict[key]["setupStockdon"] = setupValuesStockdon
            runupDict[key]["swashStockdonIncident"] = swashValuesStockdonIncident
            runupDict[key]["swashStockdonInfragravity"] = swashValuesStockdonInfragravity
            runupDict[key]["setupStockdonLow"] = setupValuesStockdonLow
            runupDict[key]["swashStockdonLow"] = swashValuesStockdonLow
            runupDict[key]["runupStockdon"] = runupValuesStockdon
            runupDict[key]["runupStockdonNoSetup"] = runupValuesStockdonNoSetup
            runupDict[key]["runupStockdonLow"] = runupValuesStockdonLow
            runupDict[key]["setupAdcirc"] = setupValuesAdcirc
            runupDict[key]["runupAdcirc"] = runupValuesAdcirc
            

            runupDict[key]["wavelength"] = offshoreWavelength
            runupDict[key]["steepness"] = offshoreSteepness
            runupDict[key]["iribarren"] = iribarrenNumbers
            runupDict[key]["predictionLocations"] = predictionLocations
            runupDict[key]["nodeIndex"] = stationName
            runupDict[key]["latitude"] = shorelineCoordinates[0]
            runupDict[key]["longitude"] = shorelineCoordinates[1]
            
            runupDict[key]["duneHeights"] = duneHeights
            
            runupDict[key]["obsRunup"] = runupValuesObs
            runupDict[key]["obsSwash"] = runupValuesObsSwash
            runupDict[key]["obsIncidentSwash"] = runupValuesObsIncidentSwash
            runupDict[key]["obsInfragravitySwash"] = runupValuesObsInfragravitySwash
            runupDict[key]["obsSwh"] = runupValuesObsSwh
            runupDict[key]["obsPwp"] = runupValuesObsPwp
            runupDict[key]["obsImpact"] = runupValuesObsImpact
            runupDict[key]["obsBeachSlope"] = runupValuesObsBeachSlope

        # print(windDict)
        print("Writing runup data file!")
        with open(RUNUP_DATA_FILE, "w") as outfile:
            json.dump(runupDict, outfile, cls=NumpyEncoder)
