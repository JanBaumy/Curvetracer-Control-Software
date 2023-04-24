from tkinter import filedialog
from tkinter import messagebox
import customtkinter as ctk
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import os
import ctypes
from sys import path
path.append('../Curvetracer-Control-Software')
from Backend.configLoader import *
from Backend.plotForGUI import *
from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
from Backend.externalDeviceControl import fug_clear
from Backend.modes import temperature_sweep, no_temperature, initialize_hardware
from Backend.saveData import check_and_create_file

#test gui class
class GUI(ctk.CTk):
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Curvetracer Control Software")
        self.root.resizable(True, True)
        #make the program stop upon closing the window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.fig, self.axs, self.canvas, self.config, self.animation_thread, self.measurement_thread = [None] * 6
        self.animation = None #this needs to keep a reference to the animation object, otherwise it will be garbage collected
        self.previous_data = 1 #previous lines in data file

        #set all of the variables
        self.has_temperature = ctk.BooleanVar(value=True)
        self.temperature_list = []
        self.temperature_tolerance = ctk.DoubleVar(value=2)
        self.mode = ctk.StringVar(value='voltage_sweep')
        self.limit_resistor = ctk.DoubleVar(value='short')
        self.input_current = ctk.DoubleVar(value=5e-3)
        self.maximum_current = ctk.DoubleVar(value=50e-6)
        self.voltage = ctk.DoubleVar(value=0)
        self.start_voltage = ctk.DoubleVar(value=0)
        self.end_voltage = ctk.DoubleVar(value=3000)
        self.voltage_step = ctk.DoubleVar(value=50)
        self.save_to_file = ctk.BooleanVar(value=True)
        self.save_folder = ctk.StringVar()
        self.file_path = ctk.StringVar(value=None)
        self.file_name = ctk.StringVar(value=None)

        #create an initial config
        self.config = {'mode': 'voltage_sweep', 'has_temperature': True, 'file_path': 'null_measurement.csv'}

        #cultivate the GUI
        self.create_canvas()
        self.create_widgets()
        self.root.state('zoomed')

    #startup function
    def run(self):
        self.root.mainloop()   

    #stop function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?\n\nWARNING: If the measurement is still running, you may need to physically restart the hardware devices afterwards."):
            #stop threads
            if self.measurement_thread != None:
                self.stop_measurement()
            if self.animation_thread != None:
                self.animation_thread.stop()

            # try:
            #     if not fug_clear():
            #         messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")
            # except:
            #     messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")

            #destroy window and stop session
            self.root.destroy()
            self.root.quit()

    #populates the GUI with widgets
    def create_widgets(self):
        # Voltage sweep frame
        self.voltage_frame = VoltageFrame(self.root, parent=self, header_name='Voltage Sweep')
        self.voltage_frame.grid(row=0, column=0, sticky='nesw')
        #--------------------------------------------
        # Temperature frame
        self.temperature_frame = TemperatureFrame(self.root, parent=self, header_name='Temperature')
        self.temperature_frame.grid(row=0, column=1, sticky='nesw')
        #--------------------------------------------
        # Limit resistor and input current frame
        self.resistor_and_current_frame = LimitResistorCurrentFrame(self.root, parent=self, header_name='Limit Resistor and Current Control')
        self.resistor_and_current_frame.grid(row=1, column=0, sticky='nesw', columnspan=2)
        #--------------------------------------------
        # Save to file frame
        self.save_to_file_frame = SaveToFileFrame(self.root, parent=self, header_name='Save to File')
        self.save_to_file_frame.grid(row=2, column=0, sticky='nw', columnspan=2)
        #--------------------------------------------
        self.start_stop_button_frame= StartStopButtonFrame(self.root, parent=self, header_name='Start/Stop')
        self.start_stop_button_frame.grid(row=2, column=2, sticky='nw')
        #--------------------------------------------
        # # Choose config file button
        # choose_config_file_button = ctk.CTkButton(self.root, text="Choose Config File", command=self.choose_config_file)
        # choose_config_file_button.grid(row=2, column=0)

        # # File name input
        # self.file_path = tk.StringVar()
        # file_name_label = ctk.CTkLabel(self.root, text="File Name")
        # file_name_label.grid(row=1, column=1)
        # file_path_entry = ctk.CTkEntry(self.root, textvariable=self.file_path)
        # file_path_entry.grid(row=2, column=1)

        # # Start measurement button
        # start_measurement_button = ctk.CTkButton(self.root, text="Start Measurement", command=self.start_measurement)
        # start_measurement_button.grid(row=2, column=2)

        # # Stop measurement button
        # stop_measurement_button = ctk.CTkButton(self.root, text="EMERGENCY Stop", command=self.stop_measurement)
        # stop_measurement_button.grid(row=2, column=3)

    #draws the static plot
    def create_canvas(self):
        #make a new frame
        self.canvas_frame = ctk.CTkFrame(self.root)
        self.canvas_frame.grid(row=0, column=2, rowspan=2, sticky='ne')

        #draw the static plot
        self.fig, self.axs = init_plot(self.config)

        #put the plot into the GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=2, sticky='s')
        self.start_animation_thread()

    #redraws the plot after config change
    def redraw_canvas(self):
        if self.animation_thread != None:
            self.animation_thread.stop()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().delete("all")
        self.canvas = self.create_canvas()
        self.start_animation_thread()

    #opens a file dialog to choose a config file
    def choose_config_file(self):
        config_file_path = filedialog.askopenfilename()
        self.config = import_config(config_file_path)

        # this legalizes the config
        self.config_to_input()
        self.input_to_config_dict()
        # update the dropdown menus
        self.voltage_frame.change_options('')
        self.temperature_frame.change_options('')

        self.redraw_canvas()

    #edits the config dictionary with the input values
    def input_to_config_dict(self):
        self.config['has_temperature'] = self.has_temperature.get()
        self.config['temperature_list'] = self.temperature_frame.get_temperature_list()
        self.config['temperature_tolerance'] = self.temperature_tolerance.get()

        self.config['mode'] = self.mode.get()

        self.config['limit_resistor'] = self.resistor_and_current_frame.get_limit_resistor()
        self.config['input_current'] = self.input_current.get()
        self.config['maximum_current'] = self.maximum_current.get()

        self.config['voltage'] = self.voltage.get()
        self.config['start_voltage'] = self.start_voltage.get()
        self.config['end_voltage'] = self.end_voltage.get()
        self.config['step'] = self.voltage_step.get()

        self.config['save_to_file'] = self.save_to_file.get()
        self.folder_and_file_to_path()
        self.config['save_folder'] = self.save_folder.get()
        self.config['file_path'] = self.file_path.get()

    #puts the loaded config values into the input fields
    def config_to_input(self):
        self.has_temperature.set(self.config.get('has_temperature', True))
        self.temperature_frame.set_temperature_list(self.config.get('temperature_list', [20]))
        self.temperature_tolerance.set(self.config.get('temperature_tolerance', 2))
        self.temperature_frame.temperature_dropdown.set('With Temperature' if self.config.get('has_temperature', True) == True else 'Without Temperature')

        self.mode.set(self.config.get('mode', 'voltage_sweep'))
        self.voltage_frame.mode_dropdown.set('Voltage Sweep' if self.config.get('mode', 'voltage_sweep') == 'voltage_sweep' else 'Single Voltage')

        self.resistor_and_current_frame.set_limit_resistor(self.config.get('limit_resistor', '12M'))
        self.input_current.set(self.config.get('input_current', 5e-3))
        self.maximum_current.set(self.config.get('maximum_current', 50e-6))

        self.voltage.set(self.config.get('voltage', 500))
        self.start_voltage.set(self.config.get('start_voltage', 0))
        self.end_voltage.set(self.config.get('end_voltage', 3000))
        self.voltage_step.set(self.config.get('step', 50))

        self.save_to_file.set(self.config.get('save_to_file', True))
        self.save_folder.set(self.config.get('save_folder', os.path.join((os.environ['USERPROFILE']), 'Desktop', 'SHA-Curvetracer Measurements')))
        self.file_path.set(self.config.get('file_path', os.path.join((os.environ['USERPROFILE']), 'Desktop', 'SHA-Curvetracer Measurements', 'measurement.csv')))

    #function to check the save_folder and file_path variables and concatenate them if necessary
    def folder_and_file_to_path(self):
        #check if there is any save folder given
        if self.save_folder.get() == '':
            self.save_folder.set(os.path.join((os.environ['USERPROFILE']), 'Desktop', 'SHA-Curvetracer Measurements', '/'))

        #ensure it ends with a backslash
        if self.save_folder.get()[-1] != '/':
            self.save_folder.set(self.save_folder.get() + '/')

        #check if the file_name ends with .csv
        if not self.file_name.get().endswith('.csv'):
            self.file_name.set(self.file_name.get() + '.csv')

        #check if the file path is in the save folder
        self.file_path.set(self.save_folder.get() + self.file_name.get())

    #starts the animation
    def start_animation_thread(self):
        self.animation_thread = AnimationThread(self)
        self.animation_thread.start()

    #starts the measurement
    def start_measurement(self):
        self.input_to_config_dict() #update the config with the input values

        valid_config = check_config(self.config)
        if valid_config != True:
            messagebox.showerror("Invalid config", valid_config)
            return
        
        print(self.config)

        #check_and_create_file(self.config.get('file_path'), has_temperature = self.config.get('has_temperature'))

        #self.measurement_thread = MeasurementThread(self) #initialize a new measurement thread
        #self.measurement_thread.start()

    #emergency stop incase of physical damage
    def stop_measurement(self):
        if self.measurement_thread != None:
            self.measurement_thread.raise_exception()
            self.measurement_thread = None

            try:
                if not fug_clear():
                    messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")
            except:
                messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")

            self.animation_thread.join()

