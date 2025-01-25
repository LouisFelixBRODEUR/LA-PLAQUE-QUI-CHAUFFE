import tkinter as tk
from tkinter import messagebox, filedialog

# TODO use https://pypi.org/project/customtkinter/ for better style

class GUI:
    def __init__(self):
        # Initialize root window
        self.root = tk.Tk()
        self.root.geometry("900x500")
        self.background_color = "#1e1e1e" # Dark gray background
        self.root.configure(bg=self.background_color)
        self.root.title("Controleur")

        # Initialize variables
        self.pix_spacing = 20
        self.Save_as_path = "Aucune Sélection"
        self.Coef_Therm = 0
        self.Simu_parameters = {
            'Coefficient thermique' : 0
        }

        self.load_frame() # Load initial frame
    
    # Uniform Button styles
    def set_button_style(self, BTT):
        BTT.config(
            cursor='hand2',
            font=("Arial", 12, "bold"), 
            bg="#005f9e", fg="white",
            relief="flat", 
            padx=10, pady=5,
            activebackground="#007acc", activeforeground="white", 
            borderwidth=0, highlightthickness=0
        )

    # Uniform Label styles
    def set_label_style(self, LBL):
        LBL.config(
            font=("Arial", 15, "bold"),
            background=self.background_color,
            foreground='white'
        )

    # Uniform Entry styles
    def set_entry_style(self, ENT):
        ENT.config(
            font=("Arial", 15),
            bd=1,  # Border width
            relief="solid",  # Solid border
            fg="#f0f0f0",  # Light gray background
            bg="#333333",  # Dark text color
            insertbackground='black',  # Cursor color
            highlightthickness=0  # No highlight
        )

    def on_key_release(self, event):
        self.Simu_parameters['Coefficient thermique'] = self.coef_therm_user_entry.get()

    def load_frame(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame for save path and button
        save_frame = tk.Frame(self.root, bg=self.background_color)
        save_frame.grid(row=0, column=0, columnspan=2, pady=(self.pix_spacing, self.pix_spacing/2), padx=self.pix_spacing, sticky="ew")
        save_frame.columnconfigure(0, weight=1)
        save_frame.columnconfigure(1, weight=0)
        # Save Path Label
        text_save_path = f"Données enregistrées dans : {self.Save_as_path}"
        label_save_path = tk.Label(save_frame, text=text_save_path, anchor="w")
        self.set_label_style(label_save_path)
        label_save_path.grid(row=0, column=0, sticky="w")
        # 'Save as' boutton
        self.Select_path_button = tk.Button(save_frame, text="Enregistrer sous", command=self.Save_as_clicked)
        self.set_button_style(self.Select_path_button)
        self.Select_path_button.grid(row=0, column=1, sticky="e")

        # Frame for coefficient thermique input
        self.coef_therm_frame = tk.Frame(self.root, bg=self.background_color)
        self.coef_therm_frame.grid(row=1, column=0, columnspan=2, pady=self.pix_spacing/2, padx=self.pix_spacing, sticky="ew")
        self.coef_therm_frame.columnconfigure(0, weight=0)
        self.coef_therm_frame.columnconfigure(1, weight=0)
        # Label for coef therm
        Coef_therm_label = tk.Label(self.coef_therm_frame, text="Coefficient Thermique : ")
        self.set_label_style(Coef_therm_label)
        Coef_therm_label.grid(row=0, column=0, sticky="w", padx=(0, 0))
        # data Entry for coef therm 
        self.coef_therm_user_entry = tk.Entry(self.coef_therm_frame, justify = 'center', width=5)
        self.coef_therm_user_entry.bind("<KeyRelease>", self.on_key_release) # Catch any keystroke
        self.set_entry_style(self.coef_therm_user_entry)
        self.coef_therm_user_entry.insert("0", str(self.Simu_parameters['Coefficient thermique']))
        self.coef_therm_user_entry.grid(row=0, column=1, sticky="w")

        # Button for greetings (Demo-Test)
        self.HW_button = tk.Button(self.root, text="Salutations", command=self.greatings)
        self.set_button_style(self.HW_button)
        self.HW_button.grid(row=2, column=0, columnspan=2, pady=(self.pix_spacing/2, self.pix_spacing), padx=self.pix_spacing, sticky="w")

        # Configure column weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def greatings(self):
        messagebox.showinfo("Info", 'Hello, world!')

    def Save_as_clicked(self):
        New_save_as_path = filedialog.askdirectory(title='Enregister Sous')
        if New_save_as_path == '':
            New_save_as_path = "Aucune Sélection"
        self.Save_as_path = New_save_as_path
        self.load_frame()

if __name__ == "__main__":
    app = GUI()
    app.root.mainloop()