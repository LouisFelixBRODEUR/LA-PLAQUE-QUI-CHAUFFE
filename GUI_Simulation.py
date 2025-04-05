from tkinter import filedialog
import customtkinter as ctk
from Simulation import Plaque
import math
import sys
import json
import matplotlib.pyplot as plt
import copy
import numpy
import tempfile

# TODO Au moins 10 autres paramètres what de fuck?
# TODO add a scroll bar
# TODO Perturbation non-ponctuelle
# TODO Flick when ENTER
# TODO Chronomètre ??en print()??
# TODO Test variables dentre qui ne bug pas pour infini -infini et zero -> Cap sur certaine valeur
# TODO manuel de l'utilisateur
# TODO Clean Comments


class GUI:
    def __init__(self):
        # Initialize root window
        self.root = ctk.CTk()
        self.root.geometry("800x850")
        self.background_color = "#1e1e1e" # Dark gray background
        self.root.configure(bg=self.background_color)
        self.root.title("Controleur Simulation")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.validate_cmd = self.root.register(self.validate_input)
        self.validate_cmd_Neg = self.root.register(self.validate_input_Neg)
        self.root.bind("<Control-q>", self.Test_function)

        ctk.set_appearance_mode("dark")  # Dark mode for better contrast
        ctk.set_default_color_theme("blue")  # Blue theme for buttons and other elements

        # Initialize variables
        self.save_txt_bool = False
        self.pix_spacing = 20
        self.pix_to_plaque_box = 3
        self.plaque_display_size = 300
        self.Save_as_path = "Aucune Sélection"

        self.Simu_parameters = {
            'plaque_largeur' : 60, # mm
            'plaque_longueur' : 116, # mm
            'mm_par_element' : 1, # mm
            'Temperature_Ambiante_C' : 25, # C
            'position_longueur_actuateur' : 15, # mm
            'position_largeur_actuateur' : 30, # mm
            'largeur_actu' : 15, # mm
            'longueur_actu' : 15, # mm
            'puissance_actuateur' : 3, # W
            'couple_actuateur' : 1, # NA
            'convection_actuateur' : 40, # W/m2*K
            'masse_volumique_plaque' : 2700, # kg/m3
            'masse_volumique_actu' : 3950, # kg/m3
            'epaisseur_plaque_mm' : 1.6, # mm
            'epaisseur_actu_mm' : 0.05, # mm
            'capacite_thermique_plaque' : 900, # J/Kg*K
            'capacite_thermique_Actu' : 760, # J/Kg*K
            'conductivite_thermique_plaque' : 110, # W/m*K
            'coefficient_convection' : 8, # W/m2*K
            'time_step' : 'auto', #sec
            'simu_duration' : 200, #sec
            'actu_start' : 10, # sec
            'actu_stop' : 150, # sec
            'point_interet_1_largeur' : 30, # mm
            'point_interet_1_longueur' : 15, # mm
            'point_interet_2_largeur' : 30, # mm
            'point_interet_2_longueur' : 60, # mm
            'point_interet_3_largeur' : 30, # mm
            'point_interet_3_longueur' : 105, # mm
            'perturbation_longueur' : 50, # mm
            'perturbation_largeur' : 10, # mm
            'perturabtion_start' : 50, #sec
            'perturabtion_stop' : 75, #sec
            'perturbation_power' : 5, #W
            'simu_acceleration_factor' : 10 #Multiplier
        }

        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as temp_file:
            self.temp_filename = temp_file.name  # Get the temporary file name
            json.dump(self.Simu_parameters, temp_file, indent=4)
        

        self.load_frame() # Load initial frame

    def on_closing(self):
        # Kill programme quand X est clique
        print("Fermeture de l'application...")
        sys.exit()

    def on_enter_key(self, event=None):
        self.Log_parameters()
        self.load_frame()

    def Log_parameters(self):
        if self.length_value_actu.get() == '':
            self.length_value_actu.insert(0, 0)
        if self.width_value_actu.get() == '':
            self.width_value_actu.insert(0,0)
        if self.length_value_pertu.get() == '':
            self.length_value_pertu.insert(0, 0)
        if self.width_value_pertu.get() == '':
            self.width_value_pertu.insert(0,0)
        if self.length_value_T1.get() == '':
            self.length_value_T1.insert(0, 0)
        if self.width_value_T1.get() == '':
            self.width_value_T1.insert(0,0)
        if self.length_value_T2.get() == '':
            self.length_value_T2.insert(0, 0)
        if self.width_value_T2.get() == '':
            self.width_value_T2.insert(0,0)
        if self.length_value_T3.get() == '':
            self.length_value_T3.insert(0, 0)
        if self.width_value_T3.get() == '':
            self.width_value_T3.insert(0,0)

        self.Simu_parameters['Temperature_Ambiante_C'] = float(self.Temp_ambiante_user_entry.get())
        self.Simu_parameters['plaque_largeur'] = float(self.plaque_width_user_entry.get())
        self.Simu_parameters['plaque_longueur'] = float(self.plaque_length_user_entry.get())
        self.Simu_parameters['position_longueur_actuateur'] = float(self.length_value_actu.get())
        self.Simu_parameters['position_largeur_actuateur'] = float(self.width_value_actu.get())
        self.Simu_parameters['perturbation_longueur'] = float(self.length_value_pertu.get())
        self.Simu_parameters['perturbation_largeur'] = float(self.width_value_pertu.get())
        self.Simu_parameters['point_interet_1_largeur'] = float(self.width_value_T1.get())
        self.Simu_parameters['point_interet_1_longueur'] = float(self.length_value_T1.get())
        self.Simu_parameters['point_interet_2_largeur'] = float(self.width_value_T2.get())
        self.Simu_parameters['point_interet_2_longueur'] = float(self.length_value_T2.get())
        self.Simu_parameters['point_interet_3_largeur'] = float(self.width_value_T3.get())
        self.Simu_parameters['point_interet_3_longueur'] = float(self.length_value_T3.get())
        self.Simu_parameters['puissance_actuateur'] = float(self.actu_puissance_user_entry.get())
        self.Simu_parameters['largeur_actu'] = float(self.actu_width_user_entry.get())
        self.Simu_parameters['longueur_actu'] = float(self.actu_length_user_entry.get())
        self.Simu_parameters['simu_duration'] = float(self.simu_length_user_entry.get())  
        self.Simu_parameters['actu_start'] = float(self.Actu_start_time_user_entry.get())  
        self.Simu_parameters['actu_stop'] = float(self.Actu_stop_time_user_entry.get())  
        self.Simu_parameters['mm_par_element'] = float(self.Maillage_user_entry.get())  
        self.Simu_parameters['masse_volumique_plaque'] = float(self.masse_volumique_plaque_user_entry.get())
        self.Simu_parameters['epaisseur_plaque_mm'] = float(self.epaisseur_plaque_mm_user_entry.get())
        self.Simu_parameters['capacite_thermique_plaque'] = float(self.capacite_thermique_plaque_user_entry.get())
        self.Simu_parameters['conductivite_thermique_plaque'] = float(self.conductivite_thermique_plaque_user_entry.get())
        self.Simu_parameters['couple_actuateur'] = float(self.Couple_user_entry.get())
        self.Simu_parameters['coefficient_convection'] = float(self.coefficient_convection_user_entry.get())
        self.Simu_parameters['perturbation_power'] = float(self.perturbation_power_user_entry.get())
        self.Simu_parameters['perturabtion_start'] = float(self.perturbation_start_user_entry.get())
        self.Simu_parameters['perturabtion_stop'] = float(self.perturbation_stop_user_entry.get())        
        self.Simu_parameters['simu_acceleration_factor'] = float(self.simu_acceleration_factor_user_entry.get())  
        self.parameters_correction()

    def Test_function(self, event=None):
        print('Paramètres de simulation actuels :')
        for param, value in self.Simu_parameters.items():
            print(f'\t{param} : {value}')
        print('Paramètres de simulation initiaux :')
        with open(self.temp_filename, 'r') as temp_file:
            loaded_parameters = json.load(temp_file)
            for param, value in loaded_parameters.items():
                print(f'\t{param} : {value}')

    def load_simu_params_from_json(self):
        json_path = filedialog.askopenfile(title="Sélectionnez un fichier JSON", filetypes=[("JSON files", "*.json")])
        if json_path != None:
            with open(json_path.name, 'r') as file:
                self.Simu_parameters = json.load(file)
            self.load_frame()
        else:
            print('Pas de JSON. Sélectionné')

    def save_simu_params_in_json(self):
        self.Log_parameters()
        save_json_path = filedialog.asksaveasfilename(title="Enregistrer JSON sous")
        if save_json_path == '':
            print('Aucun fichier sélectionné')
            return
        if not(save_json_path[-5:].lower() == '.json'):
            save_json_path+='.json'
        with open(save_json_path, 'w') as file:
            json.dump(self.Simu_parameters, file, indent=4)
        print(f'Paramètres de simulation enregistrés dans : {save_json_path}')

    def load_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame for save path and button
        save_frame = ctk.CTkFrame(self.root)
        save_frame.grid(row=0, column=0, columnspan=2, pady=(self.pix_spacing, self.pix_spacing/2), padx=self.pix_spacing, sticky="ew")
        save_frame.columnconfigure(0, weight=1)
        save_frame.columnconfigure(1, weight=0)
        # 'Save as' boutton
        self.txt_path_button = ctk.CTkButton(save_frame, text="Enregistrer sous", command=self.Save_as_clicked)
        self.txt_path_button.grid(row=0, column=1, sticky="e", padx=(0,5), pady=(5,0))
         
        # TXT Save switch
        self.TXT_switch = ctk.CTkSwitch(save_frame, text=f"Enregistrer au format texte dans : {self.Save_as_path}", command=self.TXT_toggle)
        self.TXT_switch.grid(row=0, column=0, sticky="w", padx=(5,0), pady=(0,5))
        if self.save_txt_bool:
            self.TXT_switch.select()        
        
        # load params from json
        self.Json_path_button = ctk.CTkButton(save_frame, text="Charger les paramètres à partir d'un .json", command=self.load_simu_params_from_json)
        self.Json_path_button.grid(row=1, column=0, sticky="w", padx=(5,0), pady=(0,5))

        # save params in json
        self.Json_path_button = ctk.CTkButton(save_frame, text="Sauver les paramètres dans un .json", command=self.save_simu_params_in_json)
        self.Json_path_button.grid(row=2, column=0, sticky="w", padx=(5,0), pady=(0,5))

        # Frame for plaque info
        self.plaque_info_frame = ctk.CTkFrame(self.root)
        self.plaque_info_frame.grid(row=1, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.plaque_info_frame.columnconfigure(0, weight=0)
        self.plaque_info_frame.columnconfigure(1, weight=0)
        row_count = 0 # Facilite lajout de plus de widget
        row_count2 = 0

        # Reset Boutton
        self.Reset_Actu_Posi_button = ctk.CTkButton(self.plaque_info_frame, text="Réinitialiser les Paramètres", command=self.Reset_to_default)
        self.Reset_Actu_Posi_button.grid(row=row_count, column=0, sticky="w", padx = (5, 0), pady=(5,0))
        row_count+=1

        # Label for Temp Ambiante
        Temp_Ambi_label = ctk.CTkLabel(self.plaque_info_frame, text="Température ambiante (°C) : ")
        Temp_Ambi_label.grid(row=row_count2, column=2, sticky="ws", padx=(5,0), pady=(0,0))
        # data Entry for Temp Ambiante 
        self.Temp_ambiante_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
        self.Temp_ambiante_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.Temp_ambiante_user_entry.insert("1", str(self.Simu_parameters['Temperature_Ambiante_C']))
        self.Temp_ambiante_user_entry.grid(row=row_count2, column=3, sticky="ws", pady=(0,0))
        row_count2+=1
                
        # Label for masse_volumique_plaque
        masse_volumique_plaque_label = ctk.CTkLabel(self.plaque_info_frame, text="Masse volumique (kg/m³) : ")
        masse_volumique_plaque_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # data Entry for masse_volumique_plaque 
        self.masse_volumique_plaque_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.masse_volumique_plaque_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.masse_volumique_plaque_user_entry.insert("1", str(self.Simu_parameters['masse_volumique_plaque']))
        self.masse_volumique_plaque_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for capacite_thermique_plaque
        capacite_thermique_plaque_label = ctk.CTkLabel(self.plaque_info_frame, text="Capacité Thermique (J/Kg·K) : ")
        capacite_thermique_plaque_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # data Entry for capacite_thermique_plaque
        self.capacite_thermique_plaque_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.capacite_thermique_plaque_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.capacite_thermique_plaque_user_entry.insert("1", str(self.Simu_parameters['capacite_thermique_plaque']))
        self.capacite_thermique_plaque_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for coefficient_convection
        coefficient_convection_label = ctk.CTkLabel(self.plaque_info_frame, text="Coefficient de convection (W/m²·K) : ")
        coefficient_convection_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # data Entry for coefficient_convection
        self.coefficient_convection_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.coefficient_convection_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.coefficient_convection_user_entry.insert("1", str(self.Simu_parameters['coefficient_convection']))
        self.coefficient_convection_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for epaisseur_plaque_mm
        epaisseur_plaque_mm_label = ctk.CTkLabel(self.plaque_info_frame, text="Épaisseur de la plaque (mm) : ")
        epaisseur_plaque_mm_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # data Entry for epaisseur_plaque_mm 
        self.epaisseur_plaque_mm_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.epaisseur_plaque_mm_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.epaisseur_plaque_mm_user_entry.insert("1", str(self.Simu_parameters['epaisseur_plaque_mm']))
        self.epaisseur_plaque_mm_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for conductivite_thermique_plaque
        conductivite_thermique_plaque_label = ctk.CTkLabel(self.plaque_info_frame, text="Conductivité thermique (W/m·K) : ")
        conductivite_thermique_plaque_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # data Entry for conductivite_thermique_plaque
        self.conductivite_thermique_plaque_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.conductivite_thermique_plaque_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.conductivite_thermique_plaque_user_entry.insert("1", str(self.Simu_parameters['conductivite_thermique_plaque']))
        self.conductivite_thermique_plaque_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1

        # Label for Couple
        couple_label = ctk.CTkLabel(self.plaque_info_frame, text="Couple plaque-actuateur : ")
        couple_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # data Entry for Couple
        self.Couple_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Couple_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.Couple_user_entry.insert("1", str(self.Simu_parameters['couple_actuateur']))
        self.Couple_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1

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
        Actu_puissance_Label = ctk.CTkLabel(self.plaque_info_frame, text="Puissance dans l'actuateur (Watt) : ")
        Actu_puissance_Label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for Actuateur amp
        self.actu_puissance_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
        self.actu_puissance_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.actu_puissance_user_entry.insert("1", str(self.Simu_parameters['puissance_actuateur']))
        self.actu_puissance_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        row_count = max(row_count, row_count2)
        # Code for plaque with sliders:
        # Label
        PosActu_Label = ctk.CTkLabel(self.plaque_info_frame, text="Position de l'actuateur, des thermistance et de la perturbation (mm) :")
        PosActu_Label.grid(row=row_count, column=0, columnspan=2, sticky="w", padx=(5,0))
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
        self.Perturbation_shape = self.plaque_canvas.create_oval(14, 14, 14, 14, fill="#1DBC60", outline="#1DBC60")  # Green Circle for actuateur
        self.T1_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#0096FF", width=2),  # Vertical line
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#0096FF", width=2)   # Horizontal line
        ]
        self.T2_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#006400", width=2),  # Vertical line
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#006400", width=2)   # Horizontal line
        ]
        self.T3_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#FFFFFF", width=2),  # Vertical line
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#FFFFFF", width=2)   # Horizontal line
        ]
        
        row_count += 1

        # Frame for all vertical sliders
        self.vertical_sliders_frame = ctk.CTkFrame(self.plaque_info_frame, fg_color=self.plaque_info_frame.cget("fg_color"))
        self.vertical_sliders_frame.grid(row=row_count-2, column=2, columnspan=2, rowspan=2, sticky='wns')

        # Create horizontal slider for actuateur x position (width)
        min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
        self.length_slider_actu = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_longueur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="horizontal", button_color="#ff4242")
        # print(f'from {self.length_slider_actu.cget("from_")} to {self.length_slider_actu.cget("to")}')
        if self.length_slider_actu.cget("from_") < self.length_slider_actu.cget("to"):
            self.length_slider_actu.set(float(self.Simu_parameters['position_longueur_actuateur']))  # Set initial x position to the middle
        else:
            self.length_slider_actu.configure(state="disabled")
        self.length_slider_actu.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for  actuateur x position horizontal slider
        self.length_value_actu = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_actu.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_actu.insert(0, str(self.length_slider_actu.get()))  # Set initial value
        if self.length_slider_actu.cget("from_") >= self.length_slider_actu.cget("to"):
            self.length_value_actu.configure(state="disabled")
        self.length_value_actu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_actu"))

        # Create vertical slider for the actuateur's y position (height)
        min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
        self.width_slider_actu = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="vertical", button_color="#ff4242")
        # print(f'from {self.width_slider_actu.cget("from_")} to {self.width_slider_actu.cget("to")}')
        if self.width_slider_actu.cget("from_") < self.width_slider_actu.cget("to"):
            self.width_slider_actu.set(float(self.Simu_parameters['position_largeur_actuateur']))  # Set initial x position to the middle
        else:
            self.width_slider_actu.configure(state="disabled")        
        self.width_slider_actu.grid(row=1, column=0, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for actuateur's y position vertical slider
        self.width_value_actu = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_actu.grid(row=0, column=0, pady=(0,0), padx=(0,0), sticky="w")
        self.width_value_actu.insert(0, str(self.width_slider_actu.get()))  # Set initial value (reverse the initial y position)
        if self.width_slider_actu.cget("from_") >= self.width_slider_actu.cget("to"):
            self.width_value_actu.configure(state="disabled")
        self.width_value_actu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_actu"))
        self.update_actu_red_square()
        row_count+=1

        # Create horizontal slider for perturbation x position (width)
        self.length_slider_pertu = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_pertu_green_circle, orientation="horizontal", button_color="#1DBC60")        
        self.length_slider_pertu.set(float(self.Simu_parameters['perturbation_longueur']))  # Set initial x position to the middle
        self.length_slider_pertu.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for perturbation x position horizontal slider
        self.length_value_pertu = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_pertu.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_pertu.insert(0, str(self.length_slider_pertu.get()))  # Set initial value
        self.length_value_pertu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_pertu"))

        # Create vertical slider for the perturbation y position (height)
        self.width_slider_pertu = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_pertu_green_circle, orientation="vertical", button_color="#1DBC60")
        self.width_slider_pertu.set(float(self.Simu_parameters['perturbation_largeur']))  # Set initial y position to the middle
        self.width_slider_pertu.grid(row=1, column=1, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for perturbation position vertical slider
        self.width_value_pertu = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_pertu.grid(row=0, column=1, pady=(0,0), padx=(0,0), sticky="w")
        self.width_value_pertu.insert(0, str(self.width_slider_pertu.get()))  # Set initial value (reverse the initial y position)
        self.width_value_pertu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_pertu"))
        self.update_pertu_green_circle()
        row_count+=1

        # Create horizontal slider for T1 x position (width)
        self.length_slider_T1 = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_T1_blue_cross, orientation="horizontal", button_color="#0096FF")
        self.length_slider_T1.set(float(self.Simu_parameters['point_interet_1_longueur']))  # Set initial x position to the middle
        self.length_slider_T1.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for T1 x position horizontal slider
        self.length_value_T1 = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_T1.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_T1.insert(0, str(self.length_slider_T1.get()))  # Set initial value
        self.length_value_T1.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_T1"))

        # Create vertical slider for the T1 y position (height)
        self.width_slider_T1 = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_T1_blue_cross, orientation="vertical", button_color="#0096FF")
        self.width_slider_T1.set(float(self.Simu_parameters['point_interet_1_largeur']))  # Set initial y position to the middle
        self.width_slider_T1.grid(row=1, column=2, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for T1 position vertical slider
        self.width_value_T1 = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_T1.grid(row=0, column=2, pady=(0,0), padx=(0,0), sticky="w")
        self.width_value_T1.insert(0, str(self.width_slider_T1.get()))  # Set initial value (reverse the initial y position)
        self.width_value_T1.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_T1"))
        self.update_T1_blue_cross()
        row_count+=1

        # Create horizontal slider for T2 x position (width)
        self.length_slider_T2 = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_T2_green_cross, orientation="horizontal", button_color="#006400")
        self.length_slider_T2.set(float(self.Simu_parameters['point_interet_2_longueur']))  # Set initial x position to the middle
        self.length_slider_T2.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for T2 x position horizontal slider
        self.length_value_T2 = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_T2.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_T2.insert(0, str(self.length_slider_T2.get()))  # Set initial value
        self.length_value_T2.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_T2"))

        # Create vertical slider for the T2 y position (height)
        self.width_slider_T2 = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_T2_green_cross, orientation="vertical", button_color="#006400")
        self.width_slider_T2.set(float(self.Simu_parameters['point_interet_2_largeur']))  # Set initial y position to the middle
        self.width_slider_T2.grid(row=1, column=3, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for T2 position vertical slider
        self.width_value_T2 = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_T2.grid(row=0, column=3, pady=(0,0), padx=(0,0), sticky="w")
        self.width_value_T2.insert(0, str(self.width_slider_T2.get()))  # Set initial value (reverse the initial y position)
        self.width_value_T2.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_T2"))
        self.update_T2_green_cross()
        row_count+=1

        # Create horizontal slider for T3 x position (width)
        self.length_slider_T3 = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_T3_white_cross, orientation="horizontal", button_color="#FFFFFF")
        self.length_slider_T3.set(float(self.Simu_parameters['point_interet_3_longueur']))  # Set initial x position to the middle
        self.length_slider_T3.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for T3 x position horizontal slider
        self.length_value_T3 = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_T3.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_T3.insert(0, str(self.length_slider_T3.get()))  # Set initial value
        self.length_value_T3.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_T3"))

        # Create vertical slider for the T3 y position (height)
        self.width_slider_T3 = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_T3_white_cross, orientation="vertical", button_color="#FFFFFF")
        self.width_slider_T3.set(float(self.Simu_parameters['point_interet_3_largeur']))  # Set initial y position to the middle
        self.width_slider_T3.grid(row=1, column=4, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for T3 position vertical slider
        self.width_value_T3 = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_T3.grid(row=0, column=4, pady=(0,0), padx=(0,0), sticky="w")
        self.width_value_T3.insert(0, str(self.width_slider_T3.get()))  # Set initial value (reverse the initial y position)
        self.width_value_T3.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_T3"))
        self.update_T3_white_cross()
        row_count+=1

        # Frame for Simu info
        self.simu_info_frame = ctk.CTkFrame(self.root)
        self.simu_info_frame.grid(row=2, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.simu_info_frame.columnconfigure(0, weight=0)
        self.simu_info_frame.columnconfigure(1, weight=0)
        row_count = 0 # Facilite lajout de plus de widget
        row_count2 = 0

        # Label for simu length
        simu_length_label = ctk.CTkLabel(self.simu_info_frame, text="Durée de la simulation (secondes) : ")
        simu_length_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for simu length
        self.simu_length_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.simu_length_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.simu_length_user_entry.insert("1", str(self.Simu_parameters['simu_duration']))
        self.simu_length_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1


        # Label for time actu start
        Actu_start_time_label = ctk.CTkLabel(self.simu_info_frame, text="Démarrage de l'actuateur à (secondes) : ")
        Actu_start_time_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for actu start
        self.Actu_start_time_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Actu_start_time_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.Actu_start_time_user_entry.insert("1", str(self.Simu_parameters['actu_start']))
        self.Actu_start_time_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for time actu stop
        Actu_stop_time_label = ctk.CTkLabel(self.simu_info_frame, text="Arrêt  de l'actuateur à (secondes) : ")
        Actu_stop_time_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for actu stop
        self.Actu_stop_time_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Actu_stop_time_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.Actu_stop_time_user_entry.insert("1", str(self.Simu_parameters['actu_stop']))
        self.Actu_stop_time_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Maillage
        Maillage_label = ctk.CTkLabel(self.simu_info_frame, text="Maillage (mm/éléments) : ")
        Maillage_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # data Entry for actu stop
        self.Maillage_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Maillage_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.Maillage_user_entry.insert("1", str(self.Simu_parameters['mm_par_element']))
        self.Maillage_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Perturbation Power
        perturbation_power_label = ctk.CTkLabel(self.simu_info_frame, text="Puissance de la perturbation (Watt) :")
        perturbation_power_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0))
        # data Entry for Perturbation Power
        self.perturbation_power_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
        self.perturbation_power_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.perturbation_power_user_entry.insert("1", str(self.Simu_parameters['perturbation_power']))
        self.perturbation_power_user_entry.grid(row=row_count2, column=4, sticky="w")
        row_count2+=1

        # Label for Perturbation start
        perturbation_start_label = ctk.CTkLabel(self.simu_info_frame, text="Début de la perturbation à (secondes) : ")
        perturbation_start_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0))
        # data Entry for Perturbation Power
        self.perturbation_start_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.perturbation_start_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.perturbation_start_user_entry.insert("1", str(self.Simu_parameters['perturabtion_start']))
        self.perturbation_start_user_entry.grid(row=row_count2, column=4, sticky="w")
        row_count2+=1

        # Label for Perturbation stop
        perturbation_stop_label = ctk.CTkLabel(self.simu_info_frame, text="Fin de la perturbation à (secondes) : ")
        perturbation_stop_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0))
        # data Entry for Perturbation Power
        self.perturbation_stop_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.perturbation_stop_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.perturbation_stop_user_entry.insert("1", str(self.Simu_parameters['perturabtion_stop']))
        self.perturbation_stop_user_entry.grid(row=row_count2, column=4, sticky="w")
        row_count2+=1

        # Label for simu_acceleration_factor
        simu_acceleration_factor_label = ctk.CTkLabel(self.simu_info_frame, text="Facteur d'accélération d'affichage : ")
        simu_acceleration_factor_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0))
        # data Entry for simu_acceleration_factor
        self.simu_acceleration_factor_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.simu_acceleration_factor_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.simu_acceleration_factor_user_entry.insert("1", str(self.Simu_parameters['simu_acceleration_factor']))
        self.simu_acceleration_factor_user_entry.grid(row=row_count2, column=4, sticky="w")
        row_count2+=1
        
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
            TXT_save_as_path = self.Save_as_path
            if not self.TXT_switch.get():
                TXT_save_as_path = "Aucune Sélection"
            My_plaque.Launch_Simu(save_txt=TXT_save_as_path)
        except Exception as e:
            plt.close('all')
            print(f"Une erreur s'est produite pendant la simulation : {e}")
        self.root.attributes("-disabled", False)
        self.root.lift()  # Raise the window

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
        # Coordinates of the rounded rectangles
        self.plaque_canvas.create_oval(0, 0, r*2, r*2, fill=color, outline=color)  # Top-left corner
        self.plaque_canvas.create_oval(W - r*2, 0, W, r*2, fill=color, outline=color)  # Top-right corner
        self.plaque_canvas.create_oval(0, L - r*2, r*2, L, fill=color, outline=color)  # Bottom-left corner
        self.plaque_canvas.create_oval(W - r*2, L - r*2, W, L, fill=color, outline=color)  # Bottom-right corner
        # 4 cotes
        self.plaque_canvas.create_rectangle(r, 0, W - r, L, fill=color, outline=color)  # Top and bottom
        self.plaque_canvas.create_rectangle(0, r, W, L - r, fill=color, outline=color)  # Left and right

    def update_actu_red_square(self, event=None):
        x = self.length_slider_actu.get()  
        y = self.width_slider_actu.get()
        self.update_red_square()
        self.length_value_actu.delete(0, ctk.END)
        self.length_value_actu.insert(0, str(round(x,5)))
        self.width_value_actu.delete(0, ctk.END)
        self.width_value_actu.insert(0, str(round(y,5)))

    def update_red_square(self, event=None):
        x = self.length_slider_actu.get()  
        y = self.width_slider_actu.get()
        pos_x_in_pix = int(self.plaque_length*x/(float(self.Simu_parameters['plaque_longueur'])))
        pos_y_in_pix = int(self.plaque_width*(float(self.Simu_parameters['plaque_largeur']) - y)/float(self.Simu_parameters['plaque_largeur']))
        half_longueur_actu_in_pix = int(self.plaque_length*float(self.Simu_parameters['longueur_actu'])/(float(self.Simu_parameters['plaque_longueur']))/2)
        half_largeur_actu_in_pix = int(self.plaque_width*float(self.Simu_parameters['largeur_actu'])/(float(self.Simu_parameters['plaque_largeur']))/2)
        self.plaque_canvas.coords(self.Actuateur_shape, pos_x_in_pix - half_longueur_actu_in_pix, pos_y_in_pix - half_largeur_actu_in_pix, pos_x_in_pix + half_longueur_actu_in_pix, pos_y_in_pix + half_largeur_actu_in_pix)
    
    def update_pertu_green_circle(self, event=None):
        x = self.length_slider_pertu.get()  
        y = self.width_slider_pertu.get()
        self.update_green_circle()
        self.length_value_pertu.delete(0, ctk.END)
        self.length_value_pertu.insert(0, str(round(x,5)))
        self.width_value_pertu.delete(0, ctk.END)
        self.width_value_pertu.insert(0, str(round(y,5)))
    
    def update_green_circle(self, event=None):
        x = self.length_slider_pertu.get()  
        y = self.width_slider_pertu.get()
        pos_x_in_pix = int(self.plaque_length*x/(float(self.Simu_parameters['plaque_longueur'])))
        pos_y_in_pix = int(self.plaque_width*(float(self.Simu_parameters['plaque_largeur']) - y)/float(self.Simu_parameters['plaque_largeur']))
        self.plaque_canvas.coords(self.Perturbation_shape, pos_x_in_pix+7, pos_y_in_pix+7, pos_x_in_pix-7, pos_y_in_pix-7)

    def update_T1_blue_cross(self, event=None):
        x = self.length_slider_T1.get()  # Get length slider value (used for x-coordinate)
        y = self.width_slider_T1.get()   # Get width slider value (used for y-coordinate)
        self.update_blue_cross()
        self.length_value_T1.delete(0, ctk.END)
        self.length_value_T1.insert(0, str(round(x, 5)))
        self.width_value_T1.delete(0, ctk.END)
        self.width_value_T1.insert(0, str(round(y, 5)))

    def update_blue_cross(self, event=None):
        x = self.length_slider_T1.get()  
        y = self.width_slider_T1.get()
        pos_x_in_pix = int(self.plaque_length * x / float(self.Simu_parameters['plaque_longueur']))
        pos_y_in_pix = int(self.plaque_width * (float(self.Simu_parameters['plaque_largeur']) - y) / float(self.Simu_parameters['plaque_largeur']))
        size = 7  # Half-length of the diagonal arms
        self.plaque_canvas.coords(self.T1_shape[0], pos_x_in_pix - size, pos_y_in_pix - size, pos_x_in_pix + size, pos_y_in_pix + size)  # Diagonal line (top-left to bottom-right)
        self.plaque_canvas.coords(self.T1_shape[1], pos_x_in_pix - size, pos_y_in_pix + size, pos_x_in_pix + size, pos_y_in_pix - size)  # Diagonal line (top-right to bottom-left)

    def update_T2_green_cross(self, event=None):
        x = self.length_slider_T2.get()  # Get length slider value (used for x-coordinate)
        y = self.width_slider_T2.get()   # Get width slider value (used for y-coordinate)
        self.update_green_cross()
        self.length_value_T2.delete(0, ctk.END)
        self.length_value_T2.insert(0, str(round(x, 5)))
        self.width_value_T2.delete(0, ctk.END)
        self.width_value_T2.insert(0, str(round(y, 5)))

    def update_green_cross(self, event=None):
        x = self.length_slider_T2.get()  
        y = self.width_slider_T2.get()
        pos_x_in_pix = int(self.plaque_length * x / float(self.Simu_parameters['plaque_longueur']))
        pos_y_in_pix = int(self.plaque_width * (float(self.Simu_parameters['plaque_largeur']) - y) / float(self.Simu_parameters['plaque_largeur']))
        size = 7  # Half-length of the diagonal arms
        self.plaque_canvas.coords(self.T2_shape[0], pos_x_in_pix - size, pos_y_in_pix - size, pos_x_in_pix + size, pos_y_in_pix + size)  # Diagonal line (top-left to bottom-right)
        self.plaque_canvas.coords(self.T2_shape[1], pos_x_in_pix - size, pos_y_in_pix + size, pos_x_in_pix + size, pos_y_in_pix - size)  # Diagonal line (top-right to bottom-left)

    def update_T3_white_cross(self, event=None):
        x = self.length_slider_T3.get()  # Get length slider value (used for x-coordinate)
        y = self.width_slider_T3.get()   # Get width slider value (used for y-coordinate)
        self.update_white_cross()
        self.length_value_T3.delete(0, ctk.END)
        self.length_value_T3.insert(0, str(round(x, 5)))
        self.width_value_T3.delete(0, ctk.END)
        self.width_value_T3.insert(0, str(round(y, 5)))

    def update_white_cross(self, event=None):
        x = self.length_slider_T3.get()  
        y = self.width_slider_T3.get()
        pos_x_in_pix = int(self.plaque_length * x / float(self.Simu_parameters['plaque_longueur']))
        pos_y_in_pix = int(self.plaque_width * (float(self.Simu_parameters['plaque_largeur']) - y) / float(self.Simu_parameters['plaque_largeur']))
        size = 7  # Half-length of the diagonal arms
        self.plaque_canvas.coords(self.T3_shape[0], pos_x_in_pix - size, pos_y_in_pix - size, pos_x_in_pix + size, pos_y_in_pix + size)  # Diagonal line (top-left to bottom-right)
        self.plaque_canvas.coords(self.T3_shape[1], pos_x_in_pix - size, pos_y_in_pix + size, pos_x_in_pix + size, pos_y_in_pix - size)  # Diagonal line (top-right to bottom-left)


    def validate_input(self, P):# Permet seulement les chiffres
        """Only allow numeric input (including decimal point)."""
        if P == "" or P.isdigit() or (P.replace('.', '', 1).isdigit() and P.count('.') <= 1):
            return True
        else:
            return False
    def validate_input_Neg(self, P):# Permet seulement le chiffre incluant les negatifs
        if P != "":
            if P[0] == "-":
                P = P[1:]
        if P == "" or P.isdigit() or (P.replace('.', '', 1).isdigit() and P.count('.') <= 1):
            return True
        else:
            return False

    def parameters_correction(self):
        # # Si actuateur est plus grand que plaque, reduire taille actuateur
        # # Si 



        # # # Si plaque trop large ou trop longue pour lactuateur
        # # self.Simu_parameters['plaque_largeur'] = min(self.Simu_parameters['largeur_actu'], self.Simu_parameters['plaque_largeur'])
        # # self.Simu_parameters['plaque_longueur'] = min(self.Simu_parameters['longueur_actu'], self.Simu_parameters['plaque_longueur'])
        # # # Si position actuateur hors de la plaque
        # # self.Simu_parameters['position_longueur_actuateur'] = max(self.Simu_parameters['longueur_actu']/2,min(self.Simu_parameters['plaque_longueur']-self.Simu_parameters['longueur_actu']/2, self.Simu_parameters['position_longueur_actuateur']))
        # # self.Simu_parameters['position_largeur_actuateur'] = max(self.Simu_parameters['largeur_actu']/2,min(self.Simu_parameters['plaque_largeur']-self.Simu_parameters['largeur_actu']/2, self.Simu_parameters['position_largeur_actuateur']))
        
        
        # # # Si plaque trop large ou trop longue pour lactuateur
        # # if self.Simu_parameters['largeur_actu'] > self.Simu_parameters['plaque_largeur']:
        # #     self.Simu_parameters['plaque_largeur'] = self.Simu_parameters['largeur_actu']
        # # if self.Simu_parameters['longueur_actu'] > self.Simu_parameters['plaque_longueur']:
        # #     self.Simu_parameters['plaque_longueur'] = self.Simu_parameters['longueur_actu']
        # # # Si position actuateur hors de la plaque
        # # if not(self.Simu_parameters['largeur_actu']/2 < self.Simu_parameters['position_largeur_actuateur'] < self.Simu_parameters['plaque_largeur']-self.Simu_parameters['largeur_actu']/2):
        # #     self.Simu_parameters['position_largeur_actuateur'] = self.Simu_parameters['plaque_largeur']/2
        # # if not(self.Simu_parameters['longueur_actu']/2 < self.Simu_parameters['position_longueur_actuateur'] < self.Simu_parameters['plaque_longueur']-self.Simu_parameters['longueur_actu']/2):
        # #     self.Simu_parameters['position_longueur_actuateur'] = self.Simu_parameters['plaque_longueur']/2
        
        # pass

        
        # S'assurer que la plaque est au moins aussi grande que l'actuateur
        self.Simu_parameters['plaque_largeur'] = max(
            self.Simu_parameters['plaque_largeur'],
            self.Simu_parameters['largeur_actu']
        )
        self.Simu_parameters['plaque_longueur'] = max(
            self.Simu_parameters['plaque_longueur'],
            self.Simu_parameters['longueur_actu']
        )

        # Assurer que l'actuateur est bien positionné dans la plaque
        demi_largeur = self.Simu_parameters['largeur_actu'] / 2
        demi_longueur = self.Simu_parameters['longueur_actu'] / 2

        self.Simu_parameters['position_largeur_actuateur'] = max(
            demi_largeur,
            min(
                self.Simu_parameters['plaque_largeur'] - demi_largeur,
                self.Simu_parameters['position_largeur_actuateur']
            )
        )
        self.Simu_parameters['position_longueur_actuateur'] = max(
            demi_longueur,
            min(
                self.Simu_parameters['plaque_longueur'] - demi_longueur,
                self.Simu_parameters['position_longueur_actuateur']
            )
        )


    def update_slider_from_entry(self, slider_type):
        try:
            if slider_type == "length_actu":
                value = float(self.length_value_actu.get())
                min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_longueur']) - min_max_for_actu_size:
                    self.length_slider_actu.set(value)
                    self.update_red_square()
            elif slider_type == "width_actu":
                value = float(self.width_value_actu.get())
                min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size:
                    self.width_slider_actu.set(value)  # Reverse for vertical slider
                    self.update_red_square()
            elif slider_type == "length_pertu":
                value = float(self.length_value_pertu.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_pertu.set(value)
                    self.update_green_circle()
            elif slider_type == "width_pertu":
                value = float(self.width_value_pertu.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_pertu.set(value)  # Reverse for vertical slider
                    self.update_green_circle()
            elif slider_type == "length_T1":
                value = float(self.length_value_T1.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_T1.set(value)
                    self.update_blue_cross()
            elif slider_type == "width_T1":
                value = float(self.width_value_T1.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_T1.set(value)  # Reverse for vertical slider
                    self.update_blue_cross()
            elif slider_type == "length_T2":
                value = float(self.length_value_T2.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_T2.set(value)
                    self.update_green_cross()
            elif slider_type == "width_T2":
                value = float(self.width_value_T2.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_T2.set(value)  # Reverse for vertical slider
                    self.update_green_cross()
            elif slider_type == "length_T3":
                value = float(self.length_value_T3.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_T3.set(value)
                    self.update_white_cross()
            elif slider_type == "width_T3":
                value = float(self.width_value_T3.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_T3.set(value)  # Reverse for vertical slider
                    self.update_white_cross()

        except ValueError:
            print('Erreur')
            pass  # Ignore invalid input (e.g., if the input is not a number)

    def Reset_to_default(self):
        with open(self.temp_filename, 'r') as temp_file:
            loaded_parameters = json.load(temp_file)
            self.Simu_parameters = loaded_parameters
        self.load_frame()
        
    def TXT_toggle(self):
        if self.TXT_switch.get():
            self.save_txt_bool = True
        else:
            self.save_txt_bool = False
        
if __name__ == "__main__":
    app = GUI()
    app.root.mainloop()