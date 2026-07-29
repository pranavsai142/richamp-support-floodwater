import netCDF4 as nc
from datetime import datetime, timedelta
import argparse

def main():
    p = argparse.ArgumentParser(description="Make a request to read fort file")
    p.add_argument(
        "--file", help="Fort file to read", type=str
    )
    args = p.parse_args()
    args.epsg = 4326
    dataset = nc.Dataset(args.file)
    print(dataset)
    print(dataset.variables)
    metadata = dataset.__dict__
#         print(dataset.variables)
    timeData = dataset["time"]
    datasetTimeDescription = timeData.units
#       Add UTC time marker if not existing in cold start date
    if(not ("Z" in datasetTimeDescription)):
        coldStartDateText = datasetTimeDescription[14: 24] + "T" + datasetTimeDescription[25:] + "Z"
    else:
        coldStartDateText = datasetTimeDescription[14: 24] + "T" + datasetTimeDescription[25:]
    coldStartDate = datetime.fromisoformat(coldStartDateText)
    print("coldStartDate", coldStartDate, flush=True)

    minT = float(timeData[0].data)
    maxT = float(timeData[-1].data)
    times = []
    print(minT, flush=True)
    print(maxT, flush=True)
    windDeltaT = timedelta(seconds=maxT - minT)
    print(windDeltaT)

    print("number of timesteps")
    timesteps = len(timeData[:])
    print(timesteps)

    for index in range(timesteps):
        time = coldStartDate + timedelta(seconds=float(timeData[index].data))
        times.append(time.timestamp())

    print("start of data (seconds since coldstart)")
    startDate = coldStartDate + timedelta(seconds=float(minT))
    endDate = coldStartDate + timedelta(seconds=float(maxT))
    print("startDate", startDate)
    print("endDate", endDate)
        
            # Grid origin is top right? Maybe not, Node based system!
            # y is latitude, x is longitude
    node0 = (float(dataset.variables["y"][0].data), float(dataset.variables["x"][0].data))
    print("node0 (lat, long)", node0)

    numberOfNodes = dataset.variables["x"].shape[0]
if __name__ == "__main__":
    main()
