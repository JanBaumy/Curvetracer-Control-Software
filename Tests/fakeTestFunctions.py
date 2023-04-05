#fake functions to test without hardware
from dataAnalysis import *
from saveData import *
from time import sleep
import random

#function to go through each temperature
#config needs to be a dict with these keys: mode, limit_resistor AND EITHER voltage OR start_voltage, end_voltage, step
def fake_temperature_sweep(config):
    mode = config.get('mode')
    temperature_list = config.get('temperature_list')
    temperature_tolerance = config.get('temperature_tolerance')
    limit_resistor = config.get('limit_resistor')
    save_to_file = config.get('save_to_file')
    file_path = config.get('file_path')

    #go through each temperature
    for set_temperature in temperature_list:
        #ensure to set temperature correctly
        if not fake_huber_set_temperature(set_temperature):
            print('ERROR: Failed to set temperature')
            return False

        #wait for temperature to be reached
        while not fake_set_temperature_reached(set_temperature, temperature_tolerance):
            print(f'INFO: Waiting for PT100 to reach temperature. Currently at {round(set_temperature, 3)}')
            sleep(5)
        print(f'INFO: Temperature reached: {round(set_temperature, 3)}')

        #start the corresponding measurement
        if mode == 'voltage':
            #get parameters from input dict
            voltage = config.get('voltage')
            
            actual_temperature = round(set_temperature, 3)
            dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)
            current = fake_single_voltage(voltage)

            #make a line to save to csv
            csv_line = [set_temperature, actual_temperature, dut_voltage, current]
            if save_to_file:
                append_to_csv(file_path, csv_line)

        elif mode == 'voltage_sweep':
            #get parameters from input dict
            start_voltage = config.get('start_voltage')
            end_voltage = config.get('end_voltage')
            step = config.get('step')

            #generator function returns the applied voltage and the measured current
            for voltage, current in fake_voltage_sweep(start_voltage, end_voltage, step):
                actual_temperature = round(set_temperature, 3)
                dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)

                #make a line to save to csv
                csv_line = [set_temperature, actual_temperature, dut_voltage, current]
                if save_to_file:
                    append_to_csv(file_path, csv_line)

    return True

def fake_no_temperature(config):
    #check for validity of config dict
    if 'mode' not in config:
        print('ERROR: No mode selected')
        return False
    
    mode = config.get('mode')
    if mode != 'voltage' and mode != 'voltage_sweep':
        print('ERROR: Invalid mode selected')
        return False

    #extract information for all modes
    limit_resistor = config.get('limit_resistor')

    if 'file_path' in config:
        file_path = config.get('file_path')
        save_to_file = True
    else:
        save_to_file = False

    #start the corresponding measurement
    if mode == 'voltage':
        #get parameters from input dict
        voltage = config.get('voltage')
        
        current = fake_single_voltage(voltage)
        dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)

        #make a line to save to csv
        csv_line = [dut_voltage, current]
        if save_to_file:
            append_to_csv(file_path, csv_line)

    elif mode == 'voltage_sweep':
        #get parameters from input dict
        start_voltage = config.get('start_voltage')
        end_voltage = config.get('end_voltage')
        step = config.get('step')

        #generator function returns the applied voltage and the measured current
        for voltage, current in fake_voltage_sweep(start_voltage, end_voltage, step):
            dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)

            #make a line to save to csv
            csv_line = [dut_voltage, current]
            if save_to_file:
                if not append_to_csv(file_path, csv_line):
                    print("WARNING: Failed to save data to file")

    return True

def fake_huber_set_temperature(set_temperature):
    return True

def fake_single_voltage(voltage):
    return voltage / 1000

def fake_voltage_sweep(start_voltage, end_voltage, step):
    for voltage in range(start_voltage, end_voltage, step):
        current = fake_single_voltage(voltage)
        yield voltage, current

def fake_set_temperature_reached(set_temperature, temperature_tolerance):
    return True