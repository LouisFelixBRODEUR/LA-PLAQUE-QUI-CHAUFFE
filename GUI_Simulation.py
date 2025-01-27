import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk
from Simulation import Launch_Simu

# TODO slider for interest point
# TODO link simulation and all variables

class GUI:
    def __init__(self):
        # Initialize root window
        self.root = ctk.CTk()
        self.root.geometry("900x700")
        self.background_color = "#1e1e1e" # Dark gray background
        self.root.configure(bg=self.background_color)
        self.root.title("Controleur Simulation")

        ctk.set_appearance_mode("dark")  # Dark mode for better contrast
        ctk.set_default_color_theme("blue")  # Blue theme for buttons and other elements

        # Initialize variables
        self.pix_spacing = 20
        self.pix_to_plaque_box = 3
        self.Save_as_path = "Aucune Sélection"
        # self.Coef_Therm = 0
        # # self.Simu_parameters = {
        #     'Coefficient thermique' : 'abc',
        #     # 'Largeur Plaque' : '60',
        #     # 'plaque_longueur' : '116',
        #     # 'position_largeur_actuateur' : '30',
        #     'Position Actuateur Longueur': '40',
        # }
        self.Simu_parameters = {
            'Coefficient thermique' : 'abc', # A ENLEVER
            'plaque_largeur' : 60, # mm
            'plaque_longueur' : 116, # mm
            'mm_par_element' : 5, # mm
            'Temperature_Ambiante_C' : 20, # C
            'position_longueur_actuateur' : 60, # mm
            'position_largeur_actuateur' : 30, # mm
            'largeur_actu' : 15, # mm
            'longueur_actu' : 15, # mm
            'puissance_actuateur' : 7.1, #W
            'masse_volumique_plaque' : 2698, # kg/m3
            'epaisseur_plaque_mm' : 3, # mm
            'capacite_thermique_plaque' : 900, # J/Kg*K
            'conductivite_thermique_plaque' : 220, # W/m*K
            'masse_volumique_Air' : 1.293, # kg/m3
            'capacite_thermique_Air' : 1005, # J/Kg*K
            'conductivite_thermique_Air' : 0.025, # W/m*K
            'coefficient_convection' : 22, # W/m2*K
            'time_step' : 0.01, #sec
            'simu_duration' : 10, #sec
            'animation_lenght' : 100 # frames
        }

        self.load_frame() # Load initial frame

    def on_enter_key(self, event):
        self.Log_parameters()
        self.load_frame()

    def Log_parameters(self):
        self.Simu_parameters['Coefficient thermique'] = self.coef_therm_user_entry.get()
        self.Simu_parameters['plaque_largeur'] = self.plaque_width_user_entry.get()
        self.Simu_parameters['plaque_longueur'] = self.plaque_lenght_user_entry.get()
        self.Simu_parameters['position_longueur_actuateur'] = self.lenght_value.get()
        print(self.width_value.get())
        self.Simu_parameters['position_largeur_actuateur'] = self.width_value.get()
        

    def load_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame for save path and button
        save_frame = ctk.CTkFrame(self.root)
        save_frame.grid(row=0, column=0, columnspan=2, pady=(self.pix_spacing, self.pix_spacing/2), padx=self.pix_spacing, sticky="ew")
        save_frame.columnconfigure(0, weight=1)
        save_frame.columnconfigure(1, weight=0)
        # Save Path Label
        text_save_path = f"Données enregistrées dans : {self.Save_as_path}"
        label_save_path = ctk.CTkLabel(save_frame, text=text_save_path)
        label_save_path.grid(row=0, column=0, sticky="w", padx=(5,0))
        # 'Save as' boutton
        self.Select_path_button = ctk.CTkButton(save_frame, text="Enregistrer sous", command=self.Save_as_clicked)
        self.Select_path_button.grid(row=0, column=1, sticky="e")

        # TODO add mm label to the entries
        # Frame for plaque info
        self.plaque_info_frame = ctk.CTkFrame(self.root)
        self.plaque_info_frame.grid(row=1, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.plaque_info_frame.columnconfigure(0, weight=0)
        self.plaque_info_frame.columnconfigure(1, weight=0)
        # Label for coef therm
        Coef_therm_label = ctk.CTkLabel(self.plaque_info_frame, text="Coefficient Thermique : ")
        Coef_therm_label.grid(row=0, column=0, sticky="w", padx=(5,0), pady=(5,0))
        # data Entry for coef therm 
        self.coef_therm_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.coef_therm_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.coef_therm_user_entry.insert("1", str(self.Simu_parameters['Coefficient thermique']))
        self.coef_therm_user_entry.grid(row=0, column=1, sticky="w", pady=(5,0))
        # Label for plaque width
        plaque_width = ctk.CTkLabel(self.plaque_info_frame, text="Largeur de la plaque en mm : ")
        plaque_width.grid(row=1, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque width 
        self.plaque_width_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.plaque_width_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_width_user_entry.insert("1", str(self.Simu_parameters['plaque_largeur']))
        self.plaque_width_user_entry.grid(row=1, column=1, sticky="w")
        # Label for plaque lenght
        plaque_lenght = ctk.CTkLabel(self.plaque_info_frame, text="Longueur de la plaque en mm : ")
        plaque_lenght.grid(row=2, column=0, sticky="w", padx=(5,0))
        # data Entry for plaque lenght
        self.plaque_lenght_user_entry = ctk.CTkEntry(self.plaque_info_frame, justify='center')
        self.plaque_lenght_user_entry.bind("<Return>", self.on_enter_key) # Catch any keystroke
        self.plaque_lenght_user_entry.insert("1", str(self.Simu_parameters['plaque_longueur']))
        self.plaque_lenght_user_entry.grid(row=2, column=1, sticky="w")

        # TODO
        # # Boutton
        # self.Reset_Actu_Posi_button = ctk.CTkButton(self.plaque_info_frame, text="Réinitialiser", command=self.Reset_to_default)
        # self.Reset_Actu_Posi_button.grid(row=3, column=1, sticky="w")

        # Code for plaque with sliders:
        # Label
        PosActu_Label = ctk.CTkLabel(self.plaque_info_frame, text="Position de l'actuateur :")
        PosActu_Label.grid(row=3, column=0, sticky="w", padx=(5,0))
        # Plaque
        self.plaque_width = 300*int(self.Simu_parameters['plaque_largeur'])/int(self.Simu_parameters['plaque_longueur'])
        self.plaque_lenght = 300
        self.plaque_box_frame = ctk.CTkFrame(self.plaque_info_frame, height=self.plaque_width, width=self.plaque_lenght, fg_color="black")
        self.plaque_box_frame.grid(row=4, column=0, pady=(5,5), columnspan = 2, padx=10)
        self.plaque_canvas = ctk.CTkCanvas(self.plaque_box_frame, height=self.plaque_width, width=self.plaque_lenght, bg='#2B2B2B', bd=0, highlightthickness=0)
        self.plaque_canvas.pack()
        # RedDot
        self.create_rounded_rectangle('gray10')
        self.red_dot = self.plaque_canvas.create_oval(10, 10, 20, 20, fill="red", outline="red")
        # Create horizontal slider for the red square's x position (width)
        self.lenght_slider = ctk.CTkSlider(self.plaque_info_frame, from_=0, to=int(self.Simu_parameters['plaque_longueur']), number_of_steps=100, command=self.update_red_square, orientation="horizontal")
        self.lenght_slider.set(int(self.Simu_parameters['position_longueur_actuateur']))  # Set initial x position to the middle
        self.lenght_slider.grid(row=5, column=0, columnspan=2, pady=(0,5), padx=(10,4), sticky="ew")
        # Create corresponding Entry for horizontal slider
        self.lenght_value = ctk.CTkEntry(self.plaque_info_frame, width=80)
        self.lenght_value.grid(row=5, column=2, padx=0, pady=(0,5), sticky="w")
        self.lenght_value.insert(0, str(self.lenght_slider.get()))  # Set initial value
        self.lenght_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("length"))
        # Create vertical slider for the red square's y position (height)
        slider_height = 300*int(self.Simu_parameters['plaque_largeur'])/int(self.Simu_parameters['plaque_longueur'])
        self.width_slider = ctk.CTkSlider(self.plaque_info_frame, height=slider_height, from_=0, to=int(self.Simu_parameters['plaque_largeur']), number_of_steps=100, command=self.update_red_square, orientation="vertical")
        self.width_slider.set(int(self.Simu_parameters['position_largeur_actuateur']))  # Set initial y position to the middle
        self.width_slider.grid(row=4, column=2, padx=(35,0), pady=(0,0), sticky="w")
        # Create corresponding Entry for vertical slider
        self.width_value = ctk.CTkEntry(self.plaque_info_frame, width=80)
        self.width_value.grid(row=3, column=2, pady=0, padx=(5,0), sticky="s")
        self.width_value.insert(0, str(self.plaque_lenght - self.width_slider.get()))  # Set initial value (reverse the initial y position)
        self.width_value.bind("<KeyRelease>", lambda e: self.update_slider_from_entry("width"))
        self.update_red_square()

        # Button for simulation
        self.HW_button = ctk.CTkButton(self.root, text="Lancer la Simulation", command=self.Simulate)
        self.HW_button.grid(row=2, column=0, columnspan=2, pady=(self.pix_spacing/2, self.pix_spacing), padx=self.pix_spacing, sticky="w")

        # Configure column weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def Simulate(self):
        self.Log_parameters()
        Launch_Simu(self.Simu_parameters)
        # messagebox.showinfo("Info", 'Hello, world!')

    def Save_as_clicked(self):
        New_save_as_path = filedialog.askdirectory(title='Enregister Sous')
        if New_save_as_path == '':
            New_save_as_path = "Aucune Sélection"
        self.Save_as_path = New_save_as_path
        self.load_frame()

    def create_rounded_rectangle(self, color):
        """Draw a rectangle with rounded corners."""
        r = 10
        W = 300
        L = 300*int(self.Simu_parameters['plaque_largeur'])/int(self.Simu_parameters['plaque_longueur'])

        # Coordinates of the rounded rectangle (with rounded corners)
        self.plaque_canvas.create_oval(0, 0, r*2, r*2, fill=color, outline=color)  # Top-left corner
        self.plaque_canvas.create_oval(W - r*2, 0, W, r*2, fill=color, outline=color)  # Top-right corner
        self.plaque_canvas.create_oval(0, L - r*2, r*2, L, fill=color, outline=color)  # Bottom-left corner
        self.plaque_canvas.create_oval(W - r*2, L - r*2, W, L, fill=color, outline=color)  # Bottom-right corner

        # Draw the four sides (excluding the corners)
        self.plaque_canvas.create_rectangle(r, 0, W - r, L, fill=color, outline=color)  # Top and bottom
        self.plaque_canvas.create_rectangle(0, r, W, L - r, fill=color, outline=color)  # Left and right

    def update_red_square(self, event=None):
        # Get the x position from the width slider (horizontal slider)
        x = self.lenght_slider.get()  
        # Get the y position from the length slider (vertical slider)
        # y = (300 - (300 - self.width_slider.get()))  # Reverse the y value for the vertical slider to make it move upward as the slider value increases
        y = self.width_slider.get()  # Reverse the y value for the vertical slider to make it move upward as the slider value increases

        pos_x_in_pix = x*300/int(self.Simu_parameters['plaque_longueur'])
        pos_y_in_pix = 300*((int(self.Simu_parameters['plaque_largeur'])) - y)/int(self.Simu_parameters['plaque_longueur'])

        self.plaque_canvas.coords(self.red_dot, pos_x_in_pix - 5, pos_y_in_pix - 5, pos_x_in_pix + 5, pos_y_in_pix + 5)

        # Update the corresponding Entry valueshttps://chatgpt.com/c/6793ee06-1830-800a-bef3-c475d0aae5b2
        self.lenght_value.delete(0, ctk.END)
        self.lenght_value.insert(0, str(round(x,5)))
        self.width_value.delete(0, ctk.END)
        self.width_value.insert(0, str(round(y,5)))  # Update entry with the corrected value for y

    def update_slider_from_entry(self, slider_type):
        """Update slider from entry widget."""
        try:
            if slider_type == "lenght":
                value = float(self.lenght_value.get())
                # Ensure value is within slider's range
                if 0 <= value <= int(self.Simu_parameters['plaque_longueur']):
                    self.lenght_slider.set(value)
            elif slider_type == "width":
                value = float(self.width_value.get())
                # Ensure value is within slider's range (reverse the input value for vertical slider)
                if 0 <= value <= int(self.Simu_parameters['plaque_largeur']):
                    self.width_slider.set(value)  # Reverse for vertical slider
        except ValueError:
            pass  # Ignore invalid input (e.g., if the input is not a number)

    def Reset_to_default(self):
        pass
        # TODO
        

if __name__ == "__main__":
    app = GUI()
    app.root.mainloop()