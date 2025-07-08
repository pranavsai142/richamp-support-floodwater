import json
import copy
import math
import datetime

GENERATE_TRANSECT_POINTS = False

HYPERRESOLUTION = 1
HYPERPOINTS = 120
MIN_SLOPELINE_DISTANCE = 200  # Minimum slopeline distance in meters
MAX_SLOPELINE_DISTANCE = 1000  # Maximum slopeline distance in meters
SLOPELINE_DELIM_DISTANCE = 100  # Delimitation distance for slope points in meters
DEEPLINE_DISTANCES = [
    1000, 2200, 3500, 5500, 7500, 9500, 10500, 12500, 14500, 16500,
    18500, 20500, 22500, 24500, 26500, 28500, 29500, 31500, 33500, 35500,
    37500, 39500, 41500
]

# Station-specific deepline distances with depths
DEEPLINE_DISTANCES_1 = [
    {"distance": 705, "depth": "7m"},   # Napatree1 (runup_id: 10)
    {"distance": 2323, "depth": "20m"},
    {"distance": 9000, "depth": "40m"}
]
DEEPLINE_DISTANCES_2 = [
    {"distance": 550, "depth": "7m"},   # Napatree2 (runup_id: 20)
    {"distance": 2265, "depth": "20m"},
    {"distance": 9000, "depth": "40m"},
]
DEEPLINE_DISTANCES_3 = [
    {"distance": 435, "depth": "7m"}, # Napatree3 (runup_id: 30)
    {"distance": 2233, "depth": "20m"},
    {"distance": 9000, "depth": "40m"},
]
DEEPLINE_DISTANCES_4 = [
    {"distance": 410, "depth": "7m"},  # Napatree4 (runup_id: 40)
    {"distance": 2225, "depth": "20m"},
    {"distance": 9000, "depth": "40m"}
]
DEEPLINE_DISTANCES_5 = [
    {"distance": 545, "depth": "7m"},   # Napatree5 (runup_id: 50)
    {"distance": 2175, "depth": "20m"},
    {"distance": 9000, "depth": "40m"}
]


def generate_deepline_distances(max_distance, spacing, initial_distance=75, num_stations=5):
    """
    Generate DEEPLINE_DISTANCES_X lists for specified max distance and spacing.
    
    Args:
        max_distance (float): Maximum distance in meters (e.g., 12475).
        spacing (float): Distance increment in meters (e.g., 200).
        initial_distance (float): Starting distance in meters (default: 75).
        num_stations (int): Number of stations (default: 5 for Napatree1-5).
    
    Returns:
        dict: Dictionary mapping runup_id to deepline distances list.
        Also sets global variables DEEPLINE_DISTANCES_1, ..., DEEPLINE_DISTANCES_X.
    """
    # Generate the distance list
    distances = []
    current_distance = initial_distance
    depth = 1
    while current_distance <= max_distance:
        distances.append({"distance": current_distance, "depth": f"{depth}m"})
        current_distance += spacing
        depth += 1
    
    # Create DEEPLINE_DISTANCES_X for each station
    deepline_distances_map = {}
    for station_idx in range(1, num_stations + 1):
        runup_id = str(station_idx * 10)  # 10, 20, 30, 40, 50
        # Assign the same distances list to each station
        globals()[f"DEEPLINE_DISTANCES_{station_idx}"] = distances.copy()
        deepline_distances_map[runup_id] = globals()[f"DEEPLINE_DISTANCES_{station_idx}"]
    
    return deepline_distances_map

# Example usage
# max_distance = 12475  # Maximum distance in meters
# spacing = 200         # Spacing between points in meters
if(GENERATE_TRANSECT_POINTS):
    max_distance = 25000  # Maximum distance in meters
    spacing = 200         # Spacing between points in meters
    DEEPLINE_DISTANCES_MAP = generate_deepline_distances(max_distance, spacing)

