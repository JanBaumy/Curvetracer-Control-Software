#higher level functions implementing all different modes
from externalDeviceControl import *
from dataAnalysis import *
from saveData import *
from time import sleep

def initialize_hardware(maximum_current, limit_resistor):
    if not fug_clear():
        exit('ERROR: Fug could not be reset')

    #initialize the HV source
    if not fug_set_current(maximum_current):
        exit('ERROR: Fug could not set current')

    if not fug_enable_output(True):
        exit('ERROR: Fug could not enable output')

    #initialize the RIO unit
    initialize_FPGA()

    #set limit resistor and enable power
    set_limit_resistor(resistor=limit_resistor)
    enable_power_FPGA()

#function to apply a single voltage and return the current
def single_voltage(voltage):
    fug_set_voltage(voltage)

    #wait for valid current measurement
    while not valid_current():
        pass

    current = measure_current()
    return current

#function to generate the voltage sweep (used as generator function)
def voltage_sweep(start_voltage, end_voltage, step):
    #end voltage may never be exceeded
    while (start_voltage + step) <= end_voltage:
        fug_set_voltage(start_voltage)

        #wait for valid current measurement
        while not valid_current():
            pass

        current = measure_current()
        start_voltage += step
        yield start_voltage, current

#function to go through each temperature
#config needs to be a dict with these keys: mode, limit_resistor AND EITHER voltage OR start_voltage, end_voltage, step
def temperature_sweep(config):
    #check for validity of config dict
    if 'mode' not in config:
        print('ERROR: No mode selected')
        return False
    
    mode = config.get('mode')
    if mode != 'voltage' and mode != 'voltage_sweep':
        print('ERROR: Invalid mode selected')
        return False

    #extract information for all modes
    temperature_list = config.get('temperature_list')
    temperature_tolerance = config.get('temperature_tolerance')
    limit_resistor = config.get('limit_resistor')

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
            sleep(30)
        print(f'INFO: Temperature reached: {round(measure_temperature(), 3)}')

        #start the corresponding measurement
        if mode == 'voltage':
            #get parameters from input dict
            voltage = config.get('voltage')
            
            actual_temperature = round(measure_temperature(), 3)
            dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)
            current = single_voltage(voltage)

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
            for voltage, current in voltage_sweep(start_voltage, end_voltage, step):
                actual_temperature = round(measure_temperature(), 3)
                dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)

                #make a line to save to csv
                csv_line = [set_temperature, actual_temperature, dut_voltage, current]
                if save_to_file:
                    append_to_csv(file_path, csv_line)

    return True

#function to do everything without temperature
#config needs to be a dict with these keys: mode, limit_resistor AND EITHER voltage OR start_voltage, end_voltage, step
def no_temperature(config):
    #check for validity of config dict
    if 'mode' not in config:
        print('ERROR: No mode selected')
        return False
    
    mode = config.get('mode')
    if mode != 'voltage' and mode != 'voltage_sweep':
        print('ERROR: Invalid mode selected')
        return False
    
    #extract information for all modes
    limit_resistor=config.get('limit_resistor')
    if 'file_path' in config:
        file_path = config.get('file_path')
        save_to_file = True
    else:
        save_to_file = False

    #start the corresponding measurement
    if mode == 'voltage':
        #get parameters from input dict
        voltage = config.get('voltage')
        
        current = single_voltage(voltage)
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
        for voltage, current in voltage_sweep(start_voltage, end_voltage, step):
            dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)

            #make a line to save to csv
            csv_line = [dut_voltage, current]
            if save_to_file:
                append_to_csv(file_path, csv_line)

    return True

