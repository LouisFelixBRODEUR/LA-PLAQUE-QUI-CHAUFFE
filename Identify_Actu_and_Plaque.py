from Simulation import Plaque
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
# from scipy.signal import lsim, TransferFunction
import control
import numpy as np

Simu_parameters = {
    "plaque_largeur": 60.0,
    "plaque_longueur": 116.0,
    "mm_par_element": 1.0,
    "Temperature_Ambiante_C": 25.0,
    "position_longueur_actuateur": 15.0,
    "position_largeur_actuateur": 30.0,
    "largeur_actu": 15.0,
    "longueur_actu": 15.0,
    "puissance_actuateur": 3.0,
    "couple_actuateur": 1.0,
    "voltage_actuateur": 1.2,
    "convection_actuateur": 40,
    "masse_volumique_plaque": 2700.0,
    "masse_volumique_actu": 3950,
    "epaisseur_plaque_mm": 1.6,
    "epaisseur_actu_mm": 0.05,
    "capacite_thermique_plaque": 900.0,
    "capacite_thermique_Actu": 760,
    "conductivite_thermique_plaque": 110.0,
    "coefficient_convection": 8.0,
    "time_step": "auto",
    "simu_duration": 200.0, #1000 sec pour fct de transfert realiste
    "actu_start": 50.0,
    "actu_stop": 150.0,
    "point_interet_1_largeur": 30.0,
    "point_interet_1_longueur": 15.08,
    "point_interet_2_largeur": 30.0,
    "point_interet_2_longueur": 60.32,
    "point_interet_3_largeur": 30.0,
    "point_interet_3_longueur": 105.56,
    "perturbation_longueur": 49.88,
    "perturbation_largeur": 10.2,
    "perturabtion_start": 0.0,
    "perturabtion_stop": 0.0,
    "perturbation_power": 0.0,
    "simu_acceleration_factor": 0
}

def show_data_graph(Simu_data_dict):
    # Extract time once
    time = Simu_data_dict['time']

    # Create the plot
    plt.figure(figsize=(12, 6))

    # Plot all keys except 'time'
    for key, values in Simu_data_dict.items():
        if key != 'time':
            plt.plot(time, values, label=key)

    # Formatting
    plt.xlabel("Time (s)")
    plt.ylabel("Values")
    plt.title("Simulation Data over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def identify_second_order_arbitraty_transfer_function_with_delay(time_data, in_data, out_data, name = ''):
    # Extract data
    # t = Simu_data_dict['time']
    # u = Simu_data_dict['power_in']
    # y = Simu_data_dict[identify]

    t = time_data
    y = out_data
    y -= y[0]
    u = in_data

    # Function to simulate the 2nd-order response with delay
    def second_order_arbitraty_with_delay(t, a, b, c, d, e, delay):
        # Delay the input by shifting it in time (approximate)
        u_delayed = np.interp(t - delay, t, u, left=0)  # left=0: zero input before start
        num = [a, b, c]
        den = [1, d, e]
        sys = control.TransferFunction(num, den)
        t_out, y_model = control.forced_response(sys, T=t, U=u_delayed)
        return y_model
    # Wrapper for curve_fit (scipy expects 1D return)
    def fit_func(t, a, b, c, d, e, delay):
        return second_order_arbitraty_with_delay(t, a, b, c, d, e, delay)
    initial_guess = [1, 1, 1, 1, 1, 1]
    bounds = ([-np.inf, -np.inf, -np.inf, -np.inf, -np.inf, 0], [np.inf, np.inf, np.inf, np.inf, np.inf, np.inf])  # reasonable limits
    # Fit
    params, _ = curve_fit(fit_func, t, y, p0=initial_guess, bounds=bounds)
    a_fit, b_fit, c_fit, d_fit, e_fit, delay_fit = params
    print(f"Fonction de transfert de {name} identifiée:")
    print(f" ({round(a_fit,2)}s^2+{round(b_fit,2)}s+{round(c_fit,2)})/(s^2+{round(d_fit,2)}s+{round(d_fit,2)})*e^(-s{round(delay_fit,2)})")
    # Simulate the best-fit model
    y_fit = second_order_arbitraty_with_delay(t, a_fit, b_fit, c_fit, d_fit, e_fit, delay_fit)


    tf_string = f"({round(a_fit,2)}s² + {round(b_fit,2)}s + {round(c_fit,2)}) / (s² + {round(d_fit,2)}s + {round(d_fit,2)}) · e^(-s·{round(delay_fit,2)})"
    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(t, y, label='Sortie')
    plt.plot(t, y_fit, '--', label='Entrée calculé avec fonction de tranfert identifiée')
    plt.plot(t, u, '-', label='Entrée')
    plt.xlabel("Temps (s)")
    plt.ylabel("Entré et Sortie")
    plt.legend(loc='upper right')
    plt.grid(True)

    # Add the transfer function text in the top-left corner
    plt.text(0.01, 0.95, tf_string, transform=plt.gca().transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='left',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))

    plt.tight_layout()
    plt.show()



    # # Plot
    # plt.figure(figsize=(10, 5))
    # plt.plot(t, y, label='Sortie')
    # plt.plot(t, y_fit, '--', label='Entrée calculé avec fonction de tranfert identifiée')
    # plt.plot(t, u, '-', label='Entrée')
    # plt.xlabel("Temps (s)")
    # plt.ylabel("Entré et Sortie")
    # plt.legend(loc='upper right')
    # plt.grid(True)
    # plt.tight_layout()
    # plt.show()

My_plaque = Plaque(Simu_parameters)
Simu_data_dict = My_plaque.Launch_Simu(display_animation=False, save_data_for_trsfer_fct=True)
data_T1 = Simu_data_dict['T1']
data_T2 = Simu_data_dict['T2']
data_T3 = Simu_data_dict['T3']
data_power = Simu_data_dict['power_in']
data_heat_pumped = Simu_data_dict['heat_pumped']
data_time = Simu_data_dict['time']
if len(data_time) > 1000:
    time_new = np.linspace(data_time[0], data_time[-1], 1000)
    data_T1 = np.interp(time_new, data_time, data_T1)
    data_T2 = np.interp(time_new, data_time, data_T2)
    data_T3 = np.interp(time_new, data_time, data_T3)
    data_power = np.interp(time_new, data_time, data_power)
    data_heat_pumped = np.interp(time_new, data_time, data_heat_pumped)
    data_time = time_new
identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_power, data_heat_pumped,  name = "puissance IN vers chaleur pompée par l'actuateur")
identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_heat_pumped, data_T1,  name = "chaleur pompée par l'actuateur vers thermistance 1")
identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_T1, data_T2,  name = 'thermistance 1 vers thermistance 2')
identify_second_order_arbitraty_transfer_function_with_delay(data_time, data_T2, data_T3, name = 'thermistance 2 vers thermistance 3')