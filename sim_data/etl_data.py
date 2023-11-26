import re
import os
import pandas as pd

# Global csv data
global_columns = ["ProgId", "pThreads", "Mem_HitRate",
                  "Mem_Latency", "L1_Sets", "L1_Latency", "L1_HitRate",
                  "L2_Sets", "L2_Latency", "L2_HitRate", "L3_HitRate",
                  "Instructions", "InstructionsPerSecond", "SimTime",
                  "Frequency", "Cycles", "CyclesPerSecond", "FastForwardInstructions",
                  "CommittedInstructions", "CommittedInstructionsPerCycle", "CommittedMicroInstructions", 
                  "CommittedMicroInstructionsPerCycle", "BranchPredictionAccuracy"]
global_data = []

# csv filepath
csvpath = './stats.csv'

# input statistics data path
detailsPath = '../datagen/out/'
memoutPath = '../datagen/memout/'
sysoutPath = '../datagen/sysout/'
x86Path = '../configgen/configs/x86_configs/'
memPath = '../configgen/configs/mem_configs/'

# section keys (and prefixes) to include from differnt configs to csv
x86_sections = {"General": ""}
out_sections = {"x86": ""}
mem_sections = {"Module MainMemory": "Mem_", "CacheGeometry GeoNameL1": "L1_", 
                        "CacheGeometry GeoNameL2": "L2_"}


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
 
def read_ini_file(filename):
    with open(filename, 'r') as f:
        stats = {}
        for line in f:
            if line.startswith(';'):
                continue

            elif line.startswith('['):
                section = line.split(" ]")[0].strip("[ ")

                if section not in stats:
                    stats[section] = {}
    
            elif '=' in line:
                key, value = line.strip().split('=')
                key = key.strip()
 
                if value.startswith('[') and value.endswith(']'):
                    value = value.strip('[]').strip().split(',')

                value = re.sub(r'\[.*?\]', '', value)
                stats[section][key] = value.strip()

    return stats # Only returning x86 statistics

def get_hit_rate(memfile) :
    hitRates = {"Mem_HitRate": 0, "L1_HitRate": 0, "L2_HitRate": 0, "L3_HitRate": 0}
    memout = read_ini_file(memfile)
    for key, val in memout.items():
        if key == "MainMemory":
            hitRates["Mem_HitRate"] = max(float(val["HitRatio"]), hitRates["Mem_HitRate"])
        elif key == "CacheL3":
            hitRates["L3_HitRate"] = max(float(val["HitRatio"]), hitRates["L3_HitRate"])
        elif key.startswith("CacheL1"):
            hitRates["L1_HitRate"] = max(float(val["HitRatio"]), hitRates["L1_HitRate"])
        elif key.startswith("CacheL2"):
            hitRates["L2_HitRate"] = max(float(val["HitRatio"]), hitRates["L2_HitRate"])
    
    for key, val in hitRates.items():
        if val == 0:
            hitRates[key] = 1

    return hitRates

def put_in_arr(stats, progId, hitRates, pthreads): 
    row = []
    for key in global_columns:
        if key == "ProgId":
            row.append(progId)
        elif key == "pThreads":
            row.append(pthreads)
        elif key in stats:
            row.append(stats[key])
        elif key in hitRates:
            row.append(hitRates[key])
        else:
            row.append("")

    global_data.append(row)
        

def dumpcsv():
    df = pd.DataFrame(global_data, columns=global_columns)
    df.to_csv(csvpath, index=False) # adding data in csv

def readData():
    for filename in os.listdir(detailsPath):
        
        [progId, input, pthreads, cores, x86config, memconfig] = re.findall(r'\d+', filename)

        file_path = os.path.join(detailsPath, filename)
        if os.path.isfile(file_path):

            stats = read_ini_file(file_path)
            x86Stats = read_ini_file(x86Path + cores + '/' + x86config + '.ini')
            memStats = read_ini_file(memPath + cores + '/' + memconfig + '.ini')

            hitRates = get_hit_rate(os.path.join(memoutPath, filename))
            stats = MergeStats(outStats=stats, x86Stats=x86Stats, memStats=memStats)
                    
            put_in_arr(stats, progId, hitRates, pthreads)
        
    dumpcsv()

readData()
