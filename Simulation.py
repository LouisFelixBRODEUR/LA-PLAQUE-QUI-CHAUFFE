import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import time
import copy

# TODO Check si Convection OK

My_Params = {
    'plaque_largeur' : 80, # mm
    'plaque_longueur' : 140, # mm
    'mm_par_element' : 5, # mm
    'Temperature_Ambiante_C' : 20, # C
    'position_longueur_actuateur' : 40, # mm
    'position_largeur_actuateur' : 35, # mm
    'largeur_actu' : 15, # mm
    'longueur_actu' : 15, # mm
    'puissance_actuateur' : 5, #W
    'masse_volumique_plaque' : 2698, # kg/m3
    'epaisseur_plaque_mm' : 3, # mm
    'capacite_thermique_plaque' : 900, # J/Kg*K
    'conductivite_thermique_plaque' : 220, # W/m*K
    'masse_volumique_Air' : 1.293, # kg/m3
    'capacite_thermique_Air' : 1005, # J/Kg*K
    'conductivite_thermique_Air' : 0.025, # W/m*K
    'coefficient_convection' : 22, # W/m2*K
    'time_step' : 0.01, #sec
    'simu_time' : 500, #sec
}


def actuateur_influence(Geo_Mat, Parameters):
    # plaque_largeur = float(Parameters['plaque_largeur'])
    # plaque_longueur = float(Parameters['plaque_longueur']) 
    # mm_par_element = float(Parameters['mm_par_element'])
    # Temperature_Ambiante_C = float(Parameters['Temperature_Ambiante_C'])
    # position_longueur_actuateur = float(Parameters['position_longueur_actuateur']) 
    # position_largeur_actuateur = float(Parameters['position_largeur_actuateur']) 
    # largeur_actu = float(Parameters['largeur_actu']) 
    # longueur_actu = float(Parameters['longueur_actu']) 
    # puissance_actuateur = float(Parameters['puissance_actuateur'])
    # masse_volumique_plaque = float(Parameters['masse_volumique_plaque'])
    # epaisseur_plaque_mm = float(Parameters['epaisseur_plaque_mm']) 
    # capacite_thermique_plaque = float(Parameters['capacite_thermique_plaque'])
    # conductivite_thermique_plaque = float(Parameters['conductivite_thermique_plaque'])
    # masse_volumique_Air = float(Parameters['masse_volumique_Air'])
    # capacite_thermique_Air = float(Parameters['capacite_thermique_Air']) 
    # conductivite_thermique_Air = float(Parameters['conductivite_thermique_Air'])
    # coefficient_convection = float(Parameters['coefficient_convection']) 
    # time_step = float(Parameters['time_step'])
    # simu_time = float(Parameters['simu_time'])

    mm_par_element = float(Parameters['mm_par_element'])
    position_largeur_actuateur = float(Parameters['position_largeur_actuateur'])
    position_longueur_actuateur = float(Parameters['position_longueur_actuateur']) 
    largeur_actu = float(Parameters['largeur_actu'])
    longueur_actu = float(Parameters['longueur_actu'])
    masse_volumique_plaque = float(Parameters['masse_volumique_plaque'])
    capacite_thermique_plaque =float(Parameters['capacite_thermique_plaque'])

    pos_x_actu = int(position_largeur_actuateur/mm_par_element)
    pos_y_actu = int(position_longueur_actuateur/mm_par_element)
    largeur_actu_in_element = largeur_actu/mm_par_element
    longueur_actu_in_element = longueur_actu/mm_par_element
    half_larg = int(largeur_actu_in_element/2)
    half_lon = int(longueur_actu_in_element/2)

    Chaleur_en_jeu = Parameters['puissance_actuateur']*Parameters['time_step']
    Chaleur_par_element = Chaleur_en_jeu /(largeur_actu_in_element)/(largeur_actu_in_element)

    delta_temp = Chaleur_par_element / (Parameters['epaisseur_plaque_mm'] /1000 * (mm_par_element/1000)**2 * masse_volumique_plaque) / capacite_thermique_plaque
    for y in range(pos_y_actu-half_lon, pos_y_actu+half_lon):
        for x in range(pos_x_actu-half_larg, pos_x_actu+half_larg):
            Geo_Mat[y][x] += delta_temp
    return Geo_Mat


# Nouvelle valeur = Moyenne des voisin
def iterate(Geo_Mat, Cst_Plq, Cst_Air, Temp_Ambi):
    Next_Geo_Mat = np.zeros_like(Geo_Mat)
    for y in range(len(Geo_Mat)):
        for x in range(len(Geo_Mat[0])):#Pour chaque Élément
            if x == 8 and y == 7:
                pass
            Somme_delta_T_Voisin_Plaque = 0
            Somme_delta_T_Voisin_Air = 0
            Temp_Element = Geo_Mat[y][x]
            # Si element sur une largeur, Somme_delta_T_Voisin_Air+=1
            if x == 0:
                Somme_delta_T_Voisin_Air += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y][x+1] - Temp_Element
            elif x == len(Geo_Mat[0])-1:
                Somme_delta_T_Voisin_Air += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y][x-1] - Temp_Element
            else: # Touche a aucun cote de largeur
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y][x-1] + Geo_Mat[y][x+1] - 2*Temp_Element

            # Si plaque sur une longeur, Somme_delta_T_Voisin_Air+=1
            if y == 0:
                Somme_delta_T_Voisin_Air += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y+1][x] - Temp_Element
            elif y == len(Geo_Mat)-1:
                Somme_delta_T_Voisin_Air += Temp_Ambi - Temp_Element
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y-1][x] - Temp_Element
            else: # Touche a aucun cote de largeur
                Somme_delta_T_Voisin_Plaque += Geo_Mat[y+1][x] + Geo_Mat[y-1][x] - 2*Temp_Element

            # Somme_delta_T_Voisin_Air+=2 car tout les element ont de lair dessux et en dessous
            Somme_delta_T_Voisin_Air += 2*(Temp_Ambi - Temp_Element)

            Next_Temp_Element = Temp_Element + Cst_Plq * (Somme_delta_T_Voisin_Plaque) + Cst_Air * (Somme_delta_T_Voisin_Air)
            Next_Geo_Mat[y][x] = Next_Temp_Element

    return Next_Geo_Mat

