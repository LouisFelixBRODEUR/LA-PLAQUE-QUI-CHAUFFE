import numpy as np
import matplotlib.pyplot as plt
import time
import copy

def actuateur_influence(Geo_Mat, Parameters):
    mm_par_element = float(Parameters['mm_par_element'])
    largeur_actu = float(Parameters['largeur_actu'])
    longueur_actu = float(Parameters['longueur_actu'])
    plaque_largeur = float(Parameters['plaque_largeur'])
    position_largeur_actuateur = plaque_largeur - float(Parameters['position_largeur_actuateur'])
    position_longueur_actuateur = float(Parameters['position_longueur_actuateur'])
    masse_volumique_plaque = float(Parameters['masse_volumique_plaque'])
    capacite_thermique_plaque = float(Parameters['capacite_thermique_plaque'])
    puissance_actu = float(Parameters['puissance_actuateur'])
    time_step = float(Parameters['time_step'])
    epaisseur_plaque = float(Parameters['epaisseur_plaque_mm'])

    pos_y_actu = int(position_largeur_actuateur/mm_par_element)
    pos_x_actu = int(position_longueur_actuateur/mm_par_element)
    largeur_actu_in_element = largeur_actu/mm_par_element
    longueur_actu_in_element = longueur_actu/mm_par_element
    half_larg = int(largeur_actu_in_element/2)
    half_lon = int(longueur_actu_in_element/2)

    Chaleur_en_jeu = puissance_actu*time_step
    Chaleur_par_element = Chaleur_en_jeu /(largeur_actu_in_element)/(largeur_actu_in_element)

    delta_temp = Chaleur_par_element / (epaisseur_plaque /1000 * (mm_par_element/1000)**2 * masse_volumique_plaque) / capacite_thermique_plaque
    for y in range(pos_y_actu-half_lon, pos_y_actu+half_lon):
        for x in range(pos_x_actu-half_larg, pos_x_actu+half_larg):
            Geo_Mat[y][x] += delta_temp
    return Geo_Mat


# Nouvelle valeur = Moyenne des voisin
def iterate(Geo_Mat, Cst_Plq, Cst_Air_top, Cst_Air_side, Temp_Ambi):
    Next_Geo_Mat = np.zeros_like(Geo_Mat)
    for y in range(len(Geo_Mat)):
        for x in range(len(Geo_Mat[0])):#Pour chaque Élément
            Somme_delta_T_Voisin_Plaque = 0
            Somme_delta_T_Voisin_Air_top = 0
            Somme_delta_T_Voisin_Air_side = 0
            Temp_Element = Geo_Mat[y][x]
            # Si element sur une largeur, Somme_delta_T_Voisin_Air+=1
            if x == 0:
                Somme_delta_T_Voisin_Air_side += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y][x+1] - Temp_Element
            elif x == len(Geo_Mat[0])-1:
                Somme_delta_T_Voisin_Air_side += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y][x-1] - Temp_Element
            else: # Touche a aucun cote de largeur
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y][x-1] + Geo_Mat[y][x+1] - 2*Temp_Element

            # Si plaque sur une longeur, Somme_delta_T_Voisin_Air+=1
            if y == 0:
                Somme_delta_T_Voisin_Air_side += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y+1][x] - Temp_Element
            elif y == len(Geo_Mat)-1:
                Somme_delta_T_Voisin_Air_side += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y-1][x] - Temp_Element
            else: # Touche a aucun cote de largeur
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y+1][x] + Geo_Mat[y-1][x] - 2*Temp_Element

            # Somme_delta_T_Voisin_Air+=2 car tout les element ont de lair dessux et en dessous
            Somme_delta_T_Voisin_Air_top += 2*(Temp_Ambi - Temp_Element)

            Next_Temp_Element = Temp_Element + Cst_Plq * (Somme_delta_T_Voisin_Plaque) + Cst_Air_top * (Somme_delta_T_Voisin_Air_top) + Cst_Air_side * (Somme_delta_T_Voisin_Air_side)
            Next_Geo_Mat[y][x] = Next_Temp_Element

    return Next_Geo_Mat

