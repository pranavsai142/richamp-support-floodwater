from FortReader import FortReader, GFSReader
from Grapher import Grapher
from GetBuoyWind import GetBuoyWind
import datetime
import argparse
import os

def main():
    p = argparse.ArgumentParser(description="Make a request to generate run properties")
    p.add_argument(
            "--stations", help="Stations json file", type=str
    )
    p.add_argument(
        "--wind", help="Wind netcdf file", type=str
    )
    p.add_argument(
        "--rain", help="Rain netcdf file", type=str
    )
    #TODO: Fix rhia
    p.add_argument(
        "--obs", type=bool, help="Graph observational data"
    )
    args = p.parse_args()
    args.epsg = 4326
    print("Generating Wind Graphs!")
    temp_directory = "wind_temp/"
    graphs_directory = "graphs/"
    
#     Create temp and graphs directories
    if not os.path.exists(temp_directory):
        os.makedirs(temp_directory)
    if not os.path.exists(graphs_directory):
        os.makedirs(graphs_directory)
        
    print("Loading NetCDF file!")
    GFS_WIND_FILE = args.wind
    GFS_RAIN_FILE = args.rain
    GFS_WIND_DATA_FILE = temp_directory + "gfs_wind_data_file" + ".json"
    GFS_RAIN_DATA_FILE = temp_directory + "gfs_rain_data_file" + ".json"
    STATIONS_FILE = args.stations
    OBS_WIND_FILE = temp_directory + "obs_wind_data_file" + ".json"
#     (startDateObject, endDateObject) = FortReader(ADCIRC_WIND_FORT_74, STATIONS_FILE_NAME, ADCIRC_WIND_DATA_FILE_NAME).generateWindDataForStations()
    (startDateObject, endDateObject) = GFSReader(GFS_WIND_FILE=GFS_WIND_FILE, GFS_RAIN_FILE=GFS_RAIN_FILE, STATIONS_FILE=STATIONS_FILE, GFS_WIND_DATA_FILE=GFS_WIND_DATA_FILE, GFS_RAIN_DATA_FILE=GFS_RAIN_DATA_FILE).generateWindDataForStations()
    print("Parsed start and end date from netCDF, ", startDateObject, endDateObject)
    print("Get observational", args.obs)
    GetBuoyWind(STATIONS_FILE=STATIONS_FILE, OBS_WIND_FILE=OBS_WIND_FILE, startDateObject=startDateObject, endDateObject=endDateObject)
    print("Graphing!")
    Grapher(graphObs=args.obs, graphRain=True, OBS_WIND_FILE=OBS_WIND_FILE, STATIONS_FILE=STATIONS_FILE, WIND_DATA_FILE=GFS_WIND_DATA_FILE, RAIN_DATA_FILE=GFS_RAIN_DATA_FILE).generateGraphs()

if __name__ == "__main__":
    main()
