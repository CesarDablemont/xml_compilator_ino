import xml_to_ino  # ficher local
import tkinter as tk
from tkinter import filedialog


def select_xgml_file():
    # Crée une fenêtre Tkinter (elle restera invisible)
    root = tk.Tk()
    root.withdraw()  # Cache la fenêtre principale

    # Ouvre une boîte de dialogue pour sélectionner un fichier .xgml
    file_path = filedialog.askopenfilename(
        title="Choisir un fichier .xgml",
        filetypes=[("Fichiers XGML", "*.xgml")],  # Filtre uniquement les fichiers .xgml
    )

    # Vérifie si un fichier a été sélectionné
    if not file_path:
        raise FileNotFoundError(
            "Aucun fichier sélectionné. Veuillez sélectionner un fichier .xgml."
        )

    # Retourne le chemin du fichier sélectionné
    return file_path


if __name__ == "__main__":
    selected_file = select_xgml_file()
    print(f"Fichier sélectionné : {selected_file}")
    xml_to_ino.job(selected_file)
