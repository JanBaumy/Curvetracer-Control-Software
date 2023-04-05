#function to generate all plots
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation

#function to plot voltage vs time (i is just for the animation)
def voltageVsTime(i, file_path, file_has_temperature: bool):
    #read data from file
    def get_data(file_path, file_has_temperature: bool):
        if file_has_temperature:
            voltage_column = 2
        else:
            voltage_column = 0

        voltage = np.genfromtxt(file_path, delimiter=';', skip_header=1, usecols=(voltage_column))
        return voltage

    voltage = get_data(file_path, file_has_temperature)
    ax.clear()
    ax.plot(voltage)


def animatePlot(function: function, fargs: tuple):
    #make a plot
    fig = plt.figure()
    ax = plt.axes(xlabel='Data point', ylabel='Voltage (V)', title='Voltage vs Time')

    #this needs to be run in parallel somehow
    ani = FuncAnimation(fig, voltageVsTime, fargs = (r'Tests\1M2_test_half.csv', False), interval=1000)
    plt.show()
