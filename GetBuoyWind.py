# Queries NOAA CO-OPS wind and saves the data
# Pranav 9/25/2023; product API 2026-07-25 (ERDDAP .mat dead)
# Fuck matlab

from urllib.error import HTTPError
from datetime import datetime, timezone
import json
import os
from Encoders import NumpyEncoder
import numpy as np


class GetBuoyWind:
    def __init__(self, STATIONS_FILE="", OBS_WIND_DATA_FILE="", startDateObject="", endDateObject=""):
        temp_directory = OBS_WIND_DATA_FILE[0 : OBS_WIND_DATA_FILE.rfind("/") + 1]
        if temp_directory and not os.path.isdir(temp_directory):
            os.makedirs(temp_directory, exist_ok=True)

        print(type(startDateObject), flush=True)
        print(startDateObject, flush=True)
        with open(STATIONS_FILE) as stations_file:
            stationsDict = json.load(stations_file)

        # Normalize window to UTC-aware
        if startDateObject.tzinfo is None:
            startDateObject = startDateObject.replace(tzinfo=timezone.utc)
        if endDateObject.tzinfo is None:
            endDateObject = endDateObject.replace(tzinfo=timezone.utc)

        begin = startDateObject.strftime("%Y%m%d")
        end = endDateObject.strftime("%Y%m%d")
        # CO-OPS datagetter max span is ~31 days for 6-min wind; chunk if needed
        base = "https://api.tidesandcurrents.noaa.gov/api/prod/datagetter"

        badStations = []
        windDict = {}
        for key in stationsDict["NOS"].keys():
            stationDict = stationsDict["NOS"][key]
            stationId = stationDict["id"]
            stationName = stationDict["name"]
            try:
                import urllib.request

                url = (
                    f"{base}?product=wind&application=richamp-support"
                    f"&begin_date={begin}&end_date={end}&station={stationId}"
                    f"&time_zone=gmt&units=metric&format=json"
                )
                print(f"CO-OPS API wind station={stationId} ({stationName})", flush=True)
                print("querying url: ", url, flush=True)
                with urllib.request.urlopen(url, timeout=45) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))

                unixTimes = []
                speeds = []
                directions = []
                gusts = []
                for row in payload.get("data") or []:
                    try:
                        t = datetime.strptime(row["t"], "%Y-%m-%d %H:%M").replace(
                            tzinfo=timezone.utc
                        )
                        if t < startDateObject or t > endDateObject:
                            continue
                        s = row.get("s")
                        d = row.get("d")
                        g = row.get("g")
                        if s is None or s == "" or d is None or d == "":
                            continue
                        unixTimes.append(int(t.timestamp()))
                        speeds.append(float(s))
                        # Match legacy ERDDAP path: met "from" dir + 90 aligns with
                        # Grapher.vectorDirection(atan2(-v, u)) used for model UV.
                        directions.append((float(d) + 90.0) % 360.0)
                        if g is None or g == "":
                            gusts.append(float("nan"))
                        else:
                            gusts.append(float(g))
                    except (KeyError, ValueError, TypeError):
                        continue

                # heights were sea-surface height matched for dual-axis plots; optional zeros
                heights = [0.0] * len(unixTimes)
                windDict[key] = {
                    "times": np.array(unixTimes, dtype=np.int64),
                    "directions": np.array(directions, dtype=np.float64),
                    "speeds": np.array(speeds, dtype=np.float64),
                    "gusts": np.array(gusts, dtype=np.float64),
                    "heights": np.array(heights, dtype=np.float64),
                }
                print(
                    f"station {stationId}: n_obs={len(unixTimes)}",
                    flush=True,
                )
                if not unixTimes:
                    badStations.append(stationDict)
            except Exception as e:
                print(f"CO-OPS wind API fail station {stationId}: {e}", flush=True)
                badStations.append(stationDict)
                windDict[key] = {
                    "times": np.array([], dtype=np.int64),
                    "directions": np.array([], dtype=np.float64),
                    "speeds": np.array([], dtype=np.float64),
                    "gusts": np.array([], dtype=np.float64),
                    "heights": np.array([], dtype=np.float64),
                }

        print(
            f"GetBuoyWind: wrote {len(windDict)} stations; bad={len(badStations)}",
            flush=True,
        )
        with open(OBS_WIND_DATA_FILE, "w") as outfile:
            json.dump(windDict, outfile, cls=NumpyEncoder)
