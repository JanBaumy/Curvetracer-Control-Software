import tkinter as tk
from tkinter import filedialog
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import os
import ctypes
from sys import path
path.append('../Curvetracer Control Software')
from plotForGUI import *
from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
from configLoader import *
from saveData import check_and_create_file

#test gui class
class GUI:
    fig, axs, canvas, animation_thread, measurement_thread = None, None, None, None, None
    animation = None #this needs to keep a reference to the animation object, otherwise it will be garbage collected
    previous_data = 1 #previous lines in data file

    def __init__(self):
        self.root = tk.Tk()

        #import null config
        self.config = import_config(r'Basic Configs\null_config.json')

        #cultivate the GUI
        self.create_canvas()
        self.create_widgets()

    def run(self):
        self.root.mainloop()   

    #populates the GUI with widgets
    def create_widgets(self):
        # Choose config file button
        choose_config_file_button = tk.Button(self.root, text="Choose Config File", command=self.choose_config_file)
        choose_config_file_button.grid(row=1, column=0)

        # Start measurement button
        start_measurement_button = tk.Button(self.root, text="Start Measurement", command=self.start_measurement)
        start_measurement_button.grid(row=1, column=1)

        # Stop measurement button
        stop_measurement_button = tk.Button(self.root, text="EMERGENCY Stop", command=self.stop_measurement)
        stop_measurement_button.grid(row=1, column=2)

    #draws the static plot
    def create_canvas(self):
        #draw the static plot
        self.fig, self.axs = init_plot(self.config)

        #put the plot into the GUI
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)
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

        valid_config = check_config(self.config)
        if valid_config != True:
            print(valid_config)
            return

        if os.path.exists(self.config.get('file_path')) and not self.config.get('plot_previous_data'):
            self.previous_data = sum(1 for line in open(self.config.get('file_path')))
        else:
            self.previous_data = 1

        self.redraw_canvas()

    #starts the animation
    def start_animation_thread(self):
        self.animation_thread = AnimationThread(self)
        self.animation_thread.start()

    #starts the measurement
    def start_measurement(self):
        check_and_create_file(self.config.get('file_path'), has_temperature = self.config.get('has_temperature'))

        self.measurement_thread = MeasurementThread(self)
        self.measurement_thread.start()

    #emergency stop incase of physical damage
    def stop_measurement(self):
        if self.measurement_thread != None:
            self.measurement_thread.raise_exception()
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
        while not self._stop_event.is_set():
            if self.gui.config.get('has_temperature') == True:
                fake_temperature_sweep(self.gui.config)
            else:
                fake_no_temperature(self.gui.config)

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
            print('Exception raise failure')

if __name__ == "__main__":
    gui = GUI()
    gui.run()