#debug function to test the workflow
from sys import path
path.append('../Curvetracer Control Software')

from externalDeviceControl import *
from dataAnalysis import *
from saveData import *
import time

def main():

    #config ----------------------------
    create_file = False
    file_path = "manual_test.csv"

    input_voltage = 20
    input_current = 5e-3

    has_temperature = True
    input_temperature = 35

    limit_resistor = 'short'
    #config end -------------------------

    #create the csv file
    if create_file == True:
        check_and_create_file(file=file_path, has_temperature=has_temperature)

    #initialize the HV source
    if not fug_set_current(input_current):
        exit('ERROR: Fug could not set current')

    if not fug_enable_output(True):
        exit('ERROR: Fug could not enable output')

    #initialize the RIO unit
    initialize_FPGA()

    #set limit resistor and enable power
    set_limit_resistor(resistor=limit_resistor)
    enable_power_FPGA()

    #initialize the Huber Pilot One temperature unit
    if not huber_set_temperature(set_temperature=input_temperature):
        exit('ERROR: Huber Pilot One temperature could not be set')

    #wait for temperature to be reached
    while not set_temperature_reached(set_temperature=input_temperature, tolerance=2):
        print(f'INFO: Waiting for PT100 to reach temperature. Currently at {round(measure_temperature(), 3)}')
        time.sleep(30)

    if has_temperature == True:
        measured_temperature = measure_temperature()

    #set the voltage
    if not fug_set_voltage(input_voltage):
        exit('ERROR: Fug could not set voltage')

    #wait for a valid output, then read it
    while not valid_current():
        pass
    
    measured_current = measure_current()

    #calculate DUT voltage
    DUT_voltage = calculateDUTVoltage(set_voltage=input_voltage, \
                                      measured_current=measured_current, \
                                        limit_resistor=limit_resistor)
    
    print('INFO: Measurement successful!------------')
    print(f'DUT_voltage is {DUT_voltage}')
    print(f'Measured current is {measured_current}')
    if has_temperature == True:
        print(f'Measured temperature is {measured_temperature}')

    #optionally save to the test file
    if create_file == True:
        if has_temperature == True:
            data = [input_temperature, measured_temperature, DUT_voltage, measured_current]
        else:
            data = [DUT_voltage, measured_current]
        append_to_csv(file=file_path, data=data)

    return 0

main()



