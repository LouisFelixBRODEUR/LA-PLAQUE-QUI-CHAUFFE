import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk

class GUI:
    def __init__(self):
        # Initialize root window
        self.root = ctk.CTk()
        self.root.geometry("900x700")
        self.background_color = "#1e1e1e" # Dark gray background
        self.root.configure(bg=self.background_color)
        self.root.title("Controleur Simulation")

        ctk.set_appearance_mode("dark")  # Dark mode for better contrast
        ctk.set_default_color_theme("blue")  # Blue theme for buttons and other elements

        # Initialize variables
        self.pix_spacing = 20
        self.pix_to_plaque_box = 3
        self.Save_as_path = "Aucune Sélection"
        self.Coef_Therm = 0
        self.Simu_parameters = {
            'Coefficient thermique' : 'abc',
            'Largeur Plaque' : '60',
            'Longueur Plaque' : '116',
            'Position Actuateur Largeur' : '30',
            'Position Actuateur Longueur': '40',
        }

        self.load_frame() # Load initial frame

    def on_enter_key(self, event):
        self.Simu_parameters['Coefficient thermique'] = self.coef_therm_user_entry.get()
        self.Simu_parameters['Largeur Plaque'] = self.plaque_width_user_entry.get()
        self.Simu_parameters['Longueur Plaque'] = self.plaque_lenght_user_entry.get()
        self.load_frame()

    def load_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame for save path and button
        save_frame = ctk.CTkFrame(self.root)
        save_frame.grid(row=0, column=0, columnspan=2, pady=(self.pix_spacing, self.pix_spacing/2), padx=self.pix_spacing, sticky="ew")
        save_frame.columnconfigure(0, weight=1)
        save_frame.columnconfigure(1, weight=0)
        # Save Path Label
        text_save_path = f"Données enregistrées dans : {self.Save_as_path}"
        label_save_path = ctk.CTkLabel(save_frame, text=text_save_path)
        label_save_path.grid(row=0, column=0, sticky="w", padx=(5,0))
        # 'Save as' boutton
        self.Select_path_button = ctk.CTkButton(save_frame, text="Enregistrer sous", command=self.Save_as_clicked)
        self.Select_path_button.grid(row=0, column=1, sticky="e")

        # TODO add mm label to the entries
        # Frame for plaque info
        self.plaque_info_frame = ctk.CTkFrame(self.root)
        self.plaque_info_frame.grid(row=1, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.plaque_info_frame.columnconfigure(0, weight=0)
        self.plaque_info_frame.columnconfigure(1, weight=0)
        # Label for coef therm
        Coef_therm_label = ctk.CTkLabel(self.plaque_info_frame, text="Coefficient Thermique : ")
        Coef_therm_label.grid(row=0, column=0, sticky="w", padx=(5,0), pady=(5,0))
        # data Entry for coef therm 
        self.coef_therm_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.coef_therm_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.coef_therm_user_entry.insert("1", str(self.Simu_parameters['Coefficient thermique']))
        self.coef_therm_user_entry.grid(row=0, column=1, sticky="w", pady=(5,0))
        # Label for plaque width
        plaque_width = ctk.CTkLabel(self.plaque_info_frame, text="Largeur de la plaque en mm : ")
        plaque_width.grid(row=1, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque width 
        self.plaque_width_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.plaque_width_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_width_user_entry.insert("1", str(self.Simu_parameters['Largeur Plaque']))
        self.plaque_width_user_entry.grid(row=1, column=1, sticky="w")
        # Label for plaque lenght
        plaque_lenght = ctk.CTkLabel(self.plaque_info_frame, text="Longueur de la plaque en mm : ")
        plaque_lenght.grid(row=2, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque lenght
        self.plaque_lenght_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.plaque_lenght_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_lenght_user_entry.insert("1", str(self.Simu_parameters['Longueur Plaque']))
        self.plaque_lenght_user_entry.grid(row=2, column=1, sticky="w")

        # TODO
        # # Boutton
        # self.Reset_Actu_Posi_button = ctk.CTkButton(self.plaque_info_frame, text="Réinitialiser", command=self.Reset_to_default)
        # self.Reset_Actu_Posi_button.grid(row=3, column=1, sticky="w")

        # Code for plaque with sliders:
        # Label
        PosActu_Label = ctk.CTkLabel(self.plaque_info_frame, text="Position de l'actuateur :")
        PosActu_Label.grid(row=3, column=0, sticky="w", padx=(5,0))
        # Plaque
        self.plaque_width = 300*int(self.Simu_parameters['Largeur Plaque'])/int(self.Simu_parameters['Longueur Plaque'])
        self.plaque_lenght = 300
        self.plaque_box_frame = ctk.CTkFrame(self.plaque_info_frame, height=self.plaque_width, width=self.plaque_lenght, fg_color="black")
        self.plaque_box_frame.grid(row=4, column=0, pady=(5,5), columnspan = 2, padx=10)
        self.plaque_canvas = ctk.CTkCanvas(self.plaque_box_frame, height=self.plaque_width, width=self.plaque_lenght, bg='#2B2B2B', bd=0, highlightthickness=0)
        self.plaque_canvas.pack()
        # RedDot
        self.create_rounded_rectangle('gray10')
        self.red_dot = self.plaque_canvas.create_oval(10, 10, 20, 20, fill="red", outline="red")
        # Create horizontal slider for the red square's x position (width)
        self.width_slider = ctk.CTkSlider(self.plaque_info_frame, from_=0, to=int(self.Simu_parameters['Longueur Plaque']), number_of_steps=100, command=self.update_red_square, orientation="horizontal")
        self.width_slider.set(int(self.Simu_parameters['Position Actuateur Longueur']))  # Set initial x position to the middle
        self.width_slider.grid(row=5, column=0, columnspan=2, pady=(0,5), padx=(10,4), sticky="ew")
        # Create corresponding Entry for horizontal slider
        self.width_value = ctk.CTkEntry(self.plaque_info_frame, width=80)
        self.width_value.grid(row=5, column=2, padx=0, pady=(0,5), sticky="w")
        self.width_value.insert(0, str(self.width_slider.get()))  # Set initial value
        self.width_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width"))
        # Create vertical slider for the red square's y position (height)
        slider_height = 300*int(self.Simu_parameters['Largeur Plaque'])/int(self.Simu_parameters['Longueur Plaque'])
        self.length_slider = ctk.CTkSlider(self.plaque_info_frame, height=slider_height, from_=0, to=int(self.Simu_parameters['Largeur Plaque']), number_of_steps=100, command=self.update_red_square, orientation="vertical")
        self.length_slider.set(int(self.Simu_parameters['Position Actuateur Largeur']))  # Set initial y position to the middle
        self.length_slider.grid(row=4, column=2, padx=(35,0), pady=(0,0), sticky="w")
        # Create corresponding Entry for vertical slider
        self.length_value = ctk.CTkEntry(self.plaque_info_frame, width=80)
        self.length_value.grid(row=3, column=2, pady=0, padx=(5,0), sticky="s")
        self.length_value.insert(0, str(self.plaque_lenght - self.length_slider.get()))  # Set initial value (reverse the initial y position)
        self.length_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length"))
        self.update_red_square()

        # Button for greetings (Demo-Test)
        self.HW_button = ctk.CTkButton(self.root, text="Lancer la Simulation", command=self.Simulate)
        self.HW_button.grid(row=2, column=0, columnspan=2, pady=(self.pix_spacing/2, self.pix_spacing), padx=self.pix_spacing, sticky="w")

        # Configure column weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def Simulate(self):
        messagebox.showinfo("Info", 'Hello, world!')

    def Save_as_clicked(self):
        New_save_as_path = filedialog.askdirectory(title='Enregister Sous')
        if New_save_as_path == '':
            New_save_as_path = "Aucune Sélection"
        self.Save_as_path = New_save_as_path
        self.load_frame()

    def create_rounded_rectangle(self, color):
        """Draw a rectangle with rounded corners."""
        r = 10
        W = 300
        L = 300*int(self.Simu_parameters['Largeur Plaque'])/int(self.Simu_parameters['Longueur Plaque'])

        # Coordinates of the rounded rectangle (with rounded corners)
        self.plaque_canvas.create_oval(0, 0, r*2, r*2, fill=color, outline=color)  # Top-left corner
        self.plaque_canvas.create_oval(W - r*2, 0, W, r*2, fill=color, outline=color)  # Top-right corner
        self.plaque_canvas.create_oval(0, L - r*2, r*2, L, fill=color, outline=color)  # Bottom-left corner
        self.plaque_canvas.create_oval(W - r*2, L - r*2, W, L, fill=color, outline=color)  # Bottom-right corner

        # Draw the four sides (excluding the corners)
        self.plaque_canvas.create_rectangle(r, 0, W - r, L, fill=color, outline=color)  # Top and bottom
        self.plaque_canvas.create_rectangle(0, r, W, L - r, fill=color, outline=color)  # Left and right

    def update_red_square(self, event=None):
        # Get the x position from the width slider (horizontal slider)
        x = self.width_slider.get()  
        # Get the y position from the length slider (vertical slider)
        # y = (300 - (300 - self.length_slider.get()))  # Reverse the y value for the vertical slider to make it move upward as the slider value increases
        y = self.length_slider.get()  # Reverse the y value for the vertical slider to make it move upward as the slider value increases

        pos_x_in_pix = x*300/int(self.Simu_parameters['Longueur Plaque'])
        pos_y_in_pix = 300*((int(self.Simu_parameters['Largeur Plaque'])) - y)/int(self.Simu_parameters['Longueur Plaque'])

        self.plaque_canvas.coords(self.red_dot, pos_x_in_pix - 5, pos_y_in_pix - 5, pos_x_in_pix + 5, pos_y_in_pix + 5)

        # Update the corresponding Entry valueshttps://chatgpt.com/c/6793ee06-1830-800a-bef3-c475d0aae5b2
        self.width_value.delete(0, ctk.END)
        self.width_value.insert(0, str(round(x,5)))
        self.length_value.delete(0, ctk.END)
        self.length_value.insert(0, str(round(y,5)))  # Update entry with the corrected value for y

    def update_slider_from_entry(self, slider_type):
        """Update slider from entry widget."""
        try:
            if slider_type == "width":
                value = float(self.width_value.get())
                # Ensure value is within slider's range
                if 0 <= value <= int(self.Simu_parameters['Longueur Plaque']):
                    self.width_slider.set(value)
            elif slider_type == "length":
                value = float(self.length_value.get())
                # Ensure value is within slider's range (reverse the input value for vertical slider)
                if 0 <= value <= int(self.Simu_parameters['Largeur Plaque']):
                    self.length_slider.set(value)  # Reverse for vertical slider
        except ValueError:
            pass  # Ignore invalid input (e.g., if the input is not a number)

    def Reset_to_default(self):
        pass
        # TODO
        

if __name__ == "__main__":
    app = GUI()
    app.root.mainloop()