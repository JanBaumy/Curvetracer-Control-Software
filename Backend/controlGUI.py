#main function opening the GUI and calling all subsequent functions

import tkinter as tk
from tkinter import ttk

import tkinter as tk
from tkinter import ttk

class GUI:
    def __init__(self, master):
        self.master = master
        master.title("Curvetracer Control")
        master.state('zoomed')

        # Create tabs
        tab_control = ttk.Notebook(master)
        tab1 = ttk.Frame(tab_control)
        tab2 = ttk.Frame(tab_control)
        tab3 = ttk.Frame(tab_control)

        # Add tabs to notebook
        tab_control.add(tab1, text='Tab 1')
        tab_control.add(tab2, text='Tab 2')
        tab_control.add(tab3, text='Tab 3')

        # Pack tabs
        tab_control.pack(expand=1, fill='both')

        # Tab 1
        # Column 1
        folder_name_label = tk.Label(tab1, text="Folder name")
        folder_name_label.grid(column=0, row=0)

        folder_name_entry = tk.Entry(tab1)
        folder_name_entry.grid(column=0, row=1)

        file_name_label = tk.Label(tab1, text="File name")
        file_name_label.grid(column=0, row=2)

        file_name_entry = tk.Entry(tab1)
        file_name_entry.grid(column=0, row=3)

        save_data_to_file_label = tk.Label(tab1, text="Save data to file?")
        save_data_to_file_label.grid(column=0, row=4)

        save_data_to_file_switch = tk.Checkbutton(tab1)
        save_data_to_file_switch.grid(column=0, row=5)

        #Column 2
        current_limit_label = tk.Label(tab1, text="Current limit")
        current_limit_label.grid(column=1, row=0)

        current_limit_options = ["A", "B", "C"]
        current_limit_dropdown_menu = tk.OptionMenu(tab1, *current_limit_options)
        current_limit_dropdown_menu.grid(column=1, row=1)

        exit_criteria_label = tk.Label(tab1, text="Exit criteria")
        exit_criteria_label.grid(column=1, row=2)

        current_limit_label = tk.Label(tab1, text="Current limit")
        current_limit_label.grid(column=1, row=3)

        current_limit_clickable_box = tk.Checkbutton(tab1)
        current_limit_clickable_box.grid(column=2, row=3)

        current_limit_field_entry = tk.Entry(tab1)
        current_limit_field_entry.grid(column=1, row=4)

        sweep_loop_line_label = tk.Label(tab1, text="Sweep Loop")
        sweep_loop_line_label.grid(column=1, row=6)

        sweep_loop_clickable_box = tk.Checkbutton(tab1)
        sweep_loop_clickable_box.grid(column=2, row=5)

        last_temp_line_label = tk.Label(tab1, text="Last Temp.")
        last_temp_line_label.grid(column=1, row=5)

        last_temp_clickable_box = tk.Checkbutton(tab1)
        last_temp_clickable_box.grid(column=2, row=6)


root = tk.Tk()
my_gui = GUI(root)
root.mainloop()

