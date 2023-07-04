#higher level functions implementing all different modes
from time import sleep
from Backend.externalDeviceControl import *
from Backend.dataAnalysis import *
from Backend.saveData import *
from datetime import datetime


def initialize_hardware(config):
    #get parameters from input dict
    input_current = config.get('input_current')
    limit_resistor = config.get('limit_resistor')
    
    if not fug_clear():
        exit('ERROR: Fug could not be reset')

    #initialize the HV source
    if not fug_set_current(input_current):
        exit('ERROR: Fug could not set current')

    if not fug_enable_output(True):
        exit('ERROR: Fug could not enable output')

    #initialize the RIO unit
    initialize_FPGA()

    #set limit resistor and enable power
    set_limit_resistor(resistor=limit_resistor)
    enable_power_FPGA(True)

#function to apply a single voltage and return the current
def single_voltage(voltage):
    fug_set_voltage(voltage)
    return read_current()

#function to generate the voltage sweep (used as generator function)
def voltage_sweep(start_voltage, end_voltage, step):
    current = 0

    #end voltage may never be exceeded
    while (start_voltage + step) <= end_voltage:
        current = single_voltage(start_voltage)
        actual_voltage = fug_read('voltage')

        start_voltage += step
        yield actual_voltage, current

#function to go through each temperature
#config needs to be a dict with these keys: mode, limit_resistor AND EITHER voltage OR start_voltage, end_voltage, step
def temperature_sweep(config):
    mode = config.get('mode')
    temperature_list = config.get('temperature_list')
    temperature_tolerance = config.get('temperature_tolerance')
    limit_resistor = config.get('limit_resistor')
    maximum_current = config.get('maximum_current')
    save_to_file = config.get('save_to_file')
    file_path = config.get('file_path')

    #go through each temperature
    for set_temperature in temperature_list:
        #ensure to set temperature correctly
        if not huber_set_temperature(set_temperature):
            print('ERROR: Failed to set temperature')
            return False

        #wait for temperature to be reached
        while not set_temperature_reached(set_temperature, temperature_tolerance):
            print(f'INFO: Waiting for PT100 to reach temperature. Currently at {round(read_temperature(), 3)}')
            sleep(5)
        print(f'{datetime.now().time()}: INFO: Temperature reached: {round(read_temperature(), 3)}')


        #start the corresponding measurement
        if mode == 'voltage':
            #get parameters from input dict
            voltage = config.get('voltage')
            
            #measurement
            actual_temperature = round(read_temperature(), 3)
            current = single_voltage(voltage)
            actual_voltage = fug_read('voltage')
            dut_voltage = calculateDUTVoltage(set_voltage=actual_voltage, measured_current=current, limit_resistor=limit_resistor)

            #make a line to save to csv
            csv_line = [set_temperature, actual_temperature, dut_voltage, current]
            if save_to_file:
                append_to_csv(file_path, csv_line)

            #check if current exceeds limit
            if current >= maximum_current and maximum_current != 0:
                print('INFO: Current limit exceeded')
                fug_set_voltage(0)

            #save the data to file
            if save_to_file == True:
                append_to_csv(file_path, csv_line) #appends data line
                csv_line = ["", "", "", ""]
                append_to_csv(file_path, csv_line) #appends empty line

        elif mode == 'voltage_sweep':
            #get parameters from input dict
            start_voltage = config.get('start_voltage')
            end_voltage = config.get('end_voltage')
            step = config.get('step')

            #generator function returns the applied voltage and the measured current
            for actual_voltage, current in voltage_sweep(start_voltage, end_voltage, step):
                actual_temperature = round(read_temperature(), 3)
                dut_voltage = calculateDUTVoltage(set_voltage=actual_voltage, measured_current=current, limit_resistor=limit_resistor)

                #make a line to save to csv
                csv_line = [set_temperature, actual_temperature, dut_voltage, current]
                if save_to_file == True:
                    append_to_csv(file_path, csv_line)

                #check if current exceeds limit
                if current >= maximum_current and maximum_current != 0:
                    print('INFO: Current limit exceeded')
                    fug_set_voltage(0)
                    sleep(10)
                    break
  
            if save_to_file == True:
                csv_line = ["", "", "", ""]
                append_to_csv(file_path, csv_line)

    return True

#function to do everything without temperature
#config needs to be a dict with these keys: mode, limit_resistor AND EITHER voltage OR start_voltage, end_voltage, step
def no_temperature(config):    
    mode = config.get('mode')    
    limit_resistor=config.get('limit_resistor')
    save_to_file = config.get('save_to_file')
    file_path = config.get('file_path')

    #start the corresponding measurement
    if mode == 'voltage':
        #get parameters from input dict
        voltage = config.get('voltage')
        
        current = single_voltage(voltage)
        actual_voltage = fug_read('voltage')
        dut_voltage = calculateDUTVoltage(set_voltage=actual_voltage, measured_current=current, limit_resistor=limit_resistor)

        #make a line to save to csv
        csv_line = [dut_voltage, current]
        if save_to_file:
            append_to_csv(file_path, csv_line) #appends data line
            csv_line = ["", "", "", ""]
            append_to_csv(file_path, csv_line) #appends empty line


    elif mode == 'voltage_sweep':
        #get parameters from input dict
        start_voltage = config.get('start_voltage')
        end_voltage = config.get('end_voltage')
        step = config.get('step')

        #generator function returns the applied voltage and the measured current
        for actual_voltage, current in voltage_sweep(start_voltage, end_voltage, step):
            dut_voltage = calculateDUTVoltage(set_voltage=actual_voltage, measured_current=current, limit_resistor=limit_resistor)

            #make a line to save to csv
            csv_line = [dut_voltage, current]
            if save_to_file:
                append_to_csv(file_path, csv_line)

        if save_to_file == True:
            csv_line = ["", "", "", ""]
            append_to_csv(file_path, csv_line)

    return True