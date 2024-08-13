import netCDF4 as nc
import datetime


# Rework this
class Dataset:
    def __init__(self, filename, latitudes, longitudes):
        self.filename = filename
        self.longitudes = longitudes
        self.latitudes = latitudes
        self.dataset = nc.Dataset(self.filename, "w")
        self.dataset.source = "python"
        self.dataset.author = "Pranav Sai"
        self.dataset.contact = "pranav_sai@uri.edu"


        # Create dimensions
        self.dimensionTime = self.dataset.createDimension("time", None)
        self.dimensionLongitude = self.dataset.createDimension("longitude", len(self.longitudes))
        self.dimensionLatitude = self.dataset.createDimension("latitude", len(self.latitudes))

        # Create variables (with compression)
        self.variableTime = self.dataset.createVariable("time", "f4", "time", zlib=True, complevel=2,
                                                                      fill_value=nc.default_fillvals["f4"])
        self.variableUnix = self.dataset.createVariable("time_unix", "i8", "time", zlib=True, complevel=2,
                                                                           fill_value=nc.default_fillvals["i8"])  # int64 isn't supported in DAP2; still using unless RICHAMP needs DAP2
        self.variableLongitude = self.dataset.createVariable("lon", "f8", "longitude", zlib=True, complevel=2,
                                                                     fill_value=nc.default_fillvals["f8"])
        self.variableLatitude = self.dataset.createVariable("lat", "f8", "latitude", zlib=True, complevel=2,
                                                                     fill_value=nc.default_fillvals["f8"])
        # self.dataset_var_u10       = self.dataset.createVariable("U10", "f4", ("time", "latitude", "longitude"), zlib=True,
        #                                                                     complevel=2,fill_value=nc.default_fillvals["f4"])
        # self.dataset_var_v10       = self.dataset.createVariable("V10", "f4", ("time", "latitude", "longitude"), zlib=True,
        #                                                                     complevel=2,fill_value=nc.default_fillvals["f4"])
        self.variableRain = self.dataset.createVariable("precipitation", "f4", ("time", "latitude", "longitude"), zlib=True,
                                                                     complevel=2, fill_value=nc.default_fillvals["f4"])

        # Add attributes to variables
        self.coldstartDate = datetime.datetime(1990, 1, 1, 0, 0, 0)
        self.variableTime.units = "minutes since 1990-01-01 00:00:00 Z"
        self.variableTime.axis = "T"
        self.variableTime.coordinates = "time"

        self.coldstartDateUnix = datetime.datetime(1970, 1, 1, 0, 0, 0)
        self.variableUnix.units = "seconds since 1970-01-01 00:00:00 Z"
        self.variableUnix.axis = "T"
        self.variableUnix.coordinates = "time"

        self.variableLongitude.coordinates = "lon"
        self.variableLongitude.units = "degrees_east"
        self.variableLongitude.standard_name = "longitude"
        self.variableLongitude.axis = "x"

        self.variableLatitude.coordinates = "lat"
        self.variableLatitude.units = "degrees_north"
        self.variableLatitude.standard_name = "latitude"
        self.variableLatitude.axis = "y"

        self.variableRain.units = "mm h-1"
        self.variableRain.coordinates = "time lat lon"

        self.variableLatitude[:] = self.latitudes
        self.variableLongitude[:] = self.longitudes

    def append(self, index, date, rain):
        delta = (date - self.coldstartDate)
        minutes = round((delta.days * 86400 + delta.seconds) / 60)
        deltaUnix = (date - self.coldstartDateUnix)
        seconds = round(deltaUnix.days * 86400 + deltaUnix.seconds)

        self.variableTime[index] = minutes
        self.variableUnix[index] = seconds
        # self.dataset_var_u10[idx, :, :] = uvel
        # self.dataset_var_v10[idx, :, :] = vvel
#         print(self.dataset_var_lat[::])
#         print(self.dataset_var_lon[::])
        self.variableRain[index, :, :] = rain
        
    def close(self):
        self.__nc.close()
