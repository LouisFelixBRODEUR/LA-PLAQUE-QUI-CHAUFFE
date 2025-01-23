import numpy as np
import matplotlib.pyplot as plt
import numpy as np
import time 

plaque_largeur = 80
plaque_hauteur = 140
bloc_par_dist = 1

Geometry_Matrix = np.full((int(plaque_largeur/bloc_par_dist), int(plaque_hauteur/bloc_par_dist)), 20+273)

# Temp Initial 
for x in range(30,50):
    for y in range(60,80):
        Geometry_Matrix[x][y] = 50+273

# Nouvelle valeur = Moyenne des voisin
def iterate(Geo_Mat):
    Next_Geo_Mat = np.zeros_like(Geo_Mat)
    for y in range(len(Geometry_Matrix)):
        for x in range(len(Geometry_Matrix[0])):
            sum_temp = 0
            sum_num = 0
            if x != 0:
                sum_temp += Geo_Mat[y][x-1]
                sum_num += 1
            if x != int(plaque_hauteur/bloc_par_dist)-1:
                sum_temp += Geo_Mat[y][x+1]
                sum_num += 1
            if y != 0:
                sum_temp += Geo_Mat[y-1][x]
                sum_num += 1
            if y != int(plaque_largeur/bloc_par_dist)-1:
                sum_temp += Geo_Mat[y+1][x]
                sum_num += 1
            Next_Geo_Mat[y][x] = sum_temp / sum_num
    return Next_Geo_Mat

# Processus iteratif de moyennage avec les voisins
Temp_matrix_list = []
for i in range(70):
    Geometry_Matrix = iterate(Geometry_Matrix)
    Temp_matrix_list.append(Geometry_Matrix)

# Annimation
for i, matrix in enumerate(Temp_matrix_list):
    img = plt.imshow(matrix, cmap='coolwarm', interpolation='nearest', vmin=20+273, vmax=50+273)
    cbar = plt.colorbar(img)
    cbar.set_label('Temperature')
    plt.title(f'Temperature Distribution at Time Step {i + 1}')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.pause(0.1)
    plt.clf()

plt.show()

