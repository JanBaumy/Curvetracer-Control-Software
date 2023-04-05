#function to generate all plots
import matplotlib.pyplot as plt
import numpy as np
import os
from configLoader import import_config
from matplotlib.animation import FuncAnimation

#function to plot voltage vs time (i is just for the animation)
def voltageVsTime(config):
    file_path = config.get('file_path')
    has_temperature = True if config.get('has_temperature') == True else False

    #make a figure
    fig = plt.figure()
    ax = plt.axes(xlabel='Data point', ylabel='Voltage (V)', title='Voltage vs Time')
    ax.grid(color='lightgray', linestyle='-', linewidth=0.5)

    #get data from file
    def get_data(file_path, file_has_temperature):
        if file_has_temperature:
            voltage_column = 2
        else:
            voltage_column = 0

        #if there is no file, return empty data
        if os.path.exists(file_path):
            voltage = np.genfromtxt(file_path, delimiter=';', skip_header=1, usecols=(voltage_column))
        else:
            print("WARNING: No data file found")
            voltage = []
        return voltage

    #update function for the animation
    def update(i):
        voltage = get_data(file_path, has_temperature)
        ax.plot(voltage[:i], color='royalblue')

    anim = FuncAnimation(fig, update, cache_frame_data=False, interval=500)
    plt.show()

#function to plot voltage vs time (i is just for the animation)
def currentVsVoltage(config):
    #get necessary information from config
    file_path = config.get('file_path')
    has_temperature = True if config.get('has_temperature') == True else False

    #make a figure
    fig = plt.figure()
    ax = plt.axes(xlabel='Voltage (V)', ylabel='Current (A)', title='Current vs Voltage')
    ax.grid(color='lightgray', linestyle='-', linewidth=0.5)

    #get data from file
    def get_data(file_path, file_has_temperature):
        if file_has_temperature:
            voltage_column, current_column = 2, 3
        else:
            voltage_column, current_column = 0, 1

        #if there is no file, return empty data
        if os.path.exists(file_path):
            data = np.genfromtxt(file_path, delimiter=';', skip_header=1, usecols=(voltage_column, current_column))
            if not data.size > 0:
                print("WARNING: No data found in file")
                return [], []
        else:
            print("WARNING: No data file found")
            return [], []
        
        #split file data into voltage and current for easier plotting
        voltage, current = [], []
        if data.ndim == 1:
            voltage.append(data[0])
            current.append(data[1])
        else:
            for subarray in data:
                voltage.append(subarray[0])
                current.append(subarray[1])
        return voltage, current

    #update function for animation
    def update(i):
        voltage, current = get_data(file_path, has_temperature)
        if  voltage and current:
            ax.plot(voltage[:i], current[:i], color='royalblue')

    anim = FuncAnimation(fig, update, interval=500, cache_frame_data=False)
    plt.show()

config = import_config(r'Basic Configs\1M2_resistor_test_with_temp.json')
currentVsVoltage(config)
#voltageVsTime(config)