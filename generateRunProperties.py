import os
import argparse
from urllib.request import urlretrieve
from datetime import datetime

def main():
    p = argparse.ArgumentParser(description="Make a request to generate run properties")
    p.add_argument(
        "--indir", help="ADCIRC run directory, used for generating run properties file", type=str
    )
    args = p.parse_args()
    args.epsg = 4326
    startFound = False
    endFound = False
    tcFound = False
    storm = ""
    advisory = ""
    year = ""

    properties_directory = "properties/"
    if not os.path.exists(properties_directory):
        os.makedirs(properties_directory)
    with open(args.indir + "/adcirc_simulation.1") as f:
        for line in f:
            if "SIMULATION_START" in line:
                rawstart = line [-16:][:-2]
                startFound = True
            elif "SIMULATION_END" in line:
                rawend = line [-16:][:-2]
                endFound = True
            elif "get_advisory_time.py" in line:
                storm = line[line.index("storm") + 6: line.index("--advisory") - 1]
                advisory = line[line.index("--advisory") + 11: line.index("--basin") - 1]
                year = line[line.index("--year") + 7: line.index("--end") - 1]
                tcFound = True
            elif " _______________________________________________________________________________" in line:
                break
            if(startFound and endFound and tcFound):
                break
    start = datetime.strptime(rawstart, "%y-%m-%d %H:%M")
    start = start.strftime("%Y%m%d%H%M%S")
    end = datetime.strptime(rawend, "%y-%m-%d %H:%M")
    end = end.strftime("%Y%m%d%H%M%S")
    metgetstart = datetime.strptime(rawstart, "%y-%m-%d %H:%M")
    metgetstart = metgetstart.strftime("%Y-%m-%d %H:%M")
    metgetend = datetime.strptime(rawend, "%y-%m-%d %H:%M")
    metgetend = metgetend.strftime(("%Y-%m-%d %H:%M"))
    print("start, end, storm, advisory, year", start, end, storm, advisory, year, flush=True)
    with open("properties/run.properties", "w") as f:
        f.write("forecastValidStart : " + start + "\n")
        f.write("forecastValidEnd : " + end + "\n")
        f.write("rawstart: " + rawstart + "\n")
        f.write("rawend: " + rawend + "\n")
        f.write("metgetstart: " + metgetstart + "\n")
        f.write("metgetend: " + metgetend + "\n")
        if(tcFound):
            f.write("stormnumber : " + storm + "\n")
            f.write("advisory : " + advisory + "\n")
            f.write("year : " + year + "\n")
        f.close()
    if(tcFound):
        url = "http://www.nhc.noaa.gov/gis/forecast/archive/al" + storm + year + "_5day_001.zip"
        urlretrieve(url, properties_directory + "al" + storm + year + "_5day_001.zip")
    

if __name__ == "__main__":
    main()
