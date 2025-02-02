import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from Simulation import Launch_Simu
import math
import sys
import json

# TODO slider for interest point
# TODO Graph for interest point
# TODO add mm label to the entries sliders
# TODO Export data as excel
# TODO check params de convec thermique et puissance actu

# TODO save home position (in matplotlib animation display)
# TODO remove buttonss from mpl window? (in matplotlib animation display)

class GUI:
    def __init__(self):
        # Initialize root window
        self.root = ctk.CTk()
        self.root.geometry("900x700")
        self.background_color = "#1e1e1e" # Dark gray background
        self.root.configure(bg=self.background_color)
        self.root.title("Controleur Simulation")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        ctk.set_appearance_mode("dark")  # Dark mode for better contrast
        ctk.set_default_color_theme("blue")  # Blue theme for buttons and other elements

        # Initialize variables
        self.pix_spacing = 20
        self.pix_to_plaque_box = 3
        self.Save_as_path = "Aucune Sélection"

        self.Simu_parameters = {
            'plaque_largeur' : 60, # mm
            'plaque_longueur' : 116, # mm
            'mm_par_element' : 5, # mm # TODO Data entry field
            'Temperature_Ambiante_C' : 20, # C
            'position_longueur_actuateur' : 15.5, # mm
            'position_largeur_actuateur' : 30, # mm
            'largeur_actu' : 15, # mm # TODO Data entry field
            'longueur_actu' : 15, # mm # TODO Data entry field
            'puissance_actuateur' : 1.46, #W
            'masse_volumique_plaque' : 2698, # kg/m3 # TODO Data entry field
            'epaisseur_plaque_mm' : 1.5, # mm # TODO Data entry field
            'capacite_thermique_plaque' : 900, # J/Kg*K # TODO Data entry field
            'conductivite_thermique_plaque' : 220, # W/m*K # TODO Data entry field
            'masse_volumique_Air' : 1.293, # kg/m3 # TODO Data entry field
            'capacite_thermique_Air' : 1005, # J/Kg*K # TODO Data entry field
            'conductivite_thermique_Air' : 0.025, # W/m*K
            'coefficient_convection' : 5, # W/m2*K # TODO Data entry field
            'time_step' : 0.01, #sec # TODO Data entry field
            'simu_duration' : 250, #sec # TODO Data entry field
            'animation_lenght' : 100 # frames # TODO Data entry field
        }
        self.Initial_parameters = self.Simu_parameters.copy()

        self.load_frame() # Load initial frame

    def on_closing(self):
        print("Closing the application...")
        sys.exit()  # This will terminate the program completely

    def on_enter_key(self, event):
        self.Log_parameters()
        self.load_frame()

    def Log_parameters(self):
        self.Simu_parameters['Temperature_Ambiante_C'] = self.Temp_ambiante_user_entry.get()
        self.Simu_parameters['plaque_largeur'] = self.plaque_width_user_entry.get()
        self.Simu_parameters['plaque_longueur'] = self.plaque_lenght_user_entry.get()
        self.Simu_parameters['position_longueur_actuateur'] = self.lenght_value.get()
        self.Simu_parameters['position_largeur_actuateur'] = self.width_value.get()
        self.Simu_parameters['puissance_actuateur'] = self.actu_power_user_entry.get()

    def Test_function(self):
        print(self.Simu_parameters)

    def load_simu_params_from_json(self):
        json_path = filedialog.askopenfile(title="Sélectionnez un fichier JSON", filetypes=[("JSON files", "*.json")])
        
        # if json_path.name != '':
        if json_path != None:
            with open(json_path.name, 'r') as file:
                self.Simu_parameters = json.load(file)
            self.Initial_parameters = self.Simu_parameters.copy()
            self.load_frame()
        else:
            print('No json. Selected')

    def load_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame for save path and button
        save_frame = ctk.CTkFrame(self.root)
        save_frame.grid(row=0, column=0, columnspan=2, pady=(self.pix_spacing, self.pix_spacing/2), padx=self.pix_spacing, sticky="ew")
        save_frame.columnconfigure(0, weight=1)
        save_frame.columnconfigure(1, weight=0)
        # Save Path Label
        text_save_path = f"Données de simulation enregistrées dans : {self.Save_as_path}"
        label_save_path = ctk.CTkLabel(save_frame, text=text_save_path)
        label_save_path.grid(row=0, column=0, sticky="w", padx=(5,0))
        # 'Save as' boutton
        self.Select_path_button = ctk.CTkButton(save_frame, text="Enregistrer sous", command=self.Save_as_clicked)
        self.Select_path_button.grid(row=0, column=1, sticky="e", padx=(0,5), pady=(5,0))

        # load params from json
        self.Select_path_button = ctk.CTkButton(save_frame, text="Charger les paramètres à partir d'un .json", command=self.load_simu_params_from_json)
        self.Select_path_button.grid(row=1, column=0, sticky="w", padx=(5,0), pady=(0,5))

        # Frame for plaque info
        self.plaque_info_frame = ctk.CTkFrame(self.root)
        self.plaque_info_frame.grid(row=1, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.plaque_info_frame.columnconfigure(0, weight=0)
        self.plaque_info_frame.columnconfigure(1, weight=0)
        row_count = 0 # Facilite lajout de plus de widget

        # Label for Temp Ambiante
        Temp_Ambi_label = ctk.CTkLabel(self.plaque_info_frame, text="Température Ambiante (°C) : ")
        Temp_Ambi_label.grid(row=row_count, column=0, sticky="w", padx=(5,0), pady=(5,0))
        # data Entry for Temp Ambiante 
        self.Temp_ambiante_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.Temp_ambiante_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.Temp_ambiante_user_entry.insert("1", str(self.Simu_parameters['Temperature_Ambiante_C']))
        self.Temp_ambiante_user_entry.grid(row=row_count, column=1, sticky="w", pady=(5,0))
        row_count+=1

        # Label for plaque width
        plaque_width = ctk.CTkLabel(self.plaque_info_frame, text="Largeur de la plaque (mm) : ")
        plaque_width.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque width 
        self.plaque_width_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.plaque_width_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_width_user_entry.insert("1", str(self.Simu_parameters['plaque_largeur']))
        self.plaque_width_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for plaque lenght
        plaque_lenght = ctk.CTkLabel(self.plaque_info_frame, text="Longueur de la plaque (mm) : ")
        plaque_lenght.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque lenght
        self.plaque_lenght_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.plaque_lenght_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_lenght_user_entry.insert("1", str(self.Simu_parameters['plaque_longueur']))
        self.plaque_lenght_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Actuateur Power
        Actu_Power_Label = ctk.CTkLabel(self.plaque_info_frame, text="Puissance de l'actuateur (W) : ")
        Actu_Power_Label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for Actuateur Power
        self.actu_power_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.actu_power_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.actu_power_user_entry.insert("1", str(self.Simu_parameters['puissance_actuateur']))
        self.actu_power_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Code for plaque with sliders:
        # Label
        PosActu_Label = ctk.CTkLabel(self.plaque_info_frame, text="Position de l'actuateur :")
        PosActu_Label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        row_count += 1
        # Plaque
        self.plaque_width = int(300*float(self.Simu_parameters['plaque_largeur'])/float(self.Simu_parameters['plaque_longueur']))
        self.plaque_lenght = 300
        self.plaque_box_frame = ctk.CTkFrame(self.plaque_info_frame, height=self.plaque_width, width=self.plaque_lenght, fg_color="black")
        self.plaque_box_frame.grid(row=row_count, column=0, pady=(5,5), columnspan = 2, padx=10)
        self.plaque_canvas = ctk.CTkCanvas(self.plaque_box_frame, height=self.plaque_width, width=self.plaque_lenght, bg='#2B2B2B', bd=0, highlightthickness=0)
        self.plaque_canvas.pack()
        self.create_rounded_rectangle('gray10')# Black background for actuateur red square
        self.Actuateur_shape = self.plaque_canvas.create_rectangle(10, 10, 20, 20, fill="#ff4242", outline="#ff4242")# Red Square For actuateur
        row_count += 1
        # Create horizontal slider for the red square's x position (width)
        min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
        self.lenght_slider = ctk.CTkSlider(self.plaque_info_frame, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_longueur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="horizontal", button_color="#ff4242")
        self.lenght_slider.set(float(self.Simu_parameters['position_longueur_actuateur']))  # Set initial x position to the middle
        self.lenght_slider.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,4), sticky="ew")
        # Create corresponding Entry for horizontal slider
        self.lenght_value = ctk.CTkEntry(self.plaque_info_frame, width=80)
        self.lenght_value.grid(row=row_count, column=2, padx=0, pady=(0,5), sticky="w")
        self.lenght_value.insert(0, str(self.lenght_slider.get()))  # Set initial value
        self.lenght_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length"))
        # Create vertical slider for the red square's y position (height)
        slider_height = int(300*float(self.Simu_parameters['plaque_largeur'])/float(self.Simu_parameters['plaque_longueur']))
        min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
        self.width_slider = ctk.CTkSlider(self.plaque_info_frame, height=slider_height, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="vertical", button_color="#ff4242")
        self.width_slider.set(float(self.Simu_parameters['position_largeur_actuateur']))  # Set initial y position to the middle
        self.width_slider.grid(row=row_count-1, column=2, padx=(35,0), pady=(0,0), sticky="w")
        # Create corresponding Entry for vertical slider
        self.width_value = ctk.CTkEntry(self.plaque_info_frame, width=80)
        self.width_value.grid(row=row_count - 2, column=2, pady=0, padx=(5,0), sticky="s")
        self.width_value.insert(0, str(self.plaque_lenght - self.width_slider.get()))  # Set initial value (reverse the initial y position)
        self.width_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width"))
        self.update_actu_red_square()
        row_count+=1

        # Reset Boutton
        self.Reset_Actu_Posi_button = ctk.CTkButton(self.plaque_info_frame, text="Réinitialiser les Paramètres", command=self.Reset_to_default)
        self.Reset_Actu_Posi_button.grid(row=row_count, column=0, sticky="w", padx = (5, 0), pady=(0,5))


        # Button for simulation
        self.HW_button = ctk.CTkButton(self.root, text="Lancer la Simulation", command=self.Simulate)
        self.HW_button.grid(row=2, column=0, columnspan=2, pady=(self.pix_spacing/2, self.pix_spacing), padx=self.pix_spacing, sticky="w")

        # Configure column weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def Simulate(self):
        self.Log_parameters()
        Launch_Simu(self.Simu_parameters)
        # messagebox.showinfo("Info", 'Hello, world!')

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
        L = int(300*float(self.Simu_parameters['plaque_largeur'])/float(self.Simu_parameters['plaque_longueur']))

        # Coordinates of the rounded rectangle (with rounded corners)
        self.plaque_canvas.create_oval(0, 0, r*2, r*2, fill=color, outline=color)  # Top-left corner
        self.plaque_canvas.create_oval(W - r*2, 0, W, r*2, fill=color, outline=color)  # Top-right corner
        self.plaque_canvas.create_oval(0, L - r*2, r*2, L, fill=color, outline=color)  # Bottom-left corner
        self.plaque_canvas.create_oval(W - r*2, L - r*2, W, L, fill=color, outline=color)  # Bottom-right corner

        # Draw the four sides (excluding the corners)
        self.plaque_canvas.create_rectangle(r, 0, W - r, L, fill=color, outline=color)  # Top and bottom
        self.plaque_canvas.create_rectangle(0, r, W, L - r, fill=color, outline=color)  # Left and right

    def update_actu_red_square(self, event=None):
        # Get the x position from the width slider (horizontal slider)
        x = self.lenght_slider.get()  
        # Get the y position from the length slider (vertical slider)
        # y = (300 - (300 - self.width_slider.get()))  # Reverse the y value for the vertical slider to make it move upward as the slider value increases
        y = self.width_slider.get()  # Reverse the y value for the vertical slider to make it move upward as the slider value increases

        pos_x_in_pix = int(x*300/float(self.Simu_parameters['plaque_longueur']))
        pos_y_in_pix = int(300*((float(self.Simu_parameters['plaque_largeur'])) - y)/float(self.Simu_parameters['plaque_longueur']))

        half_longueur_actu_in_pix = int(float(self.Simu_parameters['longueur_actu'])*300/float(self.Simu_parameters['plaque_longueur'])/2)
        half_largeur_actu_in_pix = int(float(self.Simu_parameters['largeur_actu'])*300/float(self.Simu_parameters['plaque_longueur'])/2)
        self.plaque_canvas.coords(self.Actuateur_shape, pos_x_in_pix - half_longueur_actu_in_pix, pos_y_in_pix - half_largeur_actu_in_pix, pos_x_in_pix + half_longueur_actu_in_pix, pos_y_in_pix + half_largeur_actu_in_pix)

        # self.plaque_canvas.coords(self.Actuateur_shape, pos_x_in_pix - 5, pos_y_in_pix - 5, pos_x_in_pix + 5, pos_y_in_pix + 5)

        # Update the corresponding Entry valueshttps://chatgpt.com/c/6793ee06-1830-800a-bef3-c475d0aae5b2
        self.lenght_value.delete(0, ctk.END)
        self.lenght_value.insert(0, str(round(x,5)))
        self.width_value.delete(0, ctk.END)
        self.width_value.insert(0, str(round(y,5)))  # Update entry with the corrected value for y

    def update_slider_from_entry(self, slider_type):
        """Update slider from entry widget."""
        try:
            if slider_type == "lenght":
                value = float(self.lenght_value.get())
                # Ensure value is within slider's range
                min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_longueur']) - min_max_for_actu_size:
                    self.lenght_slider.set(value)
            elif slider_type == "width":
                value = float(self.width_value.get())
                # Ensure value is within slider's range (reverse the input value for vertical slider)
                min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size:
                    self.width_slider.set(value)  # Reverse for vertical slider
        except ValueError:
            pass  # Ignore invalid input (e.g., if the input is not a number)

    def Reset_to_default(self):
        self.Simu_parameters = self.Initial_parameters
        self.load_frame()
        

if __name__ == "__main__":
    app = GUI()
    app.root.mainloop()