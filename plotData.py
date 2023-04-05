#function to generate all plots
import matplotlib.pyplot as plt
import numpy as np
import os
from configLoader import import_config
from matplotlib.animation import FuncAnimation

def draw_plots(config):
    #read file (returns empty data when no file exists)
    def read_file(file_path):
        if os.path.exists(file_path):
            data = np.genfromtxt(file_path, delimiter=';', skip_header=1)
            return data
        else:
            print("WARNING: No data file found")
            return np.empty(shape=(0,0))
    
    #extract data from file (returns 3 lists when has_temperature is True, 2 lists when has_temperature is False)
    def extract_data(data, has_temperature):
        if not data.size > 0:
            print("WARNING: No data found in file")
            return [], [], [] if has_temperature else [], []

        voltage, current = [], []
        temperature = [] if has_temperature else None

        #edge case for only a single line of data
        if data.ndim == 1:
            if has_temperature:
                temperature.append(data[1])
                voltage.append(data[2])
                current.append(data[3])
            else:
                voltage.append(data[0])
                current.append(data[1])

        #normal case for more than 1 line of data
        else:
            for subarray in data:
                if has_temperature:
                    temperature.append(subarray[1])
                    voltage.append(subarray[2])
                    current.append(subarray[3])
                else:
                    voltage.append(subarray[0])
                    current.append(subarray[1])

        return (voltage, current, temperature) if has_temperature else (voltage, current)
    
    #update function needs the axs object and data in the format (voltage, current (,temperature))
    def update(i, axs):
        data = read_file(file_path)

        #only plot when there is data
        if data.size > 0:
            animation_data = extract_data(data, has_temperature)

            plot_nr = 0
            for ax in axs:
                ax.plot(animation_data[plot_nr][:i], color='lawngreen')
                plot_nr += 1

    has_temperature = True if config.get('has_temperature') == True else False
    file_path = config.get('file_path')

    plt.style.use('dark_background')

    if has_temperature:
        fig, axs = plt.subplots(3, 1)
        axs[0].set_title('Voltage vs Time')
        axs[1].set_title('Current vs Voltage')
        axs[2].set_title('Temperature vs Time')
    else:
        fig, axs = plt.subplots(2, 1)
        axs[0].set_title('Voltage vs Time')
        axs[1].set_title('Current vs Voltage')

    #stylize the plots
    fig.suptitle('Real-Time Data')
    fig.tight_layout(pad=1.0)

    for ax in axs:
        ax.grid(color='white', linestyle='-', linewidth=0.2)

    #plotting at an interval of 10ms
    anim = FuncAnimation(fig, update, fargs=(axs,), cache_frame_data=False, interval=10)
 
    return anim