#class for the voltage sweep frame
class VoltageFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name, parent, **kwargs):
        super().__init__(*args, **kwargs)

        self.parent = parent
        self.header_name = header_name
        # Voltage header
        self.voltage_label = ctk.CTkLabel(self, text=self.header_name, font=('Helvetica', 16))
        self.voltage_label.grid(row=0, column=0, padx=10, sticky='nesw')

        # Mode selection menu
        self.mode_dropdown = ctk.CTkOptionMenu(self, values=["Voltage Sweep", "Single Voltage"], command=self.change_options)
        self.mode_dropdown.grid(row=1, column=0, padx=10, sticky='nw')

        # Start voltage label
        self.start_voltage_label = ctk.CTkLabel(self, text='Start Voltage [V]', padx=10, pady=10)
        self.start_voltage_label.grid(row=2, column=0, padx=10, sticky='nesw')
        # Start voltage input
        self.start_voltage_input = ctk.CTkEntry(self, textvariable=self.parent.start_voltage)
        self.start_voltage_input.grid(row=3, column=0, padx=10, sticky='nesw')

        # End voltage label
        self.end_voltage_label = ctk.CTkLabel(self, text='End Voltage [V]')
        self.end_voltage_label.grid(row=4, column=0, padx=10, sticky='nesw')
        # End voltage input
        self.end_voltage_input = ctk.CTkEntry(self, textvariable=self.parent.end_voltage)
        self.end_voltage_input.grid(row=5, column=0, padx=10, sticky='nesw')

        # Voltage step label
        self.voltage_step_label = ctk.CTkLabel(self, text='Voltage Step [V]')
        self.voltage_step_label.grid(row=6, column=0, padx=10, sticky='nesw')
        # Voltage step input
        self.voltage_step_input = ctk.CTkEntry(self, textvariable=self.parent.voltage_step)
        self.voltage_step_input.grid(row=7, column=0, padx=10, sticky='nesw')

        # Single Voltage label
        self.single_voltage_label = ctk.CTkLabel(self, text='Single Voltage [V]', padx=10, pady=10)
        self.single_voltage_label.grid(row=2, column=0, padx=10, sticky='nesw')
        self.single_voltage_label.grid_remove()

        # Single Voltage input
        self.single_voltage_input = ctk.CTkEntry(self, textvariable=self.parent.voltage)
        self.single_voltage_input.grid(row=3, column=0, padx=10, sticky='nesw')
        self.single_voltage_input.grid_remove()

    def change_options(self, event):
        if self.mode_dropdown.get() == "Voltage Sweep":
            self.parent.mode.set("voltage_sweep")
            self.single_voltage_label.grid_remove()
            self.single_voltage_input.grid_remove()

            self.start_voltage_label.grid()
            self.start_voltage_input.grid()

            self.end_voltage_label.grid()
            self.end_voltage_input.grid()

            self.voltage_step_label.grid()
            self.voltage_step_input.grid()

        elif self.mode_dropdown.get() == "Single Voltage":
            self.parent.mode.set("voltage")
            self.start_voltage_label.grid_remove()
            self.start_voltage_input.grid_remove()

            self.end_voltage_label.grid_remove()
            self.end_voltage_input.grid_remove()

            self.voltage_step_label.grid_remove()
            self.voltage_step_input.grid_remove()

            self.single_voltage_label.grid()
            self.single_voltage_input.grid()

