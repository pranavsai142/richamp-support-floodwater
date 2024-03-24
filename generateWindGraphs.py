from FortReader import FortReader, GFSReader, PostReader, WaveReader
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
        "--obs", type=bool, help="Graph observational data"
    )
    args = p.parse_args()
    args.epsg = 4326
#     print("Generating Wind Graphs!")
#     temp_directory = "wind_temp/"
    graphs_directory = "graphs/"
    
#     Create temp and graphs directories
#     if not os.path.exists(temp_directory):
#         os.makedirs(temp_directory)
#     if not os.path.exists(graphs_directory):
#         os.makedirs(graphs_directory)
        
#     print("Loading NetCDF file!")
#     POST_WIND_FILE = args.wind
#     GFS_RAIN_FILE = args.rain
#     POST_WIND_DATA_FILE = temp_directory + "post_wind_data_file" + ".json"
#     GFS_RAIN_DATA_FILE = temp_directory + "gfs_rain_data_file" + ".json"
#     STATIONS_FILE = args.stations
#     OBS_WIND_DATA_FILE = temp_directory + "obs_wind_data_file" + ".json"
#     (startDateObject, endDateObject) = FortReader(ADCIRC_WIND_FORT_74, STATIONS_FILE_NAME, ADCIRC_WIND_DATA_FILE_NAME).generateWindDataForStations()
#     (startDateObject, endDateObject) = GFSReader(GFS_WIND_FILE=GFS_WIND_FILE, GFS_RAIN_FILE=GFS_RAIN_FILE, STATIONS_FILE=STATIONS_FILE, GFS_WIND_DATA_FILE=GFS_WIND_DATA_FILE, GFS_RAIN_DATA_FILE=GFS_RAIN_DATA_FILE).generateWindDataForStations()
#     (startDateObject, endDateObject) = PostReader(POST_WIND_FILE=POST_WIND_FILE, STATIONS_FILE=STATIONS_FILE, POST_WIND_DATA_FILE=POST_WIND_DATA_FILE).generateWindDataForStations()
# 
#     print("Parsed start and end date from netCDF, ", startDateObject, endDateObject)
#     print("Get observational", args.obs)
#     GetBuoyWind(STATIONS_FILE=STATIONS_FILE, OBS_WIND_FILE=OBS_WIND_DATA_FILE, startDateObject=startDateObject, endDateObject=endDateObject)
#     print("Graphing!")
#     Grapher(graphObs=args.obs, graphRain=False, WIND_TYPE="POST", OBS_WIND_DATA_FILE=OBS_WIND_DATA_FILE, STATIONS_FILE=STATIONS_FILE, WIND_DATA_FILE=POST_WIND_DATA_FILE, RAIN_DATA_FILE=GFS_RAIN_DATA_FILE).generateGraphs()
#     
    print("Generating Wave Graphs!")
    temp_directory = "wave_temp/"
    
#     Create temp and graphs directories
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
        
    print("Loading NetCDF file!")
    WAVE_SWH_FILE = args.waveswh 
    WAVE_MWD_FILE = args.wavemwd
    WAVE_MWP_FILE = args.wavemwp
    WAVE_PWP_FILE = args.wavepwp
    WAVE_RAD_FILE = args.waverad
    WAVE_SWH_DATA_FILE = temp_directory + "wave_swh_data_file" + ".json"
    WAVE_MWD_DATA_FILE = temp_directory + "wave_mwd_data_file" + ".json"
    WAVE_MWP_DATA_FILE = temp_directory + "wave_mwp_data_file" + ".json"
    WAVE_PWP_DATA_FILE = temp_directory + "wave_pwp_data_file" + ".json"
    WAVE_RAD_DATA_FILE = temp_directory + "wave_rad_data_file" + ".json"
    STATIONS_FILE = args.stations
    print()
#     (startDateObject, endDateObject) = WaveReader(
#         WAVE_SWH_FILE=WAVE_SWH_FILE,
#         WAVE_MWD_FILE=WAVE_MWD_FILE,
#         WAVE_MWP_FILE=WAVE_MWP_FILE,
#         WAVE_PWP_FILE=WAVE_PWP_FILE,
#         WAVE_RAD_FILE=WAVE_RAD_FILE,
#         STATIONS_FILE=STATIONS_FILE, 
#         WAVE_SWH_DATA_FILE=WAVE_SWH_DATA_FILE,
#         WAVE_MWD_DATA_FILE=WAVE_MWD_DATA_FILE,
#         WAVE_MWP_DATA_FILE=WAVE_MWP_DATA_FILE,
#         WAVE_PWP_DATA_FILE=WAVE_PWP_DATA_FILE,
#         WAVE_RAD_DATA_FILE=WAVE_RAD_DATA_FILE).generateWaveDataForStations()
        
    dataToGraph = {}
    dataToGraph["SWH"] = WAVE_SWH_DATA_FILE
    dataToGraph["MWD"] = WAVE_MWD_DATA_FILE
    dataToGraph["MWP"] = WAVE_MWP_DATA_FILE
    dataToGraph["PWP"] = WAVE_PWP_DATA_FILE
    dataToGraph["RAD"] = WAVE_RAD_DATA_FILE
# 
#     print("Parsed start and end date from netCDF, ", startDateObject, endDateObject)
    Grapher(dataToGraph=dataToGraph, STATIONS_FILE=STATIONS_FILE).generateGraphs()

if __name__ == "__main__":
    main()
