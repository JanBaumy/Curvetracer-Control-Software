import tkinter as tk
from tkinter import filedialog
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import os
from sys import path
path.append('../Curvetracer Control Software')
from plotForGUI import *
from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
from configLoader import *
from saveData import check_and_create_file

class GUI:
    fig, axs, animation, measurement = None, None, None, None
    previous_data = 1

    def __init__(self):
        self.root = tk.Tk()

        #import null config
        self.config = import_config(r'Basic Configs\1M2_resistor_test_with_temp.json')

        #make the plot pretty
        self.canvas = self.create_canvas()
        self.create_widgets()

    def create_widgets(self):
        # Choose config file button
        choose_config_file_button = tk.Button(self.root, text="Choose Config File", command=self.choose_config_file)
        choose_config_file_button.grid(row=1, column=0)

        # Start measurement button
        start_measurement_button = tk.Button(self.root, text="Start Measurement", command=self.start_measurement)
        start_measurement_button.grid(row=1, column=1)

    def create_canvas(self):
        global fig, axs
        fig, axs = init_plot(self.config)
        for ax in axs:
            ax.grid(color='white', linestyle='-', linewidth=0.2)

        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0, column=0, columnspan=2)

        return canvas

    def redraw_canvas(self):
        if self.animation != None:
            self.animation.stop()
        self.canvas.get_tk_widget().delete("all")
        self.canvas = self.create_canvas()
        self.start_animation_thread()

    def choose_config_file(self):
        config_file_path = filedialog.askopenfilename()
        self.config = import_config(config_file_path)

        valid_config = check_config(self.config)
        if valid_config != True:
            print(valid_config)
            return

        if os.path.exists(self.config.get('file_path')):
            previous_lines = sum(1 for line in open(self.config.get('file_path')))
        else:
            previous_lines = 1

        self.redraw_canvas()

    def start_animation_thread(self):
        self.animation = AnimationThread(self)
        self.animation.start()

    def start_measurement(self):
        print("Starting measurement")
        check_and_create_file(self.config.get('file_path'), has_temperature = self.config.get('has_temperature'))
        self.measurement = MeasurementThread(self)
        self.measurement.start()

    def run(self):
        self.root.mainloop()        

class AnimationThread(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui

    def run(self):
        self.gui.animation = FuncAnimation(fig, update, fargs=(axs, gui.previous_data, gui.config), cache_frame_data=False, interval=500)

class MeasurementThread(threading.Thread):
    def __init__(self, gui):
        threading.Thread.__init__(self)
        self.gui = gui

    def run(self):
        if self.gui.config.get('has_temperature') == True:
            self.gui.measurement = fake_temperature_sweep(self.gui.config)
        else:
            self.gui.measurement = fake_no_temperature(self.gui.config)

if __name__ == "__main__":
    gui = GUI()
    gui.run()