# if(True):
#     DEEPLINE_DISTANCES_1 = [
#         {"distance": 75, "depth": "1m"},    # Napatree1 (runup_id: 10)
#         {"distance": 275, "depth": "2m"},
#         {"distance": 475, "depth": "3m"},
#         {"distance": 675, "depth": "4m"},
#         {"distance": 875, "depth": "5m"},
#         {"distance": 1075, "depth": "6m"},
#         {"distance": 1275, "depth": "7m"},
#         {"distance": 1475, "depth": "8m"},
#         {"distance": 1675, "depth": "9m"},
#         {"distance": 1875, "depth": "10m"},
#         {"distance": 2075, "depth": "11m"},
#         {"distance": 2275, "depth": "12m"},
#         {"distance": 2475, "depth": "13m"},
#         {"distance": 2675, "depth": "14m"},
#         {"distance": 2875, "depth": "15m"},
#         {"distance": 3075, "depth": "16m"},
#         {"distance": 3275, "depth": "17m"},
#         {"distance": 3475, "depth": "18m"},
#         {"distance": 3675, "depth": "19m"},
#         {"distance": 3875, "depth": "20m"},
#         {"distance": 4075, "depth": "21m"},
#         {"distance": 4275, "depth": "22m"},
#         {"distance": 4475, "depth": "23m"},
#         {"distance": 4675, "depth": "24m"},
#         {"distance": 4875, "depth": "25m"},
#         {"distance": 5075, "depth": "26m"},
#         {"distance": 5275, "depth": "27m"},
#         {"distance": 5475, "depth": "28m"},
#         {"distance": 5675, "depth": "29m"},
#         {"distance": 5875, "depth": "30m"},
#         {"distance": 6075, "depth": "31m"},
#         {"distance": 6275, "depth": "32m"},
#         {"distance": 6475, "depth": "33m"},
#         {"distance": 6675, "depth": "34m"},
#         {"distance": 6875, "depth": "35m"},
#         {"distance": 7075, "depth": "36m"},
#         {"distance": 7275, "depth": "37m"},
#         {"distance": 7475, "depth": "38m"},
#         {"distance": 7675, "depth": "39m"},
#         {"distance": 7875, "depth": "40m"},
#         {"distance": 8075, "depth": "41m"},
#         {"distance": 8275, "depth": "42m"},
#         {"distance": 8475, "depth": "43m"},
#         {"distance": 8675, "depth": "44m"},
#         {"distance": 8875, "depth": "45m"},
#         {"distance": 9075, "depth": "46m"},
#         {"distance": 9275, "depth": "47m"},
#         {"distance": 9475, "depth": "48m"},
#         {"distance": 9675, "depth": "49m"},
#         {"distance": 9875, "depth": "50m"},
#         {"distance": 10075, "depth": "51m"},
#         {"distance": 10275, "depth": "52m"},
#         {"distance": 10475, "depth": "53m"},
#         {"distance": 10675, "depth": "54m"},
#         {"distance": 10875, "depth": "55m"},
#         {"distance": 11075, "depth": "56m"},
#         {"distance": 11275, "depth": "57m"},
#         {"distance": 11475, "depth": "58m"},
#         {"distance": 11675, "depth": "59m"},
#         {"distance": 11875, "depth": "60m"},
#         {"distance": 12075, "depth": "61m"},
#         {"distance": 12275, "depth": "62m"},
#         {"distance": 12475, "depth": "63m"}
#     ]
#     
#     DEEPLINE_DISTANCES_2 = [
#         {"distance": 75, "depth": "1m"},    # Napatree2 (runup_id: 20)
#         {"distance": 275, "depth": "2m"},
#         {"distance": 475, "depth": "3m"},
#         {"distance": 675, "depth": "4m"},
#         {"distance": 875, "depth": "5m"},
#         {"distance": 1075, "depth": "6m"},
#         {"distance": 1275, "depth": "7m"},
#         {"distance": 1475, "depth": "8m"},
#         {"distance": 1675, "depth": "9m"},
#         {"distance": 1875, "depth": "10m"},
#         {"distance": 2075, "depth": "11m"},
#         {"distance": 2275, "depth": "12m"},
#         {"distance": 2475, "depth": "13m"},
#         {"distance": 2675, "depth": "14m"},
#         {"distance": 2875, "depth": "15m"},
#         {"distance": 3075, "depth": "16m"},
#         {"distance": 3275, "depth": "17m"},
#         {"distance": 3475, "depth": "18m"},
#         {"distance": 3675, "depth": "19m"},
#         {"distance": 3875, "depth": "20m"},
#         {"distance": 4075, "depth": "21m"},
#         {"distance": 4275, "depth": "22m"},
#         {"distance": 4475, "depth": "23m"},
#         {"distance": 4675, "depth": "24m"},
#         {"distance": 4875, "depth": "25m"},
#         {"distance": 5075, "depth": "26m"},
#         {"distance": 5275, "depth": "27m"},
#         {"distance": 5475, "depth": "28m"},
#         {"distance": 5675, "depth": "29m"},
#         {"distance": 5875, "depth": "30m"},
#         {"distance": 6075, "depth": "31m"},
#         {"distance": 6275, "depth": "32m"},
#         {"distance": 6475, "depth": "33m"},
#         {"distance": 6675, "depth": "34m"},
#         {"distance": 6875, "depth": "35m"},
#         {"distance": 7075, "depth": "36m"},
#         {"distance": 7275, "depth": "37m"},
#         {"distance": 7475, "depth": "38m"},
#         {"distance": 7675, "depth": "39m"},
#         {"distance": 7875, "depth": "40m"},
#         {"distance": 8075, "depth": "41m"},
#         {"distance": 8275, "depth": "42m"},
#         {"distance": 8475, "depth": "43m"},
#         {"distance": 8675, "depth": "44m"},
#         {"distance": 8875, "depth": "45m"},
#         {"distance": 9075, "depth": "46m"},
#         {"distance": 9275, "depth": "47m"},
#         {"distance": 9475, "depth": "48m"},
#         {"distance": 9675, "depth": "49m"},
#         {"distance": 9875, "depth": "50m"},
#         {"distance": 10075, "depth": "51m"},
#         {"distance": 10275, "depth": "52m"},
#         {"distance": 10475, "depth": "53m"},
#         {"distance": 10675, "depth": "54m"},
#         {"distance": 10875, "depth": "55m"},
#         {"distance": 11075, "depth": "56m"},
#         {"distance": 11275, "depth": "57m"},
#         {"distance": 11475, "depth": "58m"},
#         {"distance": 11675, "depth": "59m"},
#         {"distance": 11875, "depth": "60m"},
#         {"distance": 12075, "depth": "61m"},
#         {"distance": 12275, "depth": "62m"},
#         {"distance": 12475, "depth": "63m"}
#     ]
#     
#     DEEPLINE_DISTANCES_3 = [
#         {"distance": 75, "depth": "1m"},    # Napatree3 (runup_id: 30)
#         {"distance": 275, "depth": "2m"},
#         {"distance": 475, "depth": "3m"},
#         {"distance": 675, "depth": "4m"},
#         {"distance": 875, "depth": "5m"},
#         {"distance": 1075, "depth": "6m"},
#         {"distance": 1275, "depth": "7m"},
#         {"distance": 1475, "depth": "8m"},
#         {"distance": 1675, "depth": "9m"},
#         {"distance": 1875, "depth": "10m"},
#         {"distance": 2075, "depth": "11m"},
#         {"distance": 2275, "depth": "12m"},
#         {"distance": 2475, "depth": "13m"},
#         {"distance": 2675, "depth": "14m"},
#         {"distance": 2875, "depth": "15m"},
#         {"distance": 3075, "depth": "16m"},
#         {"distance": 3275, "depth": "17m"},
#         {"distance": 3475, "depth": "18m"},
#         {"distance": 3675, "depth": "19m"},
#         {"distance": 3875, "depth": "20m"},
#         {"distance": 4075, "depth": "21m"},
#         {"distance": 4275, "depth": "22m"},
#         {"distance": 4475, "depth": "23m"},
#         {"distance": 4675, "depth": "24m"},
#         {"distance": 4875, "depth": "25m"},
#         {"distance": 5075, "depth": "26m"},
#         {"distance": 5275, "depth": "27m"},
#         {"distance": 5475, "depth": "28m"},
#         {"distance": 5675, "depth": "29m"},
#         {"distance": 5875, "depth": "30m"},
#         {"distance": 6075, "depth": "31m"},
#         {"distance": 6275, "depth": "32m"},
#         {"distance": 6475, "depth": "33m"},
#         {"distance": 6675, "depth": "34m"},
#         {"distance": 6875, "depth": "35m"},
#         {"distance": 7075, "depth": "36m"},
#         {"distance": 7275, "depth": "37m"},
#         {"distance": 7475, "depth": "38m"},
#         {"distance": 7675, "depth": "39m"},
#         {"distance": 7875, "depth": "40m"},
#         {"distance": 8075, "depth": "41m"},
#         {"distance": 8275, "depth": "42m"},
#         {"distance": 8475, "depth": "43m"},
#         {"distance": 8675, "depth": "44m"},
#         {"distance": 8875, "depth": "45m"},
#         {"distance": 9075, "depth": "46m"},
#         {"distance": 9275, "depth": "47m"},
#         {"distance": 9475, "depth": "48m"},
#         {"distance": 9675, "depth": "49m"},
#         {"distance": 9875, "depth": "50m"},
#         {"distance": 10075, "depth": "51m"},
#         {"distance": 10275, "depth": "52m"},
#         {"distance": 10475, "depth": "53m"},
#         {"distance": 10675, "depth": "54m"},
#         {"distance": 10875, "depth": "55m"},
#         {"distance": 11075, "depth": "56m"},
#         {"distance": 11275, "depth": "57m"},
#         {"distance": 11475, "depth": "58m"},
#         {"distance": 11675, "depth": "59m"},
#         {"distance": 11875, "depth": "60m"},
#         {"distance": 12075, "depth": "61m"},
#         {"distance": 12275, "depth": "62m"},
#         {"distance": 12475, "depth": "63m"}
#     ]
#     
#     DEEPLINE_DISTANCES_4 = [
#         {"distance": 75, "depth": "1m"},    # Napatree4 (runup_id: 40)
#         {"distance": 275, "depth": "2m"},
#         {"distance": 475, "depth": "3m"},
#         {"distance": 675, "depth": "4m"},
#         {"distance": 875, "depth": "5m"},
#         {"distance": 1075, "depth": "6m"},
#         {"distance": 1275, "depth": "7m"},
#         {"distance": 1475, "depth": "8m"},
#         {"distance": 1675, "depth": "9m"},
#         {"distance": 1875, "depth": "10m"},
#         {"distance": 2075, "depth": "11m"},
#         {"distance": 2275, "depth": "12m"},
#         {"distance": 2475, "depth": "13m"},
#         {"distance": 2675, "depth": "14m"},
#         {"distance": 2875, "depth": "15m"},
#         {"distance": 3075, "depth": "16m"},
#         {"distance": 3275, "depth": "17m"},
#         {"distance": 3475, "depth": "18m"},
#         {"distance": 3675, "depth": "19m"},
#         {"distance": 3875, "depth": "20m"},
#         {"distance": 4075, "depth": "21m"},
#         {"distance": 4275, "depth": "22m"},
#         {"distance": 4475, "depth": "23m"},
#         {"distance": 4675, "depth": "24m"},
#         {"distance": 4875, "depth": "25m"},
#         {"distance": 5075, "depth": "26m"},
#         {"distance": 5275, "depth": "27m"},
#         {"distance": 5475, "depth": "28m"},
#         {"distance": 5675, "depth": "29m"},
#         {"distance": 5875, "depth": "30m"},
#         {"distance": 6075, "depth": "31m"},
#         {"distance": 6275, "depth": "32m"},
#         {"distance": 6475, "depth": "33m"},
#         {"distance": 6675, "depth": "34m"},
#         {"distance": 6875, "depth": "35m"},
#         {"distance": 7075, "depth": "36m"},
#         {"distance": 7275, "depth": "37m"},
#         {"distance": 7475, "depth": "38m"},
#         {"distance": 7675, "depth": "39m"},
#         {"distance": 7875, "depth": "40m"},
#         {"distance": 8075, "depth": "41m"},
#         {"distance": 8275, "depth": "42m"},
#         {"distance": 8475, "depth": "43m"},
#         {"distance": 8675, "depth": "44m"},
#         {"distance": 8875, "depth": "45m"},
#         {"distance": 9075, "depth": "46m"},
#         {"distance": 9275, "depth": "47m"},
#         {"distance": 9475, "depth": "48m"},
#         {"distance": 9675, "depth": "49m"},
#         {"distance": 9875, "depth": "50m"},
#         {"distance": 10075, "depth": "51m"},
#         {"distance": 10275, "depth": "52m"},
#         {"distance": 10475, "depth": "53m"},
#         {"distance": 10675, "depth": "54m"},
#         {"distance": 10875, "depth": "55m"},
#         {"distance": 11075, "depth": "56m"},
#         {"distance": 11275, "depth": "57m"},
#         {"distance": 11475, "depth": "58m"},
#         {"distance": 11675, "depth": "59m"},
#         {"distance": 11875, "depth": "60m"},
#         {"distance": 12075, "depth": "61m"},
#         {"distance": 12275, "depth": "62m"},
#         {"distance": 12475, "depth": "63m"}
#     ]
#     
#     DEEPLINE_DISTANCES_5 = [
#         {"distance": 75, "depth": "1m"},    # Napatree5 (runup_id: 50)
#         {"distance": 275, "depth": "2m"},
#         {"distance": 475, "depth": "3m"},
#         {"distance": 675, "depth": "4m"},
#         {"distance": 875, "depth": "5m"},
#         {"distance": 1075, "depth": "6m"},
#         {"distance": 1275, "depth": "7m"},
#         {"distance": 1475, "depth": "8m"},
#         {"distance": 1675, "depth": "9m"},
#         {"distance": 1875, "depth": "10m"},
#         {"distance": 2075, "depth": "11m"},
#         {"distance": 2275, "depth": "12m"},
#         {"distance": 2475, "depth": "13m"},
#         {"distance": 2675, "depth": "14m"},
#         {"distance": 2875, "depth": "15m"},
#         {"distance": 3075, "depth": "16m"},
#         {"distance": 3275, "depth": "17m"},
#         {"distance": 3475, "depth": "18m"},
#         {"distance": 3675, "depth": "19m"},
#         {"distance": 3875, "depth": "20m"},
#         {"distance": 4075, "depth": "21m"},
#         {"distance": 4275, "depth": "22m"},
#         {"distance": 4475, "depth": "23m"},
#         {"distance": 4675, "depth": "24m"},
#         {"distance": 4875, "depth": "25m"},
#         {"distance": 5075, "depth": "26m"},
#         {"distance": 5275, "depth": "27m"},
#         {"distance": 5475, "depth": "28m"},
#         {"distance": 5675, "depth": "29m"},
#         {"distance": 5875, "depth": "30m"},
#         {"distance": 6075, "depth": "31m"},
#         {"distance": 6275, "depth": "32m"},
#         {"distance": 6475, "depth": "33m"},
#         {"distance": 6675, "depth": "34m"},
#         {"distance": 6875, "depth": "35m"},
#         {"distance": 7075, "depth": "36m"},
#         {"distance": 7275, "depth": "37m"},
#         {"distance": 7475, "depth": "38m"},
#         {"distance": 7675, "depth": "39m"},
#         {"distance": 7875, "depth": "40m"},
#         {"distance": 8075, "depth": "41m"},
#         {"distance": 8275, "depth": "42m"},
#         {"distance": 8475, "depth": "43m"},
#         {"distance": 8675, "depth": "44m"},
#         {"distance": 8875, "depth": "45m"},
#         {"distance": 9075, "depth": "46m"},
#         {"distance": 9275, "depth": "47m"},
#         {"distance": 9475, "depth": "48m"},
#         {"distance": 9675, "depth": "49m"},
#         {"distance": 9875, "depth": "50m"},
#         {"distance": 10075, "depth": "51m"},
#         {"distance": 10275, "depth": "52m"},
#         {"distance": 10475, "depth": "53m"},
#         {"distance": 10675, "depth": "54m"},
#         {"distance": 10875, "depth": "55m"},
#         {"distance": 11075, "depth": "56m"},
#         {"distance": 11275, "depth": "57m"},
#         {"distance": 11475, "depth": "58m"},
#         {"distance": 11675, "depth": "59m"},
#         {"distance": 11875, "depth": "60m"},
#         {"distance": 12075, "depth": "61m"},
#         {"distance": 12275, "depth": "62m"},
#         {"distance": 12475, "depth": "63m"}
#     ]

