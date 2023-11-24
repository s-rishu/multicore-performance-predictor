import itertools

def read_ini_file(filename):
    with open(filename, 'r') as f:
        config = {}
        for line in f:
            if line.startswith('['):
                section = line.strip('[]').strip()
                print(section)
                config[section] = {}
            elif '=' in line:
                key, value = line.strip().split('=')
                key = key.strip()
                print(key)
                if value.startswith('[') and value.endswith(']'):
                    value = value.strip('[]').strip().split(',')
                config[section][key] = value
                print(value)
    print(config)
    return config

def generate_permutations(config):
    for section, values in config.items():
        for key, value in values.items():
            if isinstance(value, list):
                config[section][key] = itertools.permutations(value)
    return config

def print_permutations(config):
    for section, values in config.items():
        print(f'[{section}]')
        for key, value in values.items():
            if isinstance(value, itertools.permutations):
                for permutation in value:
                    print(f'{key} = {permutation}')
            else:
                print(f'{key} = {value}')

if __name__ == '__main__':
    filename = 'config.ini'
    config = read_ini_file(filename)
    config = generate_permutations(config)
    print_permutations(config)
