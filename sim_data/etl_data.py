import re
import os
import pandas as pd

# Global csv data
global_columns = ["ProgId", "pThreads", "Mem_Hits", "Mem_Misses",
                  "Mem_Latency", "L1_Sets", "L1_Latency", "L1_Hits", "L1_Misses",
                  "L2_Sets", "L2_Latency", "L2_Hits", "L2_Misses", "L3_Hits", "L3_Misses",
                  "Instructions", "InstructionsPerSecond", "SimTime",
                  "Cycles", "CyclesPerSecond",
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
    section = ""
    stats = {}
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith(';'):
                continue

            elif line.startswith('['):
                section = line.split(" ]")[0].strip("[ ")

                if section not in stats:
                    stats[section] = {}
    
            elif '=' in line and section != '':
                key, value = line.strip().split('=')
                key = key.strip()
 
                if value.startswith('[') and value.endswith(']'):
                    value = value.strip('[]').strip().split(',')

                value = re.sub(r'\[.*?\]', '', value)
                stats[section][key] = value.strip()

    return stats # Only returning x86 statistics

def get_hit_rate(memfile) :
    hitRates = {"Mem_Hits": 0, "L1_Hits": 0, "L2_Hits": 0, "L3_Hits": 0, "Mem_Misses": 0, "L1_Misses": 0, "L2_Misses": 0, "L3_Misses": 0}
    memout = read_ini_file(memfile)
    for key, val in memout.items():
        if key == "MainMemory":
            hitRates["Mem_Hits"] = max(float(val["Hits"]), hitRates["Mem_Hits"])
            hitRates["Mem_Misses"] = max(float(val["Misses"]), hitRates["Mem_Misses"])
        elif key == "CacheL3":
            hitRates["L3_Hits"] = max(float(val["Hits"]), hitRates["L3_Hits"])
            hitRates["L1_Misses"] = max(float(val["Misses"]), hitRates["L1_Misses"])
        elif key.startswith("CacheL1"):
            hitRates["L1_Hits"] = max(float(val["Hits"]), hitRates["L1_Hits"])
            hitRates["L1_Misses"] = max(float(val["Misses"]), hitRates["L1_Misses"])
        elif key.startswith("CacheL2"):
            hitRates["L2_Hits"] = max(float(val["Hits"]), hitRates["L2_Hits"])
            hitRates["L3_Misses"] = max(float(val["Misses"]), hitRates["L3_Misses"])
    
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
        memoutfile = os.path.join(memoutPath, filename)

        if os.path.isfile(memoutfile) and os.path.isfile(file_path):
            stats = read_ini_file(file_path)
            x86Stats = read_ini_file(x86Path + cores + '/' + x86config + '.ini')
            memStats = read_ini_file(memPath + cores + '/' + memconfig + '.ini')

            if len(stats) and len(x86Stats) and len(memStats):
                hitRates = get_hit_rate(memoutfile)
                stats = MergeStats(outStats=stats, x86Stats=x86Stats, memStats=memStats)
                        
                put_in_arr(stats, progId, hitRates, pthreads)
    dumpcsv()

readData()
