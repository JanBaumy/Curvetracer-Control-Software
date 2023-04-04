#CLI test for resistor
from sys import path
path.append('../Curvetracer Control Software')
from configLoader import import_config, check_config
from modes import no_temperature, temperature_sweep

def main():
    #get config
    config_path = r'Basic Configs\1M2_resistor_test_no_temp.json'
    config = import_config(config_path)
    if not check_config(config):
        print('ERROR: Config file is invalid!')
        return

    print('-----CONFIG:-----')
    for key in config:
        print(f'{key}: {config[key]}')
    print('-----------------')
    file_path = input('INPUT: Enter the name of the file to save the data to (with .csv): ')
    config['file_path'] = config.get('save_folder') + f'\{file_path}'
    print(f'INFO: File will be saved to: {config.get("file_path")}')

    #start measurement
    if config.get('has_temperature') == True:
        temperature_sweep(config)
    else:
        no_temperature(config)

if __name__ == '__main__':
    main()