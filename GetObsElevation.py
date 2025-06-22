import json
import requests
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import os
import time
import threading
import sys
import itertools

# Toggle to bypass topography API calls
BYPASS_TOPOGRAPHY = True

class GetObsElevation:
    def __init__(self, STATIONS_FILE="", OBS_ASSET_DATA_FILE=""):
        start_time = time.time()
        # Initialize API endpoints and parameters
        BASE_URL = "https://portal.opentopography.org/API/globaldem"
        temp_directory = OBS_ASSET_DATA_FILE[0:OBS_ASSET_DATA_FILE.rfind("/") + 1]
        BATHYMETRY_FILE = os.path.join(temp_directory, "bathymetry.txt")

        # Load stations data
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)

        # Loading animation
        def loading_animation(message, stop_event):
            spinner = itertools.cycle(['|', '/', '-', '\\'])
            sys.stdout.write(message)
            sys.stdout.flush()
            while not stop_event.is_set():
                sys.stdout.write(next(spinner))
                sys.stdout.flush()
                time.sleep(0.1)
                sys.stdout.write('\b')
                sys.stdout.flush()
            sys.stdout.write('\b')  # Clear spinner
            sys.stdout.flush()

        # Progress bar
        def print_progress_bar(progress, total, width=20):
            percent = progress / total * 100
            filled = int(width * progress // total)
            bar = '=' * filled + '-' * (width - filled)
            sys.stdout.write(f'\r[{bar}] {percent:.1f}%')
            sys.stdout.flush()

        # Determine bathymetry bounding box (all points)
        lats = []
        lons = []
        for key in stationsDict["ASSET"].keys():
            stationDict = stationsDict["ASSET"][key]
            try:
                lat = float(stationDict["latitude"])
                lon = float(stationDict["longitude"])
                lats.append(lat)
                lons.append(lon)
            except (KeyError, ValueError):
                print(f"Warning: Station {key} missing or invalid latitude/longitude. Assigning elevation NaN.")
                continue

        if not lats or not lons:
            print("Warning: No valid coordinates found. Bathymetry query skipped.")
            bathy_success = False
        else:
            # Define bathymetry bounding box with 0.1-degree padding
            bathy_padding = 0.1
            bathy_north = max(lats) + bathy_padding
            bathy_south = min(lats) - bathy_padding
            bathy_east = max(lons) + bathy_padding
            bathy_west = min(lons) - bathy_padding
            bathy_success = True

        # Download bathymetry data
        def downloadBathymetryData(north, south, east, west, dem_type="GEBCOIceTopo", output_format="AAIGrid", api_key="6dd04fe1048e9dfbfc6652feb1b733b1"):
            lat_delta = north - south
            lon_delta = east - west
            print(f"\nBathymetry API call: Bounding box (west={west:.6f}, south={south:.6f}, east={east:.6f}, north={north:.6f})")
            print(f"Lat delta: {lat_delta:.6f} degrees, Lon delta: {lon_delta:.6f} degrees")

            stop_event = threading.Event()
            animation_thread = threading.Thread(target=loading_animation, args=("Querying bathymetry API... ", stop_event))
            animation_thread.start()

            try:
                params = {
                    "demtype": dem_type,
                    "south": south,
                    "north": north,
                    "west": west,
                    "east": east,
                    "outputFormat": output_format,
                    "API_Key": api_key
                }
                start_dl_time = time.time()
                response = requests.get(BASE_URL, params=params, stream=True)
                if response.status_code != 200:
                    raise Exception(f"Failed with status code: {response.status_code}")

                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                chunk_size = 8192

                with open(BATHYMETRY_FILE, "wb") as file:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            if total_size > 0:
                                print_progress_bar(downloaded_size, total_size)
                sys.stdout.write('\n')

                dl_time = time.time() - start_dl_time
                dl_speed = (downloaded_size / 1024) / dl_time if dl_time > 0 else 0
                if dl_speed > 1024:
                    print(f"Bathymetry download speed: {dl_speed/1024:.2f} MB/s")
                else:
                    print(f"Bathymetry download speed: {dl_speed:.2f} KB/s")
                print(f"Bathymetry API call succeeded.")
                return True
            except Exception as e:
                print(f"Bathymetry API error: {e}")
                return False
            finally:
                stop_event.set()
                animation_thread.join()

        def InterpolatePoint(grid, Y, X, point, method='linear'):
            if grid.size == 0:
                print(f"Interpolation failed for point {point}: Empty grid")
                return np.nan
            grid = np.ma.masked_invalid(grid) if not np.ma.is_masked(grid) else grid
            try:
                interpolator = RegularGridInterpolator((Y, X), grid, method=method, bounds_error=False, fill_value=np.nan)
                value = interpolator(np.flip(point))  # Flip point since interpolator expects (y,x)
                value_float = float(value) if not np.ma.is_masked(value) and not np.isnan(value) else np.nan
                print(f"Interpolated depth at {point}: {value_float:.3f} m" if not np.isnan(value_float) else f"Interpolated depth at {point}: NaN")
                return value_float
            except ValueError as e:
                print(f"Interpolation error at point {point}: {e}")
                return np.nan

        def filterElevation(elevation, station_key):
            """
            Filter elevation values to handle outliers:
            - Depths below -100 meters or heights above 1000 meters are set to NaN.
            - Keep NaN for invalid elevations.
            """
            if np.isnan(elevation):
                print(f"Station {station_key}: Elevation is NaN")
                return np.nan
            if elevation < -100:
                print(f"Station {station_key}: Elevation {elevation:.3f} m set to NaN (below -100 m)")
                return np.nan
            if elevation > 1000:
                print(f"Station {station_key}: Elevation {elevation:.3f} m set to NaN (above 1000 m)")
                return np.nan
            print(f"Station {station_key}: Final elevation {elevation:.3f} m")
            return float(elevation)

        def readBathymetryData():
            try:
                with open(BATHYMETRY_FILE, 'r') as file:
                    lines = file.readlines()
                    longitudeDelta = int(lines[0][13:].strip())
                    latitudeDelta = int(lines[1][13:].strip())
                    minLongitude = float(lines[2][13:].strip())
                    minLatitude = float(lines[3][13:].strip())
                    coordinateDelta = float(lines[4][13:].strip())
                    noDataValue = float(lines[5][13:].strip())

                    maxLongitude = minLongitude + (longitudeDelta * coordinateDelta)
                    maxLatitude = minLatitude + (latitudeDelta * coordinateDelta)

                    longitudes = np.linspace(minLongitude, maxLongitude, longitudeDelta)
                    latitudes = np.linspace(maxLatitude, minLatitude, latitudeDelta)  # Descending order

                    bathymetryValues = []
                    for line in lines[6:]:
                        data = np.array(line.split(), dtype=float)
                        bathymetryValues.append(data)
                    bathymetryValues = np.array(bathymetryValues)
                    bathymetryValues = np.ma.masked_equal(bathymetryValues, noDataValue)
                    print(f"Bathymetry grid shape: {bathymetryValues.shape}, sample value: {bathymetryValues[0,0]:.3f} m, min: {np.min(bathymetryValues):.3f} m, max: {np.max(bathymetryValues):.3f} m")
                    return bathymetryValues, latitudes, longitudes
            except Exception as e:
                print(f"Error reading bathymetry data: {e}")
                return None, None, None

        # Download bathymetry data if valid coordinates exist
        bathymetryValues, bathy_latitudes, bathy_longitudes = (None, None, None)
        if bathy_success:
            bathy_success = downloadBathymetryData(bathy_north, bathy_south, bathy_east, bathy_west)
            if bathy_success:
                bathymetryValues, bathy_latitudes, bathy_longitudes = readBathymetryData()
            else:
                print("Warning: Bathymetry download failed. Elevations will be NaN where not found.")

        # Initialize output dictionary
        elevationDict = {}

        # Process each station
        for key in stationsDict["ASSET"].keys():
            stationDict = stationsDict["ASSET"][key]
            try:
                lat = float(stationDict["latitude"])
                lon = float(stationDict["longitude"])
            except (KeyError, ValueError):
                elevationDict[key] = {"elevation": np.nan}
                print(f"Station {key}: Invalid coordinates, elevation set to NaN")
                continue

            elevation = np.nan

            # Use bathymetry data if available
            if bathy_success and bathymetryValues is not None:
                elevation = InterpolatePoint(bathymetryValues, bathy_latitudes, bathy_longitudes, (lon, lat))

            # Apply elevation filter
            elevationDict[key] = {"elevation": filterElevation(elevation, key)}

        # Log performance metrics
        print(f"\nCompleted in {time.time() - start_time:.2f} seconds. Made 0 topography API calls, {'1' if bathy_success else '0'} bathymetry API call for {len(stationsDict['ASSET'])} stations.")

        # Save to output file
        with open(OBS_ASSET_DATA_FILE, "w") as outfile:
            json.dump(elevationDict, outfile, allow_nan=True)