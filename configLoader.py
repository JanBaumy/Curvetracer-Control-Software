#functions to import and export a config file
import json

#function to import a JSON config file
def import_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config

#function to export a JSON config file
def export_config(config, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(config, outfile)

#function to check if a config file is valid
def check_config(config):
    #check if config is a dictionary
    if type(config) != dict:
        return "ERROR: Config file could not be read. Please check if the file is a valid JSON file."
    #check if at least a mode is given
    if 'mode' not in config:
        return 'ERROR: No mode given.'
    #check if mode is valid
    if config.get('mode') not in ['voltage', 'voltage_sweep']:
        return "ERROR: Mode is invalid. It should be 'voltage' or 'voltage_sweep'."
    
    #incase mode is voltage
    if config.get('mode') == 'voltage':
        #check all minimmum required keys
        required_keys = ['voltage', 'limit_resistor', 'input_current']
        for key in required_keys:
            if key not in config:
                return f"ERROR: {key} is missing in the config file."
        if not isinstance(config.get('voltage'), (int, float)):
            return "ERROR: Voltage is not a number."
        if not isinstance(config.get('input_current'), (int, float)):
            return "ERROR: Input current is not a number."
            
    #incase mode is voltage_sweep
    elif config.get('mode') == 'voltage_sweep':
        #check all minimmum required keys
        required_keys = ['start_voltage', 'end_voltage', 'step', 'limit_resistor', 'input_current']
        for key in required_keys:
            if key not in config:
                return f"ERROR: {key} is missing in the config file."
        if not isinstance(config.get('start_voltage'), (int, float)):
            return "ERROR: Start voltage is not a number."
        if not isinstance(config.get('end_voltage'), (int, float)):
            return "ERROR: End voltage is not a number."
        if not isinstance(config.get('step'), (int, float)):
            return "ERROR: Step is not a number."
        if not isinstance(config.get('input_current'), (int, float)):
            return "ERROR: Input current is not a number."

    if config.get('limit_resistor') not in ['short', '12M', '120M', '1.2G', '12G', '120G']:
        return "ERROR: Limit resistor is invalid. It should be 'short', '12M', '120M', '1.2G', '12G' or '120G'."
            
    #check all temperature related optional keys
    if config.get('has_temperature') == True:
        required_keys = ['temperature_list', 'temperature_tolerance']
        for key in required_keys:
            if key not in config:
                return f"ERROR: {key} is missing in the config file."
        if not isinstance(config.get('temperature_list'), (int, float, list)):
            return "ERROR: Temperature list is not a number or a list."
        if not isinstance(config.get('temperature_tolerance'), (int, float)):
            return "ERROR: Temperature tolerance is not a number."
            
    #check all file related optional keys
    if config.get('save_to_file') == True:
        if 'save_folder' not in config:
            return "ERROR: Save folder is missing in the config file."
        if type(config.get('save_folder')) != str:
            return "ERROR: Save folder is not a string."
        
    return True
            