#class for the temperature frame
class TemperatureFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name, parent, **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.parent = parent
        # Temperature label
        self.temperature_label = ctk.CTkLabel(self, text="Temperature", font=("Helvetica", 16))
        self.temperature_label.grid(row=0, column=0, sticky='nesw')

        # Temperature dropdown menu
        self.temperature_dropdown = ctk.CTkOptionMenu(self, values=["With Temperature", "Without Temperature"], command=self.change_options)
        self.temperature_dropdown.grid(row=1, column=0, sticky='nesw')

        # Temperature list label
        self.temperature_list_label = ctk.CTkLabel(self, text="Temperature List")
        self.temperature_list_label.grid(row=2, column=0, sticky='nesw')
        # Temperature list input
        self.temperature_list_input = ctk.CTkTextbox(self, height=100)
        self.temperature_list_input.grid(row=3, column=0, sticky='nesw')

        # Temperature tolerance label
        self.temperature_tolerance_label = ctk.CTkLabel(self, text="Temperature Tolerance")
        self.temperature_tolerance_label.grid(row=4, column=0, sticky='nesw')
        # Temperature tolerance input
        self.temperature_tolerance_input = ctk.CTkEntry(self, textvariable=self.parent.temperature_tolerance)
        self.temperature_tolerance_input.grid(row=5, column=0, sticky='nesw')

    def get_temperature_list(self):
        temperature_list = []
        temperature_list_string = self.temperature_list_input.get("0.0", "end")
        for temperature in temperature_list_string.split(','):
            try:
                temperature_list.append(float(temperature))
            except:
                pass
        return temperature_list
    
    def set_temperature_list(self, temperature_list):
        temperature_list_string = ""

        if isinstance(temperature_list, (int, float)):
            temperature_list =[temperature_list]

        for temperature in temperature_list:
            temperature_list_string += str(temperature) + ", "
        self.temperature_list_input.delete("0.0", "end")
        temperature_list_string = temperature_list_string[:-2]
        self.temperature_list_input.insert("0.0", temperature_list_string)
    
    def change_options(self, event):
        if self.temperature_dropdown.get() == "Without Temperature":
            self.parent.has_temperature.set(False)
            self.temperature_list_label.grid_forget()
            self.temperature_list_input.grid_forget()
            self.temperature_tolerance_label.grid_forget()
            self.temperature_tolerance_input.grid_forget()
        else:
            self.parent.has_temperature.set(True)
            self.temperature_list_label.grid()
            self.temperature_list_input.grid()
            self.temperature_tolerance_label.grid()
            self.temperature_tolerance_input.grid()

