#higher level functions implementing all different modes
import multiprocessing
from externalDeviceControl import *

#function to start the temperature measurement in parallel
def parallel_temperature(queue):
    queue.put(measure_temperature())

#function to generate the voltage sweep
def voltage_sweep(start_voltage, end_voltage, step):
    voltage = start_voltage

    while voltage <= end_voltage:
        fug_set_voltage(voltage)
        voltage += step

    return True

