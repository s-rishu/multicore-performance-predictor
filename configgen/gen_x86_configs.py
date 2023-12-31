import os
from itertools import product
from collections import defaultdict


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
    #            print(value)
    # print(config)
    return config

def generate_permutations(config):
    fields = list(config.keys())
    field_values = [config[field][param] for field in config for param in config[field]]
    all_permutations = list(product(*field_values))

    result = [{fields[i]: {param: value[j] for j, param in enumerate(config[fields[i]])} for i, field in enumerate(fields)} for value in all_permutations]
    #print(result)
    return result

def print_permutations(perm):
  config_count = defaultdict(int)
  for config in perm:

    cores = int(config["General"]["Cores"])
    threads = int(config["General"]["Threads"])

    config_count["{}_{}".format(cores, threads)] += 1
    cc = config_count["{}_{}".format(cores, threads)]

    config_dir = "configs/x86_configs/{}".format(cores)
    create_directory(config_dir)

    config_path = config_dir + "/{}.ini".format(cc)
    with open(config_path, "w") as file:
     for section, values in config.items():
        file.write("[ {} ]\n".format(section))
        for key, value in values.items():
           file.write('{} = {}\n'.format(key, value))
        file.write('\n')
     print(cc)

if __name__ == '__main__':
    filename = 'x86_config.ini'
    config = read_ini_file(filename)
    config = generate_permutations(config)
    print_permutations(config)
