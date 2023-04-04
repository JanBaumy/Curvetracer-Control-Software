#all the basic configs
from configLoader import export_config
import os

measurement_folder = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop', 'SHA-Curvetracer Measurements')

no_temp_single_voltage = dict(has_temperature=False,\
                                mode='voltage',\
                                limit_resistor='short',\
                                input_current=5e-3,\
                                voltage=3000,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

no_temp_sweep_voltage = dict(has_temperature=False,\
                                mode='voltage_sweep',\
                                limit_resistor='12M',\
                                input_current=5e-3,\
                                start_voltage=0,\
                                end_voltage=3000,\
                                step=50,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

temp_single_voltage = dict(has_temperature=True,\
                                mode='voltage',\
                                limit_resistor='12M',\
                                input_current=5e-3,\
                                temperature_list=[22, 32, 42, 52, 62, 72, 82, 92, 102],\
                                temperature_tolerance=2,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

temp_sweep_voltage = dict(has_temperature=True,\
                                mode='voltage_sweep',\
                                limit_resistor='12M',\
                                input_current=5e-3,\
                                temperature_list=[22, 32, 42, 52, 62, 72, 82, 92, 102],\
                                temperature_tolerance=2,\
                                start_voltage=0,\
                                end_voltage=3000,\
                                step=50,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

#export the configs
print('Regenerating basic configs')
export_config(no_temp_single_voltage, 'Basic Configs/no_temp_single_voltage.json')
export_config(no_temp_sweep_voltage, 'Basic Configs/no_temp_sweep_voltage.json')
export_config(temp_single_voltage, 'Basic Configs/temp_single_voltage.json')
export_config(temp_sweep_voltage, 'Basic Configs/temp_sweep_voltage.json')