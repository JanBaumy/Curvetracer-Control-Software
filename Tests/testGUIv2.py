import tkinter as tk
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
#from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
from Backend.externalDeviceControl import fug_clear
from Backend.modes import temperature_sweep, no_temperature, initialize_hardware
from Backend.saveData import check_and_create_file

#test gui class
class GUI:
    fig, axs, canvas, config, animation_thread, measurement_thread = [None] * 6
    animation = None #this needs to keep a reference to the animation object, otherwise it will be garbage collected
    previous_data = 1 #previous lines in data file

    file_path = None

    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Curvetracer Control Software")
        #make the program stop upon closing the window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        #create an initial config
        self.config = {'mode': 'voltage_sweep', 'has_temperature:': True, 'file_path': 'null_measurement.csv'}

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
                self.measurement_thread.stop()
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
        voltage_sweep_frame = ctk.CTkFrame(self.root)
        voltage_sweep_frame.grid(row=0, column=0, sticky='nw', columnspan=3)
        # Voltage sweep label
        voltage_sweep_label = ctk.CTkLabel(voltage_sweep_frame, text="Voltage Sweep", font=("Helvetica", 16))
        voltage_sweep_label.grid(row=0, column=0, sticky='nw')

        # Start voltage label
        start_voltage_label = ctk.CTkLabel(voltage_sweep_frame, text="Start Voltage")
        start_voltage_label.grid(row=1, column=0, sticky='nw')
        # Start voltage input
        start_voltage_input = ctk.CTkEntry(voltage_sweep_frame)
        start_voltage_input.grid(row=2, column=0, sticky='nw')

        # End voltage label
        end_voltage_label = ctk.CTkLabel(voltage_sweep_frame, text="End Voltage")
        end_voltage_label.grid(row=3, column=0, sticky='nw')
        # End voltage input
        end_voltage_input = ctk.CTkEntry(voltage_sweep_frame)
        end_voltage_input.grid(row=4, column=0, sticky='nw')

        # Voltage step label
        voltage_step_label = ctk.CTkLabel(voltage_sweep_frame, text="Voltage Step")
        voltage_step_label.grid(row=5, column=0, sticky='nw')
        # Voltage step input
        voltage_step_input = ctk.CTkEntry(voltage_sweep_frame)
        voltage_step_input.grid(row=6, column=0, sticky='nw')

        #--------------------------------------------
        # Temperature frame
        temperature_frame = ctk.CTkFrame(self.root)
        temperature_frame.grid(row=0, column=1, sticky='nw')
        # Temperature label
        temperature_label = ctk.CTkLabel(temperature_frame, text="Temperature", font=("Helvetica", 16))
        temperature_label.grid(row=0, column=0, sticky='nw')

        # Temperature dropdown menu
        temperature_dropdown = ctk.CTkOptionMenu(temperature_frame, values=["With Temperature", "Without Temperature"])
        temperature_dropdown.grid(row=1, column=0, sticky='nw')

        # Temperature list label
        temperature_list_label = ctk.CTkLabel(temperature_frame, text="Temperature List")
        temperature_list_label.grid(row=2, column=0, sticky='nw')
        # Temperature list input
        temperature_list_input = ctk.CTkEntry(temperature_frame, height=100)
        temperature_list_input.grid(row=3, column=0, sticky='nw')

        # Temperature tolerance label
        temperature_tolerance_label = ctk.CTkLabel(temperature_frame, text="Temperature Tolerance")
        temperature_tolerance_label.grid(row=4, column=0, sticky='nw')
        # Temperature tolerance input
        temperature_tolerance_input = ctk.CTkEntry(temperature_frame)
        temperature_tolerance_input.grid(row=5, column=0, sticky='nw')

        #--------------------------------------------
        # Limit resistor and input current frame
        resistor_and_current_frame = ctk.CTkFrame(self.root)
        resistor_and_current_frame.grid(row=1, column=0, sticky='nw')
        # Limit resistor and input current frame label
        resistor_and_current_label = ctk.CTkLabel(resistor_and_current_frame, text="Limit Resistor and Input Current", font=("Helvetica", 16))
        resistor_and_current_label.grid(row=0, column=0, sticky='nw')

        # Limit resistor label
        limit_resistor_label = ctk.CTkLabel(resistor_and_current_frame, text="Limit Resistor")
        limit_resistor_label.grid(row=1, column=0, sticky='nw')
        # Limit resistor dropdown menu
        limit_resistor_dropdown = ctk.CTkOptionMenu(resistor_and_current_frame, values=["short", "12 MΩ", "120 MΩ", "1.2 GΩ", "12 GΩ", "120 GΩ"])
        limit_resistor_dropdown.grid(row=2, column=0, sticky='nw')

        # Input current label
        input_current_label = ctk.CTkLabel(resistor_and_current_frame, text="Input Current")
        input_current_label.grid(row=3, column=0, sticky='nw')
        # Input current input
        input_current_input = ctk.CTkEntry(resistor_and_current_frame)
        input_current_input.grid(row=4, column=0, sticky='nw')

        # Maximum current label
        maximum_current_label = ctk.CTkLabel(resistor_and_current_frame, text="Maximum Current")
        maximum_current_label.grid(row=5, column=0, sticky='nw')
        # Maximum current input
        maximum_current_input = ctk.CTkEntry(resistor_and_current_frame)
        maximum_current_input.grid(row=6, column=0, sticky='nw')

        #--------------------------------------------
        # Safe to file frame
        safe_to_file_frame = ctk.CTkFrame(self.root)
        safe_to_file_frame.grid(row=2, column=0, sticky='nw')
        # Safe to file frame label
        safe_to_file_label = ctk.CTkLabel(safe_to_file_frame, text="Safe to File", font=("Helvetica", 16))
        safe_to_file_label.grid(row=0, column=0, sticky='nw')

        # Safe to file checkbox
        safe_to_file_checkbox = ctk.CTkCheckBox(safe_to_file_frame, text="Safe to File")
        safe_to_file_checkbox.grid(row=1, column=0, sticky='nw')

        # Safe to file path label
        safe_to_file_path_label = ctk.CTkLabel(safe_to_file_frame, text="Safe to File Path")
        safe_to_file_path_label.grid(row=2, column=0, sticky='nw')
        # Safe to file path input
        safe_to_file_path_input = ctk.CTkButton(safe_to_file_frame, text="Choose File Path")
        safe_to_file_path_input.grid(row=3, column=0, sticky='nw')

        # Safe to file name label
        safe_to_file_name_label = ctk.CTkLabel(safe_to_file_frame, text="Safe to File Name")
        safe_to_file_name_label.grid(row=4, column=0, sticky='nw')
        # Safe to file name input
        safe_to_file_name_input = ctk.CTkEntry(safe_to_file_frame)
        safe_to_file_name_input.grid(row=5, column=0, sticky='nw')

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

        #if there is already data in the file, check if user wants to plot it again
        if os.path.exists(self.config.get('file_path')) and not self.config.get('plot_previous_data'):
            self.previous_data = sum(1 for line in open(self.config.get('file_path')))
        else:
            self.previous_data = 1

        self.redraw_canvas()

    #edits the config with the input values
    def edit_config(self):
        if not len(self.file_path.get()) == 0:
            self.config['file_path'] = self.config['save_folder'] + '\\' + self.file_path.get()

        valid_config = check_config(self.config)
        if valid_config != True:
            print(valid_config) #return is the error message
            return

    #starts the animation
    def start_animation_thread(self):
        self.animation_thread = AnimationThread(self)
        self.animation_thread.start()

    #starts the measurement
    def start_measurement(self):
        self.edit_config() #update the config with the input values
        check_and_create_file(self.config.get('file_path'), has_temperature = self.config.get('has_temperature'))

        #self.measurement_thread = MeasurementThread(self) #initialize a new measurement thread
        #self.measurement_thread.start()

    #emergency stop incase of physical damage
    def stop_measurement(self):
        if self.measurement_thread != None:
            self.measurement_thread.raise_exception()

            try:
                if not fug_clear():
                    messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")
            except:
                messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")

            self.animation_thread.join()

#class to run the animation in a separate thread
class AnimationThread(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui

    def run(self):
        self.gui.animation = FuncAnimation(self.gui.fig, update, fargs=(self.gui.axs, self.gui.previous_data, self.gui.config), cache_frame_data=False, interval=500)

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
            temperature_sweep(self.gui.config)
        else:
            no_temperature(self.gui.config)
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