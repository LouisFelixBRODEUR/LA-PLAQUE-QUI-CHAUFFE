"""
Interface graphique pour le contrôle de la simulation thermique de la plaque avec actuateur et perturbations.
Ce code utilise customtkinter pour faire l'interface.
"""

from tkinter import filedialog
import customtkinter as ctk
from Simulation import Plaque
import math
import sys
import json
import matplotlib.pyplot as plt
import tempfile
from scipy.optimize import curve_fit
import control
import numpy as np

# TODO Au moins 10 autres paramètres what de fuck?
# TODO manuel de l'utilisateur
# TODO Clean Comments

class GUI:
    def __init__(self):
        """
        Initialise la fenêtre et les paramètres initiales de simulation
        """
        # Configuration de la main window
        self.root = ctk.CTk()
        self.root.geometry("810x650")
        self.root.minsize(810, 0) 

        # Initialisation de quelques trucs pour le GUI
        self.background_color = "#1e1e1e"
        self.root.configure(bg=self.background_color)
        self.root.title("Controleur Simulation")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing) # Pour bien gérer la fermeture de la fenêtre
        self.validate_cmd = self.root.register(self.validate_input) # Commandes de validation des entrées de la fenêtre
        self.validate_cmd_Neg = self.root.register(self.validate_input_Neg)
        self.root.bind("<Control-q>", self.Test_function) # Binding d'une fonction test
        self.root.bind("<Control-g>", self.Ident_Transfer_Function) # Binding d'une fonction d'identification
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Initialisation d’un frame secondaire dans le main pour activer le scroll
        self.scroll_root = ctk.CTkScrollableFrame(self.root, fg_color=self.background_color, border_width=0, corner_radius=0)
        self.root.grid_propagate(False) # Empêche le rétrécissement du scrollable frame
        self.scroll_root.grid(row=0, column=0, sticky="nsew", pady=(0,0), padx=(0,0)) # Configuration des poids du scroll frame et du scroller
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Initialisation de variables
        self.save_txt_bool = False
        self.pix_spacing = 20
        self.pix_to_plaque_box = 3
        self.plaque_display_size = 300
        self.Save_as_path = "Aucune Sélection"

        # Paramètres par défaut de la simulation
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
            'voltage_actuateur' : 1.2, #V
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

        # Dump le dict des paramètres initiales dans un .json pour le dupliquer, car je n'ai pas réussi avec deepcopy()
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix=".json") as temp_file:
            self.temp_filename = temp_file.name
            json.dump(self.Simu_parameters, temp_file, indent=4)
        
        self.load_frame() # Load le GUI

    def on_closing(self):
        """Gère la fermeture de l'application."""
        print("Fermeture de l'application...")
        sys.exit()

    def on_enter_key(self, event=None):
        """Store les paramètres et reload l'interface quand ENTER"""
        self.Log_parameters()
        self.reload_frame()

    def Log_parameters(self):
        """Log les paramètres de simu et corrige les paramètre out of range"""
        # Remplace les fields de positions vides avec des 0
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

        # Log tous les paramètres du GUI dans le dict
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
        self.parameters_correction() # Correction

    def Test_function(self, event=None):
        """Affiche les paramètres actuels et initiaux pour du debug"""
        print('Paramètres de simulation actuels :')
        for param, value in self.Simu_parameters.items():
            print(f'\t{param} : {value}')
        print('Paramètres de simulation initiaux :')
        # Load les paramètres initiale du .json
        with open(self.temp_filename, 'r') as temp_file:
            loaded_parameters = json.load(temp_file) 
            for param, value in loaded_parameters.items():
                print(f'\t{param} : {value}')
    
    def Ident_Transfer_Function(self, event=None):
        """
        Lance une simulation avec les paramètres actuels et identifie un fonction de transfert arbitraire de la forme:
        (As^2+Bs+C)/(s^2+Ds+Es)e^{-sF}
        Pour chacun des couple entrée sortie sosrtie-suivant:
        -Power in -> Heat Pumped by actu
        -Heat Pumped by actu -> T1
        -T1 -> T2
        -T2 -> T3
        Les sorties de ces identification se trouvent au terminal. Des graphiques montrant la qualitée des identifications sont aussis affiché
        """
        print('Identification des fonctions de transferts du système en cours...')
        self.root.withdraw() # Hide la main window
        # self.root.attributes("-disabled", True)
        def identify_second_order_arbitraty_transfer_function_with_delay(time_data, in_data, out_data, name = ''):
            t = time_data
            y = out_data
            y -= y[0]
            u = in_data

            # Fonction pour simuler la reponse de la arbitrary 2nd-order avec delay
            def second_order_arbitraty_with_delay(t, a, b, c, d, e, delay):
                u_delayed = np.interp(t - delay, t, u, left=0)
                num = [a, b, c]
                den = [1, d, e]
                sys = control.TransferFunction(num, den)
                _, y_model = control.forced_response(sys, T=t, U=u_delayed)
                return y_model
            # Définission du fit pour trouver quels paramètres de cette fonction arbitrary 2nd-order se pproche le plus de la reponse
            def fit_func(t, a, b, c, d, e, delay):
                return second_order_arbitraty_with_delay(t, a, b, c, d, e, delay)
            initial_guess = [1, 1, 1, 1, 1, 1]
            bounds = ([-np.inf, -np.inf, -np.inf, -np.inf, -np.inf, 0], [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf])
            # Calcul du fit
            params, _ = curve_fit(fit_func, t, y, p0=initial_guess, bounds=bounds)
            a_fit, b_fit, c_fit, d_fit, e_fit, delay_fit = params
            print(f"Fonction de transfert de {name} identifiée:")
            pretty_tf = f"({format(a_fit, '.4g')}s^2 + {format(b_fit, '.4g')}s + {format(c_fit, '.4g')}) / (s^2 + {format(d_fit, '.4g')}s + {format(d_fit, '.4g')}) * exp(-s*{format(delay_fit, '.4g')})"
            print(pretty_tf)
            # Simule le modele avec le meilleur fit pour le graph
            y_fit = second_order_arbitraty_with_delay(t, a_fit, b_fit, c_fit, d_fit, e_fit, delay_fit)

            # Build LaTeX-style transfer function string
            transfer_function_text = (
                fr"$\frac{{{format(a_fit, '.4g')}s^2 + {format(b_fit, '.4g')}s + {format(c_fit, '.4g')}}}{{s^2 + {format(d_fit, '.4g')}s + {format(d_fit, '.4g')}}} e^{{-s{format(delay_fit, '.4g')}}}$"
            )

            # Plot
            plt.figure(figsize=(10, 5))
            plt.plot(t, y, label='Sortie')
            plt.plot(t, y_fit, '--', label='Entrée calculé avec fonction de tranfert identifiée')
            plt.plot(t, u, '-', label='Entrée')
            plt.xlabel("Temps (s)")
            plt.ylabel("Entrée et Sortie")
            plt.title(f'Fonction de transfert de {name}')
            plt.legend(loc='upper right')
            plt.grid(True)
            plt.ylim(np.min(np.concatenate([y, y_fit, u])), np.max(np.concatenate([y, y_fit, u])) + (np.max(np.concatenate([y, y_fit, u]))-np.min(np.concatenate([y, y_fit, u])))*0.3)

            # Add the LaTeX-formatted transfer function to the top-left corner
            plt.text(0.01, 0.95, transfer_function_text, transform=plt.gca().transAxes, fontsize=12,
                    verticalalignment='top', horizontalalignment='left',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

            plt.tight_layout()
            plt.show()

        self.on_enter_key() # Log et corrige tous les pramètres
        My_plaque = Plaque(self.Simu_parameters) # Simule une plaque
        Simu_data_dict = My_plaque.Launch_Simu(display_animation=False, save_data_for_trsfer_fct=True) # Lance la simulation
        data_T1 = Simu_data_dict['T1']
        data_T2 = Simu_data_dict['T2']
        data_T3 = Simu_data_dict['T3']
        data_power = Simu_data_dict['power_in']
        data_heat_pumped = Simu_data_dict['heat_pumped']
        data_time = Simu_data_dict['time']
        if len(data_time) > 1000: #Inutile davoir plus de points pour faire un bon fit
            time_new = np.linspace(data_time[0], data_time[-1], 1000)
            data_T1 = np.interp(time_new, data_time, data_T1)
            data_T2 = np.interp(time_new, data_time, data_T2)
            data_T3 = np.interp(time_new, data_time, data_T3)
            data_power = np.interp(time_new, data_time, data_power)
            data_heat_pumped = np.interp(time_new, data_time, data_heat_pumped)
            data_time = time_new
        # Identification
        identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_power, data_heat_pumped,  name = "puissance IN vers chaleur pompée par l'actuateur")
        identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_heat_pumped, data_T1,  name = "chaleur pompée par l'actuateur vers thermistance 1")
        identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_T1, data_T2,  name = 'thermistance 1 vers thermistance 2')
        identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_T2, data_T3, name = 'thermistance 2 vers thermistance 3')
        print('Fonctions de transfert identifiées!')
        self.root.deiconify() # Show la main window
        self.root.lift()

    def load_simu_params_from_json(self):
        """Demande pour un .json et load les paramètres de simu"""
        json_path = filedialog.askopenfile(title="Sélectionnez un fichier JSON", filetypes=[("JSON files", "*.json")])
        if json_path != None:
            with open(json_path.name, 'r') as file:
                self.Simu_parameters = json.load(file)
            self.load_frame()
        else:
            print('Pas de JSON. Sélectionné')

    def save_simu_params_in_json(self):
        """Demande pour un emplacement pour un .json et sauvegarde les paramètres de simu"""
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

    def update_plaque_visuals(self):
        """Update la visualisation de la plaque"""
        # Recalcule les dimensions de la plaque
        self.plaque_width = min(self.plaque_display_size, 
                            int(self.plaque_display_size * 
                            float(self.Simu_parameters['plaque_largeur']) / 
                            float(self.Simu_parameters['plaque_longueur'])))
        self.plaque_length = min(self.plaque_display_size, 
                            int(self.plaque_display_size * 
                            float(self.Simu_parameters['plaque_longueur']) / 
                            float(self.Simu_parameters['plaque_largeur'])))

        # Resize le canvas et le frame
        self.plaque_box_frame.configure(width=self.plaque_length, height=self.plaque_width)
        self.plaque_canvas.configure(width=self.plaque_length, height=self.plaque_width)
        
        # Clear et redraw la plaque
        self.plaque_canvas.delete("all")
        self.create_rounded_rectangle('gray10')
        
        # redraw les éléments visuels sur la plaque
        self.Actuateur_shape = self.plaque_canvas.create_rectangle(0, 0, 0, 0, 
                                                                fill="#ff4242", 
                                                                outline="#ff4242")
        self.Perturbation_shape = self.plaque_canvas.create_oval(0, 0, 0, 0, 
                                                            fill="#1DBC60", 
                                                            outline="#1DBC60")
        self.T1_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#0096FF", width=2),
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#0096FF", width=2)
        ]
        self.T2_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#006400", width=2),
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#006400", width=2)
        ]
        self.T3_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#FFFFFF", width=2),
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#FFFFFF", width=2)
        ]
        
        # Update les positions des éléments visuels sur la plaque
        self.update_actu_red_square()
        self.update_pertu_green_circle()
        self.update_T1_blue_cross()
        self.update_T2_green_cross()
        self.update_T3_white_cross()

    def update_sliders(self):
        '''
        Cette fonction:
        1. Update sliders et user entry pour la position de l'actuateur
        2. Update sliders et user entry pour la position de la perturbation
        3. Update sliders et user entry pour la position des thermistances
        4. Update les éléments visuels sur la plaque
        '''
        # 1. Update sliders pour la position de l'actuateur (longeur)
        min_actu_length = math.ceil(self.Simu_parameters['longueur_actu'] / 2)
        max_actu_length = float(self.Simu_parameters['plaque_longueur']) - min_actu_length
        # Rescale le min max du slider horizontal de l'actuateur
        self.length_slider_actu.configure(
            from_=min_actu_length,
            to=max_actu_length,
            width=self.plaque_length
        )
        # Active/désactive le slider si son min=max
        if min_actu_length < max_actu_length:
            self.length_slider_actu.set(float(self.Simu_parameters['position_longueur_actuateur']))
            self.length_slider_actu.configure(state="normal")
            self.length_value_actu.configure(state="normal")
        else:
            self.length_slider_actu.configure(state="disabled")
            self.length_value_actu.configure(state="disabled")

        # Update slider pour la position de l'actuateur (largeur)
        min_actu_width = math.ceil(self.Simu_parameters['largeur_actu'] / 2)
        max_actu_width = float(self.Simu_parameters['plaque_largeur']) - min_actu_width
        # Rescale le min max du slider vertical de l'actuateur
        self.width_slider_actu.configure(
            from_=min_actu_width,
            to=max_actu_width,
            height=self.plaque_width
        )
        # Active/désactive le slider si son min=max
        if min_actu_width < max_actu_width:
            self.width_slider_actu.set(float(self.Simu_parameters['position_largeur_actuateur']))
            self.width_slider_actu.configure(state="normal")
            self.width_value_actu.configure(state="normal")
        else:
            self.width_slider_actu.configure(state="disabled")
            self.width_value_actu.configure(state="disabled")

        # Update les user entry pour la position de l'actuateur
        self.length_value_actu.delete(0, 'end')
        self.length_value_actu.insert(0, str(self.Simu_parameters['position_longueur_actuateur']))
        self.width_value_actu.delete(0, 'end')
        self.width_value_actu.insert(0, str(self.Simu_parameters['position_largeur_actuateur']))
        
        # 2. Update sliders pour la position de la perturbation
        self.length_slider_pertu.configure(
            from_=0,
            to=float(self.Simu_parameters['plaque_longueur']),
            width=self.plaque_length
        )
        self.length_slider_pertu.set(float(self.Simu_parameters['perturbation_longueur']))
        
        self.width_slider_pertu.configure(
            from_=0,
            to=float(self.Simu_parameters['plaque_largeur']),
            height=self.plaque_width
        )
        self.width_slider_pertu.set(float(self.Simu_parameters['perturbation_largeur']))

        # Update les user entry pour la position de la perturbation
        self.length_value_pertu.delete(0, 'end')
        self.length_value_pertu.insert(0, str(self.Simu_parameters['perturbation_longueur']))
        self.width_value_pertu.delete(0, 'end')
        self.width_value_pertu.insert(0, str(self.Simu_parameters['perturbation_largeur']))

        # 3. Update les sliders pour la position des thermistances
        for point in ['T1', 'T2', 'T3']:
            length_slider = getattr(self, f'length_slider_{point}')
            width_slider = getattr(self, f'width_slider_{point}')
            length_value = getattr(self, f'length_value_{point}')
            width_value = getattr(self, f'width_value_{point}')

            length_slider.configure(
                from_=0,
                to=float(self.Simu_parameters['plaque_longueur']),
                width=self.plaque_length
            )
            length_slider.set(float(self.Simu_parameters[f'point_interet_{point.lower()[-1]}_longueur']))
            
            width_slider.configure(
                from_=0,
                to=float(self.Simu_parameters['plaque_largeur']),
                height=self.plaque_width
            )
            width_slider.set(float(self.Simu_parameters[f'point_interet_{point.lower()[-1]}_largeur']))
            
            # Update les user entry pour la position des thermistances
            length_value.delete(0, 'end')
            length_value.insert(0, str(length_slider.get()))
            width_value.delete(0, 'end')
            width_value.insert(0, str(width_slider.get()))

        # 4. Update les éléments visuels sur la plaque
        self.update_actu_red_square()
        self.update_pertu_green_circle()
        self.update_T1_blue_cross()
        self.update_T2_green_cross()
        self.update_T3_white_cross()

    def update_entries(self):
        """
        Efface et insère les valeurs correspondantes dans les user entry 
        """
        self.Temp_ambiante_user_entry.delete(0, 'end')
        self.Temp_ambiante_user_entry.insert("1", str(float(self.Simu_parameters['Temperature_Ambiante_C'])))
        self.masse_volumique_plaque_user_entry.delete(0, 'end')
        self.masse_volumique_plaque_user_entry.insert("1", str(float(self.Simu_parameters['masse_volumique_plaque'])))
        self.capacite_thermique_plaque_user_entry.delete(0, 'end')
        self.capacite_thermique_plaque_user_entry.insert("1", str(float(self.Simu_parameters['capacite_thermique_plaque'])))
        self.coefficient_convection_user_entry.delete(0, 'end')
        self.coefficient_convection_user_entry.insert("1", str(float(self.Simu_parameters['coefficient_convection'])))
        self.epaisseur_plaque_mm_user_entry.delete(0, 'end')
        self.epaisseur_plaque_mm_user_entry.insert("1", str(float(self.Simu_parameters['epaisseur_plaque_mm'])))
        self.conductivite_thermique_plaque_user_entry.delete(0, 'end')
        self.conductivite_thermique_plaque_user_entry.insert("1", str(float(self.Simu_parameters['conductivite_thermique_plaque'])))
        self.Couple_user_entry.delete(0, 'end')
        self.Couple_user_entry.insert("1", str(float(self.Simu_parameters['couple_actuateur'])))
        self.plaque_width_user_entry.delete(0, 'end')
        self.plaque_width_user_entry.insert("1", str(float(self.Simu_parameters['plaque_largeur'])))
        self.plaque_length_user_entry.delete(0, 'end')
        self.plaque_length_user_entry.insert("1", str(float(self.Simu_parameters['plaque_longueur'])))
        self.actu_width_user_entry.delete(0, 'end')
        self.actu_width_user_entry.insert("1", str(float(self.Simu_parameters['largeur_actu'])))
        self.actu_length_user_entry.delete(0, 'end')
        self.actu_length_user_entry.insert("1", str(float(self.Simu_parameters['longueur_actu'])))
        self.actu_puissance_user_entry.delete(0, 'end')
        self.actu_puissance_user_entry.insert("1", str(float(self.Simu_parameters['puissance_actuateur'])))
        self.simu_length_user_entry.delete(0, 'end')
        self.simu_length_user_entry.insert("1", str(float(self.Simu_parameters['simu_duration'])))
        self.Actu_start_time_user_entry.delete(0, 'end')
        self.Actu_start_time_user_entry.insert("1", str(float(self.Simu_parameters['actu_start'])))
        self.Actu_stop_time_user_entry.delete(0, 'end')
        self.Actu_stop_time_user_entry.insert("1", str(float(self.Simu_parameters['actu_stop'])))
        self.Maillage_user_entry.delete(0, 'end')
        self.Maillage_user_entry.insert("1", str(float(self.Simu_parameters['mm_par_element'])))
        self.perturbation_power_user_entry.delete(0, 'end')
        self.perturbation_power_user_entry.insert("1", str(float(self.Simu_parameters['perturbation_power'])))
        self.perturbation_start_user_entry.delete(0, 'end')
        self.perturbation_start_user_entry.insert("1", str(float(self.Simu_parameters['perturabtion_start'])))
        self.perturbation_stop_user_entry.delete(0, 'end')
        self.perturbation_stop_user_entry.insert("1", str(float(self.Simu_parameters['perturabtion_stop'])))
        self.simu_acceleration_factor_user_entry.delete(0, 'end')
        self.simu_acceleration_factor_user_entry.insert("1", str(float(self.Simu_parameters['simu_acceleration_factor'])))

    def reload_frame(self):
        """
        Actualiser le frame sans redessiner tous les widget
        """
        if self.save_txt_bool: # Gestion du toggle pour le save
            self.TXT_switch.select()
        self.Log_parameters()
        self.update_entries()
        self.update_plaque_visuals()
        self.update_sliders()

    def load_frame(self):
        """
        Build (ou rebuild) le GUI
        """
        # Clear tout les widgets
        for widget in self.scroll_root.winfo_children():
            widget.destroy()

        # Frame for save path and button
        save_frame = ctk.CTkFrame(self.scroll_root)
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
        
        # Load params from json button
        self.Json_path_button = ctk.CTkButton(save_frame, text="Charger les paramètres à partir d'un .json", command=self.load_simu_params_from_json)
        self.Json_path_button.grid(row=1, column=0, sticky="w", padx=(5,0), pady=(0,5))

        # Save params in json button
        self.Json_path_button = ctk.CTkButton(save_frame, text="Sauver les paramètres dans un .json", command=self.save_simu_params_in_json)
        self.Json_path_button.grid(row=2, column=0, sticky="w", padx=(5,0), pady=(0,5))

        # Frame for plaque info
        self.plaque_info_frame = ctk.CTkFrame(self.scroll_root)
        self.plaque_info_frame.grid(row=1, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.plaque_info_frame.columnconfigure(0, weight=0)
        self.plaque_info_frame.columnconfigure(1, weight=0)
        row_count = 0 # Facilite l'ajout de plus de widget
        row_count2 = 0

        # Reset Boutton
        self.Reset_Actu_Posi_button = ctk.CTkButton(self.plaque_info_frame, text="Réinitialiser les Paramètres", command=self.Reset_to_default)
        self.Reset_Actu_Posi_button.grid(row=row_count, column=0, sticky="w", padx = (5, 0), pady=(5,0))
        row_count+=1

        # Label for Temp Ambiante
        Temp_Ambi_label = ctk.CTkLabel(self.plaque_info_frame, text="Température ambiante (°C) : ")
        Temp_Ambi_label.grid(row=row_count2, column=2, sticky="ws", padx=(5,0), pady=(0,0))
        # Data Entry for Temp Ambiante 
        self.Temp_ambiante_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
        self.Temp_ambiante_user_entry.bind("<Return>", self.on_enter_key)
        self.Temp_ambiante_user_entry.insert("1", str(float(self.Simu_parameters['Temperature_Ambiante_C'])))
        self.Temp_ambiante_user_entry.grid(row=row_count2, column=3, sticky="ws", pady=(0,0))
        row_count2+=1
                
        # Label for masse_volumique_plaque
        masse_volumique_plaque_label = ctk.CTkLabel(self.plaque_info_frame, text="Masse volumique (kg/m³) : ")
        masse_volumique_plaque_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # Data Entry for masse_volumique_plaque 
        self.masse_volumique_plaque_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.masse_volumique_plaque_user_entry.bind("<Return>", self.on_enter_key)
        self.masse_volumique_plaque_user_entry.insert("1", str(float(self.Simu_parameters['masse_volumique_plaque'])))
        self.masse_volumique_plaque_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for capacite_thermique_plaque
        capacite_thermique_plaque_label = ctk.CTkLabel(self.plaque_info_frame, text="Capacité thermique (J/Kg·K) : ")
        capacite_thermique_plaque_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # Data Entry for capacite_thermique_plaque
        self.capacite_thermique_plaque_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.capacite_thermique_plaque_user_entry.bind("<Return>", self.on_enter_key)
        self.capacite_thermique_plaque_user_entry.insert("1", str(float(self.Simu_parameters['capacite_thermique_plaque'])))
        self.capacite_thermique_plaque_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for coefficient_convection
        coefficient_convection_label = ctk.CTkLabel(self.plaque_info_frame, text="Coefficient de convection (W/m²·K) : ")
        coefficient_convection_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # Data Entry for coefficient_convection
        self.coefficient_convection_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.coefficient_convection_user_entry.bind("<Return>", self.on_enter_key)
        self.coefficient_convection_user_entry.insert("1", str(float(self.Simu_parameters['coefficient_convection'])))
        self.coefficient_convection_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for epaisseur_plaque_mm
        epaisseur_plaque_mm_label = ctk.CTkLabel(self.plaque_info_frame, text="Épaisseur de la plaque (mm) : ")
        epaisseur_plaque_mm_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # Data Entry for epaisseur_plaque_mm 
        self.epaisseur_plaque_mm_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.epaisseur_plaque_mm_user_entry.bind("<Return>", self.on_enter_key)
        self.epaisseur_plaque_mm_user_entry.insert("1", str(float(self.Simu_parameters['epaisseur_plaque_mm'])))
        self.epaisseur_plaque_mm_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1
        
        # Label for conductivite_thermique_plaque
        conductivite_thermique_plaque_label = ctk.CTkLabel(self.plaque_info_frame, text="Conductivité thermique (W/m·K) : ")
        conductivite_thermique_plaque_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # Data Entry for conductivite_thermique_plaque
        self.conductivite_thermique_plaque_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.conductivite_thermique_plaque_user_entry.bind("<Return>", self.on_enter_key)
        self.conductivite_thermique_plaque_user_entry.insert("1", str(float(self.Simu_parameters['conductivite_thermique_plaque'])))
        self.conductivite_thermique_plaque_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1

        # Label for Couple
        couple_label = ctk.CTkLabel(self.plaque_info_frame, text="Couple plaque-actuateur : ")
        couple_label.grid(row=row_count2, column=2, sticky="w", padx=(5,0), pady=(0,0))
        # Data Entry for Couple
        self.Couple_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Couple_user_entry.bind("<Return>", self.on_enter_key)
        self.Couple_user_entry.insert("1", str(float(self.Simu_parameters['couple_actuateur'])))
        self.Couple_user_entry.grid(row=row_count2, column=3, sticky="w", pady=(0,0))
        row_count2+=1

        # Label for plaque width
        plaque_width = ctk.CTkLabel(self.plaque_info_frame, text="Largeur de la plaque (mm) : ")
        plaque_width.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for plaque width 
        self.plaque_width_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.plaque_width_user_entry.bind("<Return>", self.on_enter_key)
        self.plaque_width_user_entry.insert("1", str(float(self.Simu_parameters['plaque_largeur'])))
        self.plaque_width_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for plaque length
        plaque_length = ctk.CTkLabel(self.plaque_info_frame, text="Longueur de la plaque (mm) : ")
        plaque_length.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for plaque length
        self.plaque_length_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.plaque_length_user_entry.bind("<Return>", self.on_enter_key)
        self.plaque_length_user_entry.insert("1", str(float(self.Simu_parameters['plaque_longueur'])))
        self.plaque_length_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Actu width
        actu_width_label = ctk.CTkLabel(self.plaque_info_frame, text="Largeur de l'actuateur (mm) : ")
        actu_width_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for plaque width 
        self.actu_width_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.actu_width_user_entry.bind("<Return>", self.on_enter_key)
        self.actu_width_user_entry.insert("1", str(float(self.Simu_parameters['largeur_actu'])))
        self.actu_width_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Actu length
        actu_length_label = ctk.CTkLabel(self.plaque_info_frame, text="Longueur de l'actuateur (mm) : ")
        actu_length_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for plaque length
        self.actu_length_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.actu_length_user_entry.bind("<Return>", self.on_enter_key)
        self.actu_length_user_entry.insert("1", str(float(self.Simu_parameters['longueur_actu'])))
        self.actu_length_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Actuateur Power
        Actu_puissance_Label = ctk.CTkLabel(self.plaque_info_frame, text="Puissance dans l'actuateur (Watt) : ")
        Actu_puissance_Label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for Actuateur Power
        self.actu_puissance_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
        self.actu_puissance_user_entry.bind("<Return>", self.on_enter_key)
        self.actu_puissance_user_entry.insert("1", str(float(self.Simu_parameters['puissance_actuateur'])))
        self.actu_puissance_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1
        row_count = max(row_count, row_count2)

        # Code for plaque with sliders:
        # Label for plaque et position des éléments visuels
        PosActu_Label = ctk.CTkLabel(self.plaque_info_frame, text="Position de l'actuateur, des thermistances et de la perturbation (mm) :")
        PosActu_Label.grid(row=row_count, column=0, columnspan=2, sticky="w", padx=(5,0), pady=(5,0))
        row_count += 1

        # Plaque
        self.plaque_width = min(self.plaque_display_size, int(self.plaque_display_size*float(self.Simu_parameters['plaque_largeur'])/float(self.Simu_parameters['plaque_longueur'])))
        self.plaque_length = min(self.plaque_display_size, int(self.plaque_display_size*float(self.Simu_parameters['plaque_longueur'])/float(self.Simu_parameters['plaque_largeur'])))
        self.plaque_box_frame = ctk.CTkFrame(self.plaque_info_frame, height=self.plaque_width, width=self.plaque_length, fg_color="black") # Frame pour la plaque
        self.plaque_box_frame.grid(row=row_count, column=0, pady=(5,5), columnspan = 2, padx=10)
        self.plaque_canvas = ctk.CTkCanvas(self.plaque_box_frame, height=self.plaque_width, width=self.plaque_length, bg='#2B2B2B', bd=0, highlightthickness=0) # Canvas pour les éléments visuels sur la plaque
        self.plaque_canvas.pack()
        self.create_rounded_rectangle('gray10') # Black background for éléments visuels
        # Creating the éléments visuels
        self.Actuateur_shape = self.plaque_canvas.create_rectangle(10, 10, 20, 20, fill="#ff4242", outline="#ff4242")
        self.Perturbation_shape = self.plaque_canvas.create_oval(14, 14, 14, 14, fill="#1DBC60", outline="#1DBC60")
        self.T1_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#0096FF", width=2),
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#0096FF", width=2)
        ]
        self.T2_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#006400", width=2),
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#006400", width=2)
        ]
        self.T3_shape = [
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#FFFFFF", width=2),
            self.plaque_canvas.create_line(0, 0, 0, 0, fill="#FFFFFF", width=2)
        ]
        
        row_count += 1

        # Frame pour les sliders vertical
        self.vertical_sliders_frame = ctk.CTkFrame(self.plaque_info_frame, fg_color=self.plaque_info_frame.cget("fg_color"))
        self.vertical_sliders_frame.grid(row=row_count-2, column=2, columnspan=2, rowspan=2, sticky='wns')

        # Slider horizontal pour actuateur x position
        min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
        self.length_slider_actu = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_longueur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="horizontal", button_color="#ff4242")
        if self.length_slider_actu.cget("from_") < self.length_slider_actu.cget("to"):
            self.length_slider_actu.set(float(self.Simu_parameters['position_longueur_actuateur']))
        else:
            self.length_slider_actu.configure(state="disabled")
        self.length_slider_actu.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for actuateur x position horizontal slider
        self.length_value_actu = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_actu.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_actu.insert(0, str(self.length_slider_actu.get()))
        if self.length_slider_actu.cget("from_") >= self.length_slider_actu.cget("to"):
            self.length_value_actu.configure(state="disabled")
        self.length_value_actu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_actu"))

        # Slider vertical pour actuateur y position
        min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
        self.width_slider_actu = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=min_max_for_actu_size, to=int(float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size), number_of_steps=100, command=self.update_actu_red_square, orientation="vertical", button_color="#ff4242")
        if self.width_slider_actu.cget("from_") < self.width_slider_actu.cget("to"):
            self.width_slider_actu.set(float(self.Simu_parameters['position_largeur_actuateur']))
        else:
            self.width_slider_actu.configure(state="disabled")        
        self.width_slider_actu.grid(row=1, column=0, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for actuateur's y position vertical slider
        self.width_value_actu = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_actu.grid(row=0, column=0, pady=(5,0), padx=(0,0), sticky="w")
        self.width_value_actu.insert(0, str(self.width_slider_actu.get()))
        if self.width_slider_actu.cget("from_") >= self.width_slider_actu.cget("to"):
            self.width_value_actu.configure(state="disabled")
        self.width_value_actu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_actu"))
        self.update_actu_red_square()
        row_count+=1

        # Create horizontal slider for perturbation x position
        self.length_slider_pertu = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_pertu_green_circle, orientation="horizontal", button_color="#1DBC60")        
        self.length_slider_pertu.set(float(self.Simu_parameters['perturbation_longueur']))
        self.length_slider_pertu.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for perturbation x position horizontal slider
        self.length_value_pertu = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_pertu.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_pertu.insert(0, str(self.length_slider_pertu.get()))
        self.length_value_pertu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_pertu"))

        # Create vertical slider for the perturbation y position
        self.width_slider_pertu = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_pertu_green_circle, orientation="vertical", button_color="#1DBC60")
        self.width_slider_pertu.set(float(self.Simu_parameters['perturbation_largeur']))
        self.width_slider_pertu.grid(row=1, column=1, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for perturbation position vertical slider
        self.width_value_pertu = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_pertu.grid(row=0, column=1, pady=(5,0), padx=(0,0), sticky="w")
        self.width_value_pertu.insert(0, str(self.width_slider_pertu.get()))
        self.width_value_pertu.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_pertu"))
        self.update_pertu_green_circle()
        row_count+=1

        # Create horizontal slider for T1 x position
        self.length_slider_T1 = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_T1_blue_cross, orientation="horizontal", button_color="#0096FF")
        self.length_slider_T1.set(float(self.Simu_parameters['point_interet_1_longueur']))
        self.length_slider_T1.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for T1 x position horizontal slider
        self.length_value_T1 = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_T1.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_T1.insert(0, str(self.length_slider_T1.get()))
        self.length_value_T1.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_T1"))

        # Create vertical slider for the T1 y position
        self.width_slider_T1 = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_T1_blue_cross, orientation="vertical", button_color="#0096FF")
        self.width_slider_T1.set(float(self.Simu_parameters['point_interet_1_largeur']))
        self.width_slider_T1.grid(row=1, column=2, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for T1 position vertical slider
        self.width_value_T1 = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_T1.grid(row=0, column=2, pady=(5,0), padx=(0,0), sticky="w")
        self.width_value_T1.insert(0, str(self.width_slider_T1.get()))
        self.width_value_T1.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_T1"))
        self.update_T1_blue_cross()
        row_count+=1

        # Create horizontal slider for T2 x position
        self.length_slider_T2 = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_T2_green_cross, orientation="horizontal", button_color="#006400")
        self.length_slider_T2.set(float(self.Simu_parameters['point_interet_2_longueur']))
        self.length_slider_T2.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for T2 x position horizontal slider
        self.length_value_T2 = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_T2.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_T2.insert(0, str(self.length_slider_T2.get()))
        self.length_value_T2.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_T2"))

        # Create vertical slider for the T2 y position
        self.width_slider_T2 = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_T2_green_cross, orientation="vertical", button_color="#006400")
        self.width_slider_T2.set(float(self.Simu_parameters['point_interet_2_largeur']))
        self.width_slider_T2.grid(row=1, column=3, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for T2 position vertical slider
        self.width_value_T2 = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_T2.grid(row=0, column=3, pady=(5,0), padx=(0,0), sticky="w")
        self.width_value_T2.insert(0, str(self.width_slider_T2.get()))
        self.width_value_T2.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_T2"))
        self.update_T2_green_cross()
        row_count+=1

        # Create horizontal slider for T3 x position
        self.length_slider_T3 = ctk.CTkSlider(self.plaque_info_frame, width=self.plaque_length, from_=0, to=int(float(self.Simu_parameters['plaque_longueur'])), number_of_steps=100, command=self.update_T3_white_cross, orientation="horizontal", button_color="#FFFFFF")
        self.length_slider_T3.set(float(self.Simu_parameters['point_interet_3_longueur']))
        self.length_slider_T3.grid(row=row_count, column=0, columnspan=2, pady=(0,5), padx=(10,0), sticky="ew")
        # Create corresponding Entry for T3 x position horizontal slider
        self.length_value_T3 = ctk.CTkEntry(self.plaque_info_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.length_value_T3.grid(row=row_count, column=2, padx=0, pady=(0,0), sticky="w")
        self.length_value_T3.insert(0, str(self.length_slider_T3.get()))
        self.length_value_T3.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length_T3"))

        # Create vertical slider for the T3 y position (height)
        self.width_slider_T3 = ctk.CTkSlider(self.vertical_sliders_frame, height=self.plaque_width, from_=0, to=int(float(self.Simu_parameters['plaque_largeur'])), number_of_steps=100, command=self.update_T3_white_cross, orientation="vertical", button_color="#FFFFFF")
        self.width_slider_T3.set(float(self.Simu_parameters['point_interet_3_largeur']))
        self.width_slider_T3.grid(row=1, column=4, padx=(18,0), pady=(0,0), sticky="wns")
        # Create corresponding Entry for T3 position vertical slider
        self.width_value_T3 = ctk.CTkEntry(self.vertical_sliders_frame, width=50, validate="key", validatecommand=(self.validate_cmd, "%P"), justify='center')
        self.width_value_T3.grid(row=0, column=4, pady=(5,0), padx=(0,0), sticky="w")
        self.width_value_T3.insert(0, str(self.width_slider_T3.get()))
        self.width_value_T3.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width_T3"))
        self.update_T3_white_cross()
        row_count+=1

        # Frame for Simu info
        self.simu_info_frame = ctk.CTkFrame(self.scroll_root)
        self.simu_info_frame.grid(row=2, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.simu_info_frame.columnconfigure(0, weight=0)
        self.simu_info_frame.columnconfigure(1, weight=0)
        row_count = 0 # Facilite lajout de plus de widget
        row_count2 = 0

        # Label for simu length
        simu_length_label = ctk.CTkLabel(self.simu_info_frame, text="Durée de la simulation (secondes) : ")
        simu_length_label.grid(row=row_count, column=0, sticky="w", padx=(5,0), pady=(5,0))
        # Data Entry for simu length
        self.simu_length_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.simu_length_user_entry.bind("<Return>", self.on_enter_key)
        self.simu_length_user_entry.insert("1", str(float(self.Simu_parameters['simu_duration'])))
        self.simu_length_user_entry.grid(row=row_count, column=1, sticky="w", pady=(5,0))
        row_count+=1


        # Label for time actu start
        Actu_start_time_label = ctk.CTkLabel(self.simu_info_frame, text="Démarrage de l'actuateur à (secondes) : ")
        Actu_start_time_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for actu start
        self.Actu_start_time_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Actu_start_time_user_entry.bind("<Return>", self.on_enter_key)
        self.Actu_start_time_user_entry.insert("1", str(float(self.Simu_parameters['actu_start'])))
        self.Actu_start_time_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for time actu stop
        Actu_stop_time_label = ctk.CTkLabel(self.simu_info_frame, text="Arrêt  de l'actuateur à (secondes) : ")
        Actu_stop_time_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for actu stop
        self.Actu_stop_time_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Actu_stop_time_user_entry.bind("<Return>", self.on_enter_key)
        self.Actu_stop_time_user_entry.insert("1", str(float(self.Simu_parameters['actu_stop'])))
        self.Actu_stop_time_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Maillage
        Maillage_label = ctk.CTkLabel(self.simu_info_frame, text="Maillage (mm/éléments) : ")
        Maillage_label.grid(row=row_count, column=0, sticky="w", padx=(5,0))
        # Data Entry for actu stop
        self.Maillage_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.Maillage_user_entry.bind("<Return>", self.on_enter_key)
        self.Maillage_user_entry.insert("1", str(float(self.Simu_parameters['mm_par_element'])))
        self.Maillage_user_entry.grid(row=row_count, column=1, sticky="w")
        row_count+=1

        # Label for Perturbation Power
        perturbation_power_label = ctk.CTkLabel(self.simu_info_frame, text="Puissance de la perturbation (Watt) :")
        perturbation_power_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0), pady=(5,0))
        # Data Entry for Perturbation Power
        self.perturbation_power_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd_Neg, "%P"))
        self.perturbation_power_user_entry.bind("<Return>", self.on_enter_key)
        self.perturbation_power_user_entry.insert("1", str(float(self.Simu_parameters['perturbation_power'])))
        self.perturbation_power_user_entry.grid(row=row_count2, column=4, sticky="w", pady=(5,0))
        row_count2+=1

        # Label for Perturbation start
        perturbation_start_label = ctk.CTkLabel(self.simu_info_frame, text="Début de la perturbation à (secondes) : ")
        perturbation_start_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0))
        # Data Entry for Perturbation Power
        self.perturbation_start_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.perturbation_start_user_entry.bind("<Return>", self.on_enter_key)
        self.perturbation_start_user_entry.insert("1", str(float(self.Simu_parameters['perturabtion_start'])))
        self.perturbation_start_user_entry.grid(row=row_count2, column=4, sticky="w")
        row_count2+=1

        # Label for Perturbation stop
        perturbation_stop_label = ctk.CTkLabel(self.simu_info_frame, text="Fin de la perturbation à (secondes) : ")
        perturbation_stop_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0))
        # Data Entry for Perturbation Power
        self.perturbation_stop_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.perturbation_stop_user_entry.bind("<Return>", self.on_enter_key)
        self.perturbation_stop_user_entry.insert("1", str(float(self.Simu_parameters['perturabtion_stop'])))
        self.perturbation_stop_user_entry.grid(row=row_count2, column=4, sticky="w")
        row_count2+=1

        # Label for simu_acceleration_factor
        simu_acceleration_factor_label = ctk.CTkLabel(self.simu_info_frame, text="Facteur d'accélération d'affichage : ")
        simu_acceleration_factor_label.grid(row=row_count2, column=3, sticky="w", padx=(5,0))
        # Data Entry for simu_acceleration_factor
        self.simu_acceleration_factor_user_entry = ctk.CTkEntry(self.simu_info_frame, justify='center', validate="key", validatecommand=(self.validate_cmd, "%P"))
        self.simu_acceleration_factor_user_entry.bind("<Return>", self.on_enter_key)
        self.simu_acceleration_factor_user_entry.insert("1", str(float(self.Simu_parameters['simu_acceleration_factor'])))
        self.simu_acceleration_factor_user_entry.grid(row=row_count2, column=4, sticky="w")
        row_count2+=1
        
        # Button for simulation start
        self.HW_button = ctk.CTkButton(self.simu_info_frame, text="Lancer la Simulation", command=self.Simulate)
        self.HW_button.grid(row=row_count, column=0, pady=(5,5), padx=(5,0), sticky="w")

        # Configure column weights
        self.scroll_root.grid_columnconfigure(0, weight=1)
        self.scroll_root.grid_columnconfigure(1, weight=1)

    def Simulate(self):
        """
        Cette fonction log tous les pramètres du GUI et lance la simulation
        """
        self.on_enter_key() # Log et corrige tous les pramètres
        self.root.attributes("-disabled", True) 
        My_plaque = Plaque(self.Simu_parameters)
        try:
            TXT_save_as_path = self.Save_as_path
            if not self.TXT_switch.get():
                TXT_save_as_path = "Aucune Sélection"
            if self.Simu_parameters['simu_acceleration_factor'] == 0:
                My_plaque.Launch_Simu(save_txt=TXT_save_as_path, display_animation=False) # Launch la simu sans graph
            else:
                My_plaque.Launch_Simu(save_txt=TXT_save_as_path) # Launch la simu

        except Exception as e:
            plt.close('all')
            print(f"Une erreur s'est produite pendant la simulation : {e}")
        self.root.attributes("-disabled", False)
        self.root.lift()  # Lift la main window au premier plan lorsque la simu est done

    def Save_as_clicked(self):
        """
        Demande pour un emplacement ou enregistrer le data de la simulation
        """
        New_save_as_path = filedialog.askdirectory(title='Enregister Sous')
        if New_save_as_path == '':
            New_save_as_path = "Aucune Sélection"
        self.Save_as_path = New_save_as_path
        self.load_frame()

    def create_rounded_rectangle(self, color):
        """
        Build un rectangle noir des dimentions de la plaque pour y afficher les éléments visuels
        """
        r = 10
        W = self.plaque_length
        L = self.plaque_width
        # Build des coins Ronds
        self.plaque_canvas.create_oval(0, 0, r*2, r*2, fill=color, outline=color)  # coin top left
        self.plaque_canvas.create_oval(W - r*2, 0, W, r*2, fill=color, outline=color)  # coin top right
        self.plaque_canvas.create_oval(0, L - r*2, r*2, L, fill=color, outline=color)  # coin bot left
        self.plaque_canvas.create_oval(W - r*2, L - r*2, W, L, fill=color, outline=color)  # coin bot right
        # 2 rectangle pour 4 cotes sans couper les coins ronds
        self.plaque_canvas.create_rectangle(r, 0, W - r, L, fill=color, outline=color)  # top et bot
        self.plaque_canvas.create_rectangle(0, r, W, L - r, fill=color, outline=color)  # left et right

    def update_actu_red_square(self, update_entry=True, event=None):
        """
        Fonction pour acualiser la position du carré rouge de l'actuateur
        Peut aussi actualiser les user entry des sliders
        """
        x = self.length_slider_actu.get()  
        y = self.width_slider_actu.get()
        pos_x_in_pix = int(self.plaque_length*x/(float(self.Simu_parameters['plaque_longueur'])))
        pos_y_in_pix = int(self.plaque_width*(float(self.Simu_parameters['plaque_largeur']) - y)/float(self.Simu_parameters['plaque_largeur']))
        half_longueur_actu_in_pix = int(self.plaque_length*float(self.Simu_parameters['longueur_actu'])/(float(self.Simu_parameters['plaque_longueur']))/2)
        half_largeur_actu_in_pix = int(self.plaque_width*float(self.Simu_parameters['largeur_actu'])/(float(self.Simu_parameters['plaque_largeur']))/2)
        self.plaque_canvas.coords(self.Actuateur_shape, pos_x_in_pix - half_longueur_actu_in_pix, pos_y_in_pix - half_largeur_actu_in_pix, pos_x_in_pix + half_longueur_actu_in_pix, pos_y_in_pix + half_largeur_actu_in_pix)
        if update_entry:
            self.length_value_actu.delete(0, ctk.END)
            self.length_value_actu.insert(0, str(round(x,5)))
            self.width_value_actu.delete(0, ctk.END)
            self.width_value_actu.insert(0, str(round(y,5)))

    def update_pertu_green_circle(self, update_entry=True, event=None):
        """
        Fonction pour acualiser la position du cercle vert de la perturbation
        Peut aussi actualiser les user entry des sliders
        """
        x = self.length_slider_pertu.get()  
        y = self.width_slider_pertu.get()
        pos_x_in_pix = int(self.plaque_length*x/(float(self.Simu_parameters['plaque_longueur'])))
        pos_y_in_pix = int(self.plaque_width*(float(self.Simu_parameters['plaque_largeur']) - y)/float(self.Simu_parameters['plaque_largeur']))
        self.plaque_canvas.coords(self.Perturbation_shape, pos_x_in_pix+7, pos_y_in_pix+7, pos_x_in_pix-7, pos_y_in_pix-7)
        if update_entry:
            self.length_value_pertu.delete(0, ctk.END)
            self.length_value_pertu.insert(0, str(round(x,5)))
            self.width_value_pertu.delete(0, ctk.END)
            self.width_value_pertu.insert(0, str(round(y,5)))

    def update_T1_blue_cross(self, update_entry=True, event=None, size=7):
        """
        Fonction pour acualiser la position de la cross de la thermistance 1
        Peut aussi actualiser les user entry des sliders
        """
        x = self.length_slider_T1.get()
        y = self.width_slider_T1.get()
        pos_x_in_pix = int(self.plaque_length * x / float(self.Simu_parameters['plaque_longueur']))
        pos_y_in_pix = int(self.plaque_width * (float(self.Simu_parameters['plaque_largeur']) - y) / float(self.Simu_parameters['plaque_largeur']))
        self.plaque_canvas.coords(self.T1_shape[0], pos_x_in_pix - size, pos_y_in_pix - size, pos_x_in_pix + size, pos_y_in_pix + size)
        self.plaque_canvas.coords(self.T1_shape[1], pos_x_in_pix - size, pos_y_in_pix + size, pos_x_in_pix + size, pos_y_in_pix - size)
        if update_entry:
            self.length_value_T1.delete(0, ctk.END)
            self.length_value_T1.insert(0, str(round(x, 5)))
            self.width_value_T1.delete(0, ctk.END)
            self.width_value_T1.insert(0, str(round(y, 5)))

    def update_T2_green_cross(self, update_entry=True, event=None, size=7):
        """
        Fonction pour acualiser la position de la cross de la thermistance 2
        Peut aussi actualiser les user entry des sliders
        """
        x = self.length_slider_T2.get()
        y = self.width_slider_T2.get()
        pos_x_in_pix = int(self.plaque_length * x / float(self.Simu_parameters['plaque_longueur']))
        pos_y_in_pix = int(self.plaque_width * (float(self.Simu_parameters['plaque_largeur']) - y) / float(self.Simu_parameters['plaque_largeur']))
        self.plaque_canvas.coords(self.T2_shape[0], pos_x_in_pix - size, pos_y_in_pix - size, pos_x_in_pix + size, pos_y_in_pix + size)
        self.plaque_canvas.coords(self.T2_shape[1], pos_x_in_pix - size, pos_y_in_pix + size, pos_x_in_pix + size, pos_y_in_pix - size)
        if update_entry:
            self.length_value_T2.delete(0, ctk.END)
            self.length_value_T2.insert(0, str(round(x, 5)))
            self.width_value_T2.delete(0, ctk.END)
            self.width_value_T2.insert(0, str(round(y, 5)))

    def update_T3_white_cross(self, update_entry=True, event=None, size=7):
        """
        Fonction pour acualiser la position de la cross de la thermistance 2
        Peut aussi actualiser les user entry des sliders
        """
        x = self.length_slider_T3.get()
        y = self.width_slider_T3.get()
        pos_x_in_pix = int(self.plaque_length * x / float(self.Simu_parameters['plaque_longueur']))
        pos_y_in_pix = int(self.plaque_width * (float(self.Simu_parameters['plaque_largeur']) - y) / float(self.Simu_parameters['plaque_largeur']))
        self.plaque_canvas.coords(self.T3_shape[0], pos_x_in_pix - size, pos_y_in_pix - size, pos_x_in_pix + size, pos_y_in_pix + size)
        self.plaque_canvas.coords(self.T3_shape[1], pos_x_in_pix - size, pos_y_in_pix + size, pos_x_in_pix + size, pos_y_in_pix - size)
        if update_entry:
            self.length_value_T3.delete(0, ctk.END)
            self.length_value_T3.insert(0, str(round(x, 5)))
            self.width_value_T3.delete(0, ctk.END)
            self.width_value_T3.insert(0, str(round(y, 5)))

    def validate_input(self, P):
        """
        Permet seulement des input numerique sans les negatifs
        """
        if P == "" or P.isdigit() or (P.replace('.', '', 1).isdigit() and P.count('.') <= 1):
            return True
        else:
            return False
    def validate_input_Neg(self, P):
        """
        Permet seulement des input numerique incluant les negatifs
        """
        if P != "":
            if P[0] == "-":
                P = P[1:]
        if P == "" or P.isdigit() or (P.replace('.', '', 1).isdigit() and P.count('.') <= 1):
            return True
        else:
            return False

    def parameters_correction(self):
        """
        Corrige et redefinit les valeurs de self.Simu_parameters pour qu'elle soient toutes legitime
        """
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

        # Bounds pour pas que la simu brise trop trop
        self.Simu_parameters['plaque_largeur'] = max(1,min(1000,self.Simu_parameters['plaque_largeur']))
        self.Simu_parameters['plaque_longueur'] = max(1,min(1000,self.Simu_parameters['plaque_longueur']))
        self.Simu_parameters['puissance_actuateur'] = max(-10,min(10,self.Simu_parameters['puissance_actuateur']))
        self.Simu_parameters['Temperature_Ambiante_C'] = max(-200,min(200,self.Simu_parameters['Temperature_Ambiante_C']))
        self.Simu_parameters['masse_volumique_plaque'] = max(500,min(10000,self.Simu_parameters['masse_volumique_plaque']))
        self.Simu_parameters['capacite_thermique_plaque'] = max(100,min(10000,self.Simu_parameters['capacite_thermique_plaque']))
        self.Simu_parameters['coefficient_convection'] = max(0.01,min(1000,self.Simu_parameters['coefficient_convection']))
        self.Simu_parameters['epaisseur_plaque_mm'] = max(0.001,min(100,self.Simu_parameters['epaisseur_plaque_mm']))
        self.Simu_parameters['conductivite_thermique_plaque'] = max(1,min(1000,self.Simu_parameters['conductivite_thermique_plaque']))
        self.Simu_parameters['couple_actuateur'] = max(0.001,min(10,self.Simu_parameters['couple_actuateur']))
        self.Simu_parameters['simu_duration'] = max(10, min(10000,self.Simu_parameters['simu_duration']))
        if self.Simu_parameters['simu_acceleration_factor'] != 0:
            self.Simu_parameters['simu_acceleration_factor'] = max(1, min(100,self.Simu_parameters['simu_acceleration_factor']))
        self.Simu_parameters['actu_start'] = max(0, min(10000,self.Simu_parameters['actu_start']))
        self.Simu_parameters['actu_stop'] = max(0, min(10000,self.Simu_parameters['actu_stop']))
        self.Simu_parameters['perturabtion_start'] = max(0, min(10000,self.Simu_parameters['perturabtion_start']))
        self.Simu_parameters['perturabtion_stop'] = max(0, min(10000,self.Simu_parameters['perturabtion_stop']))
        self.Simu_parameters['mm_par_element'] = max(0.5, min(10,self.Simu_parameters['mm_par_element']))
        self.Simu_parameters['perturbation_power'] = max(-100, min(100,self.Simu_parameters['perturbation_power']))

    def update_slider_from_entry(self, slider_type):
        """
        Fonction pour permetre au slider et au visuels detre directement updater lorsque le user entry des slider est modifé
        """
        try:
            if slider_type == "length_actu":
                value = float(self.length_value_actu.get())
                min_max_for_actu_size = math.ceil(self.Simu_parameters['longueur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_longueur']) - min_max_for_actu_size:
                    self.length_slider_actu.set(value)
                    self.update_actu_red_square(update_entry=False)
            elif slider_type == "width_actu":
                value = float(self.width_value_actu.get())
                min_max_for_actu_size = math.ceil(self.Simu_parameters['largeur_actu']/ 2)
                if min_max_for_actu_size <= value <= float(self.Simu_parameters['plaque_largeur'])-min_max_for_actu_size:
                    self.width_slider_actu.set(value)
                    self.update_actu_red_square(update_entry=False)
            elif slider_type == "length_pertu":
                value = float(self.length_value_pertu.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_pertu.set(value)
                    self.update_pertu_green_circle(update_entry=False)
            elif slider_type == "width_pertu":
                value = float(self.width_value_pertu.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_pertu.set(value)
                    self.update_pertu_green_circle(update_entry=False)
            elif slider_type == "length_T1":
                value = float(self.length_value_T1.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_T1.set(value)
                    self.update_T1_blue_cross(update_entry=False)
            elif slider_type == "width_T1":
                value = float(self.width_value_T1.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_T1.set(value)
                    self.update_T1_blue_cross(update_entry=False)
            elif slider_type == "length_T2":
                value = float(self.length_value_T2.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_T2.set(value)
                    self.update_T2_green_cross(update_entry=False)
            elif slider_type == "width_T2":
                value = float(self.width_value_T2.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_T2.set(value)
                    self.update_T2_green_cross(update_entry=False)
            elif slider_type == "length_T3":
                value = float(self.length_value_T3.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_longueur']):
                    self.length_slider_T3.set(value)
                    self.update_T3_white_cross(update_entry=False)
            elif slider_type == "width_T3":
                value = float(self.width_value_T3.get())
                if 0 <= value <= float(self.Simu_parameters['plaque_largeur']):
                    self.width_slider_T3.set(value)
                    self.update_T3_white_cross(update_entry=False)

        except ValueError:
            print('Erreur')
            pass  # Ignore invalid input

    def Reset_to_default(self):
        """
        Va chercher les parames initiales dumped dans un temp file pour reloader les params initiaux
        """
        with open(self.temp_filename, 'r') as temp_file:
            loaded_parameters = json.load(temp_file)
            self.Simu_parameters = loaded_parameters
        self.load_frame()
        
    def TXT_toggle(self):
        """
        Fonction pour log la valeur dune switch booleane
        """
        if self.TXT_switch.get():
            self.save_txt_bool = True
        else:
            self.save_txt_bool = False
        
if __name__ == "__main__":
    app = GUI()
    app.root.mainloop()