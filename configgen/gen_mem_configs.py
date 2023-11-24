import os
from itertools import product
from collections import defaultdict

cores=[1,2,4,8,16,32,64,128]
threads=[1,2,4,8,16]

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def read_ini_file(filename):
    with open(filename, 'r') as f:
        config = {}
        for line in f:
            if line.startswith('['):
                section = line.split(" ")[1]
      #          print(section)
                config[section] = {}
            elif '=' in line:
                key, value = line.strip().split('=')
                key = key.strip()
     #           print(key)
                if value.startswith('[') and value.endswith(']'):
                    value = value.strip('[]').strip().split(',')
                config[section][key] = value
    return config

def generate_permutations(config):
    fields = list(config.keys())
    field_values = [config[field][param] for field in config for param in config[field]]
    all_permutations = list(product(*field_values))

    result = [{fields[i]: {param: value[j] for j, param in enumerate(config[fields[i]])} for i, field in enumerate(fields)} for value in all_permutations]
    return result

def process_permutations(perm, core, thread):
    new_result = []
    for config in perm:
        entry_temp = config.pop("Entry Core-$CORE-$THREAD")
        module_cache_l1i_temp =  config.pop("Module CacheL1-I-$CORE")
        module_cache_l1d_temp =  config.pop("Module CacheL1-D-$CORE")
        module_cache_l2_temp =  config.pop("Module CacheL2-$CORE")
        network_temp =  config.pop("Network Network$NET")
        cache_geo_temp = config.pop("CacheGeometry GeoName$CACHE")
        new_config = config    
        for c in range(core):      
            #entry  
            for t in range(thread):
                new_key = "Entry Core-{}-{}".format(c,t)
                new_config[new_key] = {}
                for key, value in entry_temp.items():
                    new_config[new_key][key] = value.replace("$CORE", c).replace("$THREAD", t)
            #l1i
            new_key = "Module CacheL1-I-{}".format(c)
            new_config[new_key] = {}
            for key, value in  module_cache_l1i_temp.items():
                new_config[new_key][key] = value.replace("$CORE", c)

            #l1d
            new_key = "Module CacheL1-D-{}".format(c)
            new_config[new_key] = {}
            for key, value in  module_cache_l1d_temp.items():
                new_config[new_key][key] = value.replace("$CORE", c)

            #l2
            new_key = "Module CacheL2-{}".format(c)
            new_config[new_key] = {}
            for key, value in  module_cache_l2_temp.items():
                new_config[new_key][key] = value.replace("$CORE", c)

            #l2l1 network
            new_key = "Network NetworkL2L1-{}".format(c)
            new_config[new_key] = network_temp

        #geo
        for cache in ["L1", "L2", "L3"]:
            new_key = "CacheGeometry GeoName{}".format(cache)
            new_config[new_key] = cache_geo_temp

        #geo
        for net in ["MainL3", "L3L2"]:
            new_key = "Network Network{}".format(net)
            new_config[new_key] = network_temp

        new_result.append(new_config)
        
    return new_result

def print_permutations(perm, cores, threads):
  config_count = defaultdict(int)

  for config in perm:
    config_count["{}_{}".format(cores, threads)] += 1
    cc = config_count["{}_{}".format(cores, threads)]

    config_dir = "configs/mem_configs/{}/{}".format(cores, threads)
    create_directory(config_dir)
    
    config_path = config_dir + "/mem_config_{}.ini".format(cc)
    with open(config_path, "w") as file:
     for section, values in config.items():
        file.write("[ {} ]\n".format(section))
        for key, value in values.items():
           file.write('{} = {}\n'.format(key, value))
        file.write('\n')
     config_count += 1
     print(config_count)

if __name__ == '__main__':
    mem_filename = 'mem_config.ini'
    mem_config = read_ini_file(mem_filename)
    mem_config = generate_permutations(mem_config)
    for core in cores:
        for thread in threads:
             mem_config = process_permutations(mem_config, core, thread)
             print_permutations(mem_config, core, thread)
        
