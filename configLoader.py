#functions to import and export a config file
import json

def import_config(file_path):
    with open(file_path, 'r') as file:
        config = json.load(file)
    return config


def export_config(config, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(config, outfile)