#functions to analyze incoming data and return necessary outputs to advance program executionmeasure_temperature'
from Backend.externalDeviceControl import read_temperature

#function to calculate the voltage across the DUT
def calculateDUTVoltage(set_voltage, measured_current, limit_resistor):
    dict = {
        'short': 1,
        '12M': 12e+6,
        '120M': 12e+7,
        '1.2G': 12e+8,
        '12G': 12e+9,
        '120G': 12e+10
    }
    
    if not limit_resistor in dict:
        return False
    else:
        limit_resistor = dict.get(limit_resistor)
    
    voltage_over_resistor = measured_current * limit_resistor
    DUT_voltage = set_voltage - voltage_over_resistor

    return DUT_voltage

#function to check if the set temperature has been reached
def set_temperature_reached(set_temperature, tolerance):
    actual_temperature = read_temperature()

    difference = abs(set_temperature - actual_temperature)

    if difference <= tolerance:
        return True
    
    return False