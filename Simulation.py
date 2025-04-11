"""
Ce code contient la classe Plaque qui pest initialiser en lui donnant un dictionnaire avec des paramètres de simulation
Ensuite, une simulation de la diffusion de la chaleur dans un plaque en accordance avec les paramètres du dictionnaire peut être lancer
La simulation est affiché en temps réel dans une fenêtre matplotlib
"""

import numpy as np
import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation
import os
import pandas as pd
from datetime import datetime

class Plaque:
    def __init__(self, Parameters):
        """
        Initialise tous les paramètres de simulation à partir d'un dictionnaire
        Calcule des constantes thermique
        Crée les matrices représentant la plaque et l'actuateur
        """
        self.Para = Parameters
        self.plaque_largeur = float(Parameters['plaque_largeur'])
        self.plaque_longueur = float(Parameters['plaque_longueur']) 
        self.mm_par_element = float(Parameters['mm_par_element'])
        self.Temperature_Ambiante_C = float(Parameters['Temperature_Ambiante_C'])
        self.largeur_actu = float(Parameters['largeur_actu']) 
        self.longueur_actu = float(Parameters['longueur_actu']) 
        self.position_longueur_actuateur = float(Parameters['position_longueur_actuateur']) 
        self.position_largeur_actuateur = float(Parameters['position_largeur_actuateur']) 
        self.puissance_actuateur = float(Parameters['puissance_actuateur'])
        self.couple_actuateur = float(Parameters['couple_actuateur'])
        self.voltage_actuateur = float(Parameters['voltage_actuateur'])
        self.convection_actuateur = float(Parameters['convection_actuateur'])
        self.masse_volumique_plaque = float(Parameters['masse_volumique_plaque'])
        self.masse_volumique_actu = float(Parameters['masse_volumique_actu'])
        self.epaisseur_plaque_mm = float(Parameters['epaisseur_plaque_mm'])
        self.epaisseur_actu_mm = float(Parameters['epaisseur_actu_mm'])
        self.capacite_thermique_plaque = float(Parameters['capacite_thermique_plaque'])
        self.capacite_thermique_Actu = float(Parameters['capacite_thermique_Actu'])
        self.conductivite_thermique_plaque = float(Parameters['conductivite_thermique_plaque'])
        self.coefficient_convection = float(Parameters['coefficient_convection']) 
        self.simu_duration = float(Parameters['simu_duration'])
        self.simu_playspeed_multiplier = float(Parameters['simu_acceleration_factor'])
        self.actu_start = float(Parameters['actu_start'])
        self.actu_stop = float(Parameters['actu_stop'])
        self.Interest_point_largeur_1 = float(Parameters['point_interet_1_largeur'])
        self.Interest_point_longueur_1 = float(Parameters['point_interet_1_longueur'])
        self.Interest_point_largeur_2 = float(Parameters['point_interet_2_largeur'])
        self.Interest_point_longueur_2 = float(Parameters['point_interet_2_longueur'])
        self.Interest_point_largeur_3 = float(Parameters['point_interet_3_largeur'])
        self.Interest_point_longueur_3 = float(Parameters['point_interet_3_longueur'])
        self.perturbation_longueur = float(Parameters['perturbation_longueur'])
        self.perturbation_largeur = float(Parameters['perturbation_largeur'])
        self.perturabtion_start = float(Parameters['perturabtion_start'])
        self.perturabtion_stop = float(Parameters['perturabtion_stop'])
        self.perturbation_power = float(Parameters['perturbation_power'])

        # Automatic time step pour respecter Courant–Friedrichs–Lewy condition
        if Parameters['time_step'] == 'auto':
            self.time_step = 1/(self.conductivite_thermique_plaque/0.2/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)**2)
        else:
            self.time_step = float(Parameters['time_step'])

        # Convection Q̇ = h•A•ΔT
        # Conduction Q̇ = κ•A•ΔT/l
        # Constantes thermique pour la plaque
        self.Temperature_Ambiante = self.Temperature_Ambiante_C + 273.15
        self.Constante_plaque = self.conductivite_thermique_plaque*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)**2
        self.Constante_Air_top_bot = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.epaisseur_plaque_mm/1000)
        self.Constante_Air_side = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)
        
        # Constante thermique pour l'actuateur
        self.Constante_Air_top_bot_Actu = self.convection_actuateur*self.time_step/self.masse_volumique_actu/self.capacite_thermique_Actu/(self.epaisseur_actu_mm/1000)
        self.Constante_Air_side_Actu = self.convection_actuateur*self.time_step/self.masse_volumique_actu/self.capacite_thermique_Actu/(self.mm_par_element/1000)
        
        # Geometrie de température initial pour la plaque et l'actuateur
        self.Geometry_Matrix = np.full((max(1,int(self.plaque_largeur/self.mm_par_element)), max(1,int(self.plaque_longueur/self.mm_par_element))), float(self.Temperature_Ambiante))
        self.Geometry_Actu = np.full((max(1,int(self.largeur_actu/self.mm_par_element)), max(1,int(self.largeur_actu/self.mm_par_element))), float(self.Temperature_Ambiante))

    def iterate(self):
        """
        Calcule une itération de diffusion thermique dans la plaque
        """
        padded_matrix = np.pad(self.Geometry_Matrix, ((1, 1), (1, 1)), mode='constant', constant_values=self.Temperature_Ambiante) # Matrix avec pad pour gérer les voisin de manière vectorielle
        # Matrice des delta de température spatial
        delta_T_voisin_plaque = np.zeros_like(self.Geometry_Matrix)
        delta_T_voisin_plaque += padded_matrix[1:-1, :-2] - self.Geometry_Matrix  # Left neighbor
        delta_T_voisin_plaque += padded_matrix[1:-1, 2:] - self.Geometry_Matrix   # Right neighbor
        delta_T_voisin_plaque += padded_matrix[:-2, 1:-1] - self.Geometry_Matrix  # Top neighbor
        delta_T_voisin_plaque += padded_matrix[2:, 1:-1] - self.Geometry_Matrix   # Bottom neighbor
        # Gestion des cotés
        delta_T_voisin_plaque[:, 0] -= padded_matrix[1:-1, 0] - self.Geometry_Matrix[:, 0] # Left cote
        delta_T_voisin_plaque[:, -1] -= padded_matrix[1:-1, -1] - self.Geometry_Matrix[:, -1] # Right cote
        delta_T_voisin_plaque[0, :] -= padded_matrix[0, 1:-1] - self.Geometry_Matrix[0, :] # Top cote
        delta_T_voisin_plaque[-1, :] -= padded_matrix[-1, 1:-1] - self.Geometry_Matrix[-1, :] # Bottom cote 
        # Somme des delta temp avec l'air pour TOP et BOT
        delta_T_voisin_air_top_bot = 2 * (self.Temperature_Ambiante - self.Geometry_Matrix)
        # Somme des delta temp avec l'air pour les sides
        delta_T_voisin_air_side = np.zeros_like(self.Geometry_Matrix)
        delta_T_voisin_air_side[:, 0] += self.Temperature_Ambiante - self.Geometry_Matrix[:, 0]
        delta_T_voisin_air_side[:, -1] += self.Temperature_Ambiante - self.Geometry_Matrix[:, -1]
        delta_T_voisin_air_side[0, :] += self.Temperature_Ambiante - self.Geometry_Matrix[0, :]
        delta_T_voisin_air_side[-1, :] += self.Temperature_Ambiante - self.Geometry_Matrix[-1, :]
        # Update la matrice de la Geometrie de la temperature
        self.Geometry_Matrix += self.Constante_plaque * delta_T_voisin_plaque + self.Constante_Air_top_bot * delta_T_voisin_air_top_bot + self.Constante_Air_side * delta_T_voisin_air_side

    def Heat_Pumped(self, Th, Delta_T_actu, Power):
        """
        Cette fonction modélise l'aproximation linéaire du graph présenté sur la data sheet de l'actuateur CP60140
        La fonction prend une puissance électrique et done une puissance thermique de chaleur pompée
        """
        Courant = Power/self.voltage_actuateur # L'approximation linéaire est en courant donc P = IV
        if Courant == 0:
            return 0
        a=1.21161+0.02535*Th
        b=-0.04109-0.00298*Th
        c=35.223+0.07174*Th
        d=-7.2969+0.00174*Th
        e=0.50796-0.000739*Th
        Power_at_0 = a*Courant+b*Courant**2
        Delta_T_actu_at_0 = c*Courant+d*Courant**2+e*Courant**3
        Power = Power_at_0*(1-Delta_T_actu/Delta_T_actu_at_0)
        return Power
    
    def perturbation_influence(self):
        """
        Cette ajoute une quantité de chaleur à la plaque à l'emplacement de la perturbation
        """
        if self.perturbation_power == 0:
            return
        pos_y_perturbation = max(0,min(len(self.Geometry_Matrix)-1, int(self.perturbation_largeur/self.mm_par_element)))
        pos_x_perturbation = max(0,min(len(self.Geometry_Matrix[0])-1, int(self.perturbation_longueur/self.mm_par_element)))

        delta_temp = self.perturbation_power*self.time_step*self.couple_actuateur / (self.epaisseur_plaque_mm /1000 * (self.mm_par_element/1000)**2 * self.masse_volumique_plaque) / self.capacite_thermique_plaque
        self.Geometry_Matrix[pos_y_perturbation, pos_x_perturbation] += delta_temp
    
    def actuateur_influence(self, save_data_for_trsfer_fct=False):
        """
        Cette ajoute une quantité de chaleur à la plaque à l'emplacement de l'actuateur
        """
        if self.largeur_actu==0 or self.longueur_actu ==0:
            if save_data_for_trsfer_fct or self.save_txt != "Aucune Sélection":
                self.data_for_trsfer_fct['power_in'] = np.append(self.data_for_trsfer_fct['power_in'], 0)
                self.data_for_trsfer_fct['heat_pumped'] = np.append(self.data_for_trsfer_fct['heat_pumped'], 0)
            return
        pos_y_actu = max(0,min(len(self.Geometry_Matrix)-1, int(self.position_largeur_actuateur/self.mm_par_element)))
        pos_x_actu = max(0,min(len(self.Geometry_Matrix[0])-1, int(self.position_longueur_actuateur/self.mm_par_element)))
        largeur_actu_in_element = self.largeur_actu/self.mm_par_element
        longueur_actu_in_element = self.longueur_actu/self.mm_par_element
        half_larg = int(largeur_actu_in_element/2)
        half_lon = int(longueur_actu_in_element/2)

        # Heat seulement 1 element if actu is smaller than 1 element
        if half_larg == 0:
            Top_range_larg = 1
        else:
            Top_range_larg = 0
        if half_lon == 0:
            Top_range_lon = 1
        else:
            Top_range_lon = 0

        y_range = slice(pos_y_actu - half_larg, pos_y_actu + half_larg + Top_range_larg)
        x_range = slice(pos_x_actu - half_lon, pos_x_actu + half_lon + Top_range_lon)

        T_Cote_plaque = np.average(self.Geometry_Matrix[y_range, x_range])
        T_Cote_Actu = np.average(self.Geometry_Actu)
        Th = max(T_Cote_plaque, T_Cote_Actu) # Cote chaud de lactuateur
        Delta_T_actu = Th - min(T_Cote_plaque, T_Cote_Actu) # Difference de temp entre les cotes de l'actuateur

        Th_C = Th-273.15
        heat_pumped = np.sign(self.puissance_actuateur)*self.Heat_Pumped(Th_C, Delta_T_actu, np.abs(self.puissance_actuateur))
        if save_data_for_trsfer_fct or self.save_txt != "Aucune Sélection":
            self.data_for_trsfer_fct['power_in'] = np.append(self.data_for_trsfer_fct['power_in'], np.abs(self.puissance_actuateur))
            self.data_for_trsfer_fct['heat_pumped'] = np.append(self.data_for_trsfer_fct['heat_pumped'], heat_pumped)
        Chaleur_en_jeu = heat_pumped*self.time_step*self.couple_actuateur
               
        Chaleur_par_element = Chaleur_en_jeu /(largeur_actu_in_element*largeur_actu_in_element)
        delta_temp = Chaleur_par_element / (self.epaisseur_plaque_mm /1000 * (self.mm_par_element/1000)**2 * self.masse_volumique_plaque) / self.capacite_thermique_plaque
                
        self.Geometry_Matrix[y_range, x_range] += delta_temp

        # Compute convection et chaleur pour l'actu
        delta_T_voisin_air_top_bot = 2 * (self.Temperature_Ambiante - self.Geometry_Actu)
        delta_T_voisin_air_side = np.zeros_like(self.Geometry_Actu)
        delta_T_voisin_air_side[:, 0] += self.Temperature_Ambiante - self.Geometry_Actu[:, 0]
        delta_T_voisin_air_side[:, -1] += self.Temperature_Ambiante - self.Geometry_Actu[:, -1]
        delta_T_voisin_air_side[0, :] += self.Temperature_Ambiante - self.Geometry_Actu[0, :]
        delta_T_voisin_air_side[-1, :] += self.Temperature_Ambiante - self.Geometry_Actu[-1, :]
        self.Geometry_Actu += self.Constante_Air_top_bot_Actu * delta_T_voisin_air_top_bot + self.Constante_Air_side_Actu * delta_T_voisin_air_side - delta_temp
        
    def Launch_Simu(self, display_animation=True, save_txt = "Aucune Sélection", Debug=False, save_data_for_trsfer_fct=False):
        """
        Fonction pour lancer la simulation
        Fait une animation mpl de la plaque qui chauffe
        Peut sauver le data de la simulation dans un format text
        """
        self.save_txt = save_txt
        simu_start_time = time.time()
        time_stamp = datetime.fromtimestamp(simu_start_time).strftime("%Y-%m-%d %H:%M:%S.%f") # Time stamp au start de la simu
        time_stamp = time_stamp.replace(' ', '_').replace(':','-').replace('.','-')
        if save_data_for_trsfer_fct or self.save_txt != "Aucune Sélection":
            self.data_for_trsfer_fct = {
                'time':np.array([]),
                'power_in':np.array([]),
                'heat_pumped':np.array([]),
                'T1':np.array([]),
                'T2':np.array([]),
                'T3':np.array([])
            }
        
        # Initialise des variables pour les graphs
        iterations_number = max(1,int(self.simu_duration / self.time_step))

        Interest_point_y_1 = int(self.Interest_point_largeur_1 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_1 = int(self.Interest_point_longueur_1 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_y_2 = int(self.Interest_point_largeur_2 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_2 = int(self.Interest_point_longueur_2 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_y_3 = int(self.Interest_point_largeur_3 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_3 = int(self.Interest_point_longueur_3 / self.plaque_longueur * len(self.Geometry_Matrix[0]))

        Interest_point_y_1 = max(0, min(len(self.Geometry_Matrix)-1, Interest_point_y_1))
        Interest_point_x_1 = max(0, min(len(self.Geometry_Matrix[0])-1, Interest_point_x_1))
        Interest_point_y_2 = max(0, min(len(self.Geometry_Matrix)-1, Interest_point_y_2))
        Interest_point_x_2 = max(0, min(len(self.Geometry_Matrix[0])-1, Interest_point_x_2))
        Interest_point_y_3 = max(0, min(len(self.Geometry_Matrix)-1, Interest_point_y_3))
        Interest_point_x_3 = max(0, min(len(self.Geometry_Matrix[0])-1, Interest_point_x_3))

        self.Interest_point_data_C_1 = []
        self.Interest_point_data_C_2 = []
        self.Interest_point_data_C_3 = []

        # Log une première valeur a température ambiante pour les 3 thermistances
        self.Interest_point_data_C_1.append(self.Geometry_Matrix[Interest_point_y_1][Interest_point_x_1] - 273.15)
        self.Interest_point_data_C_2.append(self.Geometry_Matrix[Interest_point_y_2][Interest_point_x_2] - 273.15)
        self.Interest_point_data_C_3.append(self.Geometry_Matrix[Interest_point_y_3][Interest_point_x_3] - 273.15)
      
        display_frame_step = max(1,int(iterations_number/self.simu_duration)) 
        time_data = np.append(np.arange(0, iterations_number*self.time_step, display_frame_step*self.time_step),iterations_number*self.time_step)

        if display_animation:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            if Debug:
                Info = ''
                for n, dic_item in enumerate(self.Para.items()):
                    param = dic_item[0]
                    value = dic_item[1]
                    Info += f' {param}:{value} '
                    if n%5 == 0 and n!=0:
                        Info += '\n'
                fig.suptitle(Info, fontsize=10)

            # Interpolate pour une plus belle heat map
            # img = ax1.imshow(self.Geometry_Matrix - 273.15, cmap='jet', interpolation='bilinear')
            img = ax1.imshow(self.Geometry_Matrix - 273.15, cmap='jet')
            cbar = plt.colorbar(img, pad=0.1)
            cbar.set_label('Temperature (°C)')
            ax1.scatter(Interest_point_x_1, Interest_point_y_1, color="#0096FF", s=200, marker='x')
            ax1.scatter(Interest_point_x_2, Interest_point_y_2, color="green", s=200, marker='x')
            ax1.scatter(Interest_point_x_3, Interest_point_y_3, color="black", s=200, marker='x')

            x_ticks = np.linspace(-0.5, len(self.Geometry_Matrix[0])-0.5, 5)
            x_labels = np.linspace(0, self.plaque_longueur, 5).astype(int)
            ax1.set_xticks(x_ticks)
            ax1.set_xticklabels([f"{val} mm" for val in x_labels])

            y_ticks = np.linspace(-0.5, len(self.Geometry_Matrix)-0.5, 5)
            y_labels = np.linspace(0, self.plaque_largeur, 5).astype(int)
            ax1.set_yticks(y_ticks)
            ax1.set_yticklabels([f"{val} mm" for val in y_labels])
            ax1.invert_yaxis()
            
            thermi_1, = ax2.plot([], [], 'b-', label = 'Thermistance 1')
            thermi_2, = ax2.plot([], [], 'green', label = 'Thermistance 2')
            thermi_3, = ax2.plot([], [], 'black', label = 'Thermistance Laser')
            
            ax2.set_xlim(0, iterations_number * self.time_step)
            x_ticks = np.linspace(0, iterations_number * self.time_step, num=8)
            ax2.set_xticks(x_ticks)
            
            ax2.set_ylim(-10, 100)
            ax2.grid(True)
            ax2.set_xlabel("Temps (s)")
            ax2.set_ylabel("Temperature (°C)")
            ax2.set_title("Temperature des thermistances")
            ax2.legend(loc='upper left')

        def update(i):
            """
            Fonction que animation call en loop
            """
            for j in range(display_frame_step): # Compute le nombre diteration pour faire 1 display_frame_step
                if self.actu_start < self.iteration_counter * self.time_step < self.actu_stop:
                    self.actuateur_influence(save_data_for_trsfer_fct=save_data_for_trsfer_fct)
                elif save_data_for_trsfer_fct or self.save_txt != "Aucune Sélection":
                    self.data_for_trsfer_fct['power_in'] = np.append(self.data_for_trsfer_fct['power_in'], 0)
                    self.data_for_trsfer_fct['heat_pumped'] = np.append(self.data_for_trsfer_fct['heat_pumped'], 0)
                if self.perturabtion_start < self.iteration_counter * self.time_step < self.perturabtion_stop:
                    self.perturbation_influence()
                self.iterate()
                if save_data_for_trsfer_fct or self.save_txt != "Aucune Sélection":
                    self.data_for_trsfer_fct['time'] = np.append(self.data_for_trsfer_fct['time'], self.iteration_counter * self.time_step)
                    self.data_for_trsfer_fct['T1'] = np.append(self.data_for_trsfer_fct['T1'], self.Geometry_Matrix[Interest_point_y_1][Interest_point_x_1] - 273.15)
                    self.data_for_trsfer_fct['T2'] = np.append(self.data_for_trsfer_fct['T2'], self.Geometry_Matrix[Interest_point_y_2][Interest_point_x_2] - 273.15)
                    self.data_for_trsfer_fct['T3'] = np.append(self.data_for_trsfer_fct['T3'], self.Geometry_Matrix[Interest_point_y_3][Interest_point_x_3] - 273.15)
                self.iteration_counter += 1

            if self.save_txt != "Aucune Sélection": # Sauvegarde en format texte
                output_dir = self.save_txt
                os.makedirs(output_dir, exist_ok=True)
                time_in_simulation = self.iteration_counter * self.time_step
                geometry_2D = self.Geometry_Matrix
                lines = [f"time = {time_in_simulation}\n"]
                for row in geometry_2D:
                    line = ",".join(str(val) for val in row)
                    lines.append(line + "\n")
                filename = os.path.join(output_dir, f"{time_stamp}_Simulation_Temp.csv")
                with open(filename, 'a') as f:
                    f.writelines(lines)
         
            self.Interest_point_data_C_1.append(self.Geometry_Matrix[Interest_point_y_1][Interest_point_x_1] - 273.15)
            self.Interest_point_data_C_2.append(self.Geometry_Matrix[Interest_point_y_2][Interest_point_x_2] - 273.15)
            self.Interest_point_data_C_3.append(self.Geometry_Matrix[Interest_point_y_3][Interest_point_x_3] - 273.15)

            if display_animation:
                max_value_temp = np.max(self.Geometry_Matrix)
                min_value_temp = np.min(self.Geometry_Matrix)
                img.set_data(self.Geometry_Matrix - 273.15)
                img.set_clim(min_value_temp - 273.15, max_value_temp - 273.15)
                ax1.set_title(f'Température de la plaque à T = {int(round(self.iteration_counter * self.time_step, 0))} secondes')

            # Message if last iteration
            if self.iteration_counter >= iterations_number:
                simu_elapsed_time = time.time() - simu_start_time
                hours, remainder = divmod(simu_elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f'Simulation terminée!\n{self.iteration_counter} itérations calculées en {int(hours):02}h {int(minutes):02}m {int(seconds):02}s')
            self.actual_time_data = time_data[:len(self.Interest_point_data_C_1)]
            if display_animation:
                thermi_1.set_data(self.actual_time_data, self.Interest_point_data_C_1)
                thermi_2.set_data(self.actual_time_data, self.Interest_point_data_C_2) 
                thermi_3.set_data(self.actual_time_data, self.Interest_point_data_C_3)
                # Get data to set the Y lim
                y1 = thermi_1.get_ydata()
                y2 = thermi_2.get_ydata()
                y3 = thermi_3.get_ydata()
                # Adjust the min and max pour les limites
                T_max = np.max([np.max(y1), np.max(y2), np.max(y3)]) + 5
                T_min = np.min([np.min(y1), np.min(y2), np.min(y3)]) - 5
                ax2.set_ylim(T_min, T_max)
                
                if i > 0:
                    simu_time = self.iteration_counter * self.time_step
                    while simu_time/self.simu_playspeed_multiplier > time.time()-simu_start_time:
                        pass

                return img, thermi_1, thermi_2, thermi_3

        if display_animation:
            self.iteration_counter = 0
            self.ani = animation.FuncAnimation(fig, update, frames=range(0, iterations_number - display_frame_step, display_frame_step), interval=0, blit=False, repeat=False, cache_frame_data=False)  
            plt.subplots_adjust(left=0.05, bottom=0.1, right=0.95, top=0.9, wspace=None, hspace=None)
            plt.show()
        else:
            self.iteration_counter = 0
            for _ in range(0, iterations_number, display_frame_step):
                update(_)
        if self.save_txt != "Aucune Sélection":
            df = pd.DataFrame(self.data_for_trsfer_fct)
            file_path = os.path.join(self.save_txt, f"{time_stamp}_elements_data.csv")
            df.to_csv(file_path, index=False)
        if save_data_for_trsfer_fct or self.save_txt != "Aucune Sélection":
            return self.data_for_trsfer_fct