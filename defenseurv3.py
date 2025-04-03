#!/usr/bin/env python3
import csv
import math
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt

TOTAL_PLAYERS = 22  # Nombre fixe de joueurs

def conv_float(s):
    """Convertit une chaîne avec une virgule en décimal."""
    try:
        return float(s.replace(',', '.'))
    except Exception as e:
        print(f"Erreur de conversion pour '{s}': {e}")
        return None

def distance(x1, y1, x2, y2):
    """Calcule la distance euclidienne entre deux points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calcul_porteur(row):
    """
    Calcule le porteur de balle pour une ligne du fichier.
    Utilise la colonne 'ball' pour extraire la position du ballon, puis
    parcourt les colonnes 'player_1' à 'player_22' pour trouver le joueur le plus proche.
    
    Retourne un tuple (porteur_team, porteur_x, porteur_y) ou None si non trouvé.
    """
    ball_field = row["ball"]
    ball_parts = ball_field.split(',')
    if len(ball_parts) < 2:
        return None
    try:
        ball_x = conv_float(ball_parts[0])
        ball_y = conv_float(ball_parts[1])
    except Exception:
        return None

    min_dist = float('inf')
    porteur = None

    for i in range(1, TOTAL_PLAYERS+1):
        champ = row.get(f"player_{i}", "")
        # Forcer la conversion en chaîne si nécessaire
        if not isinstance(champ, str):
            champ = str(champ)
        champ = champ.strip()
        if not champ:
            continue
        parts = champ.split(',')
        if len(parts) < 5:
            continue
        try:
            team = int(parts[0].strip())
            x = conv_float(parts[3])
            y = conv_float(parts[4])
        except Exception:
            continue
        d = distance(x, y, ball_x, ball_y)
        if d < min_dist:
            min_dist = d
            porteur = (team, x, y)
    return porteur

def calculer_distance_defenseur(fichier_entree):
    """
    Lit le fichier CSV issu de Code traitement (avec en-tête) et, pour chaque instant,
    détermine le porteur de balle et, parmi les joueurs adverses, le défenseur le plus proche du porteur.
    Le timestamp est en millisecondes et est converti en minutes (en utilisant le premier timestamp comme référence).
    
    Retourne un DataFrame avec les colonnes :
      temps_min, porteur_team, porteur_x, porteur_y, defenseur_team, defenseur_x, defenseur_y, distance
    """
    # Forcer la lecture de toutes les colonnes comme chaînes pour éviter les conversions automatiques
    df = pd.read_csv(fichier_entree, delimiter=';', encoding='utf-8', dtype=str)
    if df.empty:
        print("Aucune donnée dans le fichier d'entrée.")
        sys.exit(1)
    
    # Convertir la colonne 'timestamp' en float (timestamp en millisecondes)
    try:
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors='coerce')
    except Exception as e:
        print("Erreur lors de la conversion de 'timestamp':", e)
        sys.exit(1)
    
    # Utiliser le premier timestamp comme référence et convertir en minutes
    ref_timestamp = df["timestamp"].iloc[0]
    
    resultats = []
    for _, row in df.iterrows():
        try:
            ts = float(row["timestamp"])
        except Exception:
            continue
        temps_min = (ts - ref_timestamp) / (60 * 1000)  # Conversion millisecondes -> minutes
        porteur = calcul_porteur(row)
        if porteur is None:
            continue
        porteur_team, porteur_x, porteur_y = porteur
        
        # Extraction des positions des joueurs (player_1 à player_22)
        joueurs = []
        for i in range(1, TOTAL_PLAYERS+1):
            champ = row.get(f"player_{i}", "")
            if not isinstance(champ, str):
                champ = str(champ)
            champ = champ.strip()
            if not champ:
                continue
            parts = champ.split(',')
            if len(parts) < 5:
                continue
            try:
                team = int(parts[0].strip())
                x = conv_float(parts[3])
                y = conv_float(parts[4])
            except Exception:
                continue
            joueurs.append((team, x, y))
        if not joueurs:
            continue
        
        # Recherche du défenseur le plus proche parmi les joueurs adverses
        min_dist_def = float('inf')
        defenseur = None
        for joueur in joueurs:
            team, x, y = joueur
            if team == porteur_team:
                continue
            d = distance(porteur_x, porteur_y, x, y)
            if d < min_dist_def:
                min_dist_def = d
                defenseur = joueur
        if defenseur is None:
            continue
        defenseur_team, defenseur_x, defenseur_y = defenseur
        
        resultats.append((temps_min, porteur_team, porteur_x, porteur_y,
                           defenseur_team, defenseur_x, defenseur_y, min_dist_def))
    
    df_result = pd.DataFrame(resultats, columns=["temps_min", "porteur_team", "porteur_x", "porteur_y",
                                                 "defenseur_team", "defenseur_x", "defenseur_y", "distance"])
    return df_result

def exporter_et_tracer(df_result, csv_export, png_export):
    """
    Exporte le DataFrame df_result dans un fichier CSV et trace un graphique PNG de l'évolution
    de la distance entre le porteur et le défenseur le plus proche.
    """
    df_result.to_csv(csv_export, sep=';', index=False, encoding='utf-8')
    print(f"Résultats exportés dans {csv_export}")
    
    plt.figure(figsize=(10, 6))
    plt.plot(df_result["temps_min"], df_result["distance"], marker='o', linestyle='-', color='b')
    plt.xlabel("Temps (min)")
    plt.ylabel("Distance (m)")
    plt.title("Distance entre porteur et défenseur le plus proche")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(png_export, dpi=300)
    plt.show()
    print(f"Graphique exporté sous {png_export}")

def main():
    if len(sys.argv) != 3:
        print("Usage : python Calcul défenseur le plus proche.py <fichier_traitement> <fichier_defenseur>")
        sys.exit(1)
    
    fichier_entree = sys.argv[1]  # Fichier CSV issu de Code traitement
    fichier_export = sys.argv[2]  # Fichier CSV de sortie (par exemple, défenseur_le_plus_proche.csv)
    png_export = os.path.splitext(fichier_export)[0] + ".png"
    
    df_result = calculer_distance_defenseur(fichier_entree)
    exporter_et_tracer(df_result, fichier_export, png_export)

if __name__ == "__main__":
    main()
