# Reads FUNWAVE input.txt file and returns start date and timedelta object
# Pranav 9/25/2023

from datetime import datetime, timedelta, timezone
        
class FunInputReader:
    def __init__(self, INPUT_FILE=None):
        with open(INPUT_FILE) as file:
            lines = file.readlines()
            for line in lines:
                if("TOTAL_TIME" in line):
                    totalTime = float(line[line.find("=") + 2: -2])
                if("PLOT_INTV " in line):
                    plotInterval = float(line[line.find("=") + 2: -2])
                if("DX" in line):
                    deltaX = float(line[line.find("=") + 2: -2])
                if("DY" in line):
                    deltaY = float(line[line.find("=") + 2: -2])
                    break
        print(totalTime, plotInterval)
        self.startDateObject = datetime(year=2024, month=1, day=1, tzinfo=timezone.utc)
        self.timeDelta = timedelta(seconds=plotInterval)
        self.gridDelta = (deltaX, deltaY)
    def getTimes(self):
        return self.startDateObject, self.timeDelta
