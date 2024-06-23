from Reader import Fort74Reader, Fort63Reader, GFSWindReader, GFSRainReader, PostWindReader, WaveReader
from Grapher import Grapher
from GetBuoyWind import GetBuoyWind
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

def main():
    p = argparse.ArgumentParser(description="Make a request to generate graphs")
    p.add_argument(
            "--stations", help="Stations json file", type=str
    )
    p.add_argument(
        "--wind", help="Wind netcdf file", type=str
    )
    p.add_argument(
        "--water", help="Water elevation netcdf file", type=str
    )
    p.add_argument(
        "--rain", help="Rain netcdf file", type=str
    )
    p.add_argument(
        "--waveswh", type=str, help="Wave significant wave height netcdf file"
    )
    p.add_argument(
        "--wavemwd", help="Wave mean wave direction netcdf file", type=str
    )
    p.add_argument(
        "--wavemwp", help="Wave mean wave period netcdf file", type=str
    )
    p.add_argument(
        "--wavepwp", help="Wave peak wave period netcdf file", type=str
    )
    p.add_argument(
        "--waverad", help="Radiation stress gradient netcdf file", type=str
    )
    #TODO: Fix rhia
    p.add_argument(
        "--adcircExists", type=bool, help="Graph adcirc wind data"
    )
    p.add_argument(
        "--gfsExists", type=bool, help="Graph gfs wind data"
    )
    p.add_argument(
        "--postExists", type=bool, help="Graph post wind data"
    )
    p.add_argument(
        "--obsExists", type=bool, help="Graph observational wind data"
    )
    p.add_argument(
        "--waterExists", type=bool, help="Graph adcirc water elevation data"
    )
    p.add_argument(
        "--wavesExists", type=bool, help="Graph adcirc wave data"
    )
    p.add_argument(
        "--rainExists", type=bool, help="Graph adcirc wave data"
    )
    p.add_argument(
        "--backgroundChoice", type=str, help="Options: RHODE_ISLAND, NORTH_ATLANTIC, AMERICA, MIDWEST")
    args = p.parse_args()
    args.epsg = 4326
    print("Generating Wind Graphs!")
    wind_temp_directory = "wind_temp/"
    graphs_directory = "graphs/"
    water_temp_directory = "water_temp/"
    
#      Create temp and graphs directories
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
    if not os.path.exists(wind_temp_directory):
        os.makedirs(wind_temp_directory)
    if not os.path.exists(water_temp_directory):
        os.makedirs(water_temp_directory)
    
    dataToGraph = {}  
    print("Loading NetCDF file!")
    STATIONS_FILE = args.stations
#     Default to Rhode Island Map
    if(not args.backgroundChoice):
        backgroundChoice = "RHODE_ISLAND"
    else:
        backgroundChoice = args.backgroundChoice
        
    print("args.adcircExists", args.adcircExists)
    if(args.adcircExists):
        ADCIRC_WIND_FILE = args.wind
        ADCIRC_WIND_DATA_FILE = wind_temp_directory + "adcirc_wind_data_file" + ".json"
        (windStartDateObject, windEndDateObject) = Fort74Reader(ADCIRC_WIND_FILE=ADCIRC_WIND_FILE, STATIONS_FILE=STATIONS_FILE, ADCIRC_WIND_DATA_FILE=ADCIRC_WIND_DATA_FILE).generateWindDataForStations()
        dataToGraph["FORT"] = ADCIRC_WIND_DATA_FILE
    print("args.gfsExists", args.gfsExists)
    if(args.gfsExists):
        GFS_WIND_FILE = args.wind
        GFS_WIND_DATA_FILE = wind_temp_directory + "gfs_wind_data_file" + ".json"
        (windStartDateObject, windEndDateObject) = GFSWindReader(GFS_WIND_FILE=GFS_WIND_FILE, STATIONS_FILE=STATIONS_FILE, GFS_WIND_DATA_FILE=GFS_WIND_DATA_FILE).generateWindDataForStations()
        dataToGraph["GFS"] = GFS_WIND_DATA_FILE
    print("args.rainExists", args.rainExists)
    if(args.rainExists):
        GFS_RAIN_FILE = args.rain
        GFS_RAIN_DATA_FILE = wind_temp_directory + "gfs_rain_data_file" + ".json"
        (rainStartDateObject, rainEndDateObject) = GFSRainReader(GFS_RAIN_FILE=GFS_RAIN_FILE, STATIONS_FILE=STATIONS_FILE, GFS_RAIN_DATA_FILE=GFS_RAIN_DATA_FILE).generateRainDataForStations()
        dataToGraph["RAIN"] = GFS_RAIN_DATA_FILE
    print("args.postExists", args.postExists)
    if(args.postExists):
        POST_WIND_FILE = args.wind
        POST_WIND_DATA_FILE = wind_temp_directory + "post_wind_data_file" + ".json"
        (windStartDateObject, windEndDateObject) = PostWindReader(POST_WIND_FILE=POST_WIND_FILE, STATIONS_FILE=STATIONS_FILE, POST_WIND_DATA_FILE=POST_WIND_DATA_FILE).generateWindDataForStations()
        dataToGraph["POST"] = POST_WIND_DATA_FILE

    print("args.obsExists", args.obsExists)
    if(args.obsExists):
        print("Parsed start and end date from netCDF, ", windStartDateObject, windEndDateObject)
        OBS_WIND_DATA_FILE = wind_temp_directory + "obs_wind_data_file" + ".json"
        GetBuoyWind(STATIONS_FILE=STATIONS_FILE, OBS_WIND_DATA_FILE=OBS_WIND_DATA_FILE, startDateObject=windStartDateObject, endDateObject=windEndDateObject)
        dataToGraph["OBS"] = OBS_WIND_DATA_FILE
    
    print("args.waterExists", args.waterExists)
    if(args.waterExists):
        ADCIRC_WATER_FILE = args.water
        ADCIRC_WATER_DATA_FILE = water_temp_directory + "adcirc_water_data_file" + ".json"
        (windStartDateObject, windEndDateObject) = Fort63Reader(ADCIRC_WATER_FILE=ADCIRC_WATER_FILE, STATIONS_FILE=STATIONS_FILE, ADCIRC_WATER_DATA_FILE=ADCIRC_WATER_DATA_FILE).generateWindDataForStations()
        dataToGraph["WATER"] = ADCIRC_WATER_DATA_FILE
