from Reader import Fort14Reader, Fort74Reader, Fort63Reader, GFSWindReader, GFSRainReader, PostWindReader, WaveReader
from Grapher import Grapher
from DiffGrapher import DiffGrapher
from GetBuoyWind import GetBuoyWind
from GetBuoyWater import GetBuoyWater
from GetBuoyWaves import GetBuoyWaves
from GetObsRain import GetObsRain
from GetObsElevation import GetObsElevation
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
NEW_LONDON_MAP = "NewLondon.png"
NEW_LONDON_OUTLINE_MAP = "NewLondonOutline.png"
NEW_LONDON_AXIS = [-72.20299682617187, -71.99700317382812, 41.42727255213162, 41.27263562301683]
NEW_LONDON_NORWICH_MAP = "NewLondonNorwich.png"
NEW_LONDON_NORWICH_AXIS = [-72.30599365234374, -71.89400634765624, 41.34571806834695, 41.245298232693365]
NEW_LONDON_COAST_GUARD_OUTLINE_MAP = "NewLondonCoastGuardOutline.png"
NEW_LONDON_COAST_GUARD_MAP = "NewLondonCoastGuard.png"
NEW_LONDON_COAST_GUARD_AXIS = [-72.13649841308596, -72.03350158691408, 41.383650725307994, 41.306326318981746]
LONG_ISLAND_SOUND_EAST_OUTLINE_MAP = "LongIslandSoundEastOutline.png"
LONG_ISLAND_SOUND_EAST_MAP = "LongIslandSoundEast.png"
LONG_ISLAND_SOUND_EAST_AXIS = [-73.37397460937501, -71.72602539062501, 41.8170316891045, 40.577095781586486]
LONG_ISLAND_MAP = "LongIsland.png"
LONG_ISLAND_OUTLINE_MAP = "LongIslandOutline.png"
LONG_ISLAND_AXIS = [-74.34794921875002, -71.05205078125002, 42.23196681807541, 39.74456845975795]
BLOCK_ISLAND_SOUND_MAP = "BlockIslandSound.png"
BLOCK_ISLAND_SOUND_OUTLINE_MAP = "BlockIslandSoundOutline.png"
BLOCK_ISLAND_SOUND_AXIS = [-72.52397460937502, -70.87602539062502, 42.11417769664206, 40.87994188758605]

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
        "--mesh", help="Fort.14 mesh file", type=str
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
        "--meshExists", type=bool, help="Graph adcirc fort.14 mesh"
    )
    p.add_argument(
        "--backgroundChoice", type=str, help="Options: RHODE_ISLAND, NORTH_ATLANTIC, AMERICA, MIDWEST"
    )
    p.add_argument(
        "--tempDir", type=str, help="Temp json data file directory"
    )
    args = p.parse_args()
    args.epsg = 4326
    print("Generating Wind Graphs!", flush=True)
    wind_temp_directory = args.tempDir
    graphs_directory = "graphs/"
    water_temp_directory = args.tempDir
    wave_temp_directory = args.tempDir
    
#      Create temp and graphs directories
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
    if not os.path.exists(wind_temp_directory):
        os.makedirs(wind_temp_directory)
    if not os.path.exists(water_temp_directory):
        os.makedirs(water_temp_directory)
    
    dataToGraph = {}  
    print("Loading NetCDF file!", flush=True)
    STATIONS_FILE = args.stations
