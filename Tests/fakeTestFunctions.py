#fake functions to test without hardware
from Backend.dataAnalysis import *
from Backend.saveData import *
from random import uniform
from time import sleep

#function to go through each temperature
#config needs to be a dict with these keys: mode, limit_resistor AND EITHER voltage OR start_voltage, end_voltage, step
def fake_temperature_sweep(config):
    mode = config.get('mode')
    temperature_list = config.get('temperature_list')
    temperature_tolerance = config.get('temperature_tolerance')
    maximum_current = config.get('maximum_current')
    limit_resistor = config.get('limit_resistor')
    save_to_file = config.get('save_to_file')
    file_path = config.get('file_path')

    #go through each temperature
    for set_temperature in temperature_list:
        #set temperature
        fake_huber_set_temperature(set_temperature)

        #wait for temperature to be reached
        print('INFO: Waiting to reach temperature, going to sleep for 5 seconds')
        sleep(5)
        print(f'INFO: Temperature reached: {round(set_temperature, 3)}')

        #start the corresponding measurement
        if mode == 'voltage':
            #get parameters from input dict
            voltage = config.get('voltage')
            
            actual_temperature = round(set_temperature, 3)
            current = fake_single_voltage(voltage)
            dut_voltage = calculateDUTVoltage(set_voltage=voltage, measured_current=current, limit_resistor=limit_resistor)

            #make a line to save to csv
            csv_line = [set_temperature, actual_temperature, dut_voltage, current]
            if save_to_file:
                append_to_csv(file_path, csv_line)

            if current >= maximum_current and maximum_current != 0:
                print('INFO: Current limit exceeded')
            print('INFO: Single voltage measurement step done, going to sleep for 1 seconds')
            sleep(1)

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
                print('INFO: Voltage sweep measurement step done, going to sleep for 1 seconds')
                if current >= maximum_current and maximum_current != 0:
                    print('INFO: Current limit exceeded, immediately going to next temperature')
                    break
                sleep(1)
        print('INFO: Temperature measurement step done, going to sleep for 10 seconds')
        sleep(10)

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
            print('INFO: Voltage sweep measurement step done, going to sleep for 1 seconds')
            sleep(1)

    return True

def fake_huber_set_temperature(set_temperature):
    return True

def fake_single_voltage(voltage):
    return (voltage / 1200000) * round(uniform(0.9, 1.1), 3)

def fake_voltage_sweep(start_voltage, end_voltage, step):
    for voltage in range(start_voltage, end_voltage, step):
        current = fake_single_voltage(voltage)
        yield voltage, current

def fake_set_temperature_reached(set_temperature, temperature_tolerance):
    return True