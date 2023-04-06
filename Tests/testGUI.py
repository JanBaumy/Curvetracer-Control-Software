import tkinter as tk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
from sys import path
path.append('../Curvetracer Control Software')
from plotForGUI import *
from fakeTestFunctions import fake_no_temperature, fake_temperature_sweep
from configLoader import *
from time import sleep

class GUI:
    fig, axs, animation = None, None, None

    def __init__(self):
        self.root = tk.Tk()

        #import null config
        self.config = import_config(r'Basic Configs\null_config.json')

        #make the plot pretty
        self.canvas = self.create_canvas()
        self.create_widgets()

    def create_widgets(self):
        # Choose config file button
        choose_config_file_button = tk.Button(self.root, text="Choose Config File", command=self.choose_config_file)
        choose_config_file_button.grid(row=1, column=0)

        # Start measurement button
        start_measurement_button = tk.Button(self.root, text="Start Measurement", command=lambda: self.start_measurement(self.config))
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
        self.canvas.get_tk_widget().delete("all")
        self.canvas = self.create_canvas()
        self.animation = FuncAnimation(fig, update, fargs=(axs, 0, gui.config), cache_frame_data=False, interval=500)

    def choose_config_file(self):
        config_file_path = filedialog.askopenfilename()
        self.config = import_config(config_file_path)
        self.redraw_canvas()

    def start_measurement(self, config):
        # Matplotlib figure spot
        print("Starting measurement")

    def run(self):
        self.root.mainloop()        

if __name__ == "__main__":
    gui = GUI()
    gui.run()