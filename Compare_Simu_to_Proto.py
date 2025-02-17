import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from Simulation import Plaque

mode = 'chaud'
mode = 'froid'

if mode == 'froid':
    data_refroidissement_path = os.path.dirname(os.path.abspath(__file__))+"\\Echelon_-0_39V.csv"
    df = pd.read_csv(data_refroidissement_path, encoding="ISO-8859-1")
    column_arrays = {col: df[col].to_numpy() for col in df.columns}
    data_time = column_arrays["Temps (s)"]
    data_time = data_time[:440]
    data_temp1 = column_arrays["Temp 1 (°C)"][:440]
    data_temp2 = column_arrays["Temp 2 (°C)"][:440]
    data_temp3 = column_arrays["Temp 3 (°C)"][:440]
    simu_duration = 440
    sign_courant = -1

if mode == 'chaud':
    data_rechaufement_path = os.path.dirname(os.path.abspath(__file__))+"\\Echelon_0_39V.csv"
    df = pd.read_csv(data_rechaufement_path, encoding="ISO-8859-1")
    column_arrays = {col: df[col].to_numpy() for col in df.columns}
    data_time = column_arrays["Temps (s)"]
    data_temp1 = column_arrays["Temp 1 (°C)"]
    data_temp2 = column_arrays["Temp 2 (°C)"]
    data_temp3 = column_arrays["Temp 3 (°C)"]
    simu_duration = 510
    sign_courant = 1

# simu_duration = 50
if mode == 'chaud':
    couple_actuateur = 1.8
    convection_actuateur = 40
    conductivite_thermique_plaque = 110
    coefficient_convection = 9
if mode == 'froid':
    couple_actuateur = 1.7
    convection_actuateur = 13
    conductivite_thermique_plaque = 110
    coefficient_convection = 11.5

My_params = {
    'plaque_largeur' : 60, # mm
    'plaque_longueur' : 116, # mm
    'mm_par_element' : 1, # mm
    'Temperature_Ambiante_C' : 25, # C
    'position_longueur_actuateur' : 15, # mm
    'position_largeur_actuateur' : 30, # mm
    'largeur_actu' : 15, # mm
    'longueur_actu' : 15, # mm
    'courant_actuateur' : sign_courant*2.38, # W
    'couple_actuateur' : couple_actuateur, # NA #TODO ADJUST
    'convection_actuateur' : convection_actuateur, # W/m2*K #TODO ADJUST
    'masse_volumique_plaque' : 2700, # kg/m3
    'masse_volumique_actu' : 3950, # kg/m3
    'epaisseur_plaque_mm' : 1.6, # mm
    'epaisseur_actu_mm' : 0.05, # mm
    'capacite_thermique_plaque' : 900, # J/Kg*K
    'capacite_thermique_Actu' : 760, # J/Kg*K
    'conductivite_thermique_plaque' : conductivite_thermique_plaque, # W/m*K #TODO ADJUST
    'coefficient_convection' : coefficient_convection, # W/m2*K #TODO ADJUST
    'time_step' : 'auto', #sec
    'simu_duration' : simu_duration, #sec
    'point_interet_1_largeur' : 30, # mm # TODO add slider
    'point_interet_1_longueur' : 15, # mm # TODO add slider
    'point_interet_2_largeur' : 30, # mm # TODO add slider
    'point_interet_2_longueur' : 60, # mm # TODO add slider
    'point_interet_3_largeur' : 30, # mm # TODO add slider
    'point_interet_3_longueur' : 105, # mm # TODO add slider
}

plt.figure(figsize=(10, 5))
My_plaque = Plaque(My_params)
My_plaque.Launch_Simu(display_animation=False)
plt.plot(My_plaque.actual_time_data, My_plaque.Interest_point_data_C_1, linestyle = '--', color = 'blue', label='Thermistance 1 Simu')
plt.plot(My_plaque.actual_time_data, My_plaque.Interest_point_data_C_2, linestyle = '--', color = 'green', label='Thermistance 2 Simu')
plt.plot(My_plaque.actual_time_data, My_plaque.Interest_point_data_C_3, linestyle = '--', color = 'black', label='Thermistance Laser Simu')
if mode == 'chaud':
    plt.plot(data_time, data_temp1-0.66, color = 'blue', label='Thermistance 1')
    plt.plot(data_time, data_temp2-0.74, color = 'green', label='Thermistance 2')
    plt.plot(data_time, data_temp3-0.57, color = 'black', label='Thermistance Laser')
if mode == 'froid':
    plt.plot(data_time, data_temp1-1.8, color = 'blue', label='Thermistance 1')
    plt.plot(data_time, data_temp2-1.62, color = 'green', label='Thermistance 2')
    plt.plot(data_time, data_temp3-1.27, color = 'black', label='Thermistance Laser')
plt.xlim(0, simu_duration)
plt.grid(True)
plt.xlabel("Temps (s)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature des thermistances")
if mode == 'chaud':
    plt.legend(loc='upper left')
if mode == 'froid':
    plt.legend(loc='lower left')
plt.show()

