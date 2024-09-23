# Reads FUNWAVE input.txt file and returns start date and timedelta object
# Pranav 9/25/2023

from datetime import datetime, timedelta
        
class FunInputReader:
    def __init__(self, INPUT_FILE=None):
        with open(INPUT_FILE) as file:
            lines = file.readlines()
            for line in lines:
                if("TOTAL_TIME" in line):
                    totalTime = line[line.find("=") + 2: -1]
                if("PLOT_INTV" in line):
                    plotInterval = line[line.find("=") + 2: -1]
        print(totalTime, plotInterval)
        self.startDateObject = datetime(year=2024, month=1, day=1)
        self.timeDelta = timedelta(seconds=2)
    def getTimes(self):
        return self.startDateObject, self.timeDelta
