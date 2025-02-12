import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit



data_refroidissement = os.path.dirname(os.path.abspath(__file__))+"\\Echelon_-0_39V.csv"
df = pd.read_csv(data_refroidissement, encoding="ISO-8859-1")
column_arrays = {col: df[col].to_numpy() for col in df.columns}
data_time = column_arrays["Temps (s)"]
data_temp1 = column_arrays["Temp 1 (°C)"]
data_temp2 = column_arrays["Temp 2 (°C)"]
temp_3_base = np.max(column_arrays["Temp 3 (°C)"])
data_temp3 = column_arrays["Temp 3 (°C)"]-temp_3_base



# data_rechaufement_path = os.path.dirname(os.path.abspath(__file__))+"\\Echelon_0_39V.csv"
# df = pd.read_csv(data_rechaufement_path, encoding="ISO-8859-1")
# column_arrays = {col: df[col].to_numpy() for col in df.columns}
# data_time = column_arrays["Temps (s)"]
# data_temp1 = column_arrays["Temp 1 (°C)"]
# data_temp2 = column_arrays["Temp 2 (°C)"]
# temp_3_base = np.min(column_arrays["Temp 3 (°C)"])
# data_temp3 = column_arrays["Temp 3 (°C)"]-temp_3_base


# Identification de la fonction de Transfert
# def sys_2iem_ordre(t, K, A, B): # Reponse a lechelon 1 dun systeme du 2ieme ordre
#     Ptau2 = (B+np.sqrt(B**2-4*A))/2
#     Mtau2 = (B-np.sqrt(B**2-4*A))/2
#     tau2 = Ptau2
#     tau1 = A/tau2
#     return sys_2iem_ordre_tau1tau2(t, K, tau1, tau2)
def sys_2iem_ordre_tau1tau2(t, K, tau1, tau2):  # Reponse a lechelon 1 dun systeme du 2ieme ordre
    return K+(K/(tau2-tau1))*(tau1*np.exp(-t/tau1)-tau2*np.exp(-t/tau2))
# Fiting de la reponse experimentale
bounds = ([-50, 10, 10], [1, 500, 500])
initial_guess = [0, 100, 75]
params, covariance = curve_fit(sys_2iem_ordre_tau1tau2, data_time, data_temp3, p0=initial_guess, bounds=bounds)
K_val = params[0]+temp_3_base
a = params[1]*params[2]
b = params[1]+params[2]
print(f'Transfer Function is {round(K_val,10)}/{round(a,5)}s^2 + {round(b,5)}s + 1')

print(params[0])
print(params[1])
print(params[2])

fitted_response_temp3 = sys_2iem_ordre_tau1tau2(data_time, params[0], params[1], params[2])
# fitted_response_temp3 = sys_2iem_ordre_tau1tau2(data_time, 17, 100, 75)


plt.figure(figsize=(10, 5))
# plt.plot(data_time, data_temp1, label="Temp 1 (°C)")

# plt.plot(data_time, data_temp2, label="Temp 2 (°C)")

plt.plot(data_time, data_temp3, label="Temp 3 (°C)")
plt.plot(data_time, fitted_response_temp3, label="Fit 2ieme ordre Temp 3 (°C)")

plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Variation Over Time")
plt.legend()
plt.grid(True)
plt.show()

