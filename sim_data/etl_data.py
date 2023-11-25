import re
import os
import pandas as pd

# Global csv data
global_columns = ["ProgId", "Cores", "Threads", "PageSize", "MemFrequency", "BlockSize", 
                  "Latency", "L1_Sets", "L1_Assoc", "L1_BlockSize", "L1_Latency",
                  "L2_Sets", "L2_Assoc", "L2_BlockSize", "L2_Latency",
                  "L3_Sets", "L3_Assoc", "L3_BlockSize", "L3_Latency", 
                  "Instructions", "InstructionsPerSecond", "SimTime", 
                  "Frequency", "Cycles", "CyclesPerSecond", "FastForwardInstructions",
                  "CommittedInstructions", "CommittedInstructionsPerCycle", "CommittedMicroInstructions", 
                  "CommittedMicroInstructionsPerCycle", "BranchPredictionAccuracy"]
global_data = []

# csv filepath
csvpath = './stats.csv'

# input statistics data path
inputPath = '../datagen/out/'
x86Path = '../datagen/x86_config/'
memPath = '../datagen/mem_config/'

# section keys (and prefixes) to include from differnt configs to csv
x86_sections = {"General": ""}
out_sections = {"x86": ""}
mem_sections = {"General": "Mem", "Module MainMemory": "", "CacheGeometry GeoNameL1": "L1_", 
                        "CacheGeometry GeoNameL2": "L2_", "CacheGeometry GeoNameL3": "L3_"}


def Merge(dict1, dict2, prefix = ""):
    for key, val in dict2.items():
        dict1[prefix+key] = val
    
    return dict1


def MergeStats(outStats, x86Stats, memStats):
    stats = {}
    
    for key, prefix in out_sections.items():
        stats = Merge(stats, outStats[key], prefix)

    for key, prefix in x86_sections.items():
        stats = Merge(stats, x86Stats[key], prefix)

    for key, prefix in mem_sections.items():
        stats = Merge(stats, memStats[key], prefix)

    return stats
 
def read_ini_file(filename, count=False):
    with open(filename, 'r') as f:
        stats = {}
        for line in f:
            if line.startswith(';'):
                continue

            elif line.startswith('['):
                section = line.split(" ]")[0].strip("[ ")

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

def put_in_arr(stats, progId): 
    for i in range(0, stats["size"]):
        row = []
        for key in global_columns:
            if key == "ProgId":
                row.append(progId)
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

            stats = read_ini_file(file_path, True)
            x86Stats = read_ini_file(x86Path + x86config + '.ini')
            memStats = read_ini_file(memPath + memconfig + '.ini')

            stats = MergeStats(outStats=stats, x86Stats=x86Stats, memStats=memStats)
                    
            put_in_arr(stats, progId)
        
    dumpcsv()

readData()
