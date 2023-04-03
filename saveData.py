#functions to save the measurement data

import os
import csv

def check_and_create_file(file, has_temperature):
    if not os.path.exists(file):
        open(file, 'w').close()
        if has_temperature:
            header = ['Set Temperature', 'Actual Temperature', 'Voltage', 'Current']
        else:
            header = ['Voltage', 'Current']
        append_to_csv(file, header)

def append_to_csv(file, data):
    if not os.path.exists(file):
        return False

    with open(file, 'a', newline='') as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerow(data)

