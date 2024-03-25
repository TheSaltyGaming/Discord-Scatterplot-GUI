#!/usr/bin/env python3

import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, colorchooser
from tkinter import messagebox
import matplotlib.backends.backend_svg

import customtkinter
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

# User parameters
root = os.path.dirname(os.path.realpath(__file__))
yourNameHere = "@USERNAMEHERE"
renderHorizontal = True

dark_mode_dot_color = 'yellow'  # Default color for dark mode


def select_directory():
    global root
    root = filedialog.askdirectory()
    selected_folder_label.configure(text=f"Selected folder: {root}")
    print(f"Selected directory: {root}")


def select_dark_mode_color():
    # Handles dark mode color selection
    color = colorchooser.askcolor()[1]
    if color:
        global dark_mode_dot_color
        dark_mode_dot_color = color


def update_dark_mode_visibility(plot_type):
    # Show or hide the dark mode checkbox and color button based on the plot type
    if plot_type == "Scatterplot":
        # Show dark mode checkbox
        dark_mode_checkbox.grid()
        update_color_button_visibility()
    else:
        # Hide check box and color button
        dark_mode_checkbox.grid_remove()
        color_button_frame.grid_remove()


def update_color_button_visibility():
    if dark_mode_var.get() and plot_type_var.get() == "Scatterplot":
        color_button_frame.grid()  # Show the button
    else:
        color_button_frame.grid_remove()  # Hide the button


def file_type_callback(choice):
    print("File type selected:", choice)


def run_code():
    global yourNameHere
    yourNameHere = username_entry.get()
    dates = []
    for dir in os.listdir(root):
        if dir == '.idea':  # Skip the .idea directory
            continue
        dir_path = os.path.join(root, dir)
        if os.path.isdir(dir_path):
            print(f"reading messages for channel: {dir}")
            try:
                with open(os.path.join(dir_path, 'messages.json'), 'r', encoding="utf-8") as json_file:
                    json2 = json.load(json_file)
                    for message in json2:
                        dates.append(datetime.fromisoformat(message["Timestamp"]))
            except FileNotFoundError:
                print(f"No messages.json found in {dir_path}")
            else:
                print(f"messages.json found in {dir_path}")

    print(f"total messages: {len(dates)}")

    now = datetime.utcnow()

    days = []
    times = []

    print("processing dates")

    if not dates:
        messagebox.showerror("Error", "Wrong folder selected. Make sure you selected the messages folder")
        return

    plt.style.use('default')

    for date in dates:
        timeNoDate = datetime(1970, 1, 1, date.hour, date.minute, date.second)
        dateNoTime = datetime(date.year, date.month, date.day)
        days.append(dateNoTime)
        times.append(timeNoDate)

    if plot_type_var.get() == "Scatterplot":
        create_scatterplot(days, times, yourNameHere)
    else:  # plot_type_var.get() == "Heatmap"
        create_heatmap(dates)


def create_scatterplot(days, times, yourNameHere):
    print("processing graph")
    if dark_mode_var.get():
        plt.style.use('dark_background')
        dot_color = dark_mode_dot_color  # Use the color chosen from the color picker
    else:
        plt.style.use('default')
        dot_color = '#1f77b4c0'
    hoursMajorLocator = mdates.HourLocator(interval=6)
    hoursMinorLocator = mdates.HourLocator(interval=1)
    hoursMajorFormatter = mdates.DateFormatter('%H:%M')
    daysMajorLocator = mdates.YearLocator(base=1)
    daysMinorLocator = mdates.MonthLocator()
    daysMajorFormatter = mdates.DateFormatter('%Y')
    daysMinorFormatter = mdates.DateFormatter('%b')
    if renderHorizontal:
        fig, ax = plt.subplots(figsize=((max(days) - min(days)).days / 200, 3))
        plt.scatter(days, times, s=1, linewidths=0, color=dot_color)
        plt.xlim(min(days), max(days))
        plt.ylim(0, 1)
        dateAxis = ax.xaxis
        hoursAxis = ax.yaxis
        daysMinorFormatter = mdates.DateFormatter('')
    else:
        fig, ax = plt.subplots(figsize=(3, (max(days) - min(days)).days / 200))
        plt.scatter(times, days, s=1, linewidths=0, color=dot_color)
        plt.ylim(min(days), max(days))
        plt.xlim(0, 1)
        dateAxis = ax.yaxis
        hoursAxis = ax.xaxis
        ax.tick_params(axis='y', which='minor', labelsize=5, color='#777')
    # time goes downwards and to the right
    plt.gca().invert_yaxis()
    hoursAxis.set_major_locator(hoursMajorLocator)
    hoursAxis.set_minor_locator(hoursMinorLocator)
    hoursAxis.set_major_formatter(hoursMajorFormatter)
    dateAxis.set_major_locator(daysMajorLocator)
    dateAxis.set_minor_locator(daysMinorLocator)
    dateAxis.set_major_formatter(daysMajorFormatter)
    dateAxis.set_minor_formatter(daysMinorFormatter)
    hoursAxis.set_label('Time of day')
    dateAxis.set_label('Date')
    plt.title(f"When does {yourNameHere} post on Discord (UTC)")
    print("rendering file")
    if file_type_var.get() == "PNG":
        plt.savefig('out.png', bbox_inches='tight', pad_inches=0.3, dpi=300)
        messagebox.showinfo("Success", "PNG file created. Look for out.png in the same folder you ran this exe file in")
    else:  # file_type_var.get() == "SVG"
        plt.savefig('out.svg', bbox_inches='tight', pad_inches=0.3)
        messagebox.showinfo("Success", "SVG file created. Look for out.svg in the same folder you ran this exe file in")


