from Reader import Fort74Reader, GFSWindReader, GFSRainReader, PostWindReader, WaveReader
from Grapher import Grapher
from GetBuoyWind import GetBuoyWind
import datetime
import argparse
import os

def main():
    p = argparse.ArgumentParser(description="Make a request to generate graphs")
    p.add_argument(
            "--stations", help="Stations json file", type=str
    )
    p.add_argument(
        "--wind", help="Wind netcdf file", type=str
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
        "--wavesExists", type=bool, help="Graph adcirc wave data"
    )
    p.add_argument(
        "--rainExists", type=bool, help="Graph adcirc wave data"
    )
    args = p.parse_args()
    args.epsg = 4326
    print("Generating Wind Graphs!")
    wind_temp_directory = "wind_temp/"
    graphs_directory = "graphs/"
    
#      Create temp and graphs directories
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
    if not os.path.exists(wind_temp_directory):
        os.makedirs(wind_temp_directory)

    
    dataToGraph = {}  
    print("Loading NetCDF file!")
    STATIONS_FILE = args.stations

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
#         (startDateObject, endDateObject) = WaveReader(
#             WAVE_SWH_FILE=WAVE_SWH_FILE,
#             WAVE_MWD_FILE=WAVE_MWD_FILE,
#             WAVE_MWP_FILE=WAVE_MWP_FILE,
#             WAVE_PWP_FILE=WAVE_PWP_FILE,
#             WAVE_RAD_FILE=WAVE_RAD_FILE,
#             STATIONS_FILE=STATIONS_FILE, 
#             WAVE_SWH_DATA_FILE=WAVE_SWH_DATA_FILE,
#             WAVE_MWD_DATA_FILE=WAVE_MWD_DATA_FILE,
#             WAVE_MWP_DATA_FILE=WAVE_MWP_DATA_FILE,
#             WAVE_PWP_DATA_FILE=WAVE_PWP_DATA_FILE,
#             WAVE_RAD_DATA_FILE=WAVE_RAD_DATA_FILE).generateWaveDataForStations()
        
        dataToGraph["SWH"] = WAVE_SWH_DATA_FILE
#         dataToGraph["MWD"] = WAVE_MWD_DATA_FILE
#         dataToGraph["MWP"] = WAVE_MWP_DATA_FILE
#         dataToGraph["PWP"] = WAVE_PWP_DATA_FILE
#         dataToGraph["RAD"] = WAVE_RAD_DATA_FILE
# 
#     print("Parsed start and end date from netCDF, ", startDateObject, endDateObject)
    Grapher(dataToGraph=dataToGraph, STATIONS_FILE=STATIONS_FILE).generateGraphs()

if __name__ == "__main__":
    main()