#     Default to Rhode Island Map
    if(not args.backgroundChoice):
        backgroundChoice = "RHODE_ISLAND"
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
    elif(backgroundChoice == "NEW_LONDON"):
        backgroundMap = NEW_LONDON_MAP
        backgroundAxis = NEW_LONDON_AXIS
    elif(backgroundChoice == "NEW_LONDON_OUTLINE"):
        backgroundMap = NEW_LONDON_OUTLINE_MAP
        backgroundAxis = NEW_LONDON_AXIS
    elif(backgroundChoice == "LONG_ISLAND_SOUND_EAST_OUTLINE"):
        backgroundMap = LONG_ISLAND_SOUND_EAST_OUTLINE_MAP     
        backgroundAxis = LONG_ISLAND_SOUND_EAST_AXIS
    elif(backgroundChoice == "LONG_ISLAND_SOUND_EAST"):
        backgroundMap = LONG_ISLAND_SOUND_EAST_MAP     
        backgroundAxis = LONG_ISLAND_SOUND_EAST_AXIS  
    elif(backgroundChoice == "LONG_ISLAND"):
        backgroundMap = LONG_ISLAND_MAP     
        backgroundAxis = LONG_ISLAND_AXIS  
    elif(backgroundChoice == "LONG_ISLAND_OUTLINE"):
        backgroundMap = LONG_ISLAND_OUTLINE_MAP     
        backgroundAxis = LONG_ISLAND_AXIS 
    elif(backgroundChoice == "BLOCK_ISLAND_SOUND"):
        backgroundMap = BLOCK_ISLAND_SOUND_MAP     
        backgroundAxis = BLOCK_ISLAND_SOUND_AXIS  
    elif(backgroundChoice == "BLOCK_ISLAND_SOUND_OUTLINE"):
        backgroundMap = BLOCK_ISLAND_SOUND_OUTLINE_MAP     
        backgroundAxis = BLOCK_ISLAND_SOUND_AXIS 
        
    print("args.adcircExists", args.adcircExists, flush=True)
    if(args.adcircExists):
        ADCIRC_WIND_FILE = args.wind
        ADCIRC_WIND_DATA_FILE = wind_temp_directory + "adcirc_wind_data_file" + ".json"
        (windStartDateObject, windEndDateObject) = Fort74Reader(ADCIRC_WIND_FILE=ADCIRC_WIND_FILE, STATIONS_FILE=STATIONS_FILE, ADCIRC_WIND_DATA_FILE=ADCIRC_WIND_DATA_FILE, BACKGROUND_AXIS=backgroundAxis).generateWindDataForStations()
        dataToGraph["FORT"] = ADCIRC_WIND_DATA_FILE
    print("args.gfsExists", args.gfsExists, flush=True)
    if(args.gfsExists):
        GFS_WIND_FILE = args.wind
        GFS_WIND_DATA_FILE = wind_temp_directory + "gfs_wind_data_file" + ".json"
        (windStartDateObject, windEndDateObject) = GFSWindReader(GFS_WIND_FILE=GFS_WIND_FILE, STATIONS_FILE=STATIONS_FILE, GFS_WIND_DATA_FILE=GFS_WIND_DATA_FILE, BACKGROUND_AXIS=backgroundAxis).generateWindDataForStations()
        dataToGraph["GFS"] = GFS_WIND_DATA_FILE
    print("args.rainExists", args.rainExists, flush=True)
    if(args.rainExists):
        GFS_RAIN_FILE = args.rain
        GFS_RAIN_DATA_FILE = wind_temp_directory + "gfs_rain_data_file" + ".json"
        (rainStartDateObject, rainEndDateObject) = GFSRainReader(GFS_RAIN_FILE=GFS_RAIN_FILE, STATIONS_FILE=STATIONS_FILE, GFS_RAIN_DATA_FILE=GFS_RAIN_DATA_FILE, BACKGROUND_AXIS=backgroundAxis).generateRainDataForStations()
#         rainStartDateObject = datetime.datetime(year=2024, month=7, day=25)
#         rainEndDateObject = datetime.datetime(year=2024, month=10, day=2)
        dataToGraph["RAIN"] = GFS_RAIN_DATA_FILE
    print("args.postExists", args.postExists, flush=True)
    if(args.postExists):
        POST_WIND_FILE = args.wind
        POST_WIND_DATA_FILE = wind_temp_directory + "post_wind_data_file" + ".json"
        (windStartDateObject, windEndDateObject) = PostWindReader(POST_WIND_FILE=POST_WIND_FILE, STATIONS_FILE=STATIONS_FILE, POST_WIND_DATA_FILE=POST_WIND_DATA_FILE, BACKGROUND_AXIS=backgroundAxis).generateWindDataForStations()
        dataToGraph["POST"] = POST_WIND_DATA_FILE

    
    print("args.waterExists", args.waterExists, flush=True)
    if(args.waterExists):
        ADCIRC_WATER_FILE = args.water
#         ADCIRC_WATER_DATA_FILE = water_temp_directory + "sandy_deb_adcirc_water_data_file" + ".json"
#         ADCIRC_DIFF_WATER_DATA_FILE = water_temp_directory + "sandy_deb_adcirc_water_data_file" + ".json"

        ADCIRC_WATER_DATA_FILE = water_temp_directory + "adcirc_water_data_file" + ".json"

        (waterStartDateObject, waterEndDateObject) = Fort63Reader(ADCIRC_WATER_FILE=ADCIRC_WATER_FILE, STATIONS_FILE=STATIONS_FILE, ADCIRC_WATER_DATA_FILE=ADCIRC_WATER_DATA_FILE, BACKGROUND_AXIS=backgroundAxis).generateWindDataForStations()
#         waterStartDateObject = datetime.datetime(year=2018, month=2, day=28, hour=5)
#         waterEndDateObject = datetime.datetime(year=2018, month=3, day=4, hour=5)
        dataToGraph["WATER"] = ADCIRC_WATER_DATA_FILE
#         dataToGraph["DIFF"] = ADCIRC_DIFF_WATER_DATA_FILE
       
    print("args.meshExists", args.meshExists, flush=True)
    if(args.meshExists):
        ADCIRC_MESH_FILE = args.mesh
#         ADCIRC_WATER_DATA_FILE = water_temp_directory + "sandy_deb_adcirc_water_data_file" + ".json"
#         ADCIRC_DIFF_WATER_DATA_FILE = water_temp_directory + "sandy_deb_adcirc_water_data_file" + ".json"

        ADCIRC_MESH_DATA_FILE = water_temp_directory + "adcirc_elevation_data_file" + ".json"

