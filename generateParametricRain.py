import math
import numpy as np
import haversine
import datetime
from Dataset import Dataset


# Track radius comes in as km, track winds come in as knots
def main(minLatitude, minLongitude, maxLatitude, maxLongitude, spatialResolution, trackStartTime, trackDeltaHours, trackWinds, trackLatitudes, trackLongitudes):
    print("Generating Parametric Rain!")
    minTrackDeltaHours = min(trackDeltaHours)
    maxTrackDeltaHours = max(trackDeltaHours)
    numTimesRain = (maxTrackDeltaHours - minTrackDeltaHours) + 1
    
    print("Interpolating track to hourly intervals")
    rainDeltaHours = np.linspace(minTrackDeltaHours, maxTrackDeltaHours, num=numTimesRain)
    rainTimes = []
    for deltaHour in rainDeltaHours:
        rainTimes.append(trackStartTime + datetime.timedelta(hours=deltaHour))
#     rainTimes = np.linspace(min(trackTimes), max(trackTimes), num=numTimesRain)
    interpolatedTrackLatitudes = np.interp(rainDeltaHours, trackDeltaHours, trackLatitudes)
    interpolatedTrackLongitudes = np.interp(rainDeltaHours, trackDeltaHours, trackLongitudes)
    interpolatedTrackWinds = np.interp(rainDeltaHours, trackDeltaHours, trackWinds)
    
    numLats = math.ceil((maxLatitude - minLatitude) / spatialResolution) + 1
    numLons = math.ceil((maxLongitude - minLongitude) / spatialResolution) + 1
#         print(numLats)
    latitudes = np.linspace(minLatitude, minLatitude + (numLats - 1) * spatialResolution, numLats)
    longitudes = np.linspace(minLongitude, minLongitude + (numLons - 1) * spatialResolution, numLons)
#         print(min(latitudes), minLatitude)
#         print(max(latitudes), maxLatitude)
#         print(min(longitudes), minLongitude)
#         print(max(longitudes), maxLongitude)
    
    #         Initialize a net cdf file
    filename = "RICHAMP_rain.nc"
    rainDataset = Dataset(filename, latitudes, longitudes)
    
    for index, time in enumerate(rainTimes):
        print("Generating rain, index", index)
        trackLatitude = interpolatedTrackLatitudes[index]
        trackLongitude = interpolatedTrackLongitudes[index]
        center = (trackLatitude, trackLongitude)
        trackWind = interpolatedTrackWinds[index]
        
        lineRains = []
#         print("time", time, "lat lon", trackLatitude, trackLongitude, "wind speed", trackWind)
        for latitude in latitudes:
            lineRain = []
            for longitude in longitudes:
                coordinate = (latitude, longitude)
                pointRain = calculateRain(center, coordinate, trackWind)
                lineRain.append(pointRain)
                distanceToCenter = haversine.haversine(center, coordinate)
#                     print(distanceToCenter)
            lineRains.append(lineRain)
        rainDataset.append(index, time, lineRains)
    
    
    # For each time, 
#     For each lat in the rain grid, stored in the netCDF file
#         For each lon
#           compute distance from storm.
  
  
#     Returns rain in millimeters per hour
def calculateRain(center, coordinate, wind):
    a1 = -1.10
    a2 = -1.60
    a3 = 64.5
    a4 = 150.0
    b1 = 3.96
    b2 = 4.80
    b3  = -13.0
    b4 = -16.0
    distanceToCenter = haversine.haversine(center, coordinate)
    u = 1.0 + ((wind - 35.0)/33.0)
#       Rain rate at r=0
    t0 = a1 + b1*u
#         Maximum rain rate
    tm = a2 + b2*u
    rm = a3 + b3*u
    re = a4 + b4*u
    rain = 0.0
    if(distanceToCenter < rm):
        rain = t0 + ((tm - t0) * (distanceToCenter/rm))
    else:
        rain = tm * math.exp(-1.0 * (distanceToCenter - rm)/re)
    #     Convert to mm/hr
    rain = rain * (1.0/24.0)
#     Added factor
    rain = rain * 1.4
#         Convert from in/day to mm/day
    rain  = rain * 25.4
    return rain