# Dictionary to map runup_id to deepline distances
DEEPLINE_DISTANCES_MAP = {
    '10': DEEPLINE_DISTANCES_1,
    '20': DEEPLINE_DISTANCES_2,
    '30': DEEPLINE_DISTANCES_3,
    '40': DEEPLINE_DISTANCES_4,
    '50': DEEPLINE_DISTANCES_5
}

# Plain deepline keys to remove
PLAIN_DEEPLINE_KEYS = ['13', '23', '33', '43', '53']

# Function to convert GMT datetime string to Unix timestamp
def datetime_to_timestamp(dt_str):
    """Convert a GMT datetime string (YYYY-MM-DD HH:MM:SS) to Unix timestamp."""
    dt = datetime.datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    dt = dt.replace(tzinfo=datetime.timezone.utc)  # Ensure GMT/UTC
    return int(dt.timestamp())

# Station-specific dune heights with GMT datetime strings
DUNE_HEIGHTS_1 = [
    {"datetime": "2023-12-13 04:00:00", "height": 6.04},
    {"datetime": "2023-12-19 04:00:00", "height": 6.08}
]
DUNE_HEIGHTS_2 = [
    {"datetime": "2023-12-13 04:00:00", "height": 4.81},
    {"datetime": "2023-12-19 04:00:00", "height": 4.82}
]
DUNE_HEIGHTS_3 = [
    {"datetime": "2023-12-13 04:00:00", "height": 4.02},
    {"datetime": "2023-12-19 04:00:00", "height": 4.06}
]
DUNE_HEIGHTS_4 = [
    {"datetime": "2023-12-13 04:00:00", "height": 3.89},
    {"datetime": "2023-12-19 04:00:00", "height": 3.92}
]
DUNE_HEIGHTS_5 = [
    {"datetime": "2023-12-13 04:00:00", "height": 3.32},
    {"datetime": "2023-12-19 04:00:00", "height": 3.22}
]

