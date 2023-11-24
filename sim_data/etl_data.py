import re
import os
import pandas as pd

# Global csv data
global_columns = ["ProgId", "x86Config", "MemConfig", "RealTime", "Instructions", "InstructionsPerSecond", "SimTime", "Frequency", "Cycles", "CyclesPerSecond", "FastForwardInstructions",
                   "CommittedInstructions", "CommittedInstructionsPerCycle", "CommittedMicroInstructions", "CommittedMicroInstructionsPerCycle", "BranchPredictionAccuracy"]
global_data = []

# csv filepath
csvpath = './stats.csv'

# input statistics data path
inputPath = '../datagen/out/'

def read_ini_file(filename):
    with open(filename, 'r') as f:
        stats = {}
        for line in f:
            if line.startswith(';'):
                continue
            elif line.startswith('['):
                section = line.split(" ")[1]
                if(section not in stats):
            #       print(section)
                    stats[section] = {"size": 0}
            elif '=' in line:
                key, value = line.strip().split('=')
                key = key.strip()
     #           print(key)
                if(key not in stats[section]):
                    stats[section][key] = [] 
                if value.startswith('[') and value.endswith(']'):
                    value = value.strip('[]').strip().split(',')
                value = re.sub(r'\[.*?\]', '', value)
                stats[section][key].append(value.strip())
                stats[section]["size"] = max(stats[section]["size"], len(stats[section][key]))
    #            print(value)
    # print(stats)
    return stats["x86"] # Only returning x86 statistics

def put_in_arr(stats, progId, x86config, memconfig): 
    for i in range(0, stats["size"]):
        row = []
        for key in global_columns:
            if key == "ProgId":
                row.append(progId)
            elif key == "MemConfig":
                row.append(memconfig)
            elif key == "x86Config":
                row.append(x86config)
            elif key in stats:
                row.append(stats[key][i])
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
            stats = read_ini_file(file_path)
            put_in_arr(stats, progId, x86config, memconfig)
        
    dumpcsv()

readData()
