import subprocess
import sys
import os
import datetime

def run_script(script_path, *args):
    """
    Exécute un script Python en lui passant les arguments spécifiés.
    """
    try:
        subprocess.run(["python", script_path, *args], check=True)
        print(f"Script {script_path} exécuté avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script {script_path}: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage : python main.py <fichier_donnees> <fichier_but>")
        sys.exit(1)
    
    # Fichiers d'entrée (fichier source et fichier des scores 'but')
    fichier_entree = sys.argv[1]
    fichier_but = sys.argv[2]

    # Définition du dossier de base et du dossier d'exports
    base_dir = r"C:\Users\Luis\Documents\Fichiers matchs"
    exports_dir = os.path.join(base_dir, "Exports")
    os.makedirs(exports_dir, exist_ok=True)

    # Création d'un sous-dossier horodaté pour cette exécution
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    subfolder = os.path.join(exports_dir, timestamp)
    os.makedirs(subfolder, exist_ok=True)

    # Chemins des fichiers intermédiaires et résultats
    fichier_traitement = os.path.join(subfolder, "traitement.txt")
    fichier_hauteur = os.path.join(subfolder, "hauteur_bloc.csv")
    fichier_defenseur_csv = os.path.join(subfolder, "defenseur.csv")
    fichier_defenseur_png = os.path.join(subfolder, "defenseur.png")
    fichier_boxplots_hauteur_csv = os.path.join(subfolder, "boxplots_hauteur.csv")
    fichier_boxplots_hauteur_png = os.path.join(subfolder, "boxplots_hauteur.png")
    fichier_boxplots_defenseur_csv = os.path.join(subfolder, "boxplots_defenseur.csv")
    fichier_boxplots_defenseur_png = os.path.join(subfolder, "boxplots_defenseur.png")

    # Chemins vers les scripts
    script_traitement = os.path.join(base_dir, "Code traitement.py")
    script_hauteur = os.path.join(base_dir, "Calcul de hauteur de bloc.py")
    script_defenseur = os.path.join(base_dir, "Calcul défenseur le plus proche.py")
    script_boxplots = os.path.join(base_dir, "Code Boxplots.py")

    # Étape 1 : Traitement initial
    run_script(script_traitement, fichier_entree, fichier_traitement)

    # Étape 2 : Calcul de hauteur de bloc
    run_script(script_hauteur, fichier_traitement, fichier_hauteur)

""" # Étape 3 : Calcul du défenseur le plus proche
    # Note : Ce script attend 2 arguments : le fichier match complet (ici, fichier_traitement) et un dossier d'export
    run_script(script_defenseur, fichier_traitement, subfolder) 
"""

    # Étape 4 : Génération des boxplots pour hauteur de bloc
    run_script(script_boxplots, fichier_hauteur, fichier_but, fichier_boxplots_hauteur_csv, fichier_boxplots_hauteur_png)

"""    # Étape 5 : Génération des boxplots pour défenseur le plus proche
    run_script(script_boxplots, fichier_defenseur_csv, fichier_but, fichier_boxplots_defenseur_csv, fichier_boxplots_defenseur_png)"""

    print("Processus automatisé terminé.")
    print(f"Les résultats sont enregistrés dans : {subfolder}")

if __name__ == '__main__':
    main()
