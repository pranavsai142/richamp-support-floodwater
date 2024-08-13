import datetime
import argparse

NUM_LATITUDES = 565
NUM_LONGITUDES = 625
NUM_PRESSURE_VALUES = NUM_LATITUDES * NUM_LONGITUDES
NUM_WIND_VALUES = NUM_PRESSURE_VALUES * 2

PRESSURE_FILL_VALUE = " 1010.0000"
WIND_FILL_VALUE = "    0.0000"

def main():
    p = argparse.ArgumentParser(description="Make a request to generate oceanweather file")
    p.add_argument(
            "--start", help="Start time yyyymmddhhmm", type=str
    )
    p.add_argument(
            "--end", help="End time yyyymmddhhmm", type=str
    )
    p.add_argument(
            "--delta", help="time delta between data entries in seconds", type=str
    )
    args = p.parse_args()
    args.epsg = 4326
    if(not(len(args.start) == 12 and len(args.end) == 12)):
        print("Invalid dates! format should be yyyymmddhhmm")
        quit()
    startDate = datetime.datetime(year=int(args.start[0:4]), month=int(args.start[4:6]), day=int(args.start[6:8]), hour=int(args.start[8:10]), minute=int(args.start[10:12]))
    endDate = datetime.datetime(year=int(args.end[0:4]), month=int(args.end[4:6]), day=int(args.end[6:8]), hour=int(args.end[8:10]), minute=int(args.end[10:12]))
    with open("fort.221.generated", "w") as f:
#         Write header
        f.write("Oceanweather WIN/PRE Format                            " + args.start[0:-2] + "     " + args.end[0:-2] + "\n")
        time = startDate
        while(time <= endDate):
            writePressureSection(f, time)
            time = time + datetime.timedelta(seconds=int(args.delta))
        f.close()
    
    with open("fort.222.generated", "w") as f:
#         Write header
        f.write("Oceanweather WIN/PRE Format                            " + args.start[0:-2] + "     " + args.end[0:-2] + "\n")
        time = startDate
        while(time <= endDate):
            writeWindSection(f, time)
            time = time + datetime.timedelta(seconds=int(args.delta))
        f.close()
    
def writePressureSection(f, time):
    f.write("iLat= " + str(NUM_LATITUDES) + "iLong= " + str(NUM_LONGITUDES) + "DX=0.0833DY=0.0833SWLat= 4.01880SWLon=-101.000DT=" + time.strftime("%Y%m%d%H%M"))
    for index in range(NUM_PRESSURE_VALUES):
        if(index%8 == 0):
            f.write("\n")
        f.write(PRESSURE_FILL_VALUE)
        if(index ==(NUM_PRESSURE_VALUES - 1)):
            f.write("\n")

def writeWindSection(f, time):
    f.write("iLat= " + str(NUM_LATITUDES) + "iLong= " + str(NUM_LONGITUDES) + "DX=0.0833DY=0.0833SWLat= 4.01880SWLon=-101.000DT=" + time.strftime("%Y%m%d%H%M"))
    for index in range(NUM_WIND_VALUES):
        if(index%8 == 0):
            f.write("\n")
        f.write(WIND_FILL_VALUE)
        if(index ==(NUM_WIND_VALUES - 1)):
            f.write("\n")
    
if __name__ == "__main__":
    main()
