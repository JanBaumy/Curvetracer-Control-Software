#this is a separate plotting file for the GUI
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import os

#read file (returns empty data when no file exists)
def get_raw_data(file_path):
    if os.path.exists(file_path):
        data = np.genfromtxt(file_path, delimiter=';', skip_header=1)
        return data
    else:
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

    if has_temperature:
        return ((range(len(voltage)), voltage), (voltage, current), (range(len(temperature)), temperature))
    else:
        return ((range(len(voltage)), voltage), (voltage, current))
        
#update function needs the axs object and data in the format (voltage, current (,temperature))
def update(i, axs, config):
    file_path = config.get('file_path')
    has_temperature = True if config.get('has_temperature') == True else False
    data = get_raw_data(file_path)
    #only plot when there is data
    if data.size > 0:
        animation_data = extract_data(data, has_temperature)

        colors = ['yellow', 'lawngreen', 'deepskyblue']

        plot_nr = 0
        for ax in axs:
            ax.plot(animation_data[plot_nr][0][:i], animation_data[plot_nr][1][:i], color=colors[plot_nr])
            plot_nr += 1

#style the plot 
def init_plot(config):
    has_temperature = True if config.get('has_temperature') == True else False

    plt.style.use('dark_background')
    gs = GridSpec(nrows=2, ncols=2)

    if has_temperature:
        fig, axs = plt.subplots(3, 1)
        axs[0].set_subplotspec(gs[0, 0])

        axs[1].set_subplotspec(gs[:, 1])

        axs[2].set_subplotspec(gs[1, 0])
        axs[2].set_title('Temperature vs Time')
        axs[2].set_xlabel('Measurement step')
        axs[2].set_ylabel('Temperature [°C]')

    else:
        fig, axs = plt.subplots(2, 1)
        axs[0].set_subplotspec(gs[:, 0])

        axs[1].set_subplotspec(gs[:, 1])

    #the same whether temperature is plotted or not
    axs[0].set_title('Voltage vs Time')
    axs[0].set_xlabel('Measurement step')
    axs[0].set_ylabel('Voltage [V]')

    axs[1].set_title('Current vs Voltage')
    axs[1].set_xlabel('Voltage [V]')
    axs[1].set_ylabel('Current [A]')
    axs[1].set_yscale('log')

    for ax in axs:
        ax.grid(color='white', linestyle='-', linewidth=0.2)

    fig.suptitle('Real-Time Data')
    #fig.set_figheight(6)
    #fig.set_figwidth(10)
    fig.tight_layout(pad=1.0)

    return fig, axs