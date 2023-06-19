#to test all external device functions independently
from sys import path
path.append('../Curvetracer-Control-Software')
from Backend.externalDeviceControl import *

#write a main function to test the functions
def main():
# -----HUBER PILOT ONE----- -----------------------------------------------------------------
    # print('INFO: Starting HUBER test')
    # if not huber_set_temperature(20):
    #     print('ERROR: Failed to set temperature to 20')
    if not huber_enable_process_control(True):
        print('ERROR: Failed to enable process temperature')
    if not huber_process_temperature(20):
        print('ERROR: Failed to set process temperature')
    # if not huber_set_temperature(0):
    #     print('ERROR: Failed to set temperature to 0')
    # if not huber_set_temperature(-50):
    #     print('ERROR: Failed to set temperature to -50')
# -----FUG DEVICE----- ----------------------------------------------------------------------
    # print('INFO: Starting FUG test')
    # if not fug_set_voltage(5):
    #     print('ERROR: Failed to set voltage to 5')
    # if not fug_set_current(5e-3):
    #     print('ERROR: Failed to set current to 5e-3')
    # if not fug_enable_output(1):
    #     print('ERROR: Failed to enable output')
    # if not fug_read('voltage'):
    #     print('ERROR: Failed to read voltage')
    # else: print('INFO: Voltage is ' + fug_read('voltage'))
    # if not fug_read('current'):
    #     print('ERROR: Failed to read current')
    # else: print('INFO: Current is ' + fug_read('current'))
    # if not fug_enable_output(0):
    #     print('ERROR: Failed to disable output')
    # if not fug_clear():
    #     print('ERROR: Failed to clear FUG')
# -----NI CompactRIO----- --------------------------------------------------------------------
    # print('INFO: Starting NI test')
    # initialize_FPGA()
    # enable_power_FPGA(True)
    # set_limit_resistor('12M')
    # print(f'Valid current: {valid_current()}')
    # print(f'Current is: {measure_current()}')
    # print(f'Temperature is: {measure_temperature()}')

    # return

if __name__ == '__main__':
    main()
          
