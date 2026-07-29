import netCDF4 as nc
import numpy as np
import haversine
import json
from datetime import datetime, timedelta, timezone
import os
import scipy.interpolate
from Encoders import NumpyEncoder


# Here I will write about the fort files

# Fort 74 contains an hour by hour forecast with the wind vector x and y components

# The time is measured in seconds coldstartdate + time = time of forecast
# To access metadata of fort files, use dataset.__dict__ variable on netCDF dataset
# key rundes contains information with coldstart date
# To see dimensions of variables, use dataset.dimensions
# To see information on variables, use dataset.variables
# To get data for a variable, use dataset.variables["time"]

# FORT_74_FILE_NAME = "112123.fort.74.nc"
# FORT_74_FILE_NAME = "ricv1_122223_fort.74.nc"
# FORT_74_FILE_NAME = "ec95d_120923_fort.74.nc"
# FORT_74_FILE_NAME = "ec95d_120923_forecast_fort.74.nc"
# FORT_74_FILE_NAME = "ricv1_postnotworking_fort.74.nc"
# FORT_74_FILE_NAME = "Lee_Floodwater_LeftTrack_Advisory36_fort.74.nc"
# NOS_STATIONS_FILE_NAME = "NOS_Stations.json"
# NOS_STATION_TO_NODE_DISTANCES_FILE_NAME = "NOS_Station_To_Node_Distances.json"
# NOS_ADCIRC_NODES_FILE_NAME = "NOS_ADCIRC_Nodes.json"
# NOS_ADCIRC_WIND_DATA_FILE_NAME = "NOS_ADCIRC_Wind_Data.json"
# NOS_ADCIRC_NODES_WIND_DATA_FILE_NAME = "NOS_ADCIRC_Nodes_Wind_Data.json"
# NOS_STATION_TO_NODE_DISTANCES_FILE_NAME = "NOS_Station_To_Floodwater_Node_Distances.json"
# NOS_ADCIRC_NODES_FILE_NAME = "NOS_Floodwater_Nodes.json"
# NOS_ADCIRC_WIND_DATA_FILE_NAME = "NOS_Floodwater_Wind_Data.json"
# NOS_ADCIRC_NODES_WIND_DATA_FILE_NAME = "NOS_Floodwater_Nodes_Wind_Data.json"


# Napatree Runup Bounds
# MIN_SEARCH_LONGITUDE = -71.95
# MAX_SEARCH_LONGITUDE = -71.75
# MIN_SEARCH_LATITUDE = 40.5
# MAX_SEARCH_LATITUDE = 41.3125

MIN_SEARCH_LONGITUDE = -999
MAX_SEARCH_LONGITUDE = 999
MIN_SEARCH_LATITUDE = -999
MAX_SEARCH_LATITUDE = 999