def Launch_Simu(Parameters):
    plaque_largeur = float(Parameters['plaque_largeur'])
    plaque_longueur = float(Parameters['plaque_longueur']) 
    mm_par_element = float(Parameters['mm_par_element'])
    Temperature_Ambiante_C = float(Parameters['Temperature_Ambiante_C'])
    position_longueur_actuateur = float(Parameters['position_longueur_actuateur']) 
    position_largeur_actuateur = float(Parameters['position_largeur_actuateur']) 
    largeur_actu = float(Parameters['largeur_actu']) 
    longueur_actu = float(Parameters['longueur_actu']) 
    puissance_actuateur = float(Parameters['puissance_actuateur'])
    masse_volumique_plaque = float(Parameters['masse_volumique_plaque'])
    epaisseur_plaque_mm = float(Parameters['epaisseur_plaque_mm']) 
    capacite_thermique_plaque = float(Parameters['capacite_thermique_plaque'])
    conductivite_thermique_plaque = float(Parameters['conductivite_thermique_plaque'])
    masse_volumique_Air = float(Parameters['masse_volumique_Air'])
    capacite_thermique_Air = float(Parameters['capacite_thermique_Air']) 
    conductivite_thermique_Air = float(Parameters['conductivite_thermique_Air'])
    coefficient_convection = float(Parameters['coefficient_convection']) 
    time_step = float(Parameters['time_step'])
    simu_time = float(Parameters['simu_time']) 

    Temperature_Ambiante = Temperature_Ambiante_C + 273 # C
    Fenetre_flux_puissance = (mm_par_element/1000)*(epaisseur_plaque_mm/1000)
    Constante_plaque = conductivite_thermique_plaque/masse_volumique_plaque/capacite_thermique_plaque/Fenetre_flux_puissance * time_step

    # Constante_Air = conductivite_thermique_Air/masse_volumique_Air/capacite_thermique_Air/Fenetre_flux_puissance * time_step
    # Constante_Air = coefficient_convection/masse_volumique_plaque/capacite_thermique_plaque/Fenetre_flux_puissance * time_step * (epaisseur_plaque_mm/1000)
    # Constante_Air = coefficient_convection/masse_volumique_plaque/capacite_thermique_plaque * time_step / (epaisseur_plaque_mm/1000)
    Constante_Air = coefficient_convection/masse_volumique_plaque/capacite_thermique_plaque * time_step / (epaisseur_plaque_mm/1000)
    # print(f'C Plaque {Constante_plaque}') 
    # print(f'C Air {Constante_Air}')

    # Temp Initial 
    Geometry_Matrix = np.full((int(plaque_largeur/mm_par_element), int(plaque_longueur/mm_par_element)), float(Temperature_Ambiante))

    # Processus iteratif de moyennage avec les voisins
    Temp_matrix_list = []
    iterations = int(simu_time/time_step)

    Temp_matrix_list.append(Geometry_Matrix.copy())

    loading_queue = np.linspace(10,100,10)
    for i in range(iterations):
        Geometry_Matrix = actuateur_influence(Geometry_Matrix, Parameters)
        Geometry_Matrix = iterate(Geometry_Matrix, Constante_plaque, Constante_Air, Temperature_Ambiante)
        Temp_matrix_list.append(Geometry_Matrix.copy())
        if round(i/iterations*100,3) > loading_queue[0]:
            print(f'{round(i*time_step, 4)} seconds computed, {loading_queue[0]}% Completed')
            loading_queue = loading_queue[1:]

    # Annimation
    all_values = [value for matrix in Temp_matrix_list for row in matrix for value in row]
    max_value_temp = max(all_values)
    min_value_temp = min(all_values)
    display_queue_time = np.linspace(0, simu_time, 500)
    for i, matrix in enumerate(Temp_matrix_list):
            if i*time_step > display_queue_time[0]:
                display_queue_time = display_queue_time[1:]
                # max_value_temp = np.max(matrix)
                # min_value_temp = np.min(matrix)
                img = plt.imshow(matrix, cmap='coolwarm', interpolation='nearest', vmin=min_value_temp, vmax=max_value_temp)
                cbar = plt.colorbar(img)
                cbar.set_label('Temperature')
                plt.title(f'Temperature Distribution at {round((i*time_step), 4)} seconds')
                plt.xlabel('X-axis')
                plt.ylabel('Y-axis')

                plt.pause(0.1)
                plt.clf()

    plt.show()

# Launch_Simu(My_Params)