# DUNE_HEIGHTS_1 = [
#     {"datetime": "2022-12-20 04:00:00", "height": 3.82}
# ]
# DUNE_HEIGHTS_2 = [
#     {"datetime": "2022-12-20 04:00:00", "height": 3.37}
# ]
# DUNE_HEIGHTS_3 = [
#     {"datetime": "2022-12-20 04:00:00", "height": 3.40}
# ]
# DUNE_HEIGHTS_4 = [
#     {"datetime": "2022-12-20 04:00:00", "height": 3.84}
# ]
# DUNE_HEIGHTS_5 = [
#     {"datetime": "2022-12-20 04:00:00", "height": 3.11}
# ]

# Convert datetime strings to timestamps for JSON output
DUNE_HEIGHTS_1 = [{"timestamp": datetime_to_timestamp(h["datetime"]), "height": h["height"]} for h in DUNE_HEIGHTS_1]
DUNE_HEIGHTS_2 = [{"timestamp": datetime_to_timestamp(h["datetime"]), "height": h["height"]} for h in DUNE_HEIGHTS_2]
DUNE_HEIGHTS_3 = [{"timestamp": datetime_to_timestamp(h["datetime"]), "height": h["height"]} for h in DUNE_HEIGHTS_3]
DUNE_HEIGHTS_4 = [{"timestamp": datetime_to_timestamp(h["datetime"]), "height": h["height"]} for h in DUNE_HEIGHTS_4]
DUNE_HEIGHTS_5 = [{"timestamp": datetime_to_timestamp(h["datetime"]), "height": h["height"]} for h in DUNE_HEIGHTS_5]

