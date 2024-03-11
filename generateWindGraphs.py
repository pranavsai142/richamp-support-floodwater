from FortReader import FortReader
from Grapher import Grapher
from GetBuoyWind import GetBuoyWind
import datetime
import argparse

def main():
    p = argparse.ArgumentParser(description="Make a request to generate run properties")
    p.add_argument(
            "--stations", help="Stations json file", type=str
    )
    p.add_argument(
        "--wind", help="Wind netcdf file", type=str
    )
    p.add_argument(
        "--obs", help="Graph observational data", type=bool
    )
    args = p.parse_args()
    args.epsg = 4326
    print("Generating Wind Graphs!")
    print("Loading NetCDF file!")
    ADCIRC_WIND_DATA_FILE_NAME = args.wind + ".json"
    ADCIRC_WIND_FORT_74 = args.wind
    STATIONS_FILE_NAME = args.stations
    OBS_WIND_FILE_NAME = args.wind + ".obs.json"
    (startDateObject, endDateObject) = FortReader(ADCIRC_WIND_FORT_74, STATIONS_FILE_NAME, ADCIRC_WIND_DATA_FILE_NAME).generateWindDataForStations(NOS_ADCIRC_WIND_DATA_FILE_NAME)
    print("Parsed start and end date from netCDF, " + startDateObject, endDateObject)
    print("Get observational", args.obs)
    GetBuoyWind(STATIONS_FILE_NAME=STATIONS_FILE_NAME, OBS_WIND_FILE_NAME=OBS_WIND_FILE_NAME, startDateObject=startDateObject, endDateObject=endDateObject)
    print("Graphing!")
    Grapher(graphObs=args.obs, OBS_WIND_FILE_NAME=OBS_WIND_FILE_NAME, STATIONS_FILE_NAME=STATIONS_FILE_NAME, ADCIRC_WIND_DATA_FILE_NAME=ADCIRC_WIND_DATA_FILE_NAME).generateGraphs()

if __name__ == "__main__":
    main()