#class for the limit resistor and current frame
class LimitResistorCurrentFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name, parent, **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.parent = parent
        # Limit resistor and input current frame label
        self.resistor_and_current_label = ctk.CTkLabel(self, text="Limit Resistor and Input Current", font=("Helvetica", 16))
        self.resistor_and_current_label.grid(row=0, column=0, padx=10, sticky='nesw')

        # Limit resistor label
        self.limit_resistor_label = ctk.CTkLabel(self, text="Limit Resistor")
        self.limit_resistor_label.grid(row=1, column=0, padx=10, sticky='nsw')
        # Limit resistor dropdown menu
        self.limit_resistor_dropdown = ctk.CTkOptionMenu(self, values=["short", "12 MΩ", "120 MΩ", "1.2 GΩ", "12 GΩ", "120 GΩ"])
        self.limit_resistor_dropdown.grid(row=2, column=0, padx=10, sticky='nsw')
        self.parent.config['limit_resistor'] = "short"

        # Input current label
        self.input_current_label = ctk.CTkLabel(self, text="Input Current [A]")
        self.input_current_label.grid(row=1, column=1, padx=10, sticky='nesw')
        # Input current input
        self.input_current_input = ctk.CTkEntry(self, textvariable=self.parent.input_current)
        self.input_current_input.grid(row=2, column=1, padx=10, sticky='nesw')

        # Maximum current label
        self.maximum_current_label = ctk.CTkLabel(self, text="Maximum Current [A]")
        self.maximum_current_label.grid(row=3, column=1, padx=10, sticky='nesw')
        # Maximum current input
        self.maximum_current_input = ctk.CTkEntry(self, textvariable=self.parent.maximum_current)
        self.maximum_current_input.grid(row=4, column=1, padx=10, sticky='nesw')

    def get_limit_resistor(self):
        #formats from "12 MΩ" to "12M" etc.
        return self.limit_resistor_dropdown.get()[:-1].replace(" ", "")
    
    def set_limit_resistor(self, limit_resistor):
        if limit_resistor == 'short':
            self.limit_resistor_dropdown.set(limit_resistor)
        #formats from "12M" to "12 MΩ" etc.
        if limit_resistor[-1].isalpha():
            limit_resistor = limit_resistor[:-1] + " " + limit_resistor[-1] + "Ω"
        else:
            limit_resistor = limit_resistor + " Ω"
        self.limit_resistor_dropdown.set(limit_resistor)