# Dictionary to map runup_id to dune heights
DUNE_HEIGHTS_MAP = {
    '10': DUNE_HEIGHTS_1,
    '20': DUNE_HEIGHTS_2,
    '30': DUNE_HEIGHTS_3,
    '40': DUNE_HEIGHTS_4,
    '50': DUNE_HEIGHTS_5
}

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dLon = lon2_rad - lon1_rad
    y = math.sin(dLon) * math.cos(lat2_rad)
    x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dLon)
    bearing = math.atan2(y, x)
    return bearing

def calculate_new_point(lat, lon, bearing, distance):
    R = 6371e3
    lat_rad, lon_rad = math.radians(lat), math.radians(lon)
    bearing_rad = bearing
    new_lat = math.asin(math.sin(lat_rad) * math.cos(distance / R) + 
                       math.cos(lat_rad) * math.sin(distance / R) * math.cos(bearing_rad))
    new_lon = lon_rad + math.atan2(math.sin(bearing_rad) * math.sin(distance / R) * math.cos(lat_rad),
                                  math.cos(distance / R) - math.sin(lat_rad) * math.sin(new_lat))
    return math.degrees(new_lat), math.degrees(new_lon)

def findDuneHeight(time, duneHeights):
    if not duneHeights:
        return 0.0
    sorted_heights = sorted(duneHeights, key=lambda x: x['timestamp'])
    for entry in sorted_heights:
        if entry['timestamp'] <= time:
            return entry['height']
    return sorted_heights[0]['height']

