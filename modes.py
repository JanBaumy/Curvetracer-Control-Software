#higher level functions implementing all different modes
from externalDeviceControl import *
from dataAnalysis import *
from saveData import *
import time

#function to start the temperature measurement in parallel
def parallel_temperature(queue):
    queue.put(measure_temperature())

def single_voltage(voltage):
    fug_set_voltage(voltage)
    time.sleep(0.05) #wait 50ms for the voltage to stabilize
    current = measure_current()
    return current

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
    #check for validity of config dict
    if 'mode' not in config:
        print('ERROR: No mode selected')
        return False
    
    mode = config.get('mode')
    if mode != 'voltage' and mode != 'voltage_sweep':
        print('ERROR: Invalid mode selected')
        return False
    else:
        #extract information for all modes
        limit_resistor=config.get('limit_resistor')
        if 'file_path' in config:
            file_path = config.get('file_path')
            save_to_file = True
        else:
            save_to_file = False

    #go through each temperature
    for set_temperature in temperature_list:
        #ensure to set temperature correctly
        if not huber_set_temperature(set_temperature):
            print('ERROR: Failed to set temperature')
            return False

        #wait for temperature to be reached
        while not set_temperature_reached(set_temperature, temperature_tolerance):
            print(f'INFO: Waiting for PT100 to reach temperature. Currently at {round(measure_temperature(), 3)}')
            time.sleep(30)
        print(f'INFO: Temperature reached: {round(measure_temperature(), 3)}')

        #start the corresponding measurement
        if mode == 'voltage':
            #get parameters from input dict
            voltage = config.get('voltage')
            
            actual_temperature = round(measure_temperature(), 3)
            dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)
            current = single_voltage(voltage)
            csv_line = [set_temperature, actual_temperature, dut_voltage, current]
            if save_to_file:
                append_to_csv(file_path, csv_line)

        elif mode == 'voltage_sweep':
            #get parameters from input dict
            start_voltage = config.get('start_voltage')
            end_voltage = config.get('end_voltage')
            step = config.get('step')

            for voltage, current in voltage_sweep(start_voltage, end_voltage, step):
                actual_temperature = round(measure_temperature(), 3)
                dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)
                csv_line = [set_temperature, actual_temperature, dut_voltage, current]
                if save_to_file:
                    append_to_csv(file_path, csv_line)

    return True

