#all the basic configs
from configLoader import export_config
import os

measurement_folder = os.path.join((os.environ['USERPROFILE']), 'Desktop', 'SHA-Curvetracer Measurements')

no_temp_single_voltage = dict(has_temperature=False,\
                                mode='voltage',\
                                limit_resistor='12M',\
                                input_current=5e-3,\
                                maximum_current=50e-6,\
                                voltage=3000,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

no_temp_sweep_voltage = dict(has_temperature=False,\
                                mode='voltage_sweep',\
                                limit_resistor='12M',\
                                input_current=5e-3,\
                                maximum_current=50e-6,\
                                start_voltage=0,\
                                end_voltage=3000,\
                                step=50,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

temp_single_voltage = dict(has_temperature=True,\
                                mode='voltage',\
                                limit_resistor='12M',\
                                input_current=5e-3,\
                                maximum_current=50e-6,\
                                temperature_list=[22, 32, 42, 52, 62, 72, 82, 92, 102],\
                                temperature_tolerance=2,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

temp_sweep_voltage = dict(has_temperature=True,\
                                mode='voltage_sweep',\
                                limit_resistor='12M',\
                                input_current=5e-3,\
                                maximum_current=50e-6,\
                                temperature_list=[22, 32, 42, 52, 62, 72, 82, 92, 102],\
                                temperature_tolerance=2,\
                                start_voltage=0,\
                                end_voltage=3000,\
                                step=50,\
                                save_to_file=True,\
                                save_folder=measurement_folder)

null_config = dict(has_temperature=True,\
                    mode='voltage_sweep',\
                    limit_resistor='short',\
                    input_current=0,\
                    maximum_current=0,\
                    temperature_list=0,\
                    temperature_tolerance=0,\
                    start_voltage=0,\
                    end_voltage=0,\
                    step=0,\
                    save_to_file=False,\
                    save_folder=measurement_folder,
                    file_path='null_measurement.csv')

#export the configs
print('Regenerating basic configs')
export_config(no_temp_single_voltage, 'Basic Configs/no_temp_single_voltage.json')
export_config(no_temp_sweep_voltage, 'Basic Configs/no_temp_sweep_voltage.json')
export_config(temp_single_voltage, 'Basic Configs/temp_single_voltage.json')
export_config(temp_sweep_voltage, 'Basic Configs/temp_sweep_voltage.json')
export_config(null_config, 'Basic Configs/null_config.json')