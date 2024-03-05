from FortReader import FortReader
from Grapher import Grapher
from GetBuoyWind import GetBuoyWind
import datetime

def main():
    print("Generating Wind Graphs!")
    print("Loading NetCDF file!")
    NOS_ADCIRC_WIND_DATA_FILE_NAME = "RICV1_AWS_Analysis_Wind_Data.json"
    ADCIRC_WIND_FORT_74 = "RICV1_AWS_Forecast_fort.74.nc"
    NOS_STATIONS_FILE_NAME = "NOS_Stations.json"
    NOS_WIND_FILE_NAME = "NOS_Obs_wind_data.json"
    (startDateObject, endDateObject) = FortReader(ADCIRC_WIND_FORT_74).generateWindDataForStations(NOS_ADCIRC_WIND_DATA_FILE_NAME)
    print(startDateObject, endDateObject)
    GetBuoyWind(NOS_STATIONS_FILE_NAME=NOS_STATIONS_FILE_NAME, NOS_WIND_FILE_NAME=NOS_WIND_FILE_NAME, startDateObject=startDateObject, endDateObject=endDateObject)
    Grapher(graphObs=True, NOS_WIND_DATA_FILE_NAME=NOS_WIND_FILE_NAME, NOS_STATIONS_FILE_NAME=NOS_STATIONS_FILE_NAME, ADCIRC_WIND_DATA_FILE_NAME=NOS_ADCIRC_WIND_DATA_FILE_NAME).generateGraphs()

if __name__ == "__main__":
    main()