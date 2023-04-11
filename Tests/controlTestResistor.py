#CLI test for resistor
from sys import path
path.append('../Curvetracer-Control-Software')
from configLoader import import_config, check_config
from saveData import check_and_create_file
from modes import no_temperature, temperature_sweep
from plotData import draw_plots
import matplotlib.pyplot as plt
from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
import multiprocessing as mp

def main():
    #get config
    config_path = r'Basic Configs\1M2_resistor_test_with_temp.json'
    config = import_config(config_path)
    #check config and change values if needed
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
    check_and_create_file(config.get('file_path'), has_temperature = config.get('has_temperature'))
    print(f'INFO: File will be saved to: {config.get("file_path")}')

    print("INFO: Measurement starting----------------")
    #start measurement
    if config.get('has_temperature') == True:
        p1 = mp.Process(target=fake_temperature_sweep, args=(config,))
    else:
        p1 = mp.Process(target=fake_no_temperature, args=(config,))

    #start measurement in parallel thread
    p1.start()
    plot = draw_plots(config) #keep reference to plot so it does not get deleted
    plt.show()
    #stop measurement process after it is done
    p1.join()

if __name__ == '__main__':
    main()