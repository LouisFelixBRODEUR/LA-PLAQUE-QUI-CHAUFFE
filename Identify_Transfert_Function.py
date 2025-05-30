import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


# data_refroidissement_path = os.path.dirname(os.path.abspath(__file__))+"\\Echelon_-0_39V.csv"
# df = pd.read_csv(data_refroidissement_path, encoding="ISO-8859-1")
# column_arrays = {col: df[col].to_numpy() for col in df.columns}
# data_time = column_arrays["Temps (s)"]
# data_time = data_time[:456]
# data_temp1 = column_arrays["Temp 1 (°C)"]
# data_temp2 = column_arrays["Temp 2 (°C)"]
# temp_3_base = np.max(column_arrays["Temp 3 (°C)"])
# data_temp3 = column_arrays["Temp 3 (°C)"]-temp_3_base
# data_temp3 = data_temp3[:456]

# data_refroidissement_path = os.path.dirname(os.path.abspath(__file__))+"\\openloopdatafroid.csv"
# df = pd.read_csv(data_refroidissement_path, encoding="ISO-8859-1")
# column_arrays = {col: df[col].to_numpy() for col in df.columns}
# data_time = column_arrays["Temps (s)"]
# # data_time = data_time[:456]
# temp_1_base = np.max(column_arrays["Temp 1 (C)"])
# temp_2_base = np.max(column_arrays["Temp 2 (C)"])
# temp_3_base = np.max(column_arrays["Temp 3 (C)"])
# data_temp1 = column_arrays["Temp 1 (C)"]-temp_1_base
# data_temp2 = column_arrays["Temp 2 (C)"]-temp_2_base
# data_temp3 = column_arrays["Temp 3 (C)"]-temp_3_base
# # data_temp3 = data_temp3[:456]

# data_rechaufement_path = os.path.dirname(os.path.abspath(__file__))+"\\Echelon_0_39V.csv"
# df = pd.read_csv(data_rechaufement_path, encoding="ISO-8859-1")
# column_arrays = {col: df[col].to_numpy() for col in df.columns}
# data_time = column_arrays["Temps (s)"]
# data_temp1 = column_arrays["Temp 1 (°C)"]
# data_temp2 = column_arrays["Temp 2 (°C)"]
# temp_3_base = np.min(column_arrays["Temp 3 (°C)"])
# data_temp3 = column_arrays["Temp 3 (°C)"]-temp_3_base

data_rechaufement_path = os.path.dirname(os.path.abspath(__file__))+"\\data_openloop.csv"
df = pd.read_csv(data_rechaufement_path, encoding="ISO-8859-1")
column_arrays = {col: df[col].to_numpy() for col in df.columns}
data_time = column_arrays["Temps (s)"]
temp_1_base = np.min(column_arrays["Temp 1 (C)"])
temp_2_base = np.min(column_arrays["Temp 2 (C)"])
temp_3_base = np.min(column_arrays["Temp 3 (C)"])
data_temp1 = column_arrays["Temp 1 (C)"]-temp_1_base
data_temp2 = column_arrays["Temp 2 (C)"]-temp_2_base
data_temp3 = column_arrays["Temp 3 (C)"]-temp_3_base

# Identification de la fonction de Transfert retard
def sys_2iem_ordre_tau1tau2(t, K, tau1, tau2, retard):  # Reponse a lechelon 1 dun systeme du 2ieme ordre
    t_shifted = np.maximum(0, t - retard)
    return K+(K/(tau2-tau1))*(tau1*np.exp(-t_shifted/tau1)-tau2*np.exp(-t_shifted/tau2))
# Fiting de la reponse experimentale
bounds = ([-50, 10, 10, 0], [50, 500, 500, 50])
initial_guess = [0, 100, 75, 20]
params, covariance = curve_fit(sys_2iem_ordre_tau1tau2, data_time, data_temp1, p0=initial_guess, bounds=bounds)
# K_val = params[0]/-0.39
K_val = params[0]/0.294
a = params[1]*params[2]
b = params[1]+params[2]
print(f'Transfer Function is {round(K_val,10)}/{round(a,5)}s^2 + {round(b,5)}s + 1 * exp(-s{round(params[3],5)})')
# print(params[0])
# print(params[1])
# print(params[2])
# print(params[3])
fitted_response_temp3 = sys_2iem_ordre_tau1tau2(data_time, params[0], params[1], params[2], params[3])

# # Identification de la fonction de Transfert
# def sys_2iem_ordre_tau1tau2(t, K, tau1, tau2):  # Reponse a lechelon 1 dun systeme du 2ieme ordre
#     return K+(K/(tau2-tau1))*(tau1*np.exp(-t/tau1)-tau2*np.exp(-t/tau2))
# # Fiting de la reponse experimentale
# bounds = ([-50, 10, 10], [50, 500, 500])
# initial_guess = [0, 100, 75]
# params, covariance = curve_fit(sys_2iem_ordre_tau1tau2, data_time, data_temp2, p0=initial_guess, bounds=bounds)
# K_val = params[0]/0.39
# a = params[1]*params[2]
# b = params[1]+params[2]
# print(f'Transfer Function is {round(K_val,10)}/{round(a,5)}s^2 + {round(b,5)}s + 1')
# # print(params[0])
# # print(params[1])
# # print(params[2])
# fitted_response_temp3 = sys_2iem_ordre_tau1tau2(data_time, params[0], params[1], params[2])


plt.figure(figsize=(10, 5))
# plt.plot(data_time, data_temp2, label="Temp 1 (°C)")
# plt.plot(data_time, data_temp2, label="Temp 2 (°C)")

plt.plot(data_time, data_temp1, label="Temp 1 (°C)")
plt.plot(data_time, fitted_response_temp3, label="Fit 2ieme ordre Temp 1 (°C)")

plt.xlabel("Time (s)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Variation Over Time")
plt.legend()
plt.grid(True)

transfer_function_text = (
    fr"$G(s) = \frac{{{round(K_val,3)}}}{{{round(a,3)}s^2 + {round(b,3)}s + 1}} e^{{-s{round(params[3],3)}}}$"
)
# transfer_function_text = (
#     fr"$G(s) = \frac{{{round(K_val, 2)}}}{{{round(a, 2)}s^2 + {round(b, 2)}s + 1}}$"
# )

plt.text(
    0.4 * max(data_time),  # X position (5% from the left)
    0.5 * max(np.abs(data_temp3)),  # Y position (90% of max temp)
    transfer_function_text,
    fontsize=18,
    bbox=dict(facecolor='white', alpha=0.7)  # Background box for readability
)

plt.show()

