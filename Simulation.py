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
        self.animation_lenght = int(Parameters['animation_lenght'])
        self.Interest_point_largeur = float(Parameters['point_interet_largeur'])
        self.Interest_point_longueur = float(Parameters['point_interet_longueur'])

        self.Temperature_Ambiante = self.Temperature_Ambiante_C + 273.15 # C
        self.Constante_plaque = self.conductivite_thermique_plaque*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)**2
        self.Constante_Air_top_bot = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.epaisseur_plaque_mm/1000)
        self.Constante_Air_side = self.coefficient_convection*self.time_step/self.masse_volumique_plaque/self.capacite_thermique_plaque/(self.mm_par_element/1000)

        print(f'C Plaque {self.Constante_plaque}') 
        print(f'C Air bot_top {self.Constante_Air_top_bot}')
        print(f'C Air sides {self.Constante_Air_side}')

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
        pos_y_actu = int(self.position_largeur_actuateur/self.mm_par_element)
        pos_x_actu = int(self.position_longueur_actuateur/self.mm_par_element)
        largeur_actu_in_element = self.largeur_actu/self.mm_par_element
        longueur_actu_in_element = self.longueur_actu/self.mm_par_element
        half_larg = int(largeur_actu_in_element/2)
        half_lon = int(longueur_actu_in_element/2)

        Chaleur_en_jeu = self.puissance_actuateur*self.time_step
        Chaleur_par_element = Chaleur_en_jeu /(largeur_actu_in_element)/(largeur_actu_in_element)

        delta_temp = Chaleur_par_element / (self.epaisseur_plaque_mm /1000 * (self.mm_par_element/1000)**2 * self.masse_volumique_plaque) / self.capacite_thermique_plaque
        for y in range(pos_y_actu-half_lon, pos_y_actu+half_lon):
            for x in range(pos_x_actu-half_larg, pos_x_actu+half_larg):
                self.Geometry_Matrix[y][x] += delta_temp

    # def Launch_Simu(self, animation=True, graph = True, save_csv = False, save_MP4 = True):
    #     simu_start_time = time.time()
    #     iterations_number = int(self.simu_duration/self.time_step)

    #     Interest_point_y = int(self.Interest_point_largeur/self.plaque_largeur*len(self.Geometry_Matrix))
    #     Interest_point_x = int(self.Interest_point_longueur/self.plaque_longueur*len(self.Geometry_Matrix[0]))
    #     Interest_point_data_C = []

    #     loading_queue = np.linspace(10,100,10)
    #     display_queue_time = np.linspace(0, self.simu_duration, self.animation_lenght)
    #     for i in range(iterations_number):
    #         if animation:
    #             if (i+1)*self.time_step > display_queue_time[0]:
    #                     display_queue_time = display_queue_time[1:]
    #                     max_value_temp = np.max(self.Geometry_Matrix)
    #                     min_value_temp = np.min(self.Geometry_Matrix)
    #                     plt.rcParams['toolbar'] = 'None'  # Disable the toolbar
    #                     # img = plt.imshow(self.Geometry_Matrix-273.15, cmap='coolwarm', interpolation='nearest', vmin=min_value_temp-273.15, vmax=max_value_temp-273.15)
    #                     img = plt.imshow(self.Geometry_Matrix-273.15, cmap='jet', interpolation='bicubic', vmin=min_value_temp-273.15, vmax=max_value_temp-273.15)
    #                     cbar = plt.colorbar(img)
    #                     cbar.set_label('Temperature (°C)')
    #                     plt.title(f'Temperature Distribution at {round((i*self.time_step), 4)} seconds')
    #                     plt.pause(0.1)
    #         self.actuateur_influence()
    #         self.iterate()
    #         Interest_point_data_C.append(self.Geometry_Matrix[Interest_point_y][Interest_point_x] - 273.15)
    #         if round(i/iterations_number*100,3) > loading_queue[0]:
    #             print(f'{round(i*self.time_step, 0)} seconds computed, {loading_queue[0]}% Completed')
    #             loading_queue = loading_queue[1:]
    #         if i == iterations_number-1:
    #             print(f'{round(i*self.time_step, 0)} seconds computed, 100% Completed')
    #         if len(display_queue_time) != 0:
    #             plt.clf()
        
    #     simu_elapsed_time = time.time() - simu_start_time
    #     hours, remainder = divmod(simu_elapsed_time, 3600)
    #     minutes, seconds = divmod(remainder, 60)
    #     print(f'Simulation took {int(hours):02}:{int(minutes):02}:{int(seconds):02} to compute')
        

    #     # Interest Point
    #     if graph:
    #         time_data = np.arange(0, iterations_number*self.time_step, self.time_step)
    #         plt.plot(time_data, Interest_point_data_C)
    #         plt.grid(True)
    #         plt.xlabel("Temps (s)")
    #         plt.ylabel("Temperature (°C)")
    #         plt.title(f"Évolution de la température au point d'intérêt\nLongueur:{self.Interest_point_longueur}mm & Largeur:{self.Interest_point_largeur}mm")
    #         plt.show()
            
    def Launch_Simu_mpl_ani(self, display_animation=True, save_csv = False, save_MP4 = False):
        simu_start_time = time.time()
        iterations_number = int(self.simu_duration / self.time_step)

        Interest_point_y = int(self.Interest_point_largeur / self.plaque_largeur * len(self.Geometry_Matrix))
        Interest_point_x = int(self.Interest_point_longueur / self.plaque_longueur * len(self.Geometry_Matrix[0]))
        Interest_point_data_C = []

        # fig, ax = plt.subplots(1,1)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))  # Two side-by-side plots
        
        img = ax1.imshow(self.Geometry_Matrix - 273.15, cmap='jet', interpolation='bicubic')
        cbar = plt.colorbar(img)
        cbar.set_label('Temperature (°C)')
        title = ax1.set_title("Temperature Distribution")
        
        line, = ax2.plot([], [], 'r-')
        time_data = np.arange(0, iterations_number*self.time_step, self.time_step)
        # plt.plot(time_data, Interest_point_data_C)
        
        ax2.set_xlim(0, iterations_number * self.time_step)
        ax2.set_ylim(-10, 100)  # Adjust Y-limits
        ax2.grid(True)
        ax2.set_xlabel("Temps (s)")
        ax2.set_ylabel("Temperature (°C)")
        ax2.set_title("Temperature des thermistances")
                
        display_frame_step = int(iterations_number/self.animation_lenght)
        
        def update(i):
            """ Compute all iterations but display only 100 frames """
            # Compute required number of iterations
            for i in range(display_frame_step):
                self.actuateur_influence()
                self.iterate()
                Interest_point_data_C.append(self.Geometry_Matrix[Interest_point_y][Interest_point_x] - 273.15)
                self.iteration_counter += 1
            # Display result
            max_value_temp = np.max(self.Geometry_Matrix)
            # Set the lowest temp on first iteration
            if not hasattr(self, 'min_value_temp'):
                self.min_value_temp = np.min(self.Geometry_Matrix)
            img.set_data(self.Geometry_Matrix - 273.15)
            img.set_clim(self.min_value_temp  - 273.15, max_value_temp - 273.15)
            ax1.set_title(f'Temperature Distribution at {round(self.iteration_counter * self.time_step, 4)} seconds')
            # title.set_text(f'Temperature Distribution at {round(self.iteration_counter * self.time_step, 4)} seconds')
            # Message if last iteration
            if self.iteration_counter == iterations_number:
                simu_elapsed_time = time.time() - simu_start_time
                hours, remainder = divmod(simu_elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                print(f'Simulation Complete!\n{self.iteration_counter} iterations computed in {int(hours):02}h {int(minutes):02}m {int(seconds):02}s')
                
            # Update thermi plot
            line.set_data(time_data[:self.iteration_counter], Interest_point_data_C) 
            
            # return img, title
            return img, line

        if display_animation:
            self.iteration_counter = 0
            ani = animation.FuncAnimation(fig, update, frames=range(0,iterations_number, display_frame_step), interval=0, blit=False, repeat=False, cache_frame_data=False)
            plt.show()


        # Save as MP4 if required
        if save_MP4:
            ani.save("simulation.mp4", writer="ffmpeg")