#     Grapher(graphObs=args.obs, graphRain=False, WIND_TYPE="POST", OBS_WIND_DATA_FILE=OBS_WIND_DATA_FILE, STATIONS_FILE=STATIONS_FILE, WIND_DATA_FILE=POST_WIND_DATA_FILE, RAIN_DATA_FILE=GFS_RAIN_DATA_FILE).generateGraphs()
    print("args.wavesExists", args.wavesExists)
    if(args.wavesExists):
        print("Generating Wave Graphs!")
        wave_temp_directory = "wave_temp/"
    
    #     Create temp and graphs directories
        if not os.path.exists(wave_temp_directory):
            os.makedirs(wave_temp_directory)
        
        print("Loading NetCDF file!")
        WAVE_SWH_FILE = args.waveswh 
        WAVE_MWD_FILE = args.wavemwd
        WAVE_MWP_FILE = args.wavemwp
        WAVE_PWP_FILE = args.wavepwp
        WAVE_RAD_FILE = args.waverad
        WAVE_SWH_DATA_FILE = wave_temp_directory + "wave_swh_data_file" + ".json"
        WAVE_MWD_DATA_FILE = wave_temp_directory + "wave_mwd_data_file" + ".json"
        WAVE_MWP_DATA_FILE = wave_temp_directory + "wave_mwp_data_file" + ".json"
        WAVE_PWP_DATA_FILE = wave_temp_directory + "wave_pwp_data_file" + ".json"
        WAVE_RAD_DATA_FILE = wave_temp_directory + "wave_rad_data_file" + ".json"
        STATIONS_FILE = args.stations
        (startDateObject, endDateObject) = WaveReader(
            WAVE_SWH_FILE=WAVE_SWH_FILE,
            WAVE_MWD_FILE=WAVE_MWD_FILE,
            WAVE_MWP_FILE=WAVE_MWP_FILE,
            WAVE_PWP_FILE=WAVE_PWP_FILE,
            WAVE_RAD_FILE=WAVE_RAD_FILE,
            STATIONS_FILE=STATIONS_FILE, 
            WAVE_SWH_DATA_FILE=WAVE_SWH_DATA_FILE,
            WAVE_MWD_DATA_FILE=WAVE_MWD_DATA_FILE,
            WAVE_MWP_DATA_FILE=WAVE_MWP_DATA_FILE,
            WAVE_PWP_DATA_FILE=WAVE_PWP_DATA_FILE,
            WAVE_RAD_DATA_FILE=WAVE_RAD_DATA_FILE).generateWaveDataForStations()
        
        dataToGraph["SWH"] = WAVE_SWH_DATA_FILE
        dataToGraph["MWD"] = WAVE_MWD_DATA_FILE
        dataToGraph["MWP"] = WAVE_MWP_DATA_FILE
        dataToGraph["PWP"] = WAVE_PWP_DATA_FILE
        dataToGraph["RAD"] = WAVE_RAD_DATA_FILE
        
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
#     print("Parsed start and end date from netCDF, ", startDateObject, endDateObject)
    Grapher(
        dataToGraph=dataToGraph, 
        STATIONS_FILE=STATIONS_FILE, 
        backgroundMap=backgroundMap,
        backgroundAxis=backgroundAxis).generateGraphs()

if __name__ == "__main__":
    main()
