import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import os
import ctypes
from sys import path
path.append('../Curvetracer-Control-Software')
from configLoader import *
from plotForGUI import *
#from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
from externalDeviceControl import fug_clear
from modes import temperature_sweep, no_temperature, initialize_hardware
from saveData import check_and_create_file

#test gui class
class GUI:
    fig, axs, canvas, config, animation_thread, measurement_thread = [None] * 6
    animation = None #this needs to keep a reference to the animation object, otherwise it will be garbage collected
    previous_data = 1 #previous lines in data file

    file_path = None

    def __init__(self):
        self.root = tk.Tk()

        #create an initial config
        self.config = {'has_temperature:': True, 'file_path': 'null_measurement.csv'}

    #startup function
    def run(self):
        #make the program stop upon closing the window
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        #cultivate the GUI
        self.create_canvas()
        self.create_widgets()

        self.root.mainloop()   

    #stop function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?\n\nWARNING: If the measurement is still running, you may need to physically restart the hardware devices afterwards."):
            self.stop_measurement()
            self.animation_thread.stop()

            try:
                if not fug_clear():
                    messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")
            except:
                messagebox.showerror("DANGER: High voltage", "Could not clear the voltage source.\nHIGH VOLTAGE may still be present.")

            #destroy window and stop session
            self.root.destroy()
            self.root.quit()

    #populates the GUI with widgets
    def create_widgets(self):
        # Choose config file button
        choose_config_file_button = tk.Button(self.root, text="Choose Config File", command=self.choose_config_file)
        choose_config_file_button.grid(row=2, column=0)

        # File name input
        self.file_path = tk.StringVar()
        file_name_label = tk.Label(self.root, text="File Name")
        file_name_label.grid(row=1, column=1)
        file_path_entry = tk.Entry(self.root, textvariable=self.file_path)
        file_path_entry.grid(row=2, column=1)

        # Start measurement button
        start_measurement_button = tk.Button(self.root, text="Start Measurement", command=self.start_measurement)
        start_measurement_button.grid(row=2, column=2)

        # Stop measurement button
        stop_measurement_button = tk.Button(self.root, text="EMERGENCY Stop", command=self.stop_measurement)
        stop_measurement_button.grid(row=2, column=3)

    #draws the static plot
    def create_canvas(self):
        #draw the static plot
        self.fig, self.axs = init_plot(self.config)

        #put the plot into the GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=4)
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

        self.measurement_thread = MeasurementThread(self) #initialize a new measurement thread
        self.measurement_thread.start()

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
        del self.gui.animation
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