def generate_points_along_line(json_data, resolution=HYPERRESOLUTION, points_count=HYPERPOINTS):
    if 'NORMAL' not in json_data:
        json_data['NORMAL'] = {}
    for runup_id, runup_data in json_data['RUNUP'].items():
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        json_data['NORMAL'][runup_id] = {}
        point_counter = 0
        for i in range(-points_count // 4, 3 * points_count // 4 + 1):
            distance = i * resolution
            new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
            new_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "distance": str(distance),
                "name": f"{runup_data['name']} {distance:.3f} m",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            new_key = f"{runup_id}{point_counter:03d}"
            json_data['NORMAL'][runup_id][new_key] = new_point
            for section in ['ASSET', 'NOS']:
                json_data[section][new_key] = new_point
            point_counter += 1

def generate_slopeline_points(json_data, distance=MAX_SLOPELINE_DISTANCE):
    for runup_id, runup_data in json_data['RUNUP'].items():
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
        slopeline_key = f"{runup_id}s"
        runup_data['slopelineKey'] = slopeline_key
        runup_data['slopelineLatitude'] = f"{new_lat:.6f}"
        runup_data['slopelineLongitude'] = f"{new_lon:.6f}"
        slopeline_point = {
            "id": "RUNUP",
            "source": "RUNUP",
            "name": f"{runup_data['name']} Slopeline",
            "latitude": f"{new_lat:.6f}",
            "longitude": f"{new_lon:.6f}"
        }
        json_data['ASSET'][slopeline_key] = slopeline_point

def generate_slope_stations(json_data, min_distance=MIN_SLOPELINE_DISTANCE, max_distance=MAX_SLOPELINE_DISTANCE, delim_distance=SLOPELINE_DELIM_DISTANCE):
    slope_data = copy.deepcopy(json_data)
    slope_data['ASSET'] = {}
    for runup_id, runup_data in slope_data['RUNUP'].items():
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        point_counter = 0
        distance = min_distance
        while distance <= max_distance:
            adjusted_bearing = bearing + math.pi if distance < 0 else bearing
            adjusted_distance = abs(distance)
            new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, adjusted_bearing, adjusted_distance)
            new_key = f"{runup_id}sl{point_counter:03d}"
            slope_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "name": f"{runup_data['name']} Slope {distance:.1f}m",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            slope_data['ASSET'][new_key] = slope_point
            distance += delim_distance
            point_counter += 1
    return slope_data

# def generate_deepline_points(json_data):
#     new_runup = {}
#     
#     # Remove plain deepline keys from ASSET, NDBC, NOS
#     for section in ['ASSET', 'NDBC', 'NOS']:
#         for key in PLAIN_DEEPLINE_KEYS:
#             if key in json_data[section]:
#                 del json_data[section][key]
#     
#     for runup_id, runup_data in list(json_data['RUNUP'].items()):
#         station_id = runup_id[0:2]
#         print(f"Processing station_id: {station_id}, runup_id: {runup_id}")
#         shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
#         surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
#         bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
#         deepline_distances = DEEPLINE_DISTANCES_MAP.get(station_id, DEEPLINE_DISTANCES_1)
#         dune_heights = DUNE_HEIGHTS_MAP.get(station_id, DUNE_HEIGHTS_1)
#         
#         if 'deeplineKey' not in runup_data:
#             runup_data['deeplineKey'] = f"{station_id}d"
#         
#         for idx, deepline_info in enumerate(deepline_distances):
#             distance = deepline_info['distance']
#             depth = deepline_info['depth']
#             deepline_key = f"{runup_data['deeplineKey']}d{idx}"
#             base_name = f"{runup_data['name'].split(' ')[0]} {depth} Depth Waves {distance}m"
#             
#             # Create two RUNUP entries: one with calculateDailyAverageSlope: true, one with false
#             for slope_mode in [True, False]:
#                 new_runup_key = f"{runup_id}d{idx}_{'true' if slope_mode else 'false'}"
#                 new_runup[new_runup_key] = runup_data.copy()
#                 new_runup[new_runup_key]['deeplineKey'] = deepline_key
#                 # Include runup_id in name for clarity
#                 new_runup[new_runup_key]['name'] = f"{base_name} {new_runup_key}"
#                 new_runup[new_runup_key]['duneHeights'] = dune_heights
#                 new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
#                 new_runup[new_runup_key]['deeplineLatitude'] = f"{new_lat:.6f}"
#                 new_runup[new_runup_key]['deeplineLongitude'] = f"{new_lon:.6f}"
#                 new_runup[new_runup_key]['calculateDailyAverageSlope'] = slope_mode
#                 
#                 deepline_point = {
#                     "id": "RUNUP",
#                     "source": "RUNUP",
#                     "name": f"{base_name}",  # ASSET/NDBC/NOS use base name without runup_id
#                     "latitude": f"{new_lat:.6f}",
#                     "longitude": f"{new_lon:.6f}"
#                 }
#                 for section in ['ASSET', 'NDBC', 'NOS']:
#                     json_data[section][deepline_key] = deepline_point
#     
#     json_data['RUNUP'] = new_runup