#class for the save to file frame
class SaveToFileFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name, parent, **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.parent = parent
        # Save to file frame label
        self.save_to_file_label = ctk.CTkLabel(self, text="Save to File", font=("Helvetica", 16))
        self.save_to_file_label.grid(row=0, column=0, padx=10, sticky='nw')

        # save to file checkbox
        self.save_to_file_checkbox = ctk.CTkCheckBox(self, text="Save to File", variable=self.parent.save_to_file)
        self.save_to_file_checkbox.grid(row=1, column=0, padx=10, sticky='nw')

        # save to file path label
        self.save_to_file_path_label = ctk.CTkLabel(self, text="Folder Path")
        self.save_to_file_path_label.grid(row=2, column=0, padx=10, sticky='nw')
        # save to file path input
        self.save_to_file_path_input = ctk.CTkButton(self, text="Choose Folder Path", command=self.chooseSaveFolder)
        self.save_to_file_path_input.grid(row=3, column=0, padx=10, sticky='nw')

        # save to file name label
        self.save_to_file_name_label = ctk.CTkLabel(self, text="File Name")
        self.save_to_file_name_label.grid(row=4, column=0, padx=10, sticky='nw')
        # save to file name input
        self.save_to_file_name_input = ctk.CTkEntry(self, textvariable=self.parent.file_name)
        self.save_to_file_name_input.grid(row=5, column=0, padx=10, sticky='nw')

        #choose config file label
        self.choose_config_file_label = ctk.CTkLabel(self, text="Choose Config File")
        self.choose_config_file_label.grid(row=2, column=1, padx=10, sticky='nw')

        #choose config file button
        self.choose_config_file_button = ctk.CTkButton(self, text="Choose Config File", command=self.parent.choose_config_file)
        self.choose_config_file_button.grid(row=3, column=1, padx=10, sticky='nw')

    def chooseSaveFolder(self):
        self.parent.save_folder.set(filedialog.askdirectory())
        
#class for start/stop button frame
class StartStopButtonFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name, parent, **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.parent = parent
        # Start/Stop label
        self.start_stop_label = ctk.CTkLabel(self, text=self.header_name, font=("Helvetica", 16))
        self.start_stop_label.grid(row=0, column=0, padx=10, sticky='nw')
        # Start measurement button
        self.start_measurement_button = ctk.CTkButton(self, text="Start Measurement", command=self.parent.start_measurement)
        self.start_measurement_button.grid(row=1, column=0, padx=10)

        # Stop measurement button
        self.stop_measurement_button = ctk.CTkButton(self, text="EMERGENCY Stop", command=self.parent.stop_measurement)
        self.stop_measurement_button.grid(row=1, column=1, padx=10)

#class to run the animation in a separate thread
class AnimationThread(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui

    def run(self):
        self.gui.animation = FuncAnimation(self.gui.fig, update, fargs=(self.gui.axs, self.gui.config), cache_frame_data=False, interval=500)

    def stop(self):
        self.gui.animation._stop()
        self.gui.animation = None
        self.join()

#class to run the measurement in a separate thread
class MeasurementThread(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self._stop_event = threading.Event()
        self.gui = gui

    def run(self):
        initialize_hardware(self.config)

        if self.gui.config.get('has_temperature') == True:
            fake_temperature_sweep(self.gui.config)
        else:
            fake_no_temperature(self.gui.config)
        print("INFO: Measurement has finished!")

    def get_id(self): 
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
              ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('ERROR: Exception raise failure')

if __name__ == "__main__":
    gui = GUI()
    gui.run()