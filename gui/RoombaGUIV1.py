import tkinter
import customtkinter # type: ignore

def print_option():
    print(option_var.get())

# System Settings
customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

# Our app frame
app = customtkinter.CTk()
app.geometry("1200x650")
app.title("Roomba Robot GUI")

# Adding UI Elements
title = customtkinter.CTkLabel(app, text="Roomba Robot GUI", font=("Arial", 24))
title.pack(padx=10, pady=10)

# Camera feed box
camera_feed = customtkinter.CTkFrame(app, width=850, height=350)
camera_feed.pack(padx=10, pady=10)

# User input - trying to list names of options eventually
option_var = tkinter.StringVar()

# Button
option_selection = customtkinter.CTkButton(app, text="Select Option", command=lambda: print(option_var.get()))
option_selection.pack(padx=10, pady=10)

# Adding circular buttons at the bottom
circular_button1 = customtkinter.CTkButton(app, text="Button 1", width=100, height=80, corner_radius=50)
circular_button1.pack(side=tkinter.LEFT, padx=20, pady=20)

circular_button2 = customtkinter.CTkButton(app, text="Button 2", width=100, height=80, corner_radius=50)
circular_button2.pack(side=tkinter.RIGHT, padx=20, pady=20)

# Adding two circular joysticks in the center of the bottom
joystick1 = customtkinter.CTkButton(app, text="Joystick 1", width=100, height=100, corner_radius=50)
joystick1.place(relx=0.4, rely=1.0, anchor='s', y=-20)

joystick2 = customtkinter.CTkButton(app, text="Joystick 2", width=100, height=100, corner_radius=50)
joystick2.place(relx=0.6, rely=1.0, anchor='s', y=-20)

# Adding a small box in the bottom right-hand corner
battery_box = customtkinter.CTkButton(app, text="Battery", width=100, height=30)
battery_box.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

# Adding a circular button in the upper right-hand corner
upper_right_circle = customtkinter.CTkButton(app, text="Compass", width=70, height=70, corner_radius=37.5)
upper_right_circle.place(relx=1.0, rely=0.0, anchor='ne', x=-10, y=10)

# Adding a bigger box more centered on the left side
upper_left_box = customtkinter.CTkButton(app, text="Camera Toggle", width=100, height=100)
upper_left_box.place(relx=0.03, rely=0.1, anchor='nw')

# Run app
app.mainloop()
