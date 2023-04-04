from modes import temperature_sweep, no_temperature
from saveData import check_and_create_file

def main():
    temperature_list = [20, 25, 30, 35]

    #set the parameters for the sweep loop measurement
    file1 = 'automatic_test_temp_sweep.csv'
    check_and_create_file(file1, has_temperature=True)

    config = {
        'mode': 'voltage_sweep',
        'temperature_list': temperature_list,
        'tolerance': 2,
        'start_voltage': 0,
        'end_voltage': 1000,
        'step': 50,
        'limit_resistor': 'short',
        'file_path': 'automatic_test_temp_sweep.csv'
    }

    #start the measurement
    temperature_sweep(config)

    #set the parameters for the single voltage measurement
    file2 = 'automatic_test_temp_single_voltage.csv'
    check_and_create_file(file2, has_temperature=True) 

    config = {
        'mode': 'voltage',
        'temperature_list': temperature_list,
        'tolerance': 2,
        'voltage': 1000,
        'limit_resistor': 'short',
        'file_path': 'automatic_test_temp_single_voltage.csv'
    }

    #start the measurement
    temperature_sweep(config)