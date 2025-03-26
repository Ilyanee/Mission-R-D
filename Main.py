import subprocess
import sys
import os
import datetime

def run_script(script_path, *args):
    """
    Exécute un script Python en lui passant des arguments.
    """
    try:
        subprocess.run(["python", script_path, *args], check=True)
        print(f"Script {script_path} exécuté avec succès.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script {script_path}: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage : python main.py <fichier_donnees>")
        sys.exit(1)
    
    # Le fichier source est passé en argument
    fichier_entree = sys.argv[1]
    
    # Dossier de base et dossier de sortie
    base_dir = r"C:\Users\Luis\Documents\Fichiers matchs"
    exports_dir = os.path.join(base_dir, "Exports")
    os.makedirs(exports_dir, exist_ok=True)
    
    # Créer un sous-dossier horodaté pour cette exécution
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    subfolder = os.path.join(exports_dir, timestamp)
    os.makedirs(subfolder, exist_ok=True)
    
    # Définition des chemins pour les fichiers intermédiaires et résultats
    fichier_traitement = os.path.join(subfolder, "traitement.txt")
    fichier_hauteur = os.path.join(subfolder, "L1 J1 MHSC OM hauteur_bloc.csv")
    
    # Chemins vers les scripts
    script_traitement = os.path.join(base_dir, "Code traitement.py")
    script_calcul = os.path.join(base_dir, "Calcul de hauteur de bloc.py")
    
    # Exécution séquentielle : traitement initial, puis calcul de hauteur de bloc
    run_script(script_traitement, fichier_entree, fichier_traitement)
    run_script(script_calcul, fichier_traitement, fichier_hauteur)
    
    print("Processus automatisé terminé.")
    print(f"Les résultats sont enregistrés dans : {subfolder}")

if __name__ == '__main__':
    main()