def create_heatmap(dates):
    # Initialize a 2D array with zeros
    data = [[0 for _ in range(24)] for _ in range(7)]

    # Populate the 2D array with the number of messages sent at each hour of each day of the week
    for date in dates:
        day_of_week = date.weekday()
        hour = date.hour
        data[day_of_week][hour] += 1

    # Create the heatmap
    fig, ax = plt.subplots(figsize=(8.8, 5.5))
    plt.imshow(data, cmap='Reds', interpolation='nearest')

    # Set the labels for the x-axis and y-axis
    plt.xlabel('Hour of the Day')
    plt.ylabel('Day of the Week')

    # Set the ticks for the x-axis and y-axis
    plt.xticks(range(24))
    plt.yticks(range(7), ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])

    plt.tick_params(axis='both', which='major', labelsize=8)

    # Show the colorbar and add a label to it
    cbar = plt.colorbar()
    cbar.set_label('Total Messages')

    # Add a title to the heatmap
    plt.title(f"When does {yourNameHere} post on Discord (UTC)")

    # Adjust the space at the bottom of the plot
    plt.subplots_adjust(bottom=0.3)

    # Save the heatmap to a file instead of displaying it
    if file_type_var.get() == "PNG":
        plt.savefig('heatmap.png', bbox_inches='tight', pad_inches=0.3, dpi=300)
        messagebox.showinfo("Success",
                            "PNG file created. Look for heatmap.png in the same folder you ran this exe file in")
    else:  # file_type_var.get() == "SVG"
        plt.savefig('heatmap.svg', bbox_inches='tight', pad_inches=0.3)
        messagebox.showinfo("Success",
                            "SVG file created. Look for heatmap.svg in the same folder you ran this exe file in")


root_window = customtkinter.CTk()
root_window.title("Discord Scatter Plot Maker")
root_window.geometry('650x550')
root_window.columnconfigure(0, weight=1)

bg_color = root_window.cget('bg')

file_type_var = customtkinter.StringVar(value="PNG")
plot_type_var = tk.StringVar(value="Scatterplot")

header_label = customtkinter.CTkLabel(root_window, text="Discord Scatter plot maker", font=("Arial", 24, 'bold'))
header_label.grid(pady=10)  # Add vertical padding

label = customtkinter.CTkLabel(root_window, text="Please enter the username you'd like displayed on the final image")
label.grid(pady=0)  # Add vertical padding

username_entry = customtkinter.CTkEntry(root_window)
username_entry.grid(pady=10)  # Add vertical padding

label = customtkinter.CTkLabel(root_window, text="Please select your messages folder here")
label.grid(pady=10)  # Add vertical padding

select_button = customtkinter.CTkButton(root_window, text="Select Folder", command=select_directory)
select_button.grid(pady=0)  # Add vertical padding

selected_folder_label = customtkinter.CTkLabel(root_window, text="")  # Add a new label for the selected folder
selected_folder_label.grid(pady=0)  # Add vertical padding

# Create a label for the dropdown menu
label = customtkinter.CTkLabel(root_window, text="Select the plot type")
label.grid(pady=0)  # Add vertical padding

# Create the dropdown menu to select plot type
plot_type_dropdown = customtkinter.CTkOptionMenu(root_window, values=["Scatterplot", "Heatmap"],
                                                 command=update_dark_mode_visibility, variable=plot_type_var)
plot_type_dropdown.grid(pady=10)

dark_mode_var = tk.BooleanVar()  # Create a BooleanVar to hold the state of the checkbox
dark_mode_checkbox = customtkinter.CTkCheckBox(root_window, text="Dark Mode", variable=dark_mode_var,
                                               command=update_color_button_visibility)
dark_mode_checkbox.grid(pady=10)

color_button_frame = tk.Frame(root_window, bg=bg_color)
color_button_frame.grid()

color_button = customtkinter.CTkButton(color_button_frame, text="Select Dark Mode Dot Color (Optional)",
                                       command=select_dark_mode_color)
color_button.grid(row=0, column=0)

label = customtkinter.CTkLabel(root_window, text="Select the filetype you'd like to save the image as")
label.grid(pady=0)  # Add vertical padding
# Create a dropdown menu with the file types
file_type_dropdown = customtkinter.CTkOptionMenu(root_window, values=["PNG", "SVG"],
                                                 command=file_type_callback,
                                                 variable=file_type_var)
file_type_dropdown.grid(pady=10)

run_button = customtkinter.CTkButton(root_window, text="Run", command=run_code)
run_button.grid(pady=10)  # Add vertical padding

update_color_button_visibility()  # Call the function to show or hide the color button based on the checkbox state

root_window.mainloop()
