#functions to control all external hardware devices

huber_pilot_one_host = "192.168.0.90"
huber_pilot_one_port = 8101
fug_host = "192.168.0.42"
fug_port = 4242
rio_host = "192.168.1.8/RIO0"
rio_bitfile = 'bitfile'

import socket
from nifpga import Session

#Generic function to send and receive a single string with TCP
def tcp_send_receive(host, port, payload):
    #create socket and connect
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))

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
    set_temperature_hex = set_temperature_hex.zfill(4)

    #convert to Huber Pilot One format and send
    payload = r'{M00' + set_temperature_hex
    return_value = tcp_send_receive(huber_pilot_one_host, huber_pilot_one_port, payload)

    exspected_return = 'SB00' + set_temperature_hex

    if return_value == exspected_return:
        return True

    return False


#-----FUG DEVICE----- ----------------------------------------------------------------------
#function to set the voltage of the Fug HV source
def fug_set_voltage(voltage):
    if voltage < 0:
        voltage = 0

    #convert to Fug's exspected format
    payload = 'U' + str(voltage)
    return_value = tcp_send_receive(fug_host, fug_port, payload)

    #check for valid return
    if return_value == 'E0':
        return True
    
    return False

#function to set the current of the Fug HV source
def fug_set_current(current):
    if current < 0:
        current = 0

    payload = 'I' + str(current)
    return_value = tcp_send_receive(fug_host, fug_port, payload)

    #check for valid return
    if return_value == 'E0':
        return True

    print(payload)
    
    return False

#function to enable/disable the output of the Fug HV source
def fug_enable_output(mode):
    #1 = enable; 0 = disable; undefined also disable
    if mode != 1 or 0:
        mode = 0

    payload = 'F' + str(mode)
    return_value = tcp_send_receive(fug_host, fug_port, payload)

    #check for valid return    
    if return_value == 'E0':
        return True
    
    return False

#function to return the Fug HV source to default values
def fug_clear():
    return_value = tcp_send_receive(fug_host, fug_port, '=')

    #check for valid return    
    if return_value == 'E0':
        return True
    
    return False

#function to read the set voltage/current of the Fug HV source
def fug_read(parameter):
    if parameter == 'voltage':
        payload = '>M0?'
    elif parameter == 'current':
        payload = '>M1?'
    else:
        return False

    return tcp_send_receive(fug_host, fug_port, payload)

#-----NI CompactRIO----- ----------------------------------------------------------------------
#function to start the resistor limiting and current measuring FPGA
def initialize_FPGA():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        session.reset()
        session.run()

        #enable measurement
        start = session.registers['Boolean 2']
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
def measure_current():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        current = session.registers['Numeric 2']

        return current.read()

#function to measure temperature
def measure_temperature():
    with Session(bitfile=rio_bitfile, resource=rio_host) as session:
        pt100_value = session.registers['Mod3/RTD0']

    if (pt100_value == 100):
       temperature = 20

    elif (pt100_value < 100):
       temperature = 0.0014*(pt100_value**2) + 2.2884*pt100_value - 239
    else:
       temperature = 0.0012*(pt100_value**2) + 2.296*pt100_value - 244

    return temperature
