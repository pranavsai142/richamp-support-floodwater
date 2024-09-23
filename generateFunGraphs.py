from FunReader import EtaReader
from Grapher import Grapher
from GetBuoyWater import GetBuoyWater
from GetBuoyWaves import GetBuoyWaves
from FunInputReader import FunInputReader
import datetime
import argparse
import os

SOUTH_NEW_ENGLAND_MAP = "subsetFlipped.png"
SOUTH_NEW_ENGLAND_AXIS = [-71.905117442267496, -71.0339945492675, 42.200717972845119, 41.028319358056874]
NORTH_ATLANTIC_MAP = "NorthAtlanticBasin3.png"
NORTH_ATLANTIC_AXIS = [-76.59179620444773, -63.41595750651321, 46.70943547053439, 36.92061410517965]
ATLANTIC_MAP = "AtlanticBasin.png"
ATLANTIC_AXIS = [-89.47265625, -45.52734375, 49.402995871752374, 23.351173294924422]
# AMERICA_MAP = "America.png"
# AMERICA_AXIS = [-152.73436963558197, -47.327660052105784, 68.95333199817976, -8.92452857958399]
MIDWEST_MAP = "Midwest.png"
MIDWEST_AXIS = [-91.59179620444776, -78.41595750651324, 47.17062597464635, 37.45872529389382]
RHODE_ISLAND_MAP = "RhodeIsland.png"
RHODE_ISLAND_AXIS = [-71.82698726277798, -71.00349734415707, 41.90734758914777, 41.29154575705807]
SOUTH_RHODE_ISLAND_MAP = "SouthRhodeIsland.png"
SOUTH_RHODE_ISLAND_AXIS = [-71.82698726277798, -71.00349734415707, 41.75806308487547, 41.140832039790766]
NEWPORT_MAP = "Newport.png"
NEWPORT_AXIS = [-71.55599363138899, -71.14424867207853, 41.65409629818921, 41.34571806834695]
PROVIDENCE_MAP = "Providence.png"
PROVIDENCE_AXIS = [-71.54599363138901, -71.1342486720785, 41.853618749387486, 41.54619474986597]
NORTH_PROVIDENCE_MAP = "NorthProvidence.png"
NORTH_PROVIDENCE_AXIS = [-71.745993631389, -71.33424867207854, 41.70156547197295, 42.00824736593589]
WESTERLY_MAP = "Westerly.png"
WESTERLY_AXIS = [-71.89599363138898, -71.48424867207852, 41.45457197608142, 41.14524327341847]
NARRAGANSETT_MAP = "Narragansett.png"
NARRAGANSETT_AXIS = [-71.54599363138901, -71.13424867207856, 41.45457197608142, 41.14524327341847]
BLOCK_ISLAND_MAP = "BlockIsland.png"
BLOCK_ISLAND_AXIS = [-71.64599363138898, -71.23424867207852, 41.45457197608142, 41.14524327341847]
RHODE_ISLAND_CHAMP_MAP = "RhodeIslandChamp.png"
RHODE_ISLAND_CHAMP_AXIS = [-71.9050164752, -71.1307245329, 42.000010143316864, 41.1192500979]
EAST_COAST_MAP = "EastCoast.png"
EAST_COAST_OUTLINE_MAP = "EastCoastOutline.png"
EAST_COAST_AXIS = [-83.18359374999999, -56.816406249999986, 45.49399717614716, 24.090563202580892]
HAWAII_MAP = "Hawaii.png"
HAWAII_AXIS = [-160.7958984375, -154.2041015625, 23.06539242194311, 16.873745326186384]


def main():
    p = argparse.ArgumentParser(description="Make a request to generate graphs")
    p.add_argument(
            "--stations", help="Stations json file", type=str
    )
    p.add_argument(
        "--input", help="input.txt file", type=str
    )
    p.add_argument(
        "--output", help="Output folder", type=str
    )
    #TODO: Fix rhia
    p.add_argument(
        "--etaExists", type=bool, help="Graph surface elevation eta data"
    )
    p.add_argument(
        "--obsExists", type=bool, help="Graph observational wind data"
    )
    p.add_argument(
        "--backgroundChoice", type=str, help="Options: RHODE_ISLAND, NORTH_ATLANTIC, AMERICA, MIDWEST"
    )
    p.add_argument(
        "--tempDir", type=str, help="Temp json data file directory"
    )
    args = p.parse_args()
    args.epsg = 4326
    print("Generating FUN!!!!!! Graphs!", flush=True)
    fun_temp_directory = args.tempDir
    graphs_directory = "fungraphs/"
    
#      Create temp and graphs directories
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
    if not os.path.exists(fun_temp_directory):
        os.makedirs(fun_temp_directory)
    
    dataToGraph = {}  
    print("Processing fun files!", flush=True)
    STATIONS_FILE = args.stations
#     Default to Rhode Island Map
    if(not args.backgroundChoice):
        backgroundChoice = "RHODE_ISLAND_CHAMP"
    else:
        backgroundChoice = args.backgroundChoice
        
    backgroundMap = None
    backgroundAxis = None
    if(backgroundChoice == "RHODE_ISLAND"):
        backgroundMap = RHODE_ISLAND_MAP
        backgroundAxis = RHODE_ISLAND_AXIS
    elif(backgroundChoice == "NORTH_ATLANTIC"):
        backgroundMap = NORTH_ATLANTIC_MAP
        backgroundAxis = NORTH_ATLANTIC_AXIS
    elif(backgroundChoice == "ATLANTIC"):
        backgroundMap = ATLANTIC_MAP
        backgroundAxis = ATLANTIC_AXIS
#     elif(backgroundChoice == "AMERICA"):
#         backgroundMap = AMERICA_MAP
#         backgroundAxis = AMERICA_AXIS
    elif(backgroundChoice == "MIDWEST"):
        backgroundMap = MIDWEST_MAP
        backgroundAxis = MIDWEST_AXIS
    elif(backgroundChoice == "RHODE_ISLAND"):
        backgroundMap = RHODE_ISLAND_MAP
        backgroundAxis = RHODE_ISLAND_AXIS
    elif(backgroundChoice == "SOUTH_RHODE_ISLAND"):
        backgroundMap = SOUTH_RHODE_ISLAND_MAP
        backgroundAxis = SOUTH_RHODE_ISLAND_AXIS
    elif(backgroundChoice == "PROVIDENCE"):
        backgroundMap = PROVIDENCE_MAP
        backgroundAxis = PROVIDENCE_AXIS
    elif(backgroundChoice == "NORTH_PROVIDENCE"):
        backgroundMap = NORTH_PROVIDENCE_MAP
        backgroundAxis = NORTH_PROVIDENCE_AXIS
    elif(backgroundChoice == "WESTERLY"):
        backgroundMap = WESTERLY_MAP
        backgroundAxis = WESTERLY_AXIS
    elif(backgroundChoice == "NEWPORT"):
        backgroundMap = NEWPORT_MAP
        backgroundAxis = NEWPORT_AXIS
    elif(backgroundChoice == "NARRAGANSETT"):
        backgroundMap = NARRAGANSETT_MAP
        backgroundAxis = NARRAGANSETT_AXIS
    elif(backgroundChoice == "BLOCK_ISLAND"):
        backgroundMap = BLOCK_ISLAND_MAP
        backgroundAxis = BLOCK_ISLAND_AXIS
    elif(backgroundChoice == "RHODE_ISLAND_CHAMP"):
        backgroundMap = RHODE_ISLAND_CHAMP_MAP
        backgroundAxis = RHODE_ISLAND_CHAMP_AXIS
    elif(backgroundChoice == "EAST_COAST"):
        backgroundMap = EAST_COAST_MAP
        backgroundAxis = EAST_COAST_AXIS
    elif(backgroundChoice == "EAST_COAST_OUTLINE"):
        backgroundMap = EAST_COAST_OUTLINE_MAP
        backgroundAxis = EAST_COAST_AXIS
    elif(backgroundChoice == "HAWAII"):
        backgroundMap = HAWAII_MAP
        backgroundAxis = HAWAII_AXIS
        
    startDateObject, timeDelta = FunInputReader(INPUT_FILE=args.input).getTimes()
    print("args.etaExists", args.etaExists, flush=True)
    if(args.etaExists):
        OUTPUT_FOLDER = args.output
        ETA_DATA_FILE = fun_temp_directory + "eta_data_file" + ".json"
        (etaStartDateObject, etaEndDateObject) = EtaReader(OUTPUT_FOLDER=OUTPUT_FOLDER, STATIONS_FILE=STATIONS_FILE, ETA_DATA_FILE=ETA_DATA_FILE, BACKGROUND_AXIS=backgroundAxis, startDateObject=startDateObject, timeDelta=timeDelta).generateFunDataForStations()
        dataToGraph["ETA"] = ETA_DATA_FILE
        
    print("args.obsExists", args.obsExists, flush=True)
#     if(args.obsExists):
            
#         if(args.etaExists):
#             print("Parsed start and end date from netCDF, ", waterStartDateObject, waterEndDateObject, flush=True)
#             OBS_WATER_DATA_FILE = wind_temp_directory + "obs_water_data_file" + ".json"
#             GetBuoyWater(STATIONS_FILE=STATIONS_FILE, OBS_WATER_DATA_FILE=OBS_WATER_DATA_FILE, startDateObject=waterStartDateObject, endDateObject=waterEndDateObject)
#             dataToGraph["TIDE"] = OBS_WATER_DATA_FILE
#         if(args.wavesExists):
#             print("Parsed start and end date from netCDF, ", waveStartDateObject, waveEndDateObject, flush=True)
#             OBS_WAVE_DATA_FILE = wind_temp_directory + "obs_wave_data_file" + ".json"
#             GetBuoyWaves(STATIONS_FILE=STATIONS_FILE, OBS_WAVE_DATA_FILE=OBS_WAVE_DATA_FILE, startDateObject=waveStartDateObject, endDateObject=waveEndDateObject)
# #             This wave observational file will contain the observational data in correct format for three types of observational data,
# #           significant wave height, mean wave direction, and mean wave period
#             dataToGraph["BUOY"] = OBS_WAVE_DATA_FILE
#             
#     Grapher(graphObs=args.obs, graphRain=False, WIND_TYPE="POST", OBS_WIND_DATA_FILE=OBS_WIND_DATA_FILE, STATIONS_FILE=STATIONS_FILE, WIND_DATA_FILE=POST_WIND_DATA_FILE, RAIN_DATA_FILE=GFS_RAIN_DATA_FILE).generateGraphs()
        
#     print("Parsed start and end date from netCDF, ", startDateObject, endDateObject)
    Grapher(
        dataToGraph=dataToGraph, 
        STATIONS_FILE=STATIONS_FILE, 
        backgroundMap=backgroundMap,
        backgroundAxis=backgroundAxis).generateGraphs()

if __name__ == "__main__":
    main()