#         Fort14Reader(ADCIRC_MESH_FILE=ADCIRC_MESH_FILE, STATIONS_FILE=STATIONS_FILE, ADCIRC_MESH_DATA_FILE=ADCIRC_MESH_DATA_FILE, BACKGROUND_AXIS=backgroundAxis).generateMeshDataForStations()
#         waterStartDateObject = datetime.datetime(year=2018, month=2, day=28, hour=5)
#         waterEndDateObject = datetime.datetime(year=2018, month=3, day=4, hour=5)
        dataToGraph["MESH"] = ADCIRC_MESH_DATA_FILE
#         dataToGraph["DIFF"] = ADCIRC_DIFF_WATER_DATA_FILE 
        
    print("args.wavesExists", args.wavesExists, flush=True)
    if(args.wavesExists):
        print("Generating Wave Graphs!", flush=True)
#         wave_temp_directory = "/project/pi_iginis_uri_edu/pranav_sai_uri_edu/post_output/wave_temp/"
    
    #     Create temp and graphs directories
        if not os.path.exists(wave_temp_directory):
            os.makedirs(wave_temp_directory)
        
        print("Loading NetCDF file!", flush=True)
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
        (waveStartDateObject, waveEndDateObject) = WaveReader(
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
            WAVE_RAD_DATA_FILE=WAVE_RAD_DATA_FILE,
            BACKGROUND_AXIS=backgroundAxis).generateWaveDataForStations()
        
#         waveStartDateObject = datetime.datetime(year=2024, month=8, day=28, hour=5, tzinfo=datetime.timezone.utc)
#         waveEndDateObject = datetime.datetime(year=2024, month=12, day=4, hour=5, tzinfo=datetime.timezone.utc)
        dataToGraph["SWH"] = WAVE_SWH_DATA_FILE
        dataToGraph["MWD"] = WAVE_MWD_DATA_FILE
        dataToGraph["MWP"] = WAVE_MWP_DATA_FILE
        dataToGraph["PWP"] = WAVE_PWP_DATA_FILE
        dataToGraph["RAD"] = WAVE_RAD_DATA_FILE
        
    print("args.obsExists", args.obsExists, flush=True)
    if(args.obsExists):
        if(args.gfsExists or args.adcircExists or args.postExists):
            print("Parsed start and end date from netCDF, ", windStartDateObject, windEndDateObject, flush=True)
            OBS_WIND_DATA_FILE = wind_temp_directory + "obs_wind_data_file" + ".json"
            GetBuoyWind(STATIONS_FILE=STATIONS_FILE, OBS_WIND_DATA_FILE=OBS_WIND_DATA_FILE, startDateObject=windStartDateObject, endDateObject=windEndDateObject)
            dataToGraph["OBS"] = OBS_WIND_DATA_FILE
        
        if(args.rainExists):
            print("Parsed start and end date from netCDF, ", rainStartDateObject, rainEndDateObject, flush=True)
            OBS_RAIN_DATA_FILE = wind_temp_directory + "obs_rain_data_file" + ".json"
            GetObsRain(STATIONS_FILE=STATIONS_FILE, OBS_RAIN_DATA_FILE=OBS_RAIN_DATA_FILE, startDateObject=rainStartDateObject, endDateObject=rainEndDateObject)
            dataToGraph["GAUGE"] = OBS_RAIN_DATA_FILE
            
        if(args.waterExists):
            print("Parsed start and end date from netCDF, ", waterStartDateObject, waterEndDateObject, flush=True)
            OBS_WATER_DATA_FILE = wind_temp_directory + "obs_water_data_file" + ".json"
            GetBuoyWater(STATIONS_FILE=STATIONS_FILE, OBS_WATER_DATA_FILE=OBS_WATER_DATA_FILE, startDateObject=waterStartDateObject, endDateObject=waterEndDateObject)
            dataToGraph["TIDE"] = OBS_WATER_DATA_FILE
        if(args.meshExists):
            print("Calling get observational elevation data", flush=True)
            OBS_ASSET_DATA_FILE = wind_temp_directory + "obs_elevation_data_file" + ".json"
            GetObsElevation(STATIONS_FILE=STATIONS_FILE, OBS_ASSET_DATA_FILE=OBS_ASSET_DATA_FILE)
            dataToGraph["ASSET"] = OBS_ASSET_DATA_FILE
        if(args.wavesExists):
            print("Parsed start and end date from netCDF, ", waveStartDateObject, waveEndDateObject, flush=True)
            OBS_WAVE_DATA_FILE = wind_temp_directory + "obs_wave_data_file" + ".json"
            GetBuoyWaves(STATIONS_FILE=STATIONS_FILE, OBS_WAVE_DATA_FILE=OBS_WAVE_DATA_FILE, startDateObject=waveStartDateObject, endDateObject=waveEndDateObject)
#             This wave observational file will contain the observational data in correct format for three types of observational data,
#           significant wave height, mean wave direction, and mean wave period
            dataToGraph["BUOY"] = OBS_WAVE_DATA_FILE
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
