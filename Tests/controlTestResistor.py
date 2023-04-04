#CLI test for resistor
from sys import path
path.append('../Curvetracer Control Software')
from configLoader import import_config, check_config
from modes import no_temperature, temperature_sweep

def main():
    #get config
    config_path = r'Basic Configs\invalid_config.json'
    config = import_config(config_path)
    #check config
    valid_config = check_config(config)
    if valid_config != True:
        print(valid_config)
        return

    print('-----CONFIG:-----')
    for key in config:
        print(f'{key}: {config[key]}')
    print('-----------------')
    file_path = input('INPUT: Enter the name of the file to save the data to (with .csv): ')
    config['file_path'] = config.get('save_folder') + f'\{file_path}'
    print(f'INFO: File will be saved to: {config.get("file_path")}')

    print("INFO: Measurement starting----------------")
    #start measurement
    if config.get('has_temperature') == True:
        #temperature_sweep(config)
        pass
    else:
        #no_temperature(config)
        pass

if __name__ == '__main__':
    main()