class Reader:
    def __init__(self, STATIONS_FILE="", STATION_TO_NODE_DISTANCES_FILE="", NODES_FILE="", BACKGROUND_AXIS=[], format=""):
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = STATION_TO_NODE_DISTANCES_FILE
        self.NODES_FILE = NODES_FILE
        self.format = format
        self.BACKGROUND_AXIS = BACKGROUND_AXIS

    def _parseColdStartDate(self, timeUnits):
        """Parse ADCIRC/CF time units: 'seconds since <date>' / 'minutes since <date>'.

        Handles production fort.15 base_date quirks like '2018-02-23 0Z'.
        """
        import re
        units = (timeUnits or "").strip()
        if "since" not in units.lower():
            raise ValueError(f"Unrecognized time units (no 'since'): {timeUnits!r}")
        after = re.split(r"since", units, maxsplit=1, flags=re.IGNORECASE)[1].strip()
        # "2018-02-23 0Z" / "2018-02-23 0:0:0Z" → normalize hour-only + trailing Z
        after = re.sub(r"\s+(\d{1,2})Z\s*$", lambda m: f" {int(m.group(1)):02d}:00:00", after)
        after = after.rstrip("Z").strip()
        after = re.sub(r"\s+", " ", after)
        for fmt in (
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d",
        ):
            try:
                return datetime.strptime(after, fmt).replace(tzinfo=timezone.utc)
            except ValueError:
                continue
        # last resort: ISO with T separator
        iso = after.replace(" ", "T", 1) if "T" not in after else after
        return datetime.fromisoformat(iso).replace(tzinfo=timezone.utc)

    def extractLatitudeIndex(self, nodeIndex):
        return int(nodeIndex[1: nodeIndex.find(",")])
    def extractLongitudeIndex(self, nodeIndex):
        return int(nodeIndex[nodeIndex.find(",") + 1: nodeIndex.find(")")])
        
    def getValue(self, index, nodeIndex, dataType, dataset):
        if(dataType == "post"):
            valueX = float(dataset.variables["spd"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            valueY = float(dataset.variables["dir"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            return(valueX, valueY)
        elif(dataType == "gfs"):
            valueX = float(dataset.variables["wind_u"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            valueY = float(dataset.variables["wind_v"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
            return(valueX, valueY)
        elif(dataType == "rain"):
            return float(dataset.variables["precipitation"][index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
        elif(dataType == "fort"):
            valueX = dataset.variables["windx"][index][int(nodeIndex)]
            valueY = dataset.variables["windy"][index][int(nodeIndex)]
            return (valueX, valueY)
        elif(dataType == "water"):
            return float(dataset.variables["zeta"][index][int(nodeIndex)])
        elif(dataType == "swh"):
            return float(dataset.variables["swan_HS"][index][int(nodeIndex)])
        elif(dataType == "mwd"):
            return float(dataset.variables["swan_DIR"][index][int(nodeIndex)])
        elif(dataType == "mwp"):
           return float(dataset.variables["swan_TMM10"][index][int(nodeIndex)])
        elif(dataType == "pwp"):
            return float(dataset.variables["swan_TPS"][index][int(nodeIndex)])
        elif(dataType == "rad"):
            valueX = float(dataset.variables["radstress_x"][index][int(nodeIndex)])
            valueY = float(dataset.variables["radstress_y"][index][int(nodeIndex)])
            return(valueX, valueY)
        
    def getValuesForPoints(self, nodesIndex, dataType, dataset):
        if(dataType == "post" or dataType == "gfs"):
            # Do NOT load full field cubes. Cache unique cells only (time series
            # per point). A single bbox over all RI stations spans ~full NLCD and
            # reloads multi-GB; per-cell reads stay O(n_support × n_times).
            if dataType == "post":
                varX = dataset.variables["spd"]
                varY = dataset.variables["dir"]
            else:
                varX = dataset.variables["wind_u"]
                varY = dataset.variables["wind_v"]
            pairs = [(self.extractLatitudeIndex(n), self.extractLongitudeIndex(n)) for n in nodesIndex]
            if not pairs:
                return ([], [])
            unique = list(dict.fromkeys(pairs))
            print(f"  loading {len(unique)} unique cell time-series ({len(pairs)} support slots)", flush=True)
            cacheX = {}
            cacheY = {}
            for k, (ilat, ilon) in enumerate(unique):
                cacheX[(ilat, ilon)] = np.asarray(varX[:, ilat, ilon], dtype=float)
                cacheY[(ilat, ilon)] = np.asarray(varY[:, ilat, ilon], dtype=float)
                if (k + 1) % 10 == 0 or (k + 1) == len(unique):
                    print(f"    cell {k+1}/{len(unique)}", flush=True)
            pointsValuesX = [cacheX[p].tolist() for p in pairs]
            pointsValuesY = [cacheY[p].tolist() for p in pairs]
            return (pointsValuesX, pointsValuesY)
        if(dataType == "fort"):
            pointsValuesX = []
            pointsValuesY = []
            dataX = dataset.variables["windx"][::]
            dataY = dataset.variables["windy"][::]
            for nodeIndex in nodesIndex:
                valuesX = []
                valuesY = []
                for index in range(len(dataX)):
                    valuesX.append(dataX[index][int(nodeIndex)])
                    valuesY.append(dataY[index][int(nodeIndex)])
                pointsValuesX.append(valuesX)
                pointsValuesY.append(valuesY)
            return (pointsValuesX, pointsValuesY)
        if(dataType == "rad"):
            pointsValuesX = []
            pointsValuesY = []
            dataX = dataset.variables["radstress_x"][::]
            dataY = dataset.variables["radstress_y"][::]
            for nodeIndex in nodesIndex:
                valuesX = []
                valuesY = []
                for index in range(len(dataX)):
                    valuesX.append(dataX[index][int(nodeIndex)])
                    valuesY.append(dataY[index][int(nodeIndex)])
                pointsValuesX.append(valuesX)
                pointsValuesY.append(valuesY)
            return (pointsValuesX, pointsValuesY)
        if(dataType == "rain"):
            pointsValues = []
            data = dataset.variables["precipitation"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][self.extractLatitudeIndex(nodeIndex)][self.extractLongitudeIndex(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "water"):
            pointsValues = []
            data = dataset.variables["zeta"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "swh"):
            pointsValues = []
            data = dataset.variables["swan_HS"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "mwd"):
            pointsValues = []
            data = dataset.variables["swan_DIR"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "mwp"):
            pointsValues = []
            data = dataset.variables["swan_TMM10"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
        if(dataType == "pwp"):
            pointsValues = []
            data = dataset.variables["swan_TPS"][::]
            for nodeIndex in nodesIndex:
                values = []
                for index in range(len(data)):
                    values.append(data[index][int(nodeIndex)])
                pointsValues.append(values)
            return pointsValues
            
            
    def getValuesGrid(self, spaceSparseness, timeSparseness, dataType, dataset):
        if(dataType == "post"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["spd"][::][::][::]
            dataY = dataset.variables["dir"][::][::][::]
            for index in range(0, len(dataX), timeSparseness):
                lineX = []
                lineY = []
                for latitudeIndex in range(0, len(dataX[index]), spaceSparseness):
                    pointX = []
                    pointY = []
                    for longitudeIndex in range(0, len(dataX[index][latitudeIndex]), spaceSparseness):
                        pointX.append(float(dataX[index][latitudeIndex][longitudeIndex]))
                        pointY.append(float(dataY[index][latitudeIndex][longitudeIndex]))
                    lineX.append(pointX)
                    lineY.append(pointY)
                valuesX.append(lineX)
                valuesY.append(lineY)   
            return (valuesX, valuesY)
        elif(dataType == "gfs"):
            # Keep 2D lat/lon structure for pcolormesh map frames (wind.gif).
            # Apply sparseness so full-basin PWM (565×625×N) does not explode memory/JSON.
            dataX = np.array(
                dataset.variables["wind_u"][::timeSparseness, ::spaceSparseness, ::spaceSparseness]
            )
            dataY = np.array(
                dataset.variables["wind_v"][::timeSparseness, ::spaceSparseness, ::spaceSparseness]
            )
            return (dataX, dataY)
        elif(dataType == "rain"):
            data = dataset.variables["precipitation"][::][::][::]
            return data
        elif(dataType == "fort"):
            dataX = dataset.variables["windx"][::][::]
            dataY = dataset.variables["windy"][::][::]
            return (dataX, dataY)
        elif(dataType == "water"):
            data = dataset.variables["zeta"][::][::]
            return data
        elif(dataType == "swh"):
            data = dataset.variables["swan_HS"][::][::]
            return data
        elif(dataType == "mwd"):
            data = dataset.variables["swan_DIR"][::][::]
            return data
        elif(dataType == "mwp"):
            data = dataset.variables["swan_TMM10"][::][::]
            return data
        elif(dataType == "pwp"):
            data = dataset.variables["swan_TPS"][::][::]
            return data
        elif(dataType == "rad"):
            dataX = dataset.variables["radstress_x"][::][::]
            dataY = dataset.variables["radstress_y"][::][::]
            return (dataX, dataY)
                 
    def getValues(self, spaceSparseness, timeSparseness, dataType, dataset):
        if(dataType == "post"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["spd"][::][::][::]
            dataY = dataset.variables["dir"][::][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index]).flatten()[::spaceSparseness]
                subsetDataY = np.array(dataY[index]).flatten()[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return (valuesX, valuesY)
        elif(dataType == "gfs"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["wind_u"][::][::][::]
            dataY = dataset.variables["wind_v"][::][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index]).flatten()[::spaceSparseness]
                subsetDataY = np.array(dataY[index]).flatten()[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return (valuesX, valuesY)
        elif(dataType == "rain"):
            values = []
            data = dataset.variables["precipitation"][::][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index]).flatten()[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "fort"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["windx"][::][::]
            dataY = dataset.variables["windy"][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index])[::spaceSparseness]
                subsetDataY = np.array(dataY[index])[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return (valuesX, valuesY)
        elif(dataType == "water"):
            values = []
            data = dataset.variables["zeta"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "swh"):
            values = []
            data = dataset.variables["swan_HS"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "mwd"):
            values = []
            data = dataset.variables["swan_DIR"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index]).flatten()[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "mwp"):
            values = []
            data = dataset.variables["swan_TMM10"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "pwp"):
            values = []
            data = dataset.variables["swan_TPS"][::][::]
            for index in range(0, len(data), timeSparseness):
                subsetData = np.array(data[index])[::spaceSparseness]
                values.append(subsetData)
            return values
        elif(dataType == "rad"):
            valuesX = []
            valuesY = []
            dataX = dataset.variables["radstress_x"][::][::]
            dataY = dataset.variables["radstress_y"][::][::]
            for index in range(0, len(dataX), timeSparseness):
                subsetDataX = np.array(dataX[index])[::spaceSparseness]
                subsetDataY = np.array(dataY[index])[::spaceSparseness]
                valuesX.append(subsetDataX)
                valuesY.append(subsetDataY)
            return(valuesX, valuesY)
            
            
    def getCoordinates(self, spaceSparseness, dataset):
        nodesIndex = []
        pointsLatitudes = []
        pointsLongitudes = []
        points = []
        if(self.format == "GFS" or self.format == "POST"):
            latitudes = dataset.variables["lat"][::]
            longitudes = dataset.variables["lon"][::]
            for latitudeIndex, latitude in enumerate(latitudes):
                for longitudeIndex, longitude in enumerate(longitudes):
                    nodesIndex.append(str((latitudeIndex, longitudeIndex)))
                    pointsLatitudes.append(latitude)
                    pointsLongitudes.append(longitude)
        elif(self.format == "FORT"):
            latitudes = dataset.variables["y"][::]
            longitudes = dataset.variables["x"][::]
            for index in range(len(latitudes)):
                nodesIndex.append(str(index))
                pointsLatitudes.append(latitudes[index])
                pointsLongitudes.append(longitudes[index])
        nodesIndex = nodesIndex[::spaceSparseness]
        pointsLatitudes = pointsLatitudes[::spaceSparseness]
        pointsLongitudes = pointsLongitudes[::spaceSparseness]
        return (pointsLatitudes, pointsLongitudes), nodesIndex
        
    def getCoordinatesGrid(self, spaceSparseness, dataset):
        nodesIndex = []
        points = []
        if(self.format == "GFS" or self.format == "POST"):
            latitudes = dataset.variables["lat"][::spaceSparseness]
            longitudes = dataset.variables["lon"][::spaceSparseness]
            for latitudeIndex in range(len(latitudes)):
                for longitudeIndex in range(len(longitudes)):
                    nodesIndex.append(str((latitudeIndex, longitudeIndex)))
                    
        elif(self.format == "FORT"):
            latitudes = dataset.variables["y"][::]
            longitudes = dataset.variables["x"][::]
            for index in range(len(latitudes)):
                nodesIndex.append(str(index))
        return (latitudes, longitudes), nodesIndex

# Example background axis
# SOUTH_NEW_ENGLAND_AXIS = [-71.905117442267496, -71.0339945492675, 42.200717972845119, 41.028319358056874]
    def isOutsideBackground(self, point):
        if(point[0] > self.BACKGROUND_AXIS[0] and point[0] < self.BACKGROUND_AXIS[1]):
            if(point[1] > self.BACKGROUND_AXIS[3] and point[1] < self.BACKGROUND_AXIS[2]):
                return False
        return True
   
    def findTriangleIndicesOutsideBackground(self, triangles, dataset):
        latitudes = dataset.variables["y"][::]
        longitudes = dataset.variables["x"][::]
        maskedIndices = []
        for index, triangle in enumerate(triangles):
            point0 = [longitudes[triangle[0]], latitudes[triangle[0]]]
            point1 = [longitudes[triangle[1]], latitudes[triangle[1]]]
            point2 = [longitudes[triangle[2]], latitudes[triangle[2]]]
            if(self.isOutsideBackground(point0) or self.isOutsideBackground(point1) or self.isOutsideBackground(point2)):
                maskedIndices.append(True)
            else:
                maskedIndices.append(False)
        return maskedIndices
                
#    TODO: Get map background bounds and mask triangles with any vertices that fall outside of bounds
    def getTriangles(self, dataset):
        trianglesOffByOne = np.array(dataset.variables["element"][:])
        triangles = trianglesOffByOne - 1
        maskedIndices = self.findTriangleIndicesOutsideBackground(triangles, dataset)
#         xCoordinates = dataset.variables["x"]
#         yCoordinates = dataset.variables["y"]
#         triangleXCoordinates = []
#         triangleYCoordinates = []
#         print(len(xCoordinates))
#         print(len(yCoordinates))
#         print(np.min(triangles, axis=0))
#         for triangle in triangles:
#             triangleXCoordinates.append([xCoordinates[triangle[0]], xCoordinates[triangle[1]], xCoordinates[triangle[2]]])
#             triangleYCoordinates.append([yCoordinates[triangle[0]], yCoordinates[triangle[1]], yCoordinates[triangle[2]]])
#             
#         triangleAreas = []
#         badIndices = []
#         for index, triangleXCoordinate in enumerate(triangleXCoordinates):
#             x1 = triangleXCoordinate[0]
#             x2 = triangleXCoordinate[1]
#             x3 = triangleXCoordinate[2]
#             y1 = triangleYCoordinates[index][0]
#             y2 = triangleYCoordinates[index][1]
#             y3 = triangleYCoordinates[index][2]
#             print(x1, x2, x3)
#             if ((x1 < -71.9) or (x2 < -71.9) or (x3 < -71.9)):
#                 badIndices.append(index)
#             area = (0.5) * np.abs(((x1 * (y2 - y3)) + (x2 * (y3 - y1)) + (x3*(y1 - y2))))
#             triangleAreas.append(area)
# #             print(area)
#                 
#         for index in badIndices:
#             area = triangleAreas[index]
#             print("index, area", index, area)
#         print(badIndices)
#         print(len(triangles), len(badIndices))
        return triangles, maskedIndices
        
#     def getElevations(self, dataset):
#         elevations = np.array(dataset.variables["adcirc_mesh"][:])
#         print(len(elevations))
# #         quit()
#         return elevations
        
    def getMap(self, dataset, dataType, times, spaceSparseness, timeSparseness, data):
        print("getting map", dataType, flush=True)
        mapValuesX = []
        mapValuesY = []
        mapTriangles = []
        mapValues = []
        
        mapNodes = []
        mapNodesLatitudes = []
        mapNodesLongitudes = []
        
        if(self.format == "GFS" or self.format == "POST"):
            value = self.getValuesGrid(spaceSparseness, timeSparseness, dataType, dataset)
            nodes, nodesIndex = self.getCoordinatesGrid(spaceSparseness, dataset)
        elif(self.format == "FORT"):
            value = self.getValues(spaceSparseness, timeSparseness, dataType, dataset)
            nodes, nodesIndex = self.getCoordinates(spaceSparseness, dataset)
            mapTriangles, mapMaskedTriangles = self.getTriangles(dataset)
#             mapElevations = self.getElevations(dataset)
        if(dataType == "post" or dataType == "gfs" or dataType == "fort" or dataType == "rad"):
            mapValuesX = value[0]
            mapValuesY = value[1]
        else:
            mapValues = value
        mapNodesLatitudes = nodes[0]
        mapNodesLongitudes = nodes[1]
        mapNodes = nodesIndex
#         print(len(points))
        
        data["map_data"] = {}
        data["map_data"]["map_times"] = times[::timeSparseness]
        data["map_data"]["map_points"] = mapNodes
        data["map_data"]["map_pointsLatitudes"] = mapNodesLatitudes
        data["map_data"]["map_pointsLongitude"] = mapNodesLongitudes
        if(self.format == "FORT"):
            data["map_data"]["map_triangles"] = mapTriangles
            data["map_data"]["map_maskedTriangles"] = mapMaskedTriangles
#             data["map_data"]["map_elevation"] = mapElevations
        if(dataType == "rad"):
            data["map_data"]["map_radstressX"] = mapValuesX
            data["map_data"]["map_radstressY"] = mapValuesY
        elif(dataType == "gfs" or dataType == "fort"):
            data["map_data"]["map_windsX"] = mapValuesX
            data["map_data"]["map_windsY"] = mapValuesY
        elif(dataType == "post"):
            data["map_data"]["map_speeds"] = mapValuesX
            data["map_data"]["map_directions"] = mapValuesY
        else:
            data["map_data"]["map_" + dataType] = mapValues
        return data
            
    def getMapWithPoints(self, points, triangles, maskedTriangles, elevations, dataType, data):
        print("getting map", dataType, flush=True)
        mapTriangles = []
        mapValues = []
        
        mapNodes = []
        mapNodesLatitudes = []
        mapNodesLongitudes = []
        
        nodes, nodesIndex = points, list(range(len(points[0])))
        mapTriangles, mapMaskedTriangles = triangles, maskedTriangles
#             mapElevations = self.getElevations(dataset)

        mapValues = elevations
        mapNodesLatitudes = nodes[1]
        mapNodesLongitudes = nodes[0]
        mapNodes = nodesIndex
#         print(len(points))
        
        data["map_data"] = {}
        data["map_data"]["map_points"] = mapNodes
        data["map_data"]["map_pointsLatitudes"] = mapNodesLatitudes
        data["map_data"]["map_pointsLongitude"] = mapNodesLongitudes
        data["map_data"]["map_triangles"] = mapTriangles
        data["map_data"]["map_maskedTriangles"] = mapMaskedTriangles
        data["map_data"]["map_" + dataType] = mapValues
        return data
        
    def getNetcdfProperties(self, NETCDF_FILE, dataType):
        if(self.format == "POST"):
            dataset = nc.Dataset(NETCDF_FILE)["Main"]
        else:
            dataset = nc.Dataset(NETCDF_FILE)
        metadata = dataset.__dict__
#         print(dataset.variables)
#         quit()

        datasetTimeDescription = dataset.variables["time"].units
        # Parse CF/ADCIRC "seconds since <date>" robustly.
        # ADCIRC often writes base_date like "2018-02-23 0Z" (not ISO hour).
        coldStartDate = self._parseColdStartDate(datasetTimeDescription)
#         coldStartDate = datetime(year=2018, month=2, day=23, hour=5)
        print("coldStartDate", coldStartDate, flush=True)

        minT = float(dataset.variables["time"][0].data)
        maxT = float(dataset.variables["time"][-1].data)
        times = []
        print(minT, flush=True)
        print(maxT, flush=True)
        if(self.format == "POST" or self.format == "GFS"):
#             print("deltaT of data")
            windDeltaT = timedelta(minutes=maxT - minT)
#             print(windDeltaT)

#             print("number of timesteps")
            timesteps = len(dataset.variables["time"][:])
#             print(timesteps)

            for index in range(timesteps):
#                 print("timedelta", timedelta(minutes=float(dataset.variables["time"][index].data)))
                time = coldStartDate + timedelta(minutes=float(dataset.variables["time"][index].data))
#                 time.replace(timezone.utc)
#                 print("tzinfo", time.tzinfo)
                times.append(time.timestamp())
#                 print(times)
#                 quit()

#             print("start of data (seconds since coldstart)")
            startDate = coldStartDate + timedelta(minutes=float(minT))
            endDate = coldStartDate + timedelta(minutes=float(maxT))
            print("startDate", startDate, flush=True)
            print("endDate", endDate, flush=True)
#         
            # GFS Data is grid based system
#             print("min max latitude and longitude")
            minLatitude = dataset.variables["lat"][0].data
            minLongitude = dataset.variables["lon"][0].data
            maxLatitude = dataset.variables["lat"][-1].data
            maxLongitude = dataset.variables["lon"][-1].data

#             print("minLatitude", minLatitude)
#             print("minLongitude", minLongitude)
#             print("maxLatitude", maxLatitude)
#             print("maxLongitude", maxLongitude)

            deltaLatitude = maxLatitude - minLatitude
            deltaLongitude = maxLongitude - minLongitude

            print("deltaLatitude", deltaLatitude, flush=True)
            print("deltaLongitude", deltaLongitude, flush=True)

            deltaNodesLatitude = len(dataset.variables["lat"][:])
            deltaNodesLongitude = len(dataset.variables["lon"][:])

            print("deltaNodesLatitude", deltaNodesLatitude, flush=True)
            print("deltaNodesLongitude", deltaNodesLongitude, flush=True)
        elif(self.format == "FORT"):
    #         print("deltaT of data")
            windDeltaT = timedelta(seconds=maxT - minT)
     #        print(windDeltaT)

    #         print("number of timesteps")
            timesteps = len(dataset.variables["time"][:])
    #         print(timesteps)

            for index in range(timesteps):
                time = coldStartDate + timedelta(seconds=float(dataset.variables["time"][index].data))
                times.append(time.timestamp())

    #         print("start of data (seconds since coldstart)")
            startDate = coldStartDate + timedelta(seconds=float(minT))
            endDate = coldStartDate + timedelta(seconds=float(maxT))
    #         print("startDate", startDate)
    #         print("endDate", endDate)
        
            # Grid origin is top right? Maybe not, Node based system!
            # y is latitude, x is longitude
            node0 = (float(dataset.variables["y"][0].data), float(dataset.variables["x"][0].data))
    #         print("node0 (lat, long)", node0)

            numberOfNodes = dataset.variables["x"].shape[0]

#         print("number of nodes", numberOfNodes)

        # Debug sample node: ricv1-scale meshes have >>200k nodes; ec95d has ~31k.
        # Indexing a fixed 200000 OOBs on coarse meshes and aborts post.
        _nnodes = int(dataset.variables["x"].shape[0]) if "x" in dataset.variables else 0
        _dbg_node = min(200000, max(0, _nnodes - 1))
        
        if (dataType == "swh"):
            print(f"significant wave height at node{_dbg_node}", flush=True)
        
            swhX0 = dataset.variables["swan_HS"][0][_dbg_node]

            print("swhX0", swhX0, flush=True)
        elif (dataType == "mwd"):
            print(f"mean wave direction at node{_dbg_node}", flush=True)
        
            mwdX0 = dataset.variables["swan_DIR"][0][_dbg_node]

            print("mwdX0", mwdX0, flush=True)
        elif (dataType == "mwp"):
            print(f"mean wave period at node{_dbg_node}", flush=True)
        
            mwpX0 = dataset.variables["swan_TMM10"][0][_dbg_node]

            print("mwpX0", mwpX0, flush=True)
        elif (dataType == "pwp"):
            print(f"peak wave period at node{_dbg_node}", flush=True)
        
            tpsX0 = dataset.variables["swan_TPS"][0][_dbg_node]

            print("tpsX0", tpsX0, flush=True)
        elif (dataType == "rad"):
            print(f"radiation stress gradient at node{_dbg_node}", flush=True)
        
            radX0 = dataset.variables["radstress_x"][0][_dbg_node]
            radY0 = dataset.variables["radstress_y"][0][_dbg_node]

            print("radX0", radX0, flush=True)
            print("radY0", radY0, flush=True)
        elif (dataType == "fort"):
            print("wind at node0")
        
            windX0 = dataset.variables["windx"][0][0]
            windY0 = dataset.variables["windy"][0][0]

            print("windX0", windX0, flush=True)
            print("windY0", windY0, flush=True)
        elif (dataType == "water"):
            print("water at node0", flush=True)
            
            zeta0 = dataset.variables["zeta"][0][0]
#             elevation0 = dataset.variables["adcirc_mesh"][:]
#             print(elevation0)
#             quit()
            print("zeta0", zeta0, flush=True)
#             print("elevation0", elevation0, flush=True)
#             quit()
            
        elif (dataType == "rain"):
            print("rain at (0,0)", flush=True)
            
            rain0 = dataset.variables["precipitation"][0][0][0]
            print("rain", rain0, flush=True)
        elif (dataType == "gfs"):
            print("Wind at t=0, point(0, 0)", flush=True)
            windX0 = dataset.variables["wind_u"][0][0][0]
            windY0 = dataset.variables["wind_v"][0][0][0]
            print("windX000", windX0, flush=True)
            print("windY000", windY0, flush=True)
        elif (dataType == "post"):
            speed0 = dataset.variables["spd"][0][0][0]
            direction0 = dataset.variables["dir"][0][0][0]
            print("speed0", speed0, flush=True)
            print("direction0", direction0, flush=True)

        return dataset, times
        
      
    def initializeClosestNodesForPoints(self, points, thresholdDistance, dataType):
        # Find node indexes that are closest to NOS_Stations
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
        stationToNodeDistancesDict = {}
        if(dataType == "rain"):
            stationKeys = stationsDict["USGS"].keys()
        elif(dataType in ["swh", "mwd", "mwp", "pwp", "rad"]):
            stationKeys = stationsDict["NDBC"].keys()
#             print(stationKeys)
        elif(dataType == "elevation"):
            stationKeys = stationsDict["ASSET"].keys()
        else:
            stationKeys = stationsDict["NOS"].keys()
        for stationKey in stationKeys:
            stationToNodeDistancesDict[stationKey] = {}
        # recreate station to node distances calculations dictionary
        print("retreving coordinates for all nodes", flush=True)
        (nodesLongitudes, nodesLatitudes), nodesIndex = points, list(range(len(points[0])))
        for index in range(len(nodesIndex)):
            node = (nodesLatitudes[index], nodesLongitudes[index])
            nodeIndex = nodesIndex[index]
#             print(node)
            if(node[0] <= 90 and node[0] >= -90 and node[0] <= MAX_SEARCH_LATITUDE and node[0] >= MIN_SEARCH_LATITUDE and node[1] >= MIN_SEARCH_LONGITUDE and node[1] <= MAX_SEARCH_LONGITUDE):
                for stationKey in stationKeys:
#                     print(stationKey)
                    if(dataType == "rain"):
                        stationDict = stationsDict["USGS"][stationKey]
                    elif(dataType in ["swh", "mwd", "mwp", "pwp", "rad"]):
                        stationDict = stationsDict["NDBC"][stationKey]
                    elif(dataType == "elevation"):
                        stationDict = stationsDict["ASSET"][stationKey]
                    else:
                        stationDict = stationsDict["NOS"][stationKey]
                    stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
    #                             distance and threshold in kilometers
                    distance = haversine.haversine(stationCoordinates, node)
#                     print("stationCoordinates", stationCoordinates)
#                     print("distance", distance)
                    if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
                        stationToNodeDistancesDict[stationKey]["closestNodes"] = []
                    elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
                    if(thresholdDistance > distance):
#                         print("Found a closest node", node, nodeIndex, "distance ", distance, "station", stationKey)
                        stationToNodeDistancesDict[stationKey]["closestNodes"].append(nodeIndex)
#             else:
#                 badNodes.append(nodeIndex)
#                 print("bad node", nodeIndex, node, flush=True)
            if(index % 100000 == 0):
                print("index", index, flush=True)

        with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
            json.dump(stationToNodeDistancesDict, outfile)
                
        with open(self.STATION_TO_NODE_DISTANCES_FILE) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
        
        nodes = {"NOS": {}}
    
        for stationKey in stationToNodeDistancesDict.keys():
            stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
            nodeIndex = stationToNodeDistanceDict["nodeIndex"]
            closestNodes = stationToNodeDistancesDict[stationKey]["closestNodes"]
            nodes["NOS"][stationKey] = {}
            nodes["NOS"][stationKey]["closestNodes"] = closestNodes
            nodes["NOS"][stationKey]["nodeIndex"] = nodeIndex
            nodes["NOS"][stationKey]["latitude"] = float(points[1][int(nodeIndex)])
            nodes["NOS"][stationKey]["longitude"] = float(points[0][int(nodeIndex)])
            
        with open(self.NODES_FILE, "w") as outfile:
            json.dump(nodes, outfile)
              
        
    def initializeClosestNodes(self, dataset, thresholdDistance, dataType):
        # Find node indexes that are closest to NOS_Stations
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
        stationToNodeDistancesDict = {}
        if(dataType == "rain"):
            stationKeys = stationsDict["USGS"].keys()
            stationGroup = "USGS"
        elif(dataType in ["swh", "mwd", "mwp", "pwp", "rad"]):
            stationKeys = stationsDict["NDBC"].keys()
            stationGroup = "NDBC"
            print(stationKeys)
        else:
            stationKeys = stationsDict["NOS"].keys()
            stationGroup = "NOS"
        for stationKey in stationKeys:
            stationToNodeDistancesDict[stationKey] = {}

        # Fast path: regular lat/lon grids (GFS / RICHAMP post). Full scan of NLCD
        # (~7e6 cells × N stations × haversine) is multi-hour; use local windows.
        if self.format in ("GFS", "POST"):
            print("retreving coordinates (regular-grid fast path)", flush=True)
            lats = np.asarray(dataset.variables["lat"][:], dtype=float).ravel()
            lons = np.asarray(dataset.variables["lon"][:], dtype=float).ravel()
            # pad threshold window in degrees (~1° lat ≈ 111 km)
            pad_km = max(float(thresholdDistance), 0.15)  # at least ~150 m for dense grids
            for stationKey in stationKeys:
                stationDict = stationsDict[stationGroup][stationKey]
                slat = float(stationDict["latitude"])
                slon = float(stationDict["longitude"])
                dlat = pad_km / 111.0
                coslat = max(0.2, abs(np.cos(np.deg2rad(slat))))
                dlon = pad_km / (111.0 * coslat)
                ilat0 = int(np.searchsorted(lats, slat - dlat))
                ilat1 = int(np.searchsorted(lats, slat + dlat))
                ilon0 = int(np.searchsorted(lons, slon - dlon))
                ilon1 = int(np.searchsorted(lons, slon + dlon))
                ilat0 = max(0, ilat0 - 1)
                ilon0 = max(0, ilon0 - 1)
                ilat1 = min(len(lats), ilat1 + 1)
                ilon1 = min(len(lons), ilon1 + 1)
                # if station outside grid, still take nearest cell as nodeIndex
                i_near = int(np.argmin(np.abs(lats - slat)))
                j_near = int(np.argmin(np.abs(lons - slon)))
                best_d = haversine.haversine((slat, slon), (float(lats[i_near]), float(lons[j_near])))
                best_idx = str((i_near, j_near))
                # collect (distance, idx) then keep only the nearest few — enough for
                # LinearND, avoids 80× stencil reads on multi-GB RICHAMP files
                candidates = []
                thr = max(float(thresholdDistance), 0.15)
                for i in range(ilat0, ilat1):
                    for j in range(ilon0, ilon1):
                        node = (float(lats[i]), float(lons[j]))
                        d = haversine.haversine((slat, slon), node)
                        idx = str((i, j))
                        if d < best_d:
                            best_d = d
                            best_idx = idx
                        if d < thr:
                            candidates.append((d, idx))
                candidates.sort(key=lambda t: t[0])
                max_stencil = 9
                closest = [idx for _, idx in candidates[:max_stencil]]
                if not closest:
                    closest = [best_idx]
                stationToNodeDistancesDict[stationKey] = {
                    "nodeIndex": best_idx,
                    "distance": best_d,
                    "closestNodes": closest,
                }
                print(
                    f"  station {stationKey}: nearest={best_idx} d={best_d:.3f}km n_close={len(closest)}",
                    flush=True,
                )
            with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
                json.dump(stationToNodeDistancesDict, outfile)
            nodes = {"NOS": {}}
            for stationKey in stationToNodeDistancesDict.keys():
                rec = stationToNodeDistancesDict[stationKey]
                nodeIndex = rec["nodeIndex"]
                nodes["NOS"][stationKey] = {
                    "closestNodes": rec["closestNodes"],
                    "nodeIndex": nodeIndex,
                    "latitude": float(lats[self.extractLatitudeIndex(nodeIndex)]),
                    "longitude": float(lons[self.extractLongitudeIndex(nodeIndex)]),
                }
            with open(self.NODES_FILE, "w") as outfile:
                json.dump(nodes, outfile)
            return

        # recreate station to node distances calculations dictionary (unstructured / fort mesh)
        print("retreving coordinates for all nodes", flush=True)
        (nodesLatitudes, nodesLongitudes), nodesIndex = self.getCoordinates(1, dataset)
        for index in range(len(nodesIndex)):
            node = (nodesLatitudes[index], nodesLongitudes[index])
            nodeIndex = nodesIndex[index]
#             print(node)
            if(node[0] <= 90 and node[0] >= -90 and node[0] <= MAX_SEARCH_LATITUDE and node[0] >= MIN_SEARCH_LATITUDE and node[1] >= MIN_SEARCH_LONGITUDE and node[1] <= MAX_SEARCH_LONGITUDE):
                for stationKey in stationKeys:
#                     print(stationKey)
                    if(dataType == "rain"):
                        stationDict = stationsDict["USGS"][stationKey]
                    elif(dataType in ["swh", "mwd", "mwp", "pwp", "rad"]):
                        stationDict = stationsDict["NDBC"][stationKey]
                    else:
                        stationDict = stationsDict["NOS"][stationKey]
                    stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
    #                             distance and threshold in kilometers
                    distance = haversine.haversine(stationCoordinates, node)
#                     print("stationCoordinates", stationCoordinates)
#                     print("distance", distance)
                    if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
                        stationToNodeDistancesDict[stationKey]["closestNodes"] = []
                    elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
                        stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
                        stationToNodeDistancesDict[stationKey]["distance"] = distance
                    if(thresholdDistance > distance):
    #                                 print("Found a closest node", node, nodeIndex, "distance ", distance, "station", stationKey)
                        stationToNodeDistancesDict[stationKey]["closestNodes"].append(nodeIndex)

            if(index % 100000 == 0):
                print("index", index, flush=True)
#         if(self.format == "GFS" or self.format == "POST"):
#             deltaNodesLatitude = len(dataset.variables["lat"][:])
#             deltaNodesLongitude = len(dataset.variables["lon"][:])
#             for longitudeIndex in range(deltaNodesLongitude):
#                 for latitudeIndex in range(deltaNodesLatitude):
#                     node = (float(dataset.variables["lat"][latitudeIndex].data), float(dataset.variables["lon"][longitudeIndex].data))
#                     nodeIndex = str((latitudeIndex, longitudeIndex))
#                     if(node[0] <= 90 and node[0] >= -90):
#                         for stationKey in stationsDict["NOS"].keys():
#                             stationDict = stationsDict["NOS"][stationKey]
#                             stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
# #                             distance and threshold in kilometers
#                             distance = haversine.haversine(stationCoordinates, node)
# #                             print("stationCoordinates", stationCoordinates)
# #                             print("distance", distance)
#                             if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
#                                 stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                                 stationToNodeDistancesDict[stationKey]["distance"] = distance
#                                 stationToNodeDistancesDict[stationKey]["closestNodes"] = []
#                             elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
#                                 stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                                 stationToNodeDistancesDict[stationKey]["distance"] = distance
#                             if(thresholdDistance > distance):
# #                                 print("Found a closest node", node, nodeIndex, "distance ", distance, "station", stationKey)
#                                 stationToNodeDistancesDict[stationKey]["closestNodes"].append(nodeIndex)
#                     else:
#                         badNodes.append(nodeIndex)
#                         print("bad node", nodeIndex, node)
#                 if(longitudeIndex % 100 == 0):
#                     print("longitudeIndex", longitudeIndex)
#                         
#         if(self.format == "FORT"):
#             numberOfNodes = dataset.variables["x"].shape[0]
#             for nodeIndex in range(numberOfNodes):
#         #     There are nodes in the gulf of mexico between node 400000 - 500000 for rivc1 map
#         #     for nodeIndex in range(100000):
#         #         nodeIndex = nodeIndex + 400000
#                 node = (float(dataset.variables["y"][nodeIndex].data), float(dataset.variables["x"][nodeIndex].data))
#                 if(node[0] <= 90 and node[0] >= -90):
#                     for stationKey in stationsDict["NOS"].keys():
#                         stationDict = stationsDict["NOS"][stationKey]
#                         stationCoordinates = (float(stationDict["latitude"]), float(stationDict["longitude"]))
#                         distance = haversine.haversine(stationCoordinates, node)
#                         if(len(stationToNodeDistancesDict[stationKey].keys()) == 0):
#                             stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                             stationToNodeDistancesDict[stationKey]["distance"] = distance
#                             stationToNodeDistancesDict[stationKey]["closestNodes"] = []
#                         elif(stationToNodeDistancesDict[stationKey]["distance"] > distance):
#                             stationToNodeDistancesDict[stationKey]["nodeIndex"] = nodeIndex
#                             stationToNodeDistancesDict[stationKey]["distance"] = distance
#                         if(thresholdDistance > distance):
# #                             print("Found a closest node", node, nodeIndex, "distance ", distance, "station", stationKey)
#                             stationToNodeDistancesDict[stationKey]["closestNodes"].append(nodeIndex)
#                 else:
#                     badNodes.append(nodeIndex)
#                     print("bad node", nodeIndex, node)
# #                 Print progress
#                 if(nodeIndex % 50000 == 0):
#                     print("nodeIndex", nodeIndex, node)

#         print("stationToNodeDistancesDict", stationToNodeDistancesDict)

        with open(self.STATION_TO_NODE_DISTANCES_FILE, "w") as outfile:
            json.dump(stationToNodeDistancesDict, outfile)
                
        with open(self.STATION_TO_NODE_DISTANCES_FILE) as outfile:
            stationToNodeDistancesDict = json.load(outfile)
        
        nodes = {"NOS": {}}
    
        for stationKey in stationToNodeDistancesDict.keys():
            stationToNodeDistanceDict = stationToNodeDistancesDict[stationKey]
            nodeIndex = stationToNodeDistanceDict["nodeIndex"]
            closestNodes = stationToNodeDistancesDict[stationKey]["closestNodes"]
#             nodes["NOS"][nodeIndex] = {}
#             nodes["NOS"][nodeIndex]["closestNodes"] = closestNodes
#             nodes["NOS"][nodeIndex]["stationKey"] = stationKey
            nodes["NOS"][stationKey] = {}
            nodes["NOS"][stationKey]["closestNodes"] = closestNodes
            nodes["NOS"][stationKey]["nodeIndex"] = nodeIndex
            if(self.format == "GFS" or self.format == "POST"):
                nodes["NOS"][stationKey]["latitude"] = float(dataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                nodes["NOS"][stationKey]["longitude"] = float(dataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
            if(self.format == "FORT"):
                nodes["NOS"][stationKey]["latitude"] = float(dataset.variables["y"][int(nodeIndex)].data)
                nodes["NOS"][stationKey]["longitude"] = float(dataset.variables["x"][int(nodeIndex)].data)
            
        with open(self.NODES_FILE, "w") as outfile:
            json.dump(nodes, outfile)
            
    
    
    def generateDataFiles(self, dataset, dataType, times, DATA_FILE):
    
        with open(self.NODES_FILE) as outfile:
            nodes = json.load(outfile)
            
        data = {}
        print("Reading data", dataType, flush=True)
        for stationKey in nodes["NOS"].keys():
#                 print("getting wind data for node", nodeIndex)
            data[stationKey] = {}
            nodeIndex = nodes["NOS"][stationKey]["nodeIndex"]
            data[stationKey]["nodeIndex"] = nodeIndex
            data[stationKey]["times"] = times
            if(self.format == "GFS" or self.format == "POST"):
                data[stationKey]["latitude"] = float(dataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                data[stationKey]["longitude"] = float(dataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
            elif(self.format == "FORT"):
                data[stationKey]["latitude"] = float(dataset.variables["y"][int(nodeIndex)].data)
                data[stationKey]["longitude"] = float(dataset.variables["x"][int(nodeIndex)].data)

            values = []
            valuesX = []
            valuesY = []
            # Bulk time-series read for gridded wind (avoid 265 separate netCDF gets)
            if dataType == "post" and self.format == "POST":
                ilat = self.extractLatitudeIndex(nodeIndex)
                ilon = self.extractLongitudeIndex(nodeIndex)
                print(f"  station {stationKey} cell ({ilat},{ilon})", flush=True)
                valuesX = np.asarray(dataset.variables["spd"][:, ilat, ilon], dtype=float).tolist()
                valuesY = np.asarray(dataset.variables["dir"][:, ilat, ilon], dtype=float).tolist()
            elif dataType == "gfs" and self.format == "GFS":
                ilat = self.extractLatitudeIndex(nodeIndex)
                ilon = self.extractLongitudeIndex(nodeIndex)
                valuesX = np.asarray(dataset.variables["wind_u"][:, ilat, ilon], dtype=float).tolist()
                valuesY = np.asarray(dataset.variables["wind_v"][:, ilat, ilon], dtype=float).tolist()
            else:
                for index in range(len(times)):
                    value = self.getValue(index, nodeIndex, dataType, dataset)
                    if(type(value) is float):
                        values.append(value)
                    else:
                        valuesX.append(value[0])
                        valuesY.append(value[1])

#           Write values
            if(dataType == "rad"):
                data[stationKey]["radstressX"] = valuesX
                data[stationKey]["radstressY"] = valuesY
            elif(dataType == "gfs" or dataType == "fort"):
                data[stationKey]["windsX"] = valuesX
                data[stationKey]["windsY"] = valuesY
            elif(dataType == "post"):
                data[stationKey]["speeds"] = valuesX
                data[stationKey]["directions"] = valuesY
            else:
                data[stationKey][dataType] = values
    
        with open(DATA_FILE, "w") as outfile:
            json.dump(data, outfile)
        
    def generateDataFilesWithInterpolation(self, dataset, dataType, times, spaceSparseness, timeSparseness, DATA_FILE):
        
        with open(self.NODES_FILE) as outfile:
            nodes = json.load(outfile)
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
            
        data = {}
        # Map frames → Grapher wind.gif / rain.gif / swath. Was hard-disabled (if False)
        # which left only station series. Re-enable for field maps; sparsify large GFS/PWM.
        if dataType in ("gfs", "post", "rain"):
            map_space = spaceSparseness
            map_time = timeSparseness
            if dataType == "gfs":
                # Full Atlantic PWM basin ~565×625; 3-hourly, every 3rd cell is enough for GIF
                map_space = max(spaceSparseness, 3)
                map_time = max(timeSparseness, 3)
            data = self.getMap(dataset, dataType, times, map_space, map_time, data)

        print("Interpolating", dataType, flush=True)
        nodesIndex = []
        points = []
        pointsValues = []
        pointsValuesX = []
        pointsValuesY = []
        # Optional distances (regular-grid path writes them) — skip far stations'
        # edge cells so a shared support cloud stays local (RICHAMP is RI-only).
        station_distances = {}
        try:
            with open(self.STATION_TO_NODE_DISTANCES_FILE) as _df:
                _dd = json.load(_df)
            for _sk, _rec in _dd.items():
                if isinstance(_rec, dict) and "distance" in _rec:
                    station_distances[_sk] = float(_rec["distance"])
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
        # RICHAMP post grid is fine (RI); GFS 0.25° nearest cell can be ~10–20 km away.
        # Using 5 km for GFS zeroed the support cloud and crashed Interp (0 unique points).
        if dataType == "gfs":
            MAX_STATION_GRID_KM = 50.0
        elif dataType == "post":
            MAX_STATION_GRID_KM = 5.0  # RI-only product: keep stencil local
        else:
            MAX_STATION_GRID_KM = 25.0
        for stationKey in nodes["NOS"].keys():
            print("Getting coordinates for closest nodes around station",  stationKey, flush=True)
#                 print("getting wind data for node", nodeIndex)
            # Coarse meshes (e.g. ec95d) often leave closestNodes empty while
            # nodeIndex is still set — fall back so interpolation has support.
            stencil = list(nodes["NOS"][stationKey].get("closestNodes") or [])
            if not stencil and nodes["NOS"][stationKey].get("nodeIndex") is not None:
                stencil = [nodes["NOS"][stationKey]["nodeIndex"]]
            d_station = station_distances.get(stationKey)
            if d_station is not None and d_station > MAX_STATION_GRID_KM:
                # Outside product domain (e.g. TX station on RI RICHAMP grid):
                # keep a single nearest for that station later, not global support.
                print(
                    f"  skip station {stationKey} for global stencil (d={d_station:.1f}km > {MAX_STATION_GRID_KM})",
                    flush=True,
                )
                continue
            for closestNode in stencil:
                nodesIndex.append(closestNode)
                x = 0.0
                y = 0.0
                if(self.format == "GFS" or self.format == "POST"):
                    x = float(dataset.variables["lon"][self.extractLongitudeIndex(closestNode)].data)
                    y = float(dataset.variables["lat"][self.extractLatitudeIndex(closestNode)].data)
                elif(self.format == "FORT"):
                    x = float(dataset.variables["x"][int(closestNode)].data)
                    y = float(dataset.variables["y"][int(closestNode)].data)
                point = (x, y)
                points.append(point)
        print("getting time series data for closest nodes", flush=True)
        values = self.getValuesForPoints(nodesIndex, dataType, dataset)
        if(dataType == "post" or dataType == "gfs" or dataType == "fort" or dataType == "rad"):
            pointsValuesX.extend(values[0])
            pointsValuesY.extend(values[1])
        else:
            pointsValues.extend(values)
#                 for index in range(len(times)):
# #                     print("getttingTime")
#                     value = self.getValue(index, closestNode, dataType, dataset)
#                     if(type(value) is float):
#                         values.append(value)
#                     else:
#                         valuesX.append(value[0])
#                         valuesY.append(value[1])
#                 pointsValues.append(values)
#                 pointsValuesX.append(valuesX)
#                 pointsValuesY.append(valuesY)
#             Interpolate values
        print("initializing interpolator", flush=True)
        # LinearND needs >= 3 unique points (4 with Qhull); use nearest otherwise.
        # LinearND also returns NaN *outside the convex hull* even with many points —
        # e.g. Providence (lat 41.81) north of northernmost stencil cell (41.75), or
        # Aransas outside the sparse TX edge. Always keep Nearest as fill for those.
        n_unique = len(set(points))
        use_nearest = n_unique < 4
        if use_nearest:
            print(f"Only {n_unique} unique support points; using NearestNDInterpolator", flush=True)
            Interp = scipy.interpolate.NearestNDInterpolator
        else:
            Interp = scipy.interpolate.LinearNDInterpolator
        vector_field = dataType in ("rad", "gfs", "fort", "post")
        if vector_field:
            interpolatorX = Interp(points, pointsValuesX)
            interpolatorY = Interp(points, pointsValuesY)
            nearestX = None if use_nearest else scipy.interpolate.NearestNDInterpolator(points, pointsValuesX)
            nearestY = None if use_nearest else scipy.interpolate.NearestNDInterpolator(points, pointsValuesY)
        else:
            interpolator = Interp(points, pointsValues)
            nearest = None if use_nearest else scipy.interpolate.NearestNDInterpolator(points, pointsValues)

        def _fill_outside_hull(primary, backup):
            """Replace LinearND outside-hull NaNs with nearest-neighbor values."""
            if backup is None:
                return primary
            arr = np.asarray(primary, dtype=float)
            if not np.any(np.isnan(arr)):
                return primary
            fill = np.asarray(backup, dtype=float)
            out = np.where(np.isnan(arr), fill, arr)
            n_filled = int(np.isnan(arr).sum())
            print(f"  filled {n_filled} outside-hull NaN(s) with nearest", flush=True)
            return out

        for stationKey in nodes["NOS"].keys():
            nodeIndex = nodes["NOS"][stationKey]["nodeIndex"]
            data[stationKey] = {}
            data[stationKey]["nodeIndex"] = nodeIndex
            latitude = ""
            longitude = ""
            if(self.format == "GFS" or self.format == "POST"):
                latitude = float(dataset.variables["lat"][self.extractLatitudeIndex(nodeIndex)].data)
                longitude = float(dataset.variables["lon"][self.extractLongitudeIndex(nodeIndex)].data)
            elif(self.format == "FORT"):
                latitude = float(dataset.variables["y"][int(nodeIndex)].data)
                longitude = float(dataset.variables["x"][int(nodeIndex)].data)
            data[stationKey]["latitude"] = latitude
            data[stationKey]["longitude"] = longitude
            data[stationKey]["times"] = times
            if(dataType == "rain"):
                stationDict = stationsDict["USGS"][stationKey]
            elif(dataType in ["swh", "mwd", "mwp", "pwp", "rad"]):
                stationDict = stationsDict["NDBC"][stationKey]   
            else:
                stationDict = stationsDict["NOS"][stationKey]
            stationLatitude = float(stationDict["latitude"])
            stationLongitude = float(stationDict["longitude"])
            stationCoordinates = (stationLongitude, stationLatitude)
            print("interpolating data for station", stationKey, "at", stationCoordinates, flush=True)
            if vector_field:
                interpolatedValuesX = interpolatorX(stationLongitude, stationLatitude)
                interpolatedValuesY = interpolatorY(stationLongitude, stationLatitude)
                if nearestX is not None:
                    interpolatedValuesX = _fill_outside_hull(
                        interpolatedValuesX, nearestX(stationLongitude, stationLatitude)
                    )
                    interpolatedValuesY = _fill_outside_hull(
                        interpolatedValuesY, nearestY(stationLongitude, stationLatitude)
                    )
            else:
                interpolatedValues = interpolator(stationLongitude, stationLatitude)
                if nearest is not None:
                    interpolatedValues = _fill_outside_hull(
                        interpolatedValues, nearest(stationLongitude, stationLatitude)
                    )
            if(dataType == "rad"):
                data[stationKey]["radstressX"] = interpolatedValuesX
                data[stationKey]["radstressY"] = interpolatedValuesY
            elif(dataType == "gfs" or dataType == "fort"):
                data[stationKey]["windsX"] = interpolatedValuesX
                data[stationKey]["windsY"] = interpolatedValuesY
            elif(dataType == "post"):
                data[stationKey]["speeds"] = interpolatedValuesX
                data[stationKey]["directions"] = interpolatedValuesY
            else:
                data[stationKey][dataType] = interpolatedValues
        
        print("Writing data to", DATA_FILE, flush=True)
        with open(DATA_FILE, "w") as outfile:
            json.dump(data, outfile, cls=NumpyEncoder)
        
    def generateDataFilesWithInterpolationForPoints(self, points, triangles, maskedTriangles, elevations, dataType, DATA_FILE):
        
        with open(self.NODES_FILE) as outfile:
            nodes = json.load(outfile)
        with open(self.STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)
            
        data = {}
        data = self.getMapWithPoints(points, triangles, maskedTriangles, elevations, dataType, data)
#                 
        print("Interpolating", dataType, flush=True)
        closestPoints = []
        nodesIndex = []
        pointsValues = []
        for stationKey in nodes["NOS"].keys():
            print("Getting coordinates for closest nodes around station",  stationKey, flush=True)
#                 print("getting wind data for node", nodeIndex)
            stencil = list(nodes["NOS"][stationKey].get("closestNodes") or [])
            if not stencil and nodes["NOS"][stationKey].get("nodeIndex") is not None:
                stencil = [nodes["NOS"][stationKey]["nodeIndex"]]
            for closestNode in stencil:
                nodesIndex.append(closestNode)
                x = 0.0
                y = 0.0
                x = float(points[0][int(closestNode)])
                y = float(points[1][int(closestNode)])
                point = (x, y)
                closestPoints.append(point)
        print("getting time series data for closest nodes", flush=True)
        for nodeIndex in nodesIndex:
            pointsValues.append(elevations[nodeIndex])
#                 for index in range(len(times)):
# #                     print("getttingTime")
#                     value = self.getValue(index, closestNode, dataType, dataset)
#                     if(type(value) is float):
#                         values.append(value)
#                     else:
#                         valuesX.append(value[0])
#                         valuesY.append(value[1])
#                 pointsValues.append(values)
#                 pointsValuesX.append(valuesX)
#                 pointsValuesY.append(valuesY)
#             Interpolate values
        print("initializing interpolator", flush=True)
        n_unique = len(set(closestPoints))
        if n_unique < 4:
            print(f"Only {n_unique} unique support points; using NearestNDInterpolator", flush=True)
            interpolator = scipy.interpolate.NearestNDInterpolator(closestPoints, pointsValues)
        else:
            interpolator = scipy.interpolate.LinearNDInterpolator(closestPoints, pointsValues)
        for stationKey in nodes["NOS"].keys():
            nodeIndex = nodes["NOS"][stationKey]["nodeIndex"]
            data[stationKey] = {}
            data[stationKey]["nodeIndex"] = nodeIndex
            latitude = 0.0
            longitude = 0.0
            latitude = float(points[1][int(nodeIndex)])
            longitude = float(points[0][int(nodeIndex)])
            data[stationKey]["latitude"] = latitude
            data[stationKey]["longitude"] = longitude
            if(dataType == "rain"):
                stationDict = stationsDict["USGS"][stationKey]
            elif(dataType in ["swh", "mwd", "mwp", "pwp", "rad"]):
                stationDict = stationsDict["NDBC"][stationKey]   
            elif(dataType == "elevation"):
                stationDict = stationsDict["ASSET"][stationKey]
            else:
                stationDict = stationsDict["NOS"][stationKey]
            stationLatitude = float(stationDict["latitude"])
            stationLongitude = float(stationDict["longitude"])
            stationCoordinates = (stationLongitude, stationLatitude)
            print("interpolating data for station", stationKey, "at", stationCoordinates, flush=True)
            interpolatedValues = interpolator(stationLongitude, stationLatitude)
            data[stationKey][dataType] = interpolatedValues
        
        print("Writing data to", DATA_FILE, flush=True)
        with open(DATA_FILE, "w") as outfile:
            json.dump(data, outfile, cls=NumpyEncoder)
         
class GFSRainReader:
    def __init__(self, GFS_RAIN_FILE="", STATIONS_FILE="", GFS_RAIN_DATA_FILE="", BACKGROUND_AXIS=[]):
        temp_directory = GFS_RAIN_DATA_FILE[0:GFS_RAIN_DATA_FILE.rfind("/") + 1]
        self.GFS_RAIN_FILE = GFS_RAIN_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "GFS_Station_To_Node_Distances.json"
        self.GFS_NODES_FILE = temp_directory + "GFS_Nodes.json"
        self.GFS_RAIN_DATA_FILE = GFS_RAIN_DATA_FILE
        self.GFS_NODES_WIND_DATA_FILE = temp_directory + "GFS_Nodes_Wind_Data.json"
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.GFS_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS, format="GFS")
    
    def generateRainDataForStations(self):
        print("Rain file", flush=True)
        print(self.GFS_RAIN_FILE, flush=True)
        rainDataset, timesRain = self.reader.getNetcdfProperties(self.GFS_RAIN_FILE, "rain")
        initializeClosestRainNodes = True
        if(initializeClosestRainNodes):
            thresholdDistance = 20
#             thresholdDistance = 100
            self.reader.initializeClosestNodes(rainDataset, thresholdDistance, "rain")
        interpolateValues = True
        spaceSparseness = 1
        timeSparseness = 1
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(rainDataset, "rain", timesRain, spaceSparseness, timeSparseness, self.GFS_RAIN_DATA_FILE)
        else:
            self.reader.generateDataFiles(rainDataset, "rain", timesRain, self.GFS_RAIN_DATA_FILE)
        return (datetime.fromtimestamp(timesRain[0], timezone.utc), datetime.fromtimestamp(timesRain[-1], timezone.utc))
            
class GFSWindReader:
    def __init__(self, GFS_WIND_FILE="", STATIONS_FILE="", GFS_WIND_DATA_FILE="", BACKGROUND_AXIS=[]):
        temp_directory = GFS_WIND_DATA_FILE[0:GFS_WIND_DATA_FILE.rfind("/") + 1]
        self.GFS_WIND_FILE = GFS_WIND_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "GFS_Station_To_Node_Distances.json"
        self.GFS_NODES_FILE = temp_directory + "GFS_Nodes.json"
        self.GFS_WIND_DATA_FILE = GFS_WIND_DATA_FILE
        self.GFS_NODES_WIND_DATA_FILE = temp_directory + "GFS_Nodes_Wind_Data.json"
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.GFS_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS, format="GFS")
    
    def generateWindDataForStations(self):
        print("Wind file", flush=True)
        print(self.GFS_WIND_FILE, flush=True)
        windDataset, timesWind = self.reader.getNetcdfProperties(self.GFS_WIND_FILE, "gfs")
        initializeClosestWindNodes = True
        if(initializeClosestWindNodes):
            thresholdDistance = 20
#             thresholdDistance = 100
#             Use higher threshold distance if working with 306 data?
#             thresholdDistance = 800
            self.reader.initializeClosestNodes(windDataset, thresholdDistance, "gfs")
        interpolateValues = True
        spaceSparseness = 1
        timeSparseness = 1
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(windDataset, "gfs", timesWind, spaceSparseness, timeSparseness, self.GFS_WIND_DATA_FILE)
        else:
            self.reader.generateDataFiles(windDataset, "gfs", timesWind, self.GFS_WIND_DATA_FILE)
        return (datetime.fromtimestamp(timesWind[0], timezone.utc), datetime.fromtimestamp(timesWind[-1], timezone.utc))
            
class Fort74Reader:
    def __init__(self, ADCIRC_WIND_FILE="", STATIONS_FILE="", ADCIRC_WIND_DATA_FILE="", BACKGROUND_AXIS=[]):
        temp_directory = ADCIRC_WIND_DATA_FILE[0:ADCIRC_WIND_DATA_FILE.rfind("/") + 1]
        self.ADCIRC_WIND_FILE = ADCIRC_WIND_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "ADCIRC_Station_To_Node_Distances.json"
        self.ADCIRC_NODES_FILE = temp_directory + "ADCIRC_Nodes.json"
        self.ADCIRC_WIND_DATA_FILE = ADCIRC_WIND_DATA_FILE
        self.ADCIRC_NODES_WIND_DATA_FILE = temp_directory + "ADCIRC_Nodes_Wind_Data.json"
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.ADCIRC_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS, format="FORT")
    
    def generateWindDataForStations(self):
        print("Wind file", flush=True)
        print(self.ADCIRC_WIND_FILE, flush=True)
        windDataset, timesWind = self.reader.getNetcdfProperties(self.ADCIRC_WIND_FILE, "fort")
        initializeClosestWindNodes = True
        if(initializeClosestWindNodes):
            thresholdDistance = 0.1
            self.reader.initializeClosestNodes(windDataset, thresholdDistance, "fort")
        spaceSparseness = 1
        timeSparseness = 1
        interpolateValues = True
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(windDataset, "fort", timesWind, spaceSparseness, timeSparseness, self.ADCIRC_WIND_DATA_FILE)
        else:
            self.reader.generateDataFiles(windDataset, "fort", timesWind, self.ADCIRC_WIND_DATA_FILE)
        return (datetime.fromtimestamp(timesWind[0], timezone.utc), datetime.fromtimestamp(timesWind[-1], timezone.utc))
  
class Fort63Reader:
    def __init__(self, ADCIRC_WATER_FILE="", STATIONS_FILE="", ADCIRC_WATER_DATA_FILE="", BACKGROUND_AXIS=[]):
        temp_directory = ADCIRC_WATER_DATA_FILE[0:ADCIRC_WATER_DATA_FILE.rfind("/") + 1]
        self.ADCIRC_WATER_FILE = ADCIRC_WATER_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "ADCIRC_Station_To_Node_Distances.json"
        self.ADCIRC_NODES_FILE = temp_directory + "ADCIRC_Nodes.json"
        self.ADCIRC_WATER_DATA_FILE = ADCIRC_WATER_DATA_FILE
        self.ADCIRC_NODES_WIND_DATA_FILE = temp_directory + "ADCIRC_Nodes_Water_Data.json"
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.ADCIRC_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS, format="FORT")
    
    def generateWindDataForStations(self):
        print("Water file", flush=True)
        print(self.ADCIRC_WATER_FILE, flush=True)
        waterDataset, timesWater = self.reader.getNetcdfProperties(self.ADCIRC_WATER_FILE, "water")
        initializeClosestWaterNodes = True
        if(initializeClosestWaterNodes):
#             thresholdDistance = 10
            # Mesh-density dependent (degrees-ish search radius for neighbor nodes):
            #   ricv1 dense coastal → small (0.1–0.25); v18 medium; ec95d coarse → larger
            #   or stations get few neighbors. ec95d graphs still not science-grade (mesh).
            # See run-adcirc skill S9d / research foundations §F.
            thresholdDistance = 0.25
            self.reader.initializeClosestNodes(waterDataset, thresholdDistance, "water")
        spaceSparseness = 1
#         spaceSparseness = 10
        timeSparseness = 1
        interpolateValues = True
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(waterDataset, "water", timesWater, spaceSparseness, timeSparseness, self.ADCIRC_WATER_DATA_FILE)
        else:
            self.reader.generateDataFiles(waterDataset, "water", timesWater, self.ADCIRC_WATER_DATA_FILE)
        return (datetime.fromtimestamp(timesWater[0], timezone.utc), datetime.fromtimestamp(timesWater[-1], timezone.utc))
                  
class PostWindReader:
    def __init__(self, POST_WIND_FILE="", STATIONS_FILE="", POST_WIND_DATA_FILE="", BACKGROUND_AXIS=[]):
        temp_directory = POST_WIND_DATA_FILE[0:POST_WIND_DATA_FILE.rfind("/") + 1]
        self.POST_WIND_FILE = POST_WIND_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "Post_Station_To_Node_Distances.json"
        self.POST_NODES_FILE = temp_directory + "Post_Nodes.json"
        self.POST_WIND_DATA_FILE = POST_WIND_DATA_FILE
        self.POST_NODES_WIND_DATA_FILE = temp_directory + "Post_Nodes_Wind_Data.json"
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.POST_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS, format="POST")
    
    def generateWindDataForStations(self):
        print("start, ", datetime.now(), flush=True)
        print("Wind file", flush=True)
        print(self.POST_WIND_FILE, flush=True)
        windDataset, timesWind = self.reader.getNetcdfProperties(self.POST_WIND_FILE, "post")
        initializeClosestWindNodes = True
        if(initializeClosestWindNodes):
            # km — NLCD RICHAMP ~30 m. Nearest cell is enough (d~0.02 km); multi-cell
            # LinearND forces multi-GB slab reads because RICHAMP.nc is time-chunked.
            thresholdDistance = 0.15
            #If working with post low res high altitude, the threshold distance needs to be increased
            #Because there is no longer a high density of points in the post wind
#             thresholdDistance = 20
            self.reader.initializeClosestNodes(windDataset, thresholdDistance, "post")
        # Nearest-node series only (not LinearND). 30 m grid + d≈0.02 km is denser
        # than GFS; avoid multi-point load of time-chunked 5+ GB files.
        interpolateValues = False
        spaceSparseness = 10
#         Uncomment for low res wind post generation
#         spaceSparseness = 1
        timeSparseness = 1
        if(interpolateValues):
            self.reader.generateDataFilesWithInterpolation(windDataset, "post", timesWind, spaceSparseness, timeSparseness, self.POST_WIND_DATA_FILE)
        else:
            self.reader.generateDataFiles(windDataset, "post", timesWind, self.POST_WIND_DATA_FILE)
        return (datetime.fromtimestamp(timesWind[0], timezone.utc), datetime.fromtimestamp(timesWind[-1], timezone.utc))
        print("end, ", datetime.now(), flush=True)
   
class Fort14Reader:
    def __init__(self, ADCIRC_MESH_FILE="", STATIONS_FILE="", ADCIRC_MESH_DATA_FILE="", BACKGROUND_AXIS=[]):
        temp_directory = ADCIRC_MESH_DATA_FILE[0:ADCIRC_MESH_DATA_FILE.rfind("/") + 1]
        self.ADCIRC_MESH_FILE = ADCIRC_MESH_FILE
        self.STATIONS_FILE = STATIONS_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "ADCIRC_Station_To_Node_Distances.json"
        self.ADCIRC_NODES_FILE = temp_directory + "ADCIRC_Nodes.json"
        self.ADCIRC_MESH_DATA_FILE = ADCIRC_MESH_DATA_FILE
        self.ADCIRC_NODES_MESH_DATA_FILE = temp_directory + "ADCIRC_Nodes_Mesh_Data.json"
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.ADCIRC_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS, format="FORT")
    
    def readMeshElevations(self):
        points = ([], [])
        elevations = []
        triangles = []
        maskedTriangles = []
        with open(self.ADCIRC_MESH_FILE) as file:
            lines = file.readlines()
            data = ((lines[1]).split())
            numberOfTriangles = int(data[0])
            numberOfPoints = int(data[1])
            print("Number of points", numberOfPoints)
            print("Number of triangles", numberOfTriangles)
#             quit()
            if(len(lines) > 0):
                startLine = 2
                endLine = 2+numberOfPoints
                print("reading points")
                for line in lines[startLine:endLine]:
                    data = line.split()
                    points[0].append(float(data[1]))
                    points[1].append(float(data[2]))
                    elevations.append(-1 * float(data[3]))
                startLine = endLine
                endLine = endLine + numberOfTriangles
#                 print(lines[startLine])
                print("reading triangles")
                for line in lines[startLine:endLine]:
                    data = line.split()
                    triangle = []
                    triangle.append(int(data[2]) - 1)
                    triangle.append(int(data[3]) - 1)
                    triangle.append(int(data[4]) - 1)
                    triangles.append(triangle)
                    point0 = [points[0][triangle[0]], points[1][triangle[0]]]
                    point1 = [points[0][triangle[1]], points[1][triangle[1]]]
                    point2 = [points[0][triangle[2]], points[1][triangle[2]]]
                    if(self.reader.isOutsideBackground(point0) or self.reader.isOutsideBackground(point1) or self.reader.isOutsideBackground(point2)):
                        maskedTriangles.append(True)
                    else:
                        maskedTriangles.append(False)
        return points, elevations, triangles, maskedTriangles
    
    def generateMeshDataForStations(self):
        print("Fort 14 file", flush=True)
        print(self.ADCIRC_MESH_FILE, flush=True)
        points, elevations, triangles, maskedTriangles = self.readMeshElevations()
#         waterDataset, timesWater = self.reader.getNetcdfProperties(self.ADCIRC_WATER_FILE, "water")
        initializeClosestMeshNodes = True
#         Interpolates elevation data according to available stations for below dataType
        dataType = "elevation"
        if(initializeClosestMeshNodes):
            thresholdDistance = 3
#             thresholdDistance = 1
            self.reader.initializeClosestNodesForPoints(points, thresholdDistance, dataType)
        self.reader.generateDataFilesWithInterpolationForPoints(points, triangles, maskedTriangles, elevations, dataType, self.ADCIRC_MESH_DATA_FILE)

class WaveReader:
    def __init__(
        self,
        WAVE_SWH_FILE="",
        WAVE_MWD_FILE="",
        WAVE_MWP_FILE="",
        WAVE_PWP_FILE="",
        WAVE_RAD_FILE="",
        STATIONS_FILE="", 
        WAVE_SWH_DATA_FILE="",
        WAVE_MWD_DATA_FILE="",
        WAVE_MWP_DATA_FILE="",
        WAVE_PWP_DATA_FILE="",
        WAVE_RAD_DATA_FILE="", 
        BACKGROUND_AXIS=[]):
        temp_directory = WAVE_SWH_DATA_FILE[0:WAVE_SWH_DATA_FILE.rfind("/") + 1]
        self.WAVE_SWH_FILE=WAVE_SWH_FILE
        self.WAVE_MWD_FILE=WAVE_MWD_FILE
        self.WAVE_MWP_FILE=WAVE_MWP_FILE
        self.WAVE_PWP_FILE=WAVE_PWP_FILE
        self.WAVE_RAD_FILE=WAVE_RAD_FILE
        self.WAVE_SWH_DATA_FILE=WAVE_SWH_DATA_FILE
        self.WAVE_MWD_DATA_FILE=WAVE_MWD_DATA_FILE
        self.WAVE_MWP_DATA_FILE=WAVE_MWP_DATA_FILE
        self.WAVE_PWP_DATA_FILE=WAVE_PWP_DATA_FILE
        self.WAVE_RAD_DATA_FILE=WAVE_RAD_DATA_FILE
        self.STATION_TO_NODE_DISTANCES_FILE = temp_directory + "Wave_Station_To_Node_Distances.json"
        self.WAVE_NODES_FILE = temp_directory + "Wave_Nodes.json"
        self.BACKGROUND_AXIS = BACKGROUND_AXIS
        self.reader = Reader(STATIONS_FILE=STATIONS_FILE, STATION_TO_NODE_DISTANCES_FILE=self.STATION_TO_NODE_DISTANCES_FILE, NODES_FILE=self.WAVE_NODES_FILE, BACKGROUND_AXIS=self.BACKGROUND_AXIS, format="FORT")
    
    def generateWaveDataForStations(self):
        print("Wave files", flush=True)
        print(self.WAVE_SWH_FILE, flush=True)
        print(self.WAVE_MWD_FILE, flush=True)
        print(self.WAVE_MWP_FILE, flush=True)
        print(self.WAVE_PWP_FILE, flush=True)
        print(self.WAVE_RAD_FILE, flush=True)
        swhExists = True
        mwdExists = True
        mwpExists = True
        pwpExists = True
        radExists = True
        if(self.WAVE_SWH_FILE == ""):
            swhExists = False
        if(self.WAVE_MWD_FILE == ""):
            mwdExists = False
        if(self.WAVE_MWP_FILE == ""):
            mwpExists = False
        if(self.WAVE_PWP_FILE == ""):
            pwpExists = False
        if(self.WAVE_RAD_FILE == ""):
            radExists = False
        if(swhExists):
            swhDataset, timesSWH = self.reader.getNetcdfProperties(self.WAVE_SWH_FILE, "swh")
            dataset = swhDataset
            times = timesSWH
        if(mwdExists):
            mwdDataset, timesMWD = self.reader.getNetcdfProperties(self.WAVE_MWD_FILE, "mwd")
            dataset = mwdDataset
            times = timesMWD
        if(mwpExists):
            mwpDataset, timesMWP = self.reader.getNetcdfProperties(self.WAVE_MWP_FILE, "mwp")
            dataset = mwpDataset
            times = timesMWP
        if(pwpExists):
            pwpDataset, timesPWP = self.reader.getNetcdfProperties(self.WAVE_PWP_FILE, "pwp")
            dataset = pwpDataset
            times = timesPWP
        if(radExists):
            radDataset, timesRAD = self.reader.getNetcdfProperties(self.WAVE_RAD_FILE, "rad")
            datset = radDataset
            times = timesRAD
#         timesEqual = True
#         if(timesSWH == timesMWD == timesMWP == timesPWP == timesRAD):
#             timesEqual = True
#         if(timesEqual):
        spaceSparseness = 1
        timeSparseness = 1
        initializeClosestWaveNodes = True
        if(initializeClosestWaveNodes):
            # Mesh-density dependent — larger than water default so coarse meshes still
            # find neighbors. ricv1 should use a *small* value; v18 medium; ec95d large.
            # Water Fort63Reader often uses ~0.25 while waves use 7 → different node sets.
            # ec95d: post "works" but station series can look bad (resolution, not only thr).
            # See run-adcirc skill S9d / research foundations §F.
            thresholdDistance = 7
#             thresholdDistance = 
            self.reader.initializeClosestNodes(swhDataset, thresholdDistance, "swh")
        interpolateValues = True
        if(interpolateValues):
            if(swhExists):
                self.reader.generateDataFilesWithInterpolation(swhDataset, "swh", timesSWH, spaceSparseness, timeSparseness, self.WAVE_SWH_DATA_FILE)
            if(mwdExists):
                self.reader.generateDataFilesWithInterpolation(mwdDataset, "mwd", timesMWD, spaceSparseness, timeSparseness, self.WAVE_MWD_DATA_FILE)
            if(mwpExists):
                self.reader.generateDataFilesWithInterpolation(mwpDataset, "mwp", timesMWP, spaceSparseness, timeSparseness, self.WAVE_MWP_DATA_FILE)
            if(pwpExists):
                self.reader.generateDataFilesWithInterpolation(pwpDataset, "pwp", timesSWH, spaceSparseness, timeSparseness, self.WAVE_PWP_DATA_FILE)
            if(radExists):
                self.reader.generateDataFilesWithInterpolation(radDataset, "rad", timesSWH, spaceSparseness, timeSparseness, self.WAVE_RAD_DATA_FILE)
        else:
            self.reader.generateDataFiles(swhDataset, "swh", timesSWH, self.WAVE_SWH_DATA_FILE)
            self.reader.generateDataFiles(mwdDataset, "mwd", timesSWH, self.WAVE_MWD_DATA_FILE)
            self.reader.generateDataFiles(mwpDataset, "mwp", timesSWH, self.WAVE_MWP_DATA_FILE)
            self.reader.generateDataFiles(pwpDataset, "pwp", timesSWH, self.WAVE_PWP_DATA_FILE)
            self.reader.generateDataFiles(radDataset, "rad", timesSWH, self.WAVE_RAD_DATA_FILE)
        return (datetime.fromtimestamp(times[0], timezone.utc), datetime.fromtimestamp(times[-1], timezone.utc))
