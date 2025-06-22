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
        GEOID_URL = "https://geodesy.noaa.gov/api/geoid/ght"
        temp_directory = OBS_ASSET_DATA_FILE[0:OBS_ASSET_DATA_FILE.rfind("/") + 1]
        BATHYMETRY_FILE = os.path.join(temp_directory, "bathymetry.txt")

        # Load stations data
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)

        # Cache for geoid heights to avoid duplicate API calls
        self.geoid_cache = {}

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

        # Query NGS Geoid API for geoid height
        def get_geoid_height(lat, lon, model="GEOID18"):
            cache_key = (round(lat, 6), round(lon, 6))
            if cache_key in self.geoid_cache:
                return self.geoid_cache[cache_key]

            try:
                params = {
                    "lat": lat,
                    "lon": lon,
                    "model": model
                }
                response = requests.get(GEOID_URL, params=params, timeout=5)
                if response.status_code != 200:
                    raise Exception(f"Geoid API error: Status code {response.status_code}")
                data = response.json()
                geoid_height = float(data["geoidHeight"])
                error = float(data["error"])
                print(f"Geoid height for ({lat:.6f}, {lon:.6f}): {geoid_height:.3f} m (error: {error:.3f} m)")
                self.geoid_cache[cache_key] = geoid_height
                return geoid_height
            except Exception as e:
                print(f"Failed to fetch geoid height for ({lat:.6f}, {lon:.6f}): {e}. Using default 0.0 m.")
                self.geoid_cache[cache_key] = 0.0
                return 0.0

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
                print(f"Warning: Station {key} missing or invalid latitude/longitude. Assigning NaN elevation.")
                continue

        if not lats or not lons:
            raise ValueError("No valid station coordinates found in STATIONS_FILE for bathymetry query.")

        # Define bathymetry bounding box with 0.1-degree padding
        bathy_padding = 0.1
        bathy_north = max(lats) + bathy_padding
        bathy_south = min(lats) - bathy_padding
        bathy_east = max(lons) + bathy_padding
        bathy_west = min(lons) - bathy_padding

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
                return np.nan
            grid = np.ma.masked_invalid(grid) if not np.ma.is_masked(grid) else grid
            try:
                interpolator = RegularGridInterpolator((Y, X), grid, method=method, bounds_error=False, fill_value=None)
                value = interpolator(np.flip(point))  # Flip point since interpolator expects (y,x)
                return float(value) if not np.ma.is_masked(value) else np.nan
            except ValueError as e:
                print(f"Interpolation error at point {point}: {e}")
                return np.nan

        def filterElevation(elevation, lat, lon, station_key):
            """
            Convert GEBCO bathymetry depths (positive downward, MSL) to NAVD88 elevations and cap outliers:
            - Depths below -50 meters are set to -10 meters.
            - Heights above 1000 meters are set to 10 meters.
            """
            if np.isnan(elevation):
                print(f"Station {station_key}: Elevation is NaN, returning NaN")
                return np.nan

            # GEBCO depth (positive downward) to MSL elevation (negative for depths)
            elevation_msl = -elevation
            print(f"Station {station_key}: Raw GEBCO depth {elevation:.3f} m, MSL elevation {elevation_msl:.3f} m")

            # Convert to NAVD88 using geoid height
            geoid_height = get_geoid_height(lat, lon)
            elevation_navd88 = elevation_msl + geoid_height
            print(f"Station {station_key}: Geoid height {geoid_height:.3f} m, NAVD88 elevation {elevation_navd88:.3f} m")

            # Apply outlier filter
            if elevation_navd88 < -50:
                print(f"Station {station_key}: NAVD88 elevation {elevation_navd88:.3f} m capped at -10.0 m")
                return -10.0
            if elevation_navd88 > 1000:
                print(f"Station {station_key}: NAVD88 elevation {elevation_navd88:.3f} m capped at 10.0 m")
                return 10.0
            print(f"Station {station_key}: Final NAVD88 elevation {elevation_navd88:.3f} m")
            return float(elevation_navd88)

        def readBathymetryData():
            try:
                with open(BATHYMETRY_FILE, 'r') as file:
                    lines = file.readlines()
                    longitudeDelta = int(lines[0][13::].strip())
                    latitudeDelta = int(lines[1][13::].strip())
                    minLongitude = float(lines[2][13::].strip())
                    minLatitude = float(lines[3][13::].strip())
                    coordinateDelta = float(lines[4][13::].strip())
                    noDataValue = float(lines[5][13::].strip())

                    maxLongitude = minLongitude + (longitudeDelta * coordinateDelta)
                    maxLatitude = minLatitude + (latitudeDelta * coordinateDelta)

                    longitudes = np.linspace(minLongitude, maxLongitude, longitudeDelta)
                    latitudes = np.linspace(maxLatitude, minLatitude, latitudeDelta)

                    bathymetryValues = []
                    for line in lines[6::]:
                        data = np.array(line.split(), dtype=float)
                        bathymetryValues.append(data)
                    bathymetryValues = np.ma.masked_equal(bathymetryValues, noDataValue)
                    return np.array(bathymetryValues), np.array(latitudes), np.array(longitudes)
            except Exception as e:
                print(f"Error reading bathymetry data: {e}")
                return None, None, None

        # Download bathymetry data once
        bathy_success = downloadBathymetryData(bathy_north, bathy_south, bathy_east, bathy_west)
        bathymetryValues, bathy_latitudes, bathy_longitudes = (None, None, None)
        if bathy_success:
            bathymetryValues, bathy_latitudes, bathy_longitudes = readBathymetryData()

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
                continue

            elevationDict[key] = {}
            elevation = np.nan

            # Use bathymetry data if available
            if bathy_success and bathymetryValues is not None:
                elevation = InterpolatePoint(bathymetryValues, bathy_latitudes, bathy_longitudes, (lon, lat))

            # Apply elevation filter with NAVD88 conversion
            elevationDict[key]["elevation"] = filterElevation(elevation, lat, lon, key)

        # Ensure all stations are in output
        for key in stationsDict["ASSET"].keys():
            if key not in elevationDict:
                elevationDict[key] = {"elevation": np.nan}

        # Log performance metrics
        print(f"\nCompleted in {time.time() - start_time:.2f} seconds. Made 0 topography API calls, 1 bathymetry API call, and {len(self.geoid_cache)} geoid API calls for {len(stationsDict['ASSET'])} stations.")

        # Save to output file
        with open(OBS_ASSET_DATA_FILE, "w") as outfile:
            json.dump(elevationDict, outfile)