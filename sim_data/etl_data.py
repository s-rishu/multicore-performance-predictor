import re
import os
import pandas as pd

# Global csv data
global_columns = ["ProgId", "Cores", "Threads", "MemConfig", "PageSize", "Instructions", "InstructionsPerSecond", "SimTime", 
                  "Frequency", "Cycles", "CyclesPerSecond", "FastForwardInstructions",
                  "CommittedInstructions", "CommittedInstructionsPerCycle", "CommittedMicroInstructions", 
                  "CommittedMicroInstructionsPerCycle", "BranchPredictionAccuracy"]
global_data = []

# csv filepath
csvpath = './stats.csv'

# input statistics data path
inputPath = '../datagen/out/'
x86Path = '../datagen/x86_config/'

def Merge(dict1, dict2):
    return(dict2.update(dict1))

def read_ini_file(filename, count=False):
    with open(filename, 'r') as f:
        stats = {}
        for line in f:
            if line.startswith(';'):
                continue

            elif line.startswith('['):
                section = line.split(" ")[1]

                if section not in stats:
                    stats[section] = {}
                if count:
                    stats[section]["size"] = 0
    
            elif '=' in line:
                key, value = line.strip().split('=')
                key = key.strip()

                if(key not in stats[section]):
                    stats[section][key] = [] 
                if value.startswith('[') and value.endswith(']'):
                    value = value.strip('[]').strip().split(',')

                value = re.sub(r'\[.*?\]', '', value)
                stats[section][key].append(value.strip())

                if count:
                    stats[section]["size"] = max(stats[section]["size"], len(stats[section][key]))

    return stats # Only returning x86 statistics

def put_in_arr(stats, progId, memconfig): 
    for i in range(0, stats["size"]):
        row = []
        for key in global_columns:
            if key == "ProgId":
                row.append(progId)
            elif key == "MemConfig":
                row.append(memconfig)
            elif key in stats:
                if len(stats[key]) > 1:
                    row.append(stats[key][i])
                else:
                    row.append(stats[key][0])
            else:
                row.append("")

        global_data.append(row)

def dumpcsv():
    df = pd.DataFrame(global_data, columns=global_columns)
    df.to_csv(csvpath, index=False) # adding data in csv

def readData():
    for filename in os.listdir(inputPath):
        
        nums = re.findall(r'\d+', filename)
        x86config = nums[len(nums)-2]
        memconfig = nums[len(nums)-1]
        progId = nums[0]

        file_path = os.path.join(inputPath, filename)
        if os.path.isfile(file_path):

            stats = read_ini_file(file_path, True)["x86"]
            x86Stats = read_ini_file(x86Path+x86config+'.ini')["General"]

            Merge(x86Stats, stats)
            put_in_arr(stats, progId, memconfig)
        
    dumpcsv()

readData()
