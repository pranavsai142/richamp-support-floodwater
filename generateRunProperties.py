import os
import argparse
from urllib.request import urlretrieve
from datetime import datetime
from zipfile import ZipFile

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
                simulationStartIndex = line.index("SIMULATION_START")
                rawstart = line[simulationStartIndex + 18: simulationStartIndex + 34]
                print(rawstart, flush=True)
                startFound = True
            elif "SIMULATION_END" in line:
                simulationEndIndex = line.index("SIMULATION_END")
                rawend = line[simulationEndIndex + 16: simulationEndIndex + 32]
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
    start = datetime.strptime(rawstart, "%Y-%m-%d %H:%M")
    start = start.strftime("%Y%m%d%H%M%S")
    end = datetime.strptime(rawend, "%Y-%m-%d %H:%M")
    end = end.strftime("%Y%m%d%H%M%S")
    print("start, end, storm, advisory, year", start, end, storm, advisory, year, flush=True)
    with open(properties_directory + "run.properties", "w") as f:
        f.write("forecastValidStart : " + start + "\n")
        f.write("forecastValidEnd : " + end + "\n")
        f.write("rawstart: " + rawstart + "\n")
        f.write("rawend: " + rawend + "\n")
        if(tcFound):
            f.write("stormtype : nhc\n")
            f.write("stormnumber : " + storm + "\n")
            f.write("advisory : " + advisory + "\n")
            f.write("year : " + year + "\n")
            if("veerLeftEdge" in args.indir):
                f.write("track : veerLeftEdge\n")
            elif("veerRightEdge" in args.indir):
                f.write("track : veerRightEdge\n")    
            else:
                f.write("track : center\n")      
        else:
            f.write("stormtype : gfs\n")
        f.close()
    if(tcFound):
        if(len(storm) == 1):
            storm = "0" + storm
        filename = "al" + storm + year + "_5day_" + advisory + ".zip"
        url = "http://www.nhc.noaa.gov/gis/forecast/archive/" + filename
        urlretrieve(url, properties_directory + filename)

        # loading the temp.zip and creating a zip object 
        with ZipFile(properties_directory + filename, 'r') as zObject: 
  
            # Extracting all the members of the zip  
            # into a specific location. 
            zObject.extractall( 
                path=properties_directory) 
            files = os.listdir(properties_directory)
            for file in files:
                fileExtension = file[file.index("."):]
                if "ww_wwlin" in file:
                    os.remove(properties_directory + file)
                elif "lin" in file:
                    os.rename(properties_directory + file, properties_directory + "track" + fileExtension)
                elif "pgn" in file:
                    os.rename(properties_directory + file, properties_directory + "cone" + fileExtension)
                elif "pts" in file:
                    os.rename(properties_directory + file, properties_directory + "points" + fileExtension)
                
    

if __name__ == "__main__":
    main()
