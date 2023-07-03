#basic functions to control all external hardware devices
huber_pilot_one_host = "192.168.1.90"
huber_pilot_one_port = 8101
fug_host = "192.168.1.42"
fug_port = 4242
rio_host = 'rio://192.168.1.8/RIO0'
rio_bitfile = 'FPGA Bitfile/FPGA Bitfile v3 (Recalibrated).lvbitx'

import socket
from time import sleep
from nifpga import Session

#Generic function to send and receive a single string with TCP
def tcp_send_receive(host, port, payload):
    #create socket and connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    sock.connect((host, port))
    sock.settimeout(None)

    #send, receive, close
    sock.sendall(payload.encode('utf-8'))
    received_string = sock.recv(1024).decode('utf-8')
    sock.close()

    return received_string

#-----HUBER PILOT ONE----- ----------------------------------------------------------------------
#function to set the temperature on the Huber Pilot One Temperature unit
def huber_set_temperature(set_temperature):
    #minimum/maximum temperatures of Huber Pilot One
    if set_temperature > 245:
        set_temperature = 245
    elif set_temperature < -45:
        set_temperature = -45

    #multiply by 100 and convert to integer (because Huber Pilot One specification)
    set_temperature = int(100*set_temperature)

    #convert to hex signed 2's complement and make it four characters
    set_temperature_hex = format(set_temperature & (2**16-1), 'x')
    set_temperature_hex = set_temperature_hex.zfill(4).upper()

    #convert to Huber Pilot One format and send
    payload = r'{M00' + set_temperature_hex + '\r\n'
    return_value = tcp_send_receive(huber_pilot_one_host, huber_pilot_one_port, payload)

    exspected_return = r'{S00' + set_temperature_hex + '\r\n'

    if return_value == exspected_return:
        return True

    return False

#function to give the DUT temperature to the Huber Pilot One Temperature unit
def huber_process_temperature(set_temperature):

    #multiply by 100 and convert to integer (because Huber Pilot One specification)
    set_temperature = int(100*set_temperature)

    #convert to hex signed 2's complement and make it four characters
    set_temperature_hex = format(set_temperature & (2**16-1), 'x')
    set_temperature_hex = set_temperature_hex.zfill(4).upper()

    #convert to Huber Pilot One format and send
    payload = r'{M09' + set_temperature_hex + '\r\n'
    return_value = tcp_send_receive(huber_pilot_one_host, huber_pilot_one_port, payload)

    exspected_return = r'{S09' + set_temperature_hex + '\r\n'

    if return_value == exspected_return:
        return True

    return False

#function to enable process control on the Huber Pilot One Temperature unit
def huber_enable_process_control(mode: bool):
    mode = '01' if mode == True else '00'

    payload = r'{M1900' + mode + '\r\n'
    return_value = tcp_send_receive(huber_pilot_one_host, huber_pilot_one_port, payload)

    exspected_return = r'{S1900' + mode + '\r\n'

    if return_value == exspected_return:
        return True

    return False

#-----FUG DEVICE----- ----------------------------------------------------------------------
#function to set the voltage of the Fug HV source
def fug_set_voltage(voltage):
    if voltage < 0:
        voltage = 0

    #convert to Fug's exspected format
    payload = 'U' + str(voltage) + '\r\n'
    return_value = tcp_send_receive(fug_host, fug_port, payload)

    #check for valid return
    if return_value == 'E0\n':
        return True
    
    return False

#function to set the current of the Fug HV source
def fug_set_current(current):
    if current < 0:
        current = 0

    payload = 'I' + str(current) + '\r\n'
    return_value = tcp_send_receive(fug_host, fug_port, payload)

    #check for valid return
    if return_value == 'E0\n':
        return True

    print(payload)
    
    return False

#function to enable/disable the output of the Fug HV source
def fug_enable_output(mode: bool):
    mode = '1' if mode == True else '0'

    payload = 'F' + mode +'\r\n'
    return_value = tcp_send_receive(fug_host, fug_port, payload)

    #check for valid return    
    if return_value == 'E0\n':
        return True
    
    return False

#function to return the Fug HV source to default values
def fug_clear():
    return_value = tcp_send_receive(fug_host, fug_port, '=\r\n')

    #check for valid return    
    if return_value == 'E0\n':
        return True
    
    return False

#function to read the set voltage/current of the Fug HV source
def fug_read(parameter):
    if parameter == 'voltage':
        payload = '>M0?\r\n'
    elif parameter == 'current':
        payload = '>M1?\r\n'
    else:
        return False
    
    # answer will be "M0: +X.XXXXXE+XX" or "M1: +X.XXXXXE+XX", so we need to remove the first 3 characters
    return float(tcp_send_receive(fug_host, fug_port, payload)[3:])    

#-----NI CompactRIO----- ----------------------------------------------------------------------
#function to start the resistor limiting and current measuring FPGA
def initialize_FPGA():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        session.download()
        session.reset()
        session.run()

#function to reset the current measurement but keep the limit resistor, needed to stop continuous measurement
def reset_current_measurement():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        start = session.registers['Boolean 2']
        valid_current = session.registers['Boolean']

        #stop the measurement after current cycle
        start.write(False)

        #wait for FPGA to reset "valid current" flag to false
        while valid_current.read():
            pass

        start.write(True)

#function to enable power to DUT
def enable_power_FPGA(boolean):
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        control = session.registers['SW 7']
        control.write(boolean)

#function to set the limiting resistor
def set_limit_resistor(resistor):
    dict = {
        'short': 'SW 6',
        '12M': 'SW 1',
        '120M': 'SW 2',
        '1.2G': 'SW 3',
        '12G': 'SW 4',
        '120G': 'SW 5'
    }
        
    #eliminate invalid inputs    
    if not resistor in dict:
        return False
    
    #get switch number for FPGA
    wanted_control = dict.get(resistor)
    
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        disable_all_limit_resistors()
        session.registers[wanted_control].write(True)

    return True

#function to disable all limiting resistors
def disable_all_limit_resistors():
    all_controls = ['SW 1', 'SW 2', 'SW 3', 'SW 4', 'SW 5', 'SW 6']

    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        for control in all_controls:
            session.registers[control].write(False)

#function to check validity of output
def valid_current():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        valid = session.registers['Boolean']

        return valid.read()

#function to measure the current
def read_current():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        current = session.registers['Numeric 2']

        return current.read()
    
def read_current_dynamic_calibration():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        # ranges are 100pA, 10nA, 100nA, 1uA, 10uA, 100uA, 1mA
        current_ranges = ['Numeric, Numeric 3, Numeric 4, Numeric 5, Numeric 6, Numeric 7, Numeric 8']
        current_range_100pA = session.registers['Numeric'].read()
        current_range_10nA = session.registers['Numeric 3'].read()
        current_range_100nA = session.registers['Numeric 4'].read()
        current_range_1uA = session.registers['Numeric 5'].read()
        current_range_10uA = session.registers['Numeric 6'].read()
        current_range_100uA = session.registers['Numeric 7'].read()
        current_range_1mA = session.registers['Numeric 8'].read()

#function to measure temperature
def read_temperature():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        pt100 = session.registers['Mod3/RTD0']
        pt100_value = float(pt100.read())

        #convert PT100 value to temperature with parameters gained from quadratic regression
        temperature = 0.00105938*(pt100_value**2) + 2.3448*pt100_value - 245.092

    return temperature