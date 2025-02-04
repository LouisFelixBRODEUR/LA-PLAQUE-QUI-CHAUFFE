import numpy as np
import matplotlib.pyplot as plt
import time
import copy
import matplotlib.animation as animation

class Plaque:
    def __init__(self, Parameters):
        self.plaque_largeur = float(Parameters['plaque_largeur'])
        self.plaque_longueur = float(Parameters['plaque_longueur']) 
        self.mm_par_element = float(Parameters['mm_par_element'])
        self.Temperature_Ambiante_C = float(Parameters['Temperature_Ambiante_C'])
        self.largeur_actu = float(Parameters['largeur_actu']) 
        self.longueur_actu = float(Parameters['longueur_actu']) 
        self.position_longueur_actuateur = float(Parameters['position_longueur_actuateur']) 
        self.position_largeur_actuateur = float(Parameters['position_largeur_actuateur']) 
        self.puissance_actuateur = float(Parameters['puissance_actuateur'])
        self.masse_volumique_plaque = float(Parameters['masse_volumique_plaque'])
        self.epaisseur_plaque_mm = float(Parameters['epaisseur_plaque_mm']) 
        self.capacite_thermique_plaque = float(Parameters['capacite_thermique_plaque'])
        self.conductivite_thermique_plaque = float(Parameters['conductivite_thermique_plaque'])
        self.coefficient_convection = float(Parameters['coefficient_convection']) 
        self.time_step = float(Parameters['time_step'])
        self.simu_duration = float(Parameters['simu_duration'])
        self.animation_length = int(Parameters['animation_length'])
        self.Interest_point_largeur_1 = float(Parameters['point_interet_1_largeur'])
        self.Interest_point_longueur_1 = float(Parameters['point_interet_1_longueur'])
        self.Interest_point_largeur_2 = float(Parameters['point_interet_2_largeur'])
        self.Interest_point_longueur_2 = float(Parameters['point_interet_2_longueur'])
        self.Interest_point_largeur_3 = float(Parameters['point_interet_3_largeur'])
        self.Interest_point_longueur_3 = float(Parameters['point_interet_3_longueur'])

        self.Temperature_Ambiante = self.Temperature_Ambiante_C + 273.15 # C
        self.Constante_plaque = self.conductivite_thermique_plaque*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)**2
        self.Constante_Air_top_bot = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.epaisseur_plaque_mm/1000)
        self.Constante_Air_side = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)

        print(f'C Plaque {self.Constante_plaque}') 
        # print(f'C Air bot_top {self.Constante_Air_top_bot}')
        # print(f'C Air sides {self.Constante_Air_side}')

        # Temp Initial 
        self.Geometry_Matrix = np.full((int(self.plaque_largeur/self.mm_par_element), int(self.plaque_longueur/self.mm_par_element)), float(self.Temperature_Ambiante))

    def iterate(self):
        Next_Geo_Mat = np.zeros_like(self.Geometry_Matrix)
        for y in range(len(self.Geometry_Matrix)):
            for x in range(len(self.Geometry_Matrix[0])):#Pour chaque Élément
                Somme_delta_T_Voisin_Plaque = 0
                Somme_delta_T_Voisin_Air_top = 0
                Somme_delta_T_Voisin_Air_side = 0
                Temp_Element = self.Geometry_Matrix[y][x]
                # Si element sur une largeur, Somme_delta_T_Voisin_Air+=1
                if x == 0:
                    Somme_delta_T_Voisin_Air_side += self.Temperature_Ambiante - Temp_Element
                    Somme_delta_T_Voisin_Plaque += self.Geometry_Matrix[y][x+1] - Temp_Element
                elif x == len(self.Geometry_Matrix[0])-1:
                    Somme_delta_T_Voisin_Air_side += self.Temperature_Ambiante - Temp_Element
                    Somme_delta_T_Voisin_Plaque += self.Geometry_Matrix[y][x-1] - Temp_Element
                else: # Touche a aucun cote de largeur
                    Somme_delta_T_Voisin_Plaque += self.Geometry_Matrix[y][x-1] + self.Geometry_Matrix[y][x+1] - 2*Temp_Element
                # Si plaque sur une longeur, Somme_delta_T_Voisin_Air+=1
                if y == 0:
                    Somme_delta_T_Voisin_Air_side += self.Temperature_Ambiante - Temp_Element
                    Somme_delta_T_Voisin_Plaque += self.Geometry_Matrix[y+1][x] - Temp_Element
                elif y == len(self.Geometry_Matrix)-1:
                    Somme_delta_T_Voisin_Air_side += self.Temperature_Ambiante - Temp_Element
                    Somme_delta_T_Voisin_Plaque += self.Geometry_Matrix[y-1][x] - Temp_Element
                else: # Touche a aucun cote de largeur
                    Somme_delta_T_Voisin_Plaque += self.Geometry_Matrix[y+1][x] + self.Geometry_Matrix[y-1][x] - 2*Temp_Element
                # Somme_delta_T_Voisin_Air+=2 car tout les element ont de lair dessux et en dessous
                Somme_delta_T_Voisin_Air_top += 2*(self.Temperature_Ambiante - Temp_Element)
                Next_Temp_Element = Temp_Element + self.Constante_plaque*(Somme_delta_T_Voisin_Plaque) + self.Constante_Air_top_bot*(Somme_delta_T_Voisin_Air_top) + self.Constante_Air_side*(Somme_delta_T_Voisin_Air_side)
                Next_Geo_Mat[y][x] = Next_Temp_Element
        self.Geometry_Matrix = Next_Geo_Mat

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

        Chaleur_en_jeu = self.puissance_actuateur*self.time_step
        Chaleur_par_element = Chaleur_en_jeu /(largeur_actu_in_element*largeur_actu_in_element)
        delta_temp = Chaleur_par_element / (self.epaisseur_plaque_mm /1000 * (self.mm_par_element/1000)**2 * self.masse_volumique_plaque) / self.capacite_thermique_plaque

        for y in range(pos_y_actu-half_larg, pos_y_actu+half_larg+Top_range_larg):
            for x in range(pos_x_actu-half_lon, pos_x_actu+half_lon+Top_range_lon):
                self.Geometry_Matrix[y][x] += delta_temp
        
    def Launch_Simu_mpl_ani(self, display_animation=True, save_csv = False, save_MP4 = False):
        simu_start_time = time.time()
        iterations_number = max(1,int(self.simu_duration / self.time_step))

        Interest_point_y_1 = int(self.Interest_point_largeur_1 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_1 = int(self.Interest_point_longueur_1 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_y_2 = int(self.Interest_point_largeur_2 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_2 = int(self.Interest_point_longueur_2 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_y_3 = int(self.Interest_point_largeur_3 / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x_3 = int(self.Interest_point_longueur_3 / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_data_C_1 = []
        Interest_point_data_C_2 = []
        Interest_point_data_C_3 = []

        # fig, ax = plt.subplots(1,1)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))  # Two side-by-side plots

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
        time_data = np.arange(0, iterations_number*self.time_step, self.time_step)
        
        ax2.set_xlim(0, iterations_number * self.time_step)
        ax2.set_ylim(-10, 100)  # Adjust Y-limits
        ax2.grid(True)
        ax2.set_xlabel("Temps (s)")
        ax2.set_ylabel("Temperature (°C)")
        ax2.set_title("Temperature des thermistances")
        ax2.legend()
                
        display_frame_step = max(1,int(iterations_number/self.animation_length))

        
        def update(i):
            """ Compute all iterations but display only 100 frames """
            # Compute required number of iterations
            for j in range(display_frame_step):
                self.actuateur_influence()
                self.iterate()
                Interest_point_data_C_1.append(self.Geometry_Matrix[Interest_point_y_1][Interest_point_x_1] - 273.15)
                Interest_point_data_C_2.append(self.Geometry_Matrix[Interest_point_y_2][Interest_point_x_2] - 273.15)
                Interest_point_data_C_3.append(self.Geometry_Matrix[Interest_point_y_3][Interest_point_x_3] - 273.15)
                self.iteration_counter += 1
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
                
            # Update thermi plot
            # if self.iteration_counter <= iterations_number:
            thermi_1.set_data(time_data[:self.iteration_counter], Interest_point_data_C_1)
            thermi_2.set_data(time_data[:self.iteration_counter], Interest_point_data_C_2) 
            thermi_3.set_data(time_data[:self.iteration_counter], Interest_point_data_C_3)
            # Get data to set the Y lim
            y1 = thermi_1.get_ydata()
            y2 = thermi_2.get_ydata()
            y3 = thermi_3.get_ydata()
            T_max = np.max([np.max(y1), np.max(y2), np.max(y3)])
            T_min = np.min([np.min(y1), np.min(y2), np.min(y3)])
            if T_max > 80:
                T_max += 20
            else:
                T_max = 100
            if T_min < 10:
                T_min -= 20
            else:
                T_min = -10
            ax2.set_ylim(T_min, T_max)  # Adjust Y-limits

            
            # return img, title
            return img, thermi_1, thermi_2, thermi_3

        if display_animation:
            self.iteration_counter = 0
            ani = animation.FuncAnimation(fig, update, frames=range(0,iterations_number-display_frame_step, display_frame_step), interval=0, blit=False, repeat=False, cache_frame_data=False)
            plt.show()


        # Save as MP4 if required
        if save_MP4:
            ani.save("simulation.mp4", writer="ffmpeg")