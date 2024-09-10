import netCDF4 as nc
import datetime
import numpy as np

# =================================================================
#Precipitation
# =================================================================
precipNC = nc.Dataset("RICHAMP_rain.nc")
# Read lat and Lons and rPrecip
xP = precipNC['lon'][:]
yP = precipNC['lat'][:]
r = precipNC['precipitation'][:]
tP = precipNC['time'][:]
#get units attribute to add offset to time
units = precipNC['time'].getncattr('units')
# Parse the units attribute
unit_parts = units.split(' ')
offset = unit_parts[2] + " " + unit_parts[3]
offset = datetime.datetime.strptime(offset, '%Y-%m-%d %H:%M:%S')
#datetime conversion
# tP = tP.astype(np.float64)
tP = [datetime.timedelta(minutes=x) for x in tP]
tP = [datetime.datetime.strftime(offset + x, '%Y-%m-%d %H:%M:%S') for x in tP]