def generate_deepline_points(json_data):
    new_runup = {}
    
    # Remove plain deepline keys from ASSET, NDBC, NOS
    for section in ['ASSET', 'NDBC', 'NOS']:
        for key in PLAIN_DEEPLINE_KEYS:
            if key in json_data[section]:
                del json_data[section][key]
    
    for runup_id, runup_data in list(json_data['RUNUP'].items()):
        station_id = runup_id[0:2]
        print(f"Processing station_id: {station_id}, runup_id: {runup_id}")
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        deepline_distances = DEEPLINE_DISTANCES_MAP.get(station_id, DEEPLINE_DISTANCES_1)
        dune_heights = DUNE_HEIGHTS_MAP.get(station_id, DUNE_HEIGHTS_1)
        
        if 'deeplineKey' not in runup_data:
            runup_data['deeplineKey'] = f"{station_id}d"
        
        for idx, deepline_info in enumerate(deepline_distances):
            distance = deepline_info['distance']
            depth = deepline_info['depth']
            deepline_key = f"{runup_data['deeplineKey']}d{idx}"
            base_name = f"{runup_data['name'].split(' ')[0]} {depth} Depth Waves {distance}m"
            
            # Create two RUNUP entries: one with calculateDailyAverageSlope: true, one with false
            for slope_mode in [True]:
                new_runup_key = f"{runup_id}d{idx}"
                new_runup[new_runup_key] = runup_data.copy()
                new_runup[new_runup_key]['deeplineKey'] = deepline_key
                # Include runup_id in name for clarity
                new_runup[new_runup_key]['name'] = f"{base_name} {new_runup_key}"
                new_runup[new_runup_key]['duneHeights'] = dune_heights
                new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
                new_runup[new_runup_key]['deeplineLatitude'] = f"{new_lat:.6f}"
                new_runup[new_runup_key]['deeplineLongitude'] = f"{new_lon:.6f}"
                new_runup[new_runup_key]['calculateDailyAverageSlope'] = slope_mode
                
                deepline_point = {
                    "id": "RUNUP",
                    "source": "RUNUP",
                    "name": f"{base_name}",  # ASSET/NDBC/NOS use base name without runup_id
                    "latitude": f"{new_lat:.6f}",
                    "longitude": f"{new_lon:.6f}"
                }
                for section in ['ASSET', 'NDBC', 'NOS']:
                    json_data[section][deepline_key] = deepline_point
    
    json_data['RUNUP'] = new_runup

def generate_deepline_only_stations(json_data):
    deepline_data = {"ASSET": {}}
    
    for runup_id, runup_data in json_data['RUNUP'].items():
        station_id = runup_id.rstrip('d0123456789')
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        
        deepline_distances = DEEPLINE_DISTANCES_MAP.get(station_id, DEEPLINE_DISTANCES_1)
        
        # Ensure deeplineKey exists
        if 'deeplineKey' not in runup_data:
            runup_data['deeplineKey'] = f"{station_id}d"
        
        for idx, deepline_info in enumerate(deepline_distances):
            distance = deepline_info['distance']
            depth = deepline_info['depth']
            
            deepline_key = f"{runup_data['deeplineKey']}d{idx}"
            
            new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
            deepline_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "name": f"{runup_data['name'].split(' ')[0]} {depth} Depth Waves",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            
            deepline_data['ASSET'][deepline_key] = deepline_point
    
    return deepline_data

