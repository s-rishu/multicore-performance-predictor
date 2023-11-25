import os
import itertools
import numpy as np
from collections import defaultdict

cores=[1,2,4,8,16,32,64,128]
threads=[1,2,4,8,16]

SINGLE_DIM_FIELDS = ["Module CacheL3", "Network Network$NET", "Module CacheL2-$CORE", "Module CacheL1-D-$CORE", "Module CacheL1-I-$CORE", "Entry Core-$CORE"]

def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def cartesian_product_mixed_type(*arrays):
    arrays = *map(np.asanyarray, arrays),
    dtype = np.dtype([(f'f{i}', a.dtype) for i, a in enumerate(arrays)])
    out = np.empty((*map(len, arrays),), dtype)
    idx = slice(None), *itertools.repeat(None, len(arrays) - 1)
    for i, a in enumerate(arrays):
        out[f'f{i}'] = a[idx[:len(arrays) - i]]
    return out.ravel()

def read_ini_file(filename):
    with open(filename, 'r') as f:
        config = {}
        for line in f:
            if line.startswith('['):
                start_index = line.find('[')
                end_index = line.find(']')
                section = line[start_index + 2:end_index-1].strip()
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
    print("generating permutations..")
    fields = list(config.keys())
    #print(fields)
    field_values = [np.array(config[field][param]) for field in config for param in config[field] if field not in SINGLE_DIM_FIELDS]
    print(field_values)
    all_permutations = cartesian_product_mixed_type(*field_values) #list(product(*field_values))
    print(all_permutations)
    result = []

    for value in all_permutations:
        value_idx = 0
        permutation_dict = {}
            
        for i, field in enumerate(fields):
            if field in SINGLE_DIM_FIELDS:
                permutation_dict[field] = config[field]
            else:
                field_dict = {}
                for j, param in enumerate(config[field]):
                    field_dict[param] = value[j+value_idx]
                    print(j + value_idx)
                permutation_dict[field] = field_dict
                value_idx = j+value_idx+1
        result.append(permutation_dict)
    print("done generating permutations..")
    return result

def process_permutations(perm, core, thread):
    new_result = []
    print("processing for cores: {}, threads: {}".format(core, thread))
    for config in perm:
        print(config.keys())
        entry_temp = config.pop("Entry Core-$CORE-$THREAD")
        module_cache_l1i_temp =  config.pop("Module CacheL1-I-$CORE")
        module_cache_l1d_temp =  config.pop("Module CacheL1-D-$CORE")
        module_cache_l2_temp =  config.pop("Module CacheL2-$CORE")
        network_temp =  config.pop("Network Network$NET")
        new_config = config
        for c in range(core):
            print("processing for cores: {}".format(core))
            #entry  
            for t in range(thread):
                new_key = "Entry Core-{}-{}".format(c,t)
                new_config[new_key] = {}
                for key, value in entry_temp.items():
                    new_config[new_key][key] = value.replace("$CORE",str(c)).replace("$THREAD", str(t))
            #l1i
            new_key = "Module CacheL1-I-{}".format(c)
            new_config[new_key] = {}
            for key, value in  module_cache_l1i_temp.items():
                new_config[new_key][key] = value.replace("$CORE", str(c))

            #l1d
            new_key = "Module CacheL1-D-{}".format(c)
            new_config[new_key] = {}
            for key, value in  module_cache_l1d_temp.items():
                new_config[new_key][key] = value.replace("$CORE", str(c))

            #l2
            new_key = "Module CacheL2-{}".format(c)
            new_config[new_key] = {}
            for key, value in  module_cache_l2_temp.items():
                new_config[new_key][key] = value.replace("$CORE", str(c))

            #l2l1 network
            new_key = "Network NetworkL2L1-{}".format(c)
            new_config[new_key] = network_temp

        #network
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
     print(cc)

if __name__ == '__main__':
    mem_filename = 'test.ini'
    mem_config = read_ini_file(mem_filename)
    #print(mem_config)
    mem_config = generate_permutations(mem_config)
    print(mem_config)
    import copy
    for core in cores:
        for thread in threads:
             new_mem_config = process_permutations(copy.deepcopy(mem_config), core, thread)
             print_permutations(new_mem_config, core, thread)