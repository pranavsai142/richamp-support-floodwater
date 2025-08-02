import json
import requests
import numpy as np
from scipy.interpolate import RegularGridInterpolator
import os
import time
import threading
import sys
import itertools
import matplotlib.pyplot as plt
from pyproj import Transformer

# Define topography file
TOPOGRAPHY_FILE = "topography.txt"

# Toggle to bypass topography API calls
BYPASS_TOPOGRAPHY = True

class GetObsElevation:
    def __init__(self, STATIONS_FILE="", OBS_ASSET_DATA_FILE=""):
        start_time = time.time()
        # Initialize API endpoints and parameters
        BASE_URL = "https://portal.opentopography.org/API/globaldem"
        temp_directory = OBS_ASSET_DATA_FILE[0:OBS_ASSET_DATA_FILE.rfind("/") + 1]
        BATHYMETRY_FILE = os.path.join(temp_directory, "bathymetry.txt")

        # Coordinate transformation (UTM Zone 19N to WGS84 for plotting, WGS84 to UTM for interpolation)
        utm_to_wgs84 = Transformer.from_crs("EPSG:32619", "EPSG:4326", always_xy=True)  # UTM Zone 19N to WGS84
        wgs84_to_utm = Transformer.from_crs("EPSG:4326", "EPSG:32619", always_xy=True)  # WGS84 to UTM Zone 19N

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

        # Read raster data (for both bathymetry and topography)
        def readRasterData(file_path, is_bathymetry=False):
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()
                    if len(lines) < 6:
                        print(f"Error reading {file_path}: Too few lines.")
                        return None, None, None, None, None, None, None
                    longitudeDelta = int(lines[0][13:].strip())
                    latitudeDelta = int(lines[1][13:].strip())
                    minLongitude = float(lines[2][13:].strip())
                    minLatitude = float(lines[3][13:].strip())
                    coordinateDelta = float(lines[4][13:].strip())
                    noDataValue = float(lines[5][13:].strip())

                    maxLongitude = minLongitude + (longitudeDelta * coordinateDelta)
                    maxLatitude = minLatitude + (latitudeDelta * coordinateDelta)

                    if len(lines) < 6 + latitudeDelta:
                        print(f"Error reading {file_path}: Insufficient data lines ({len(lines)-6} vs {latitudeDelta}).")
                        return None, None, None, None, None, None, None

                    longitudes = np.linspace(minLongitude, maxLongitude, longitudeDelta)
                    latitudes = np.linspace(maxLatitude, minLatitude, latitudeDelta)  # Descending order

                    values = []
                    for line in lines[6:]:
                        data = np.array(line.split(), dtype=float)
                        if len(data) != longitudeDelta:
                            print(f"Error reading {file_path}: Line {len(values)+7} has {len(data)} values, expected {longitudeDelta}.")
                            return None, None, None, None, None, None, None
                        values.append(data)
                    values = np.array(values)
                    # Flip topography data to align with bathymetry and negate to treat as negative depth
                    if not is_bathymetry:
                        values = np.flipud(values)  # Flip vertically to align orientation
                        values = -values  # Convert positive elevation to negative depth
                    # Bathymetry is already positive depth (negative downward)
                    # Mask NODATA values
                    values = np.ma.masked_equal(values, noDataValue)
                    # Verify grid
                    if values.size == 0 or np.all(values.mask):
                        print(f"Error reading {file_path}: Grid is empty or all values are masked.")
                        return None, None, None, None, None, None, None
                    print(f"{file_path} grid shape: {values.shape}, sample value: {values[0,0]:.3f} m, min: {np.min(values):.3f} m, max: {np.max(values):.3f} m")
                    return values, latitudes, longitudes, minLongitude, maxLongitude, minLatitude, maxLatitude
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                return None, None, None, None, None, None, None

        # Check if point is within grid bounds
        def is_within_bounds(lon, lat, min_lon, max_lon, min_lat, max_lat):
            tolerance = 1e-6
            return (min_lon - tolerance <= lon <= max_lon + tolerance and
                    min_lat - tolerance <= lat <= max_lat + tolerance)

        # Interpolate depth at a point
        def InterpolatePoint(grid, Y, X, point, method='linear'):
            if grid is None or grid.size == 0:
                print(f"Interpolation failed for point {point}: Empty grid")
                return np.nan
            grid = np.ma.masked_invalid(grid) if not np.ma.is_masked(grid) else grid
            try:
                interpolator = RegularGridInterpolator((Y, X), grid, method=method, bounds_error=False, fill_value=np.nan)
                value = interpolator(point)  # Use (northing, easting) or (lat, lon) based on grid
                value_float = float(value) if not np.ma.is_masked(value) and not np.isnan(value) else np.nan
                print(f"Interpolated {'depth (bathymetry)' if grid is bathymetryValues else 'depth (topography)'} at {point}: {value_float:.3f} m" if not np.isnan(value_float) else f"Interpolated {'depth (bathymetry)' if grid is bathymetryValues else 'depth (topography)'} at {point}: NaN")
                return value_float
            except ValueError as e:
                print(f"Interpolation error at point {point}: {e}")
                return np.nan

        # Filter depth values
        def filterElevation(depth, station_key):
            """
            Filter depth values to handle outliers:
            - Depths below -100 meters or heights above 1000 meters are set to NaN.
            - Keep NaN for invalid depths.
            - Output is elevation (positive upward) for JSON compatibility.
            """
            if np.isnan(depth):
                print(f"Station {station_key}: Depth is NaN")
                return np.nan
            if depth < -100:
                print(f"Station {station_key}: Depth {depth:.3f} m set to NaN (below -100 m)")
                return np.nan
            if depth > 1000:
                print(f"Station {station_key}: Depth {depth:.3f} m set to NaN (above 1000 m)")
                return np.nan
            elevation = -depth  # Convert negative depth to positive elevation for JSON
            print(f"Station {station_key}: Final elevation {elevation:.3f} m")
            return float(elevation)

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

        # Plot heatmap of depth data in lat/lon
        def plot_heatmap(values, latitudes, longitudes, title, filename, is_projected=False):
            if values is None or np.all(values.mask):
                print(f"Cannot plot {filename}: No valid data available.")
                return
            plt.figure(figsize=(10, 8), dpi=300)
            # If projected (topography), convert UTM to lat/lon
            if is_projected:
                lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)
                lon_grid, lat_grid = utm_to_wgs84.transform(lon_grid, lat_grid)
            else:
                lon_grid, lat_grid = np.meshgrid(longitudes, latitudes)
            # Mask NODATA values explicitly for plotting
            plot_values = np.ma.masked_equal(values, -999999, copy=True)
            plt.pcolormesh(lon_grid, lat_grid, plot_values, cmap='terrain', shading='auto')
            plt.colorbar(label='meters')
            plt.title(title)
            plt.xlabel('Longitude (degrees)')
            plt.ylabel('Latitude (degrees)')
            plt.savefig(filename, bbox_inches='tight')
            print(f"Saved plot: {filename}")
            plt.close()

        # Determine bounding box (all points)
        lats = []
        lons = []
        for key in stationsDict["ASSET"].keys():
            stationDict = stationsDict["ASSET"][key]
            try:
                lat = float(stationDict["latitude"])
                lon = float(stationDict["longitude"])
                # Basic coordinate validation
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    print(f"Warning: Station {key} has invalid coordinates (lat={lat}, lon={lon}). Assigning elevation NaN.")
                    continue
                lats.append(lat)
                lons.append(lon)
            except (KeyError, ValueError):
                print(f"Warning: Station {key} missing or invalid latitude/longitude. Assigning elevation NaN.")
                continue

        if not lats or not lons:
            print("Warning: No valid coordinates found. Data queries skipped.")
            bathy_success = False
            topo_success = False
            bathy_called = False
        else:
            # Define bounding box with 0.1-degree padding
            padding = 0.1
            north = max(lats) + padding
            south = min(lats) - padding
            east = max(lons) + padding
            west = min(lons) - padding
            bathy_success = True
            topo_success = True
            bathy_called = False

        # Read topography data (always assume file exists)
        topographyValues, topo_latitudes, topo_longitudes, topo_min_lon, topo_max_lon, topo_min_lat, topo_max_lat = readRasterData(TOPOGRAPHY_FILE, is_bathymetry=False)
        if topographyValues is None:
            topo_success = False
            print(f"Warning: Topography data unavailable from {TOPOGRAPHY_FILE}. Elevations may rely on bathymetry only.")
        else:
            print(f"Topography bounds: (west={topo_min_lon:.6f}, south={topo_min_lat:.6f}, east={topo_max_lon:.6f}, north={topo_max_lat:.6f})")

        # Download and read bathymetry data
        bathymetryValues, bathy_latitudes, bathy_longitudes, bathy_min_lon, bathy_max_lon, bathy_min_lat, bathy_max_lat = (None, None, None, None, None, None, None)
        if bathy_success:
            bathy_success = downloadBathymetryData(north, south, east, west)
            bathy_called = True
            if bathy_success:
                bathymetryValues, bathy_latitudes, bathy_longitudes, bathy_min_lon, bathy_max_lon, bathy_min_lat, bathy_max_lat = readRasterData(BATHYMETRY_FILE, is_bathymetry=True)
            else:
                print("Warning: Bathymetry data unavailable. Elevations may rely on topography only.")

        # Initialize output dictionary
        elevationDict = {}

        # Process each station
        for key in stationsDict["ASSET"].keys():
            stationDict = stationsDict["ASSET"][key]
            try:
                lat = float(stationDict["latitude"])
                lon = float(stationDict["longitude"])
                # Basic coordinate validation
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    print(f"Warning: Station {key} has invalid coordinates (lat={lat}, lon={lon}). Assigning elevation NaN.")
                    elevationDict[key] = {"elevation": np.nan}
                    continue
            except (KeyError, ValueError):
                print(f"Warning: Station {key} missing or invalid latitude/longitude. Assigning elevation NaN.")
                elevationDict[key] = {"elevation": np.nan}
                continue

            depth = np.nan

            # Convert station coordinates to UTM for topography interpolation
            if topo_success and topographyValues is not None:
                easting, northing = wgs84_to_utm.transform(lon, lat)
                if is_within_bounds(easting, northing, topo_min_lon, topo_max_lon, topo_min_lat, topo_max_lat):
                    depth = InterpolatePoint(topographyValues, topo_latitudes, topo_longitudes, (northing, easting))
                    if not np.isnan(depth):
                        print(f"Station {key}: Using topography depth {depth:.3f} m")
                    else:
                        print(f"Station {key}: Topography depth is NaN or invalid, trying bathymetry")
                else:
                    print(f"Station {key}: Outside topography bounds (easting={easting:.2f}, northing={northing:.2f}), trying bathymetry")

            # Fall back to bathymetry data if topography depth is NaN or point is outside topography bounds
            if np.isnan(depth) and bathy_success and bathymetryValues is not None and is_within_bounds(lon, lat, bathy_min_lon, bathy_max_lon, bathy_min_lat, bathy_max_lat):
                depth = InterpolatePoint(bathymetryValues, bathy_latitudes, bathy_longitudes, (lat, lon))
                if not np.isnan(depth):
                    print(f"Station {key}: Using bathymetry depth {depth:.3f} m")

            # Apply elevation filter (converts depth to elevation for JSON)
            elevationDict[key] = {"elevation": filterElevation(depth, key)}

        # Log performance metrics
        print(f"\nCompleted processing in {time.time() - start_time:.2f} seconds. Made 0 topography API calls, {'1' if bathy_called else '0'} bathymetry API call for {len(stationsDict['ASSET'])} stations.")

        # Save elevation dictionary to output file
        with open(OBS_ASSET_DATA_FILE, "w") as outfile:
            json.dump(elevationDict, outfile, allow_nan=True)

        # Generate and save heatmap plots
        if topo_success and topographyValues is not None:
            plot_heatmap(topographyValues, topo_latitudes, topo_longitudes, "Topography Depth", "obs_topo_debug.png", is_projected=True)
        else:
            print("Skipping topography plot: No valid topography data available.")

        if bathy_success and bathymetryValues is not None:
            plot_heatmap(bathymetryValues, bathy_latitudes, bathy_longitudes, "Bathymetry Depth", "obs_bathy_debug.png", is_projected=False)
        else:
            print("Skipping bathymetry plot: No valid bathymetry data available.")

        # Exit after saving plots
        print("Plots saved. Exiting.")
        sys.exit(0)

if __name__ == "__main__":
    # Example usage (replace with actual file paths)
    GetObsElevation(STATIONS_FILE="stations.json", OBS_ASSET_DATA_FILE="output/elevations.json")