def Launch_Simu(Parameters):
    plaque_largeur = float(Parameters['plaque_largeur'])
    plaque_longueur = float(Parameters['plaque_longueur']) 
    mm_par_element = float(Parameters['mm_par_element'])
    Temperature_Ambiante_C = float(Parameters['Temperature_Ambiante_C'])
    largeur_actu = float(Parameters['largeur_actu']) 
    longueur_actu = float(Parameters['longueur_actu']) 
    position_longueur_actuateur = float(Parameters['position_longueur_actuateur']) 
    position_largeur_actuateur = float(Parameters['position_largeur_actuateur']) 
    puissance_actuateur = float(Parameters['puissance_actuateur'])
    masse_volumique_plaque = float(Parameters['masse_volumique_plaque'])
    epaisseur_plaque_mm = float(Parameters['epaisseur_plaque_mm']) 
    capacite_thermique_plaque = float(Parameters['capacite_thermique_plaque'])
    conductivite_thermique_plaque = float(Parameters['conductivite_thermique_plaque'])
    coefficient_convection = float(Parameters['coefficient_convection']) 
    time_step = float(Parameters['time_step'])
    simu_duration = float(Parameters['simu_duration'])
    animation_lenght = int(Parameters['animation_lenght'])
    Interest_point_largeur = float(Parameters['point_interet_largeur'])
    Interest_point_longueur = float(Parameters['point_interet_longueur'])

    Temperature_Ambiante = Temperature_Ambiante_C + 273.15 # C
    Constante_plaque = conductivite_thermique_plaque*time_step/masse_volumique_plaque/capacite_thermique_plaque/(mm_par_element/1000)**2
    Constante_Air_top_bot = coefficient_convection*time_step/masse_volumique_plaque/capacite_thermique_plaque/(epaisseur_plaque_mm/1000)
    Constante_Air_side = coefficient_convection*time_step/masse_volumique_plaque/capacite_thermique_plaque/(mm_par_element/1000)

    # print(f'C Plaque {Constante_plaque}') 
    # print(f'C Air bot_top {Constante_Air_top_bot}')
    # print(f'C Air sides {Constante_Air_side}')

    # Temp Initial 
    Geometry_Matrix = np.full((int(plaque_largeur/mm_par_element), int(plaque_longueur/mm_par_element)), float(Temperature_Ambiante))

    # Processus iteratif de moyennage avec les voisins
    Temp_matrix_list = []
    iterations = int(simu_duration/time_step)

    Temp_matrix_list.append(Geometry_Matrix.copy())

    loading_queue = np.linspace(10,100,10)
    for i in range(iterations):
        Geometry_Matrix = actuateur_influence(Geometry_Matrix, Parameters)
        Geometry_Matrix = iterate(Geometry_Matrix, Constante_plaque, Constante_Air_top_bot, Constante_Air_side, Temperature_Ambiante)
        Temp_matrix_list.append(Geometry_Matrix.copy())
        if round(i/iterations*100,3) > loading_queue[0]:
            print(f'{round(i*time_step, 0)} seconds computed, {loading_queue[0]}% Completed')
            loading_queue = loading_queue[1:]
        if i == iterations-1:
            print(f'{round(i*time_step, 0)} seconds computed, 100% Completed')

    # Interest Point
    Interest_point_y = int(Interest_point_largeur/plaque_largeur*len(Geometry_Matrix))
    Interest_point_x = int(Interest_point_longueur/plaque_longueur*len(Geometry_Matrix[0]))
    Interest_point_data = [mat[Interest_point_y][Interest_point_x] for mat in Temp_matrix_list]
    Interest_point_data_Celsius = np.array(Interest_point_data) - 273.15
    time_data = np.arange(0, len(Temp_matrix_list)*time_step, time_step)
    plt.plot(time_data, Interest_point_data_Celsius)
    plt.grid(True)
    plt.xlabel("Temps (s)")
    plt.ylabel("Temperature (°C)")
    plt.title(f"Évolution de la température au point d'intérêt\nLongueur:{Interest_point_longueur}mm & Largeur:{Interest_point_largeur}mm")
    plt.show()

    # HeatMap Animation
    all_values = [value for matrix in Temp_matrix_list for row in matrix for value in row]
    max_value_temp = max(all_values)
    min_value_temp = min(all_values)
    display_queue_time = np.linspace(0, simu_duration, animation_lenght)
    for i, matrix in enumerate(Temp_matrix_list):
            if (i+1)*time_step > display_queue_time[0]:
                display_queue_time = display_queue_time[1:]
                # Uncomment pour avoir la colourbar min max total de la simu ou du frame seulement
                # max_value_temp = np.max(matrix)
                # min_value_temp = np.min(matrix)
                img = plt.imshow(matrix-273.15, cmap='coolwarm', interpolation='nearest', vmin=min_value_temp-273.15, vmax=max_value_temp-273.15)
                cbar = plt.colorbar(img)
                cbar.set_label('Temperature (°C)')
                plt.title(f'Temperature Distribution at {round((i*time_step), 4)} seconds')

                if i != 0:
                    # Set position and zoom from last image
                    plt.gca().set_xlim(stored_xlim)
                    plt.gca().set_ylim(stored_ylim)
                    plt.gca().set_position(stored_position)
                plt.pause(0.1)
                # Store position and zoom for next image
                stored_xlim = plt.gca().get_xlim()
                stored_ylim = plt.gca().get_ylim()
                stored_position = plt.gca().get_position()
                
                if len(display_queue_time) != 0:
                    plt.clf()
                else:
                    print('Animation Done')

    plt.show()

def on_close(event, arg='no_test'):
    print('Figure Closed Need to implement Fucntion to stop animation')
    


My_Params = {
    'plaque_largeur' : 60, # mm
    'plaque_longueur' : 116, # mm
    'mm_par_element' : 5, # mm # TODO Data entry field
    'Temperature_Ambiante_C' : 25, # C
    'position_longueur_actuateur' : 15.5, # mm
    'position_largeur_actuateur' : 30, # mm
    'largeur_actu' : 15, # mm # TODO Data entry field
    'longueur_actu' : 15, # mm # TODO Data entry field
    'puissance_actuateur' : 1.46, #W
    'masse_volumique_plaque' : 2698, # kg/m3 # TODO Data entry field
    'epaisseur_plaque_mm' : 1.5, # mm # TODO Data entry field
    'capacite_thermique_plaque' : 900, # J/Kg*K # TODO Data entry field
    'conductivite_thermique_plaque' : 220, # W/m*K # TODO Data entry field
    'coefficient_convection' : 10, # W/m2*K # TODO Data entry field
    'time_step' : 0.05, #sec # TODO Data entry field
    'simu_duration' : 350, #sec # TODO Data entry field
    'animation_lenght' : 100, # frames # TODO Data entry field
    'point_interet_largeur' : 30, # mm # TODO add slider
    'point_interet_longueur' : 105 # mm # TODO add slider
}
# Launch_Simu(My_Params)
