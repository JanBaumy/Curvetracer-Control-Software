#function to generate all plots
import matplotlib.pyplot as plt
import numpy as np
import os
from configLoader import import_config
from matplotlib.animation import FuncAnimation

def draw_plots(config):
    #read file
    def read_file(file_path):
        if os.path.exists(file_path):
            data = np.genfromtxt(file_path, delimiter=';', skip_header=1)
        else:
            print("WARNING: No data file found")
            data = np.empty(shape=(0,0))
        return data
    
    #extract data from file
    def extract_data(data, has_temperature):
        if not data.size > 0:
            print("WARNING: No data found in file")
            return [], [], [] if has_temperature else [], []

        voltage, current = [], []
        temperature = [] if has_temperature else None
        for subarray in data:
            if has_temperature:
                temperature.append(subarray[1])
            voltage.append(subarray[2])
            current.append(subarray[3])

        return (voltage, current, temperature) if has_temperature else (voltage, current)
    
    #update function needs the axs object and data in the format (voltage, current (,temperature))
    def update(i, axs):
        animation_data = extract_data(data, has_temperature)

        plot_nr = 0
        for ax in axs:
            ax.plot(animation_data[plot_nr][:i], color='royalblue')
            plot_nr += 1

    has_temperature = True if config.get('has_temperature') == True else False
    file_path = config.get('file_path')
    data = read_file(file_path)

    if has_temperature:
        fig, axs = plt.subplots(3, 1)
    else:
        fig, axs = plt.subplots(2, 1)

    anim = FuncAnimation(fig, update, fargs=(axs,), cache_frame_data=False, interval=500)
 
    plt.show()

config = import_config(r'Basic Configs\1M2_resistor_test_with_temp.json')
draw_plots(config)