def generate_multiple_deepline_points(json_data, distances=DEEPLINE_DISTANCES):
    if 'NORMAL' not in json_data:
        json_data['NORMAL'] = {}
    if 'TANGENT' not in json_data:
        json_data['TANGENT'] = {}
    new_runup = {}
    
    # Remove plain deepline keys from ASSET, NDBC, NOS
    for section in ['ASSET', 'NDBC', 'NOS']:
        for key in PLAIN_DEEPLINE_KEYS:
            if key in json_data[section]:
                del json_data[section][key]
    
    for orig_runup_id, runup_data in json_data['RUNUP'].items():
        station_id = orig_runup_id.rstrip('d0123456789')
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        tangent_lat, tangent_lon = float(runup_data['tangentLatitude']), float(runup_data['tangentLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        
        dune_heights = DUNE_HEIGHTS_MAP.get(station_id, DUNE_HEIGHTS_1)
        
        # Generate NORMAL points
        json_data['NORMAL'][orig_runup_id] = {}
        point_counter = 0
        for i in range(-HYPERPOINTS // 4, 3 * HYPERPOINTS // 4 + 1):
            distance = i * HYPERRESOLUTION
            new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
            new_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "distance": str(distance),
                "name": f"{runup_data['name']} {distance:.3f} m",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            new_key = f"{orig_runup_id}{point_counter:03d}"
            json_data['NORMAL'][orig_runup_id][new_key] = new_point
            for section in ['ASSET', 'NOS']:
                json_data[section][new_key] = new_point
            point_counter += 1
        
        # Generate TANGENT points
        json_data['TANGENT'][station_id] = {}
        point_counter = 0
        for i in range(-HYPERPOINTS // 4, 3 * HYPERPOINTS // 4 + 1):
            distance = i * HYPERRESOLUTION
            new_lat, new_lon = calculate_new_point(tangent_lat, tangent_lon, bearing, distance)
            new_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "distance": str(distance),
                "name": f"{runup_data['name'].replace(' 7m Depth Waves', '').replace(' 15m Depth Waves', '').replace(' 20m Depth Waves', '')} Tangent {distance:.3f} m",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            new_key = f"{station_id}{point_counter:03d}"
            json_data['TANGENT'][station_id][new_key] = new_point
            point_counter += 1
        
        # Generate multiple deepline points
        for idx, distance in enumerate(distances):
            new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
            new_key = f"{station_id}d{idx:02d}"
            
            new_runup[new_key] = {
                "id": "RUNUP",
                "source": "RUNUP",
                "surfKey": runup_data['surfKey'],
                "offshoreKey": runup_data['offshoreKey'],
                "deeplineKey": new_key,
                "name": f"{runup_data['name'].replace(' 7m Depth Waves', '').replace(' 15m Depth Waves', '').replace(' 20m Depth Waves', '')} Deepline {distance}m",
                "latitude": runup_data['latitude'],
                "longitude": runup_data['longitude'],
                "tangentLatitude": runup_data['tangentLatitude'],
                "tangentLongitude": runup_data['tangentLongitude'],
                "surfLatitude": runup_data['surfLatitude'],
                "surfLongitude": runup_data['surfLongitude'],
                "offshoreLatitude": runup_data['offshoreLatitude'],
                "offshoreLongitude": runup_data['offshoreLongitude'],
                "deeplineLatitude": f"{new_lat:.6f}",
                "deeplineLongitude": f"{new_lon:.6f}",
                "duneHeights": dune_heights
            }
            
            deepline_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "name": f"{runup_data['name'].replace(' 7m Depth Waves', '').replace(' 15m Depth Waves', '').replace(' 20m Depth Waves', '')} Deepline {distance}m",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            for section in ['ASSET', 'NDBC', 'NOS']:
                json_data[section][new_key] = deepline_point
    
    json_data['RUNUP'] = new_runup

def offshore_generate_points_along_line(json_data, resolution=200, points_count=15):
    point_counter = 0
    for runup_id, runup_data in json_data['RUNUP'].items():
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        for i in range(points_count):
            distance = i * resolution
            new_lat, new_lon = calculate_new_point(shoreline_lat, shoreline_lon, bearing, distance)
            new_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "distance": str(distance),
                "name": f"{runup_data['name']} {distance:.1f} m",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            new_key = f"{runup_id}{point_counter:03d}"
            for section in ['ASSET', 'NDBC', 'NOS']:
                json_data[section][new_key] = new_point
            point_counter += 1

def generate_tangent_points(json_data, resolution=HYPERRESOLUTION, points_count=HYPERPOINTS):
    if 'TANGENT' not in json_data:
        json_data['TANGENT'] = {}
    
    for runup_id, runup_data in json_data['RUNUP'].items():
#         print("runup_id", runup_id)
        # Extract base station_id (e.g., "40" from "40d0")
        station_id = runup_id[0:2]
#         print("station_id", station_id)
        
        # Skip if TANGENT section for this station_id already exists
        if station_id in json_data['TANGENT']:
            continue
        
        shoreline_lat, shoreline_lon = float(runup_data['latitude']), float(runup_data['longitude'])
        surf_lat, surf_lon = float(runup_data['surfLatitude']), float(runup_data['surfLongitude'])
        tangent_lat, tangent_lon = float(runup_data['tangentLatitude']), float(runup_data['tangentLongitude'])
        bearing = calculate_bearing(shoreline_lat, shoreline_lon, surf_lat, surf_lon)
        
        json_data['TANGENT'][station_id] = {}
        point_counter = 0
        
        for i in range(-points_count // 4, 3 * points_count // 4 + 1):
            distance = i * resolution
            new_lat, new_lon = calculate_new_point(tangent_lat, tangent_lon, bearing, distance)
            new_point = {
                "id": "RUNUP",
                "source": "RUNUP",
                "distance": str(distance),
                "name": f"{runup_data['name'].replace(' 7m Depth Waves', '').replace(' 15m Depth Waves', '').replace(' 20m Depth Waves', '')} Tangent {distance:.3f} m",
                "latitude": f"{new_lat:.6f}",
                "longitude": f"{new_lon:.6f}"
            }
            # Use station_id prefix for keys, e.g., "40000" for station_id "40"
            new_key = f"{station_id}{point_counter:03d}"
            json_data['TANGENT'][station_id][new_key] = new_point
            point_counter += 1

# NORMAL stations
with open('RUNUP_NAPATREE_STATIONS.json', 'r') as file:
    data_normal = json.load(file)
generate_points_along_line(data_normal)
generate_deepline_points(data_normal)
generate_slopeline_points(data_normal, distance=MAX_SLOPELINE_DISTANCE)
generate_tangent_points(data_normal)
with open('NAPATREE_NORMAL_STATIONS.json', 'w') as file:
    json.dump(data_normal, file, indent=2)

# LONG stations
with open('RUNUP_NAPATREE_STATIONS.json', 'r') as file:
    data_long = json.load(file)
offshore_generate_points_along_line(data_long)
generate_deepline_points(data_long)
with open('NAPATREE_LONG_STATIONS.json', 'w') as file:
    json.dump(data_long, file, indent=2)

# DEEP stations
with open('RUNUP_NAPATREE_STATIONS.json', 'r') as file:
    data_deep = json.load(file)
generate_multiple_deepline_points(data_deep)
with open('NAPATREE_DEEP_STATIONS.json', 'w') as file:
    json.dump(data_deep, file, indent=2)

# SLOPE stations
with open('RUNUP_NAPATREE_STATIONS.json', 'r') as file:
    data_slope = json.load(file)
slope_data = generate_slope_stations(data_slope)
with open('NAPATREE_SLOPE_STATIONS.json', 'w') as file:
    json.dump(slope_data, file, indent=2)

# DEEPLINE stations
with open('RUNUP_NAPATREE_STATIONS.json', 'r') as file:
    data_deepline = json.load(file)
deepline_data = generate_deepline_only_stations(data_deepline)
with open('NAPATREE_DEEPLINE_STATIONS.json', 'w') as file:
    json.dump(deepline_data, file, indent=2)