import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import multiprocessing as mp
from sys import path
path.append('../Curvetracer Control Software')
from plotData import draw_plots
from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
from configLoader import *

class GUI:
    def __init__(self):
        self.root = tk.Tk()

        self.config = import_config(r'Basic Configs\null_config.json')

        self.create_widgets()

    def create_widgets(self):
        # Choose config file button
        choose_config_file_button = tk.Button(self.root, text="Choose Config File", command=self.choose_config_file)
        choose_config_file_button.pack()

        # File name entry field
        file_name_entry = tk.Entry(self.root)
        file_name_entry.pack()

        # Start measurement button
        start_measurement_button = tk.Button(self.root, text="Start Measurement", command=lambda: self.start_measurement(self.config))
        start_measurement_button.pack()

    def choose_config_file(self):
        config_file_path = filedialog.askopenfilename()
        self.config = import_config(config_file_path)

    def start_measurement(self, config):
        # Matplotlib figure spot
        #start measurement
        print(self.config)

        # if config.get('has_temperature') == True:
        #     p1 = mp.Process(target=fake_temperature_sweep, args=(config,))
        # else:
        #     p1 = mp.Process(target=fake_no_temperature, args=(config,))

        # p1.start()

        fig, anim = draw_plots(self.config) #anim needs to stay referenced so it doesn't get deleted
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        #fake_temperature_sweep(config)

        # p1.join()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    gui = GUI()
    gui.run()