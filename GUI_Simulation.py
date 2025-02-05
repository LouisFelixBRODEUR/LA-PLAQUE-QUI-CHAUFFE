from tkinter import filedialog
import customtkinter as ctk
from Simulation import Plaque
import math
import sys
import json
import matplotlib.pyplot as plt

# TODO checker leffet de time_step et mm+element sur lexactitude de la simu
# TODO automatiser le set des parametre de sium
# TODO slider for interest point
# TODO add mm label to the entries sliders
# TODO Export data as excel
# TODO save animation as mp4
# TODO save interest point data
# TODO check params de convec thermique et puissance actu to fit avec les tests
# TODO refroidissement
# TODO add contraite pour que C < 0.5s

class GUI:
    def __init__(self):
        # Initialize root window
        self.root = ctk.CTk()
        self.root.geometry("700x780")
        self.background_color = "#1e1e1e" # Dark gray background
        self.root.configure(bg=self.background_color)
        self.root.title("Controleur Simulation")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.validate_cmd = self.root.register(self.validate_input)
        self.validate_cmd_Neg = self.root.register(self.validate_input_Neg)

        ctk.set_appearance_mode("dark")  # Dark mode for better contrast
        ctk.set_default_color_theme("blue")  # Blue theme for buttons and other elements

        # Initialize variables
        self.pix_spacing = 20
        self.pix_to_plaque_box = 3
        self.plaque_display_size = 300
        self.Save_as_path = "Aucune Sélection"

        self.Simu_parameters = {
            'plaque_largeur' : 60, # mm
            'plaque_longueur' : 116, # mm
            'mm_par_element' : 4, # mm # TODO Automatic set
            'Temperature_Ambiante_C' : 25, # C
            'position_longueur_actuateur' : 15, # mm
            'position_largeur_actuateur' : 30, # mm
            'largeur_actu' : 15, # mm
            'longueur_actu' : 15, # mm
            'puissance_actuateur' : 6, #W
            'masse_volumique_plaque' : 2698, # kg/m3 # TODO Data entry field
            'epaisseur_plaque_mm' : 1.5, # mm # TODO Data entry field
            'capacite_thermique_plaque' : 900, # J/Kg*K # TODO Data entry field
            'conductivite_thermique_plaque' : 220, # W/m*K # TODO Data entry field
            'coefficient_convection' : 10, # W/m2*K # TODO Data entry field
            'time_step' : 0.01, #sec # TODO Automatic set
            'simu_duration' : 100, #sec
            'animation_length' : 100, # frames # TODO Data entry field
            'point_interet_1_largeur' : 30, # mm # TODO add slider
            'point_interet_1_longueur' : 15, # mm # TODO add slider
            'point_interet_2_largeur' : 30, # mm # TODO add slider
            'point_interet_2_longueur' : 60, # mm # TODO add slider
            'point_interet_3_largeur' : 30, # mm # TODO add slider
            'point_interet_3_longueur' : 105, # mm # TODO add slider
        }
        self.Initial_parameters = self.Simu_parameters.copy()

        self.load_frame() # Load initial frame

    def on_closing(self):
        # Kill programme quand X est clique
        print("Closing the application...")
        sys.exit()

    def on_enter_key(self, event=None):
        self.Log_parameters()
        self.load_frame()

    def Log_parameters(self):
        self.Simu_parameters['Temperature_Ambiante_C'] = float(self.Temp_ambiante_user_entry.get())
        self.Simu_parameters['plaque_largeur'] = float(self.plaque_width_user_entry.get())
        self.Simu_parameters['plaque_longueur'] = float(self.plaque_length_user_entry.get())
        self.Simu_parameters['position_longueur_actuateur'] = float(self.length_value.get())
        self.Simu_parameters['position_largeur_actuateur'] = float(self.width_value.get())
        self.Simu_parameters['puissance_actuateur'] = float(self.actu_power_user_entry.get())
        self.Simu_parameters['largeur_actu'] = float(self.actu_width_user_entry.get())
        self.Simu_parameters['longueur_actu'] = float(self.actu_length_user_entry.get())
        self.Simu_parameters['simu_duration'] = float(self.simu_length_user_entry.get())
        self.parameters_correction()

    def Test_function(self):
        print(self.Simu_parameters)

    def load_simu_params_from_json(self):
        json_path = filedialog.askopenfile(title="Sélectionnez un fichier JSON", filetypes=[("JSON files", "*.json")])
        
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

        # Reset Boutton
        self.Reset_Actu_Posi_button = ctk.CTkButton(self.plaque_info_frame, text="Réinitialiser les Paramètres", command=self.Reset_to_default)
        self.Reset_Actu_Posi_button.grid(row=row_count, column=0, sticky="w", padx = (5, 0), pady=(5,0))
        row_count+=1

        # Label for Temp Ambiante
        Temp_Ambi_label = ctk.CTkLabel(self.plaque_info_frame, text="Température ambiante (°C) : ")
        Temp_Ambi_label.grid(row=row_count, column=0, sticky="w", padx=(5,0), pady=(0,0))
        # data Entry for Temp Ambiante 
        self.Temp_ambiante_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
        self.Temp_ambiante_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.Temp_ambiante_user_entry.insert("1", str(self.Simu_parameters['Temperature_Ambiante_C']))
        self.Temp_ambiante_user_entry.grid(row=row_count, column=1, sticky="w", pady=(0,0))
        row_count+=1

        # Label for plaque width
        plaque_width = ctk.CTkLabel(self.plaque_info_frame, text="Largeur de la plaque (mm) : ")
        plaque_width.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque width 
        self.plaque_width_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.plaque_width_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_width_user_entry.insert("1", str(self.Simu_parameters['plaque_largeur']))
        self.plaque_width_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for plaque length
        plaque_length = ctk.CTkLabel(self.plaque_info_frame, text="Longueur de la plaque (mm) : ")
        plaque_length.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque length
        self.plaque_length_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.plaque_length_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_length_user_entry.insert("1", str(self.Simu_parameters['plaque_longueur']))
        self.plaque_length_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Actu width
        actu_width_label = ctk.CTkLabel(self.plaque_info_frame, text="Largeur de l'actuateur (mm) : ")
        actu_width_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque width 
        self.actu_width_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.actu_width_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.actu_width_user_entry.insert("1", str(self.Simu_parameters['largeur_actu']))
        self.actu_width_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Actu length
        actu_length_label = ctk.CTkLabel(self.plaque_info_frame, text="Longueur de l'actuateur (mm) : ")
        actu_length_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque length
        self.actu_length_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.actu_length_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.actu_length_user_entry.insert("1", str(self.Simu_parameters['longueur_actu']))
        self.actu_length_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Actuateur Power
        Actu_Power_Label = ctk.CTkLabel(self.plaque_info_frame, text="Puissance de l'actuateur (W) : ")
        Actu_Power_Label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for Actuateur Power
        self.actu_power_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
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
        self.plaque_width = min(self.plaque_display_size, int(self.plaque_display_size*float(self.Simu_parameters['plaque_largeur'])/float(self.Simu_parameters['plaque_longueur'])))
        self.plaque_length = min(self.plaque_display_size, int(self.plaque_display_size*float(self.Simu_parameters['plaque_longueur'])/float(self.Simu_parameters['plaque_largeur'])))
        self.plaque_box_frame = ctk.CTkFrame(self.plaque_info_frame, height=self.plaque_width, width=self.plaque_length, fg_color="black")
        self.plaque_box_frame.grid(row=row_count, column=0, pady=(5,5), columnspan = 2, padx=10)
        self.plaque_canvas = ctk.CTkCanvas(self.plaque_box_frame, height=self.plaque_width, width=self.plaque_length, bg='#2B2B2B', bd=0, highlightthickness=0)
        self.plaque_canvas.pack()
        self.create_rounded_rectangle('gray10')# Black background for actuateur red square
        self.Actuateur_shape = self.plaque_canvas.create_rectangle(10, 10, 20, 20, fill="#ff4242", outline="#ff4242")# Red Square For actuateur
        row_count += 1
        # Create horizontal slider for the red square's x position (width)
        min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
        self.length_slider = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_longueur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="horizontal", button_color="#ff4242")
        self.length_slider.set(float(self.Simu_parameters['position_longueur_actuateur']))  # Set initial x position to the middle
        self.length_slider.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,4), sticky="ew")
        # Create corresponding Entry for horizontal slider
        self.length_value = ctk.CTkEntry(self.plaque_info_frame, width=80, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.length_value.grid(row=row_count, column=2, padx=0, pady=(0,5), sticky="w")
        self.length_value.insert(0, str(self.length_slider.get()))  # Set initial value
        self.length_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length"))
        # Create vertical slider for the red square's y position (height)
        min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
        self.width_slider = ctk.CTkSlider(self.plaque_info_frame, height=self.plaque_width, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="vertical", button_color="#ff4242")
        # print(float(self.Simu_parameters['position_largeur_actuateur']))
        self.width_slider.set(float(self.Simu_parameters['position_largeur_actuateur']))  # Set initial y position to the middle
        self.width_slider.grid(row=row_count-1, column=2, padx=(35,0), pady=(0,0), sticky="w")
        # Create corresponding Entry for vertical slider
        self.width_value = ctk.CTkEntry(self.plaque_info_frame, width=80, validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.width_value.grid(row=row_count - 2, column=2, pady=0, padx=(5,0), sticky="s")
        self.width_value.insert(0, str(self.plaque_length - self.width_slider.get()))  # Set initial value (reverse the initial y position)
        self.width_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width"))
        self.update_actu_red_square()
        row_count+=1

        # Frame for Simu info
        self.simu_info_frame = ctk.CTkFrame(self.root)
        self.simu_info_frame.grid(row=2, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.simu_info_frame.columnconfigure(0, weight=0)
        self.simu_info_frame.columnconfigure(1, weight=0)
        row_count = 0 # Facilite lajout de plus de widget

        # Label for simu length
        simu_length_label = ctk.CTkLabel(self.simu_info_frame, text="Durée de la simulation (secondes) : ")
        simu_length_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque length
        self.simu_length_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.simu_length_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.simu_length_user_entry.insert("1", str(self.Simu_parameters['simu_duration']))
        self.simu_length_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Button for simulation
        self.HW_button = ctk.CTkButton(self.simu_info_frame, text="Lancer la Simulation", command=self.Simulate)
        self.HW_button.grid(row=row_count, column=0, pady=(5,5), padx=(5,0), sticky="w")

        # Configure column weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def Simulate(self):
        self.on_enter_key()
        self.root.attributes("-disabled", True)
        My_plaque = Plaque(self.Simu_parameters)
        try:
            My_plaque.Launch_Simu_mpl_ani()
        except Exception as e:
            plt.close('all')
            print(f"An error occurred during Simulation: {e}")
        self.root.attributes("-disabled", False)

    def Save_as_clicked(self):
        New_save_as_path = filedialog.askdirectory(title='Enregister Sous')
        if New_save_as_path == '':
            New_save_as_path = "Aucune Sélection"
        self.Save_as_path = New_save_as_path
        self.load_frame()

    def create_rounded_rectangle(self, color):
        """Draw a rectangle with rounded corners."""
        r = 10
        W = self.plaque_length
        L = self.plaque_width
        # Coordinates of the rounded rectangle (with rounded corners)
        self.plaque_canvas.create_oval(0, 0, r*2, r*2, fill=color, outline=color)  # Top-left corner
        self.plaque_canvas.create_oval(W - r*2, 0, W, r*2, fill=color, outline=color)  # Top-right corner
        self.plaque_canvas.create_oval(0, L - r*2, r*2, L, fill=color, outline=color)  # Bottom-left corner
        self.plaque_canvas.create_oval(W - r*2, L - r*2, W, L, fill=color, outline=color)  # Bottom-right corner
        # Draw the four sides (excluding the corners)
        self.plaque_canvas.create_rectangle(r, 0, W - r, L, fill=color, outline=color)  # Top and bottom
        self.plaque_canvas.create_rectangle(0, r, W, L - r, fill=color, outline=color)  # Left and right

    def update_actu_red_square(self, event=None):
        x = self.length_slider.get()  
        y = self.width_slider.get()
        self.update_red_square()
        self.length_value.delete(0, ctk.END)
        self.length_value.insert(0, str(round(x,5)))
        self.width_value.delete(0, ctk.END)
        self.width_value.insert(0, str(round(y,5)))

    def update_red_square(self, event=None):
        x = self.length_slider.get()  
        y = self.width_slider.get()
        pos_x_in_pix = int(self.plaque_length*x/(float(self.Simu_parameters['plaque_longueur'])))
        pos_y_in_pix = int(self.plaque_width*(float(self.Simu_parameters['plaque_largeur']) - y)/float(self.Simu_parameters['plaque_largeur']))
        half_longueur_actu_in_pix = int(self.plaque_length*float(self.Simu_parameters['longueur_actu'])/(float(self.Simu_parameters['plaque_longueur']))/2)
        half_largeur_actu_in_pix = int(self.plaque_width*float(self.Simu_parameters['largeur_actu'])/(float(self.Simu_parameters['plaque_largeur']))/2)
        self.plaque_canvas.coords(self.Actuateur_shape, pos_x_in_pix - half_longueur_actu_in_pix, pos_y_in_pix - half_largeur_actu_in_pix, pos_x_in_pix + half_longueur_actu_in_pix, pos_y_in_pix + half_largeur_actu_in_pix)

    def validate_input(self, P):# Permet seulement les chiffres
        """Only allow numeric input (including decimal point)."""
        if P == "" or P.isdigit() or (P.replace('.', '', 1).isdigit() and P.count('.') <= 1):
            return True
        else:
            return False
    def validate_input_Neg(self, P):# Permet seulement le chiffre incluant les negatifs
        if P[0] == "-":
            P = P[1:]
        if P == "" or P.isdigit() or (P.replace('.', '', 1).isdigit() and P.count('.') <= 1):
            return True
        else:
            return False

    def parameters_correction(self):
        # Si plaque trop large ou trop longue
        if self.Simu_parameters['largeur_actu'] > self.Simu_parameters['plaque_largeur']:
            self.Simu_parameters['plaque_largeur'] = self.Simu_parameters['largeur_actu']
            print('OUT OF BONDS plaque')
        if self.Simu_parameters['longueur_actu'] > self.Simu_parameters['plaque_longueur']:
            self.Simu_parameters['plaque_longueur'] = self.Simu_parameters['longueur_actu']
            print('OUT OF BONDS plaque')
        # Si position actuateur hors de la plaque
        if not(self.Simu_parameters['largeur_actu']/2 < self.Simu_parameters['position_largeur_actuateur'] < self.Simu_parameters['plaque_largeur']-self.Simu_parameters['largeur_actu']/2):
            self.Simu_parameters['position_largeur_actuateur'] = self.Simu_parameters['plaque_largeur']/2
            print('OUT OF BONDS actuateur')
        if not(self.Simu_parameters['longueur_actu']/2 < self.Simu_parameters['position_longueur_actuateur'] < self.Simu_parameters['plaque_longueur']-self.Simu_parameters['longueur_actu']/2):
            self.Simu_parameters['position_longueur_actuateur'] = self.Simu_parameters['plaque_longueur']/2
            print('OUT OF BONDS actuateur')
        # Si point_interet pas dans le range
        if not (0 < self.Simu_parameters['point_interet_1_largeur'] < self.Simu_parameters['plaque_largeur']):
            self.Simu_parameters['point_interet_1_largeur'] = self.Simu_parameters['plaque_largeur']/2
            print('OUT OF BONDS point_interet')
        if not (0 < self.Simu_parameters['point_interet_1_longueur'] < self.Simu_parameters['plaque_longueur']):
            self.Simu_parameters['point_interet_1_longueur'] = self.Simu_parameters['plaque_longueur']/4
            print('OUT OF BONDS point_interet')
        if not (0 < self.Simu_parameters['point_interet_2_largeur'] < self.Simu_parameters['plaque_largeur']):
            self.Simu_parameters['point_interet_2_largeur'] = self.Simu_parameters['plaque_largeur']/2
            print('OUT OF BONDS point_interet')
        if not (0 < self.Simu_parameters['point_interet_2_longueur'] < self.Simu_parameters['plaque_longueur']):
            self.Simu_parameters['point_interet_2_longueur'] = self.Simu_parameters['plaque_longueur']/2
            print('OUT OF BONDS point_interet')
        if not (0 < self.Simu_parameters['point_interet_3_largeur'] < self.Simu_parameters['plaque_largeur']):
            self.Simu_parameters['point_interet_3_largeur'] = self.Simu_parameters['plaque_largeur']/2
            print('OUT OF BONDS point_interet')
        if not (0 < self.Simu_parameters['point_interet_3_longueur'] < self.Simu_parameters['plaque_longueur']):
            self.Simu_parameters['point_interet_3_longueur'] = self.Simu_parameters['plaque_longueur']/4*3
            print('OUT OF BONDS point_interet')


    def update_slider_from_entry(self, slider_type):
        try:
            if slider_type == "length":
                value = float(self.length_value.get())
                min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_longueur']) - min_max_for_actu_size:
                    self.length_slider.set(value)
                    self.update_red_square()
            elif slider_type == "width":
                value = float(self.width_value.get())
                min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size:
                    self.width_slider.set(value)  # Reverse for vertical slider
                    self.update_red_square()
        except ValueError:
            print('Error')
            pass  # Ignore invalid input (e.g., if the input is not a number)

    def Reset_to_default(self):
        self.Simu_parameters = self.Initial_parameters
        self.load_frame()
        

if __name__ == "__main__":
    app = GUI()
    app.root.mainloop()