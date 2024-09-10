import argparse
import datetime
import generateParametricRain

def convertLongitude(longitudeString):
    longitude = float(longitudeString[0:-1])
    if (longitudeString[-1] == "W"):
        longitude = longitude * -1.0
    return longitude

def convertLatitude(latitudeString):
    latitude = float(latitudeString[0:-1])
    if (latitudeString[-1] == "S"):
        latitude = latitude * -1.0
    return latitude

def main():
    RAIN_FILENAME = "RICHAMP_rain.nc"
#     MIN_LATITUDE = 4.0
#     MAX_LATITUDE = 51.0
#     MIN_LONGITUDE = -101.0
#     MAX_LONGITUDE = -49.0
#     Hawaii
    MIN_LATITUDE = 15.0
    MAX_LATITUDE = 25.0
    MIN_LONGITUDE = -161.0
    MAX_LONGITUDE = -154.0
    SPATIAL_RESOLUTION = 1.0/12.0

    p = argparse.ArgumentParser(description="Make a request read parametric track and generate rain")
    p.add_argument(
            "--file", help="track file in parametric track format", type=str
    )
    args = p.parse_args()
    args.epsg = 4326
    
    trackTimes = []
    trackDeltaHours = []
    latitudes = []
    longitudes = []
    maxWindSpeedsKnots = []
    startTime = None

    
    with open(args.file) as trackFile:
        lines = trackFile.readlines()
        for line in lines:
            data = line.split(", ")
            print(data)
            dateStr = data[0]
            timeStr = data[1]
            latitudeStr = data[4]
            longitudeStr = data[5]
            windStr = data[6]
            
            time = datetime.datetime(year=int(dateStr[0:4]), month=int(dateStr[4:6]), day=int(dateStr[6:8]), hour=int(timeStr[0:2]), minute=int(timeStr[2:4]))
            print(time)
            if (startTime == None):
                startTime = time
            deltaHour = int(((time - startTime).total_seconds()) / 3600)
            print(deltaHour)
            
            trackTimes.append(time)
            trackDeltaHours.append(deltaHour)
            
            latitudes.append(convertLatitude(latitudeStr))
            longitudes.append(convertLongitude(longitudeStr))
            
            wind = float(windStr)
            maxWindSpeedsKnots.append(wind)
            print(wind)
    
    generateParametricRain.main(MIN_LATITUDE, MIN_LONGITUDE, MAX_LATITUDE, MAX_LONGITUDE, SPATIAL_RESOLUTION, startTime, trackDeltaHours, maxWindSpeedsKnots, latitudes, longitudes)


if __name__ == "__main__":
    main()
