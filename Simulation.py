import numpy as np
import matplotlib.pyplot as plt
import time
import matplotlib.animation as animation
import os
from datetime import datetime
import pandas as pd

class Plaque:
    def __init__(self, Parameters):
        self.Para = Parameters
        self.plaque_largeur = float(Parameters['plaque_largeur'])
        self.plaque_longueur = float(Parameters['plaque_longueur']) 
        self.mm_par_element = float(Parameters['mm_par_element'])
        self.Temperature_Ambiante_C = float(Parameters['Temperature_Ambiante_C'])
        self.largeur_actu = float(Parameters['largeur_actu']) 
        self.longueur_actu = float(Parameters['longueur_actu']) 
        self.position_longueur_actuateur = float(Parameters['position_longueur_actuateur']) 
        self.position_largeur_actuateur = float(Parameters['position_largeur_actuateur']) 
        self.courant_actuateur = float(Parameters['courant_actuateur'])
        self.couple_actuateur = float(Parameters['couple_actuateur'])
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
        self.Interest_point_largeur_1 = float(Parameters['point_interet_1_largeur'])
        self.Interest_point_longueur_1 = float(Parameters['point_interet_1_longueur'])
        self.Interest_point_largeur_2 = float(Parameters['point_interet_2_largeur'])
        self.Interest_point_longueur_2 = float(Parameters['point_interet_2_longueur'])
        self.Interest_point_largeur_3 = float(Parameters['point_interet_3_largeur'])
        self.Interest_point_longueur_3 = float(Parameters['point_interet_3_longueur'])
        # Automatic time step
        if Parameters['time_step'] == 'auto':
            self.time_step = 1/(self.conductivite_thermique_plaque/0.2/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)**2)
        else:
            self.time_step = float(Parameters['time_step'])

        # Convection Q̇ = h•A•ΔT
        # Conduction Q̇ = κ•A•ΔT/l
        self.Temperature_Ambiante = self.Temperature_Ambiante_C + 273.15 # C
        self.Constante_plaque = self.conductivite_thermique_plaque*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)**2
        self.Constante_Air_top_bot = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.epaisseur_plaque_mm/1000)
        self.Constante_Air_side = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)

        self.capacite_thermique_Actu
        self.masse_volumique_actu
        
        self.Constante_Air_top_bot_Actu = self.convection_actuateur*self.time_step/self.masse_volumique_actu/self.capacite_thermique_Actu/(self.epaisseur_actu_mm/1000)
        self.Constante_Air_side_Actu = self.convection_actuateur*self.time_step/self.masse_volumique_actu/self.capacite_thermique_Actu/(self.mm_par_element/1000)
        
        # print(f'C Plaque {self.Constante_plaque}') 
        # print(f'C Air bot_top {self.Constante_Air_top_bot}')
        # print(f'C Air sides {self.Constante_Air_side}')

        # Temp Initial 
        self.Geometry_Matrix = np.full((int(self.plaque_largeur/self.mm_par_element), int(self.plaque_longueur/self.mm_par_element)), float(self.Temperature_Ambiante))
        self.Geometry_Actu = np.full((int(self.largeur_actu/self.mm_par_element), int(self.largeur_actu/self.mm_par_element)), float(self.Temperature_Ambiante))

        self.Cooling = False
        if self.courant_actuateur < 0:
            self.Cooling = True



    def iterate(self):
        padded_matrix = np.pad(self.Geometry_Matrix, ((1, 1), (1, 1)), mode='constant', constant_values=self.Temperature_Ambiante)
        # Initialize delta_T_voisin_plaque with zeros
        delta_T_voisin_plaque = np.zeros_like(self.Geometry_Matrix)
        # Temperature des elements interieurs
        delta_T_voisin_plaque += padded_matrix[1:-1, :-2] - self.Geometry_Matrix  # Left neighbor
        delta_T_voisin_plaque += padded_matrix[1:-1, 2:] - self.Geometry_Matrix   # Right neighbor
        delta_T_voisin_plaque += padded_matrix[:-2, 1:-1] - self.Geometry_Matrix  # Top neighbor
        delta_T_voisin_plaque += padded_matrix[2:, 1:-1] - self.Geometry_Matrix   # Bottom neighbor
        # Left cote
        delta_T_voisin_plaque[:, 0] -= padded_matrix[1:-1, 0] - self.Geometry_Matrix[:, 0]
        # Right cote
        delta_T_voisin_plaque[:, -1] -= padded_matrix[1:-1, -1] - self.Geometry_Matrix[:, -1]
        # Top cote
        delta_T_voisin_plaque[0, :] -= padded_matrix[0, 1:-1] - self.Geometry_Matrix[0, :]
        # Bottom cote 
        delta_T_voisin_plaque[-1, :] -= padded_matrix[-1, 1:-1] - self.Geometry_Matrix[-1, :]
        # Somme des delta temp avec lair TOP BOT
        delta_T_voisin_air_top_bot = 2 * (self.Temperature_Ambiante - self.Geometry_Matrix)
        # Somme des delta temp avec lair sides
        delta_T_voisin_air_side = np.zeros_like(self.Geometry_Matrix)
        delta_T_voisin_air_side[:, 0] += self.Temperature_Ambiante - self.Geometry_Matrix[:, 0]
        delta_T_voisin_air_side[:, -1] += self.Temperature_Ambiante - self.Geometry_Matrix[:, -1]
        delta_T_voisin_air_side[0, :] += self.Temperature_Ambiante - self.Geometry_Matrix[0, :]
        delta_T_voisin_air_side[-1, :] += self.Temperature_Ambiante - self.Geometry_Matrix[-1, :]
        # Update the temperature matrix
        self.Geometry_Matrix += self.Constante_plaque * delta_T_voisin_plaque + self.Constante_Air_top_bot * delta_T_voisin_air_top_bot + self.Constante_Air_side * delta_T_voisin_air_side

        # # Iterate Actuateur
        # # Initialize delta_T_voisin_Actu with zeros
        # delta_T_voisin_Actu = np.zeros_like(self.Geometry_Actu)
        # # Somme des delta temp avec lair TOP BOT
        # delta_T_voisin_air_top_bot = 2 * (self.Temperature_Ambiante - self.Geometry_Actu)
        # # Somme des delta temp avec lair sides
        # delta_T_voisin_air_side = np.zeros_like(self.Geometry_Actu)
        # delta_T_voisin_air_side[:, 0] += self.Temperature_Ambiante - self.Geometry_Actu[:, 0]
        # delta_T_voisin_air_side[:, -1] += self.Temperature_Ambiante - self.Geometry_Actu[:, -1]
        # delta_T_voisin_air_side[0, :] += self.Temperature_Ambiante - self.Geometry_Actu[0, :]
        # delta_T_voisin_air_side[-1, :] += self.Temperature_Ambiante - self.Geometry_Actu[-1, :]
        # # Update the temperature matrix
        # self.Geometry_Actu += self.Constante_Air_top_bot_Actu * delta_T_voisin_air_top_bot + self.Constante_Air_side_Actu * delta_T_voisin_air_side

    def Heat_Pumped(self, Th, Delta_T, Courant):
        a=1.21161+0.02535*Th
        b=-0.04109-0.00298*Th
        c=35.223+0.07174*Th
        d=-7.2969+0.00174*Th
        e=0.50796-0.000739*Th
        Power_at_0 = a*Courant+b*Courant**2
        Delta_T_at_0 = c*Courant+d*Courant**2+e*Courant**3
        Power = Power_at_0*(1-Delta_T/Delta_T_at_0)
        self.count_power_queue =  self.count_power_queue+1
        if self.count_power_queue % 1000 == 0:
            print(f'{Power} W pumped by actuator' )
        return Power
    
    def actuateur_influence(self):
        
        pos_y_actu = max(0,min(len(self.Geometry_Matrix)-1, int(self.position_largeur_actuateur/self.mm_par_element)))
        pos_x_actu = max(0,min(len(self.Geometry_Matrix[0])-1, int(self.position_longueur_actuateur/self.mm_par_element)))
        largeur_actu_in_element = self.largeur_actu/self.mm_par_element
        longueur_actu_in_element = self.longueur_actu/self.mm_par_element
        half_larg = int(largeur_actu_in_element/2)
        half_lon = int(longueur_actu_in_element/2)
        # Only heat 1 element if actu is smaller than 1 element
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

        # Calcul de la chaleur transmise par l'actuateur
        if self.Cooling:
            Th = np.average(self.Geometry_Actu)
            Delta_T = Th - np.average(self.Geometry_Matrix[y_range, x_range])
        else:
            Th = np.average(self.Geometry_Matrix[y_range, x_range])
            Delta_T = Th - np.average(self.Geometry_Actu)
            # print(np.average(self.Geometry_Actu))
            # print(self.Temperature_Ambiante)

        Th_C = Th-273.15
        if self.Cooling:
            Chaleur_en_jeu = -self.Heat_Pumped(Th_C, Delta_T, -self.courant_actuateur)*self.time_step*self.couple_actuateur
        else:
            Chaleur_en_jeu = self.Heat_Pumped(Th_C, Delta_T, self.courant_actuateur)*self.time_step*self.couple_actuateur

        # print(f'Th : {Th}')
        # print(f'Delta_T : {Delta_T}')
        # print(f'Heat Pumped : {Chaleur_en_jeu/self.time_step}W')
               
        Chaleur_par_element = Chaleur_en_jeu /(largeur_actu_in_element*largeur_actu_in_element)
        delta_temp = Chaleur_par_element / (self.epaisseur_plaque_mm /1000 * (self.mm_par_element/1000)**2 * self.masse_volumique_plaque) / self.capacite_thermique_plaque
                
        self.Geometry_Matrix[y_range, x_range] += delta_temp

        # Compute convection et chaleur ajoute dans lactu
        delta_T_voisin_air_top_bot = 2 * (self.Temperature_Ambiante - self.Geometry_Actu)
        delta_T_voisin_air_side = np.zeros_like(self.Geometry_Actu)
        delta_T_voisin_air_side[:, 0] += self.Temperature_Ambiante - self.Geometry_Actu[:, 0]
        delta_T_voisin_air_side[:, -1] += self.Temperature_Ambiante - self.Geometry_Actu[:, -1]
        delta_T_voisin_air_side[0, :] += self.Temperature_Ambiante - self.Geometry_Actu[0, :]
        delta_T_voisin_air_side[-1, :] += self.Temperature_Ambiante - self.Geometry_Actu[-1, :]
        self.Geometry_Actu += self.Constante_Air_top_bot_Actu * delta_T_voisin_air_top_bot + self.Constante_Air_side_Actu * delta_T_voisin_air_side - delta_temp
        
    def Launch_Simu(self, display_animation=True, save_csv = "Aucune Sélection", Debug=False):
        self.count_power_queue = 0
        simu_start_time = time.time()
        dt_object = datetime.fromtimestamp(simu_start_time)
        time_stamp = dt_object.strftime("%Y-%m-%d %H:%M:%S.%f")  # With microseconds
        time_stamp = time_stamp.replace(' ', '_').replace(':','-').replace('.','-')
        
        iterations_number = max(1,int(self.simu_duration / self.time_step))

        Interest_point_y_1 = int(self.Interest_point_largeur_1 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_1 = int(self.Interest_point_longueur_1 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_y_2 = int(self.Interest_point_largeur_2 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_2 = int(self.Interest_point_longueur_2 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_y_3 = int(self.Interest_point_largeur_3 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_3 = int(self.Interest_point_longueur_3 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        self.Interest_point_data_C_1 = []
        self.Interest_point_data_C_2 = []
        self.Interest_point_data_C_3 = []
        # Interest Point at 0
        self.Interest_point_data_C_1.append(self.Geometry_Matrix[Interest_point_y_1][Interest_point_x_1] - 273.15)
        self.Interest_point_data_C_2.append(self.Geometry_Matrix[Interest_point_y_2][Interest_point_x_2] - 273.15)
        self.Interest_point_data_C_3.append(self.Geometry_Matrix[Interest_point_y_3][Interest_point_x_3] - 273.15)
      
        display_frame_step = max(1,int(iterations_number/self.simu_duration))
        time_data = np.append(np.arange(0, iterations_number*self.time_step, display_frame_step*self.time_step),iterations_number*self.time_step)


        if display_animation:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))  # Two side-by-side plots
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
            ax1.scatter(Interest_point_x_1, Interest_point_y_1, color="blue", s=200, marker='x')
            ax1.scatter(Interest_point_x_2, Interest_point_y_2, color="green", s=200, marker='x')
            ax1.scatter(Interest_point_x_3, Interest_point_y_3, color="black", s=200, marker='x')

            # Set x-axis ticks en mm
            x_ticks = np.linspace(-0.5, len(self.Geometry_Matrix[0])-0.5, 5)
            x_labels = np.linspace(0, self.plaque_longueur, 5).astype(int)
            ax1.set_xticks(x_ticks)
            ax1.set_xticklabels([f"{val} mm" for val in x_labels])
            # Set y-axis ticks en mm
            y_ticks = np.linspace(-0.5, len(self.Geometry_Matrix)-0.5, 5)
            y_labels = np.linspace(0, self.plaque_largeur, 5).astype(int)
            ax1.set_yticks(y_ticks)
            ax1.set_yticklabels([f"{val} mm" for val in y_labels])
            ax1.invert_yaxis()
            
            thermi_1, = ax2.plot([], [], 'b-', label = 'Thermistance 1')
            thermi_2, = ax2.plot([], [], 'green', label = 'Thermistance 2')
            thermi_3, = ax2.plot([], [], 'black', label = 'Thermistance Laser')
            
            
            ax2.set_xlim(0, iterations_number * self.time_step)
            x_ticks = np.linspace(0, iterations_number * self.time_step, num=8)  # 5 ticks, including the last one
            ax2.set_xticks(x_ticks)
            
            ax2.set_ylim(-10, 100)  # Adjust Y-limits
            ax2.grid(True)
            ax2.set_xlabel("Temps (s)")
            ax2.set_ylabel("Temperature (°C)")
            ax2.set_title("Temperature des thermistances")
            ax2.legend(loc='upper left')

        def update(i):
            for j in range(display_frame_step): # Compute le nombre diteration pour faire 1 display_frame_step
                self.actuateur_influence()
                self.iterate()
                self.iteration_counter += 1
            if save_csv != "Aucune Sélection": #Sauve a chaque secondes de simu
                output_dir = save_csv
                os.makedirs(output_dir, exist_ok=True)
                df = pd.DataFrame(self.Geometry_Matrix)
                time_in_simulation = self.iteration_counter * self.time_step
                df['Time (s)'] = time_in_simulation
                filename = os.path.join(output_dir, f"{time_stamp}_Simulation_Temp.csv")
                if not os.path.exists(filename):
                    df.to_csv(filename, index=False, header=True, mode='w')
                else:
                    df.to_csv(filename, index=False, header=False, mode='a')
                
            self.Interest_point_data_C_1.append(self.Geometry_Matrix[Interest_point_y_1][Interest_point_x_1] - 273.15)
            self.Interest_point_data_C_2.append(self.Geometry_Matrix[Interest_point_y_2][Interest_point_x_2] - 273.15)
            self.Interest_point_data_C_3.append(self.Geometry_Matrix[Interest_point_y_3][Interest_point_x_3] - 273.15)
            if display_animation:
                # Display result
                max_value_temp = np.max(self.Geometry_Matrix)
                # Set the lowest temp on first iteration
                if not hasattr(self, 'min_value_temp'):
                    self.min_value_temp = np.min(self.Geometry_Matrix)
                img.set_data(self.Geometry_Matrix - 273.15)
                img.set_clim(self.min_value_temp  - 273.15, max_value_temp - 273.15)
                ax1.set_title(f'Température de la plaque à T = {round(self.iteration_counter * self.time_step, 4)} secondes')
            # Message if last iteration
            if self.iteration_counter >= iterations_number:
                simu_elapsed_time = time.time() - simu_start_time
                hours, remainder = divmod(simu_elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f'Simulation Complete!\n{self.iteration_counter} iterations computed in {int(hours):02}h {int(minutes):02}m {int(seconds):02}s')
            self.actual_time_data = time_data[:len(self.Interest_point_data_C_1)]
            if display_animation:
                thermi_1.set_data(self.actual_time_data, self.Interest_point_data_C_1)
                thermi_2.set_data(self.actual_time_data, self.Interest_point_data_C_2) 
                thermi_3.set_data(self.actual_time_data, self.Interest_point_data_C_3)
                # Get data to set the Y lim
                y1 = thermi_1.get_ydata()
                y2 = thermi_2.get_ydata()
                y3 = thermi_3.get_ydata()
                # FOllow the min and max
                T_max = np.max([np.max(y1), np.max(y2), np.max(y3)]) + 5
                T_min = np.min([np.min(y1), np.min(y2), np.min(y3)]) - 5
                ax2.set_ylim(T_min, T_max)  # Adjust Y-limits
                return img, thermi_1, thermi_2, thermi_3

        if display_animation:  
            self.iteration_counter = 0
            ani = animation.FuncAnimation(fig, update, frames=range(0, iterations_number - display_frame_step, display_frame_step), interval=0, blit=False, repeat=False, cache_frame_data=False)            
            plt.show()
        else:
            self.iteration_counter = 0
            for _ in range(0, iterations_number, display_frame_step):
                update(_)