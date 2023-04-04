#higher level functions implementing all different modes
from externalDeviceControl import *
from dataAnalysis import *
import time

#function to start the temperature measurement in parallel
def parallel_temperature(queue):
    queue.put(measure_temperature())

def single_voltage(voltage):
    fug_set_voltage(voltage)
    time.sleep(0.05) #wait 50ms for the voltage to stabilize
    current = measure_current()
    yield current

#function to generate the voltage sweep (used as generator function)
def voltage_sweep(start_voltage, end_voltage, step):
    #end voltage may never be exceeded
    while (start_voltage + step) <= end_voltage:
        fug_set_voltage(start_voltage)
        time.sleep(0.05) #wait 50ms for the voltage to stabilize
        current = measure_current()
        start_voltage += step
        yield start_voltage, current

#function to go through each temperature
def temperature_sweep(temperature_list, temperature_tolerance, config):
    mode = config.get('mode')

    if mode != 'voltage' and mode != 'voltage_sweep':
        print('ERROR: Invalid mode selected')
        return False
    else:
        #extract information for all modes
        limit_resistor=config.get('limit_resistor')

    #go through each temperature
    for temperature in temperature_list:
        data = [temperature]

        #ensure to set temperature correctly
        if not huber_set_temperature(temperature):
            print('ERROR: Failed to set temperature')
            return False

        #wait for temperature to be reached
        while not set_temperature_reached(temperature, temperature_tolerance):
            print(f'INFO: Waiting for PT100 to reach temperature. Currently at {round(measure_temperature(), 3)}')
            time.sleep(30)
        print(f'INFO: Temperature reached: {round(measure_temperature(), 3)}')

        #start the corresponding measurement
        if mode == 'voltage':
            #get parameters from input dict
            voltage = config.get('voltage')

            data.append(round(measure_temperature(), 3))
            data.append(single_voltage(voltage))
            data.append(calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor='short'))

        elif mode == 'voltage_sweep':
            #get parameters from input dict
            start_voltage = config.get('start_voltage')
            end_voltage = config.get('end_voltage')
            step = config.get('step')

            for voltage, current in voltage_sweep(start_voltage, end_voltage, step):
                data.append(round(measure_temperature(), 3))
                data.append(current)
                data.append(calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor))

    return True

