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
    Identifie le porteur de balle, y compris les gardiens des équipes 0 et 1 (respectivement identifiés
    par les équipes 3 et 4 dans les données).
    """
    ball_parts = row["ball"].split(',')
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
        champ = str(row.get(f"player_{i}", "")).strip()
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
        
        # Vérification si le joueur est plus proche du ballon
        d = distance(x, y, ball_x, ball_y)
        if d < min_dist:
            min_dist = d
            porteur = (team, x, y)
    
    return porteur

def calculer_distance_defenseur(fichier_entree):
    """
    Modifié pour tenir compte des gardiens comme porteurs de balle et pour garantir une variation correcte
    de la distance du défenseur le plus proche.
    
    Retourne un DataFrame avec les colonnes :
      temps_min, distance_team1, distance_team2
      
    Pour chaque ligne :
      - Si le porteur appartient à l'équipe 0 ou est gardien de l'équipe (identifié par 3), alors\n        distance_team1 = NaN et distance_team2 = distance (défenseur le plus proche parmi l'équipe 2).\n      - Si le porteur appartient à l'équipe 1 ou est gardien de l'équipe (identifié par 4), alors\n        distance_team1 = distance (défenseur le plus proche parmi l'équipe 1) et distance_team2 = NaN.
    """
    df = pd.read_csv(fichier_entree, delimiter=';', encoding='utf-8', dtype=str)
    if df.empty:
        print("Aucune donnée dans le fichier d'entrée.")
        sys.exit(1)

    df["timestamp"] = pd.to_numeric(df["timestamp"], errors='coerce')
    ref_timestamp = df["timestamp"].iloc[0]
    
    resultats = []
    
    for _, row in df.iterrows():
        try:
            ts = float(row["timestamp"])
        except Exception:
            continue
        temps_min = (ts - ref_timestamp) / (60 * 1000)
        
        porteur = calcul_porteur(row)
        if porteur is None:
            continue
        porteur_team, porteur_x, porteur_y = porteur
        
        joueurs = []
        for i in range(1, TOTAL_PLAYERS+1):
            champ = str(row.get(f"player_{i}", "")).strip()
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
        
        min_dist_def = float('inf')
        for joueur in joueurs:
            team, x, y = joueur
            if team == porteur_team:
                continue
            d = distance(porteur_x, porteur_y, x, y)
            if d < min_dist_def:
                min_dist_def = d
        
        if porteur_team in [0, 3]:  # Équipe 0 ou gardien de l'équipe 0
            distance_team1 = float('nan')
            distance_team2 = min_dist_def
        elif porteur_team in [1, 4]:  # Équipe 1 ou gardien de l'équipe 1
            distance_team1 = min_dist_def
            distance_team2 = float('nan')
        else:
            continue
        
        resultats.append((temps_min, distance_team1, distance_team2))
    
    df_result = pd.DataFrame(resultats, columns=["temps_min", "distance_team1", "distance_team2"])
    return df_result

def exporter(df_result, csv_export):
    """
    Exporte le DataFrame df_result dans un fichier CSV 
    """
    df_result.to_csv(csv_export, sep=';', index=False, encoding='utf-8')
    print(f"Résultats exportés dans {csv_export}")
    
def lineariser_dataframe(df, intervalle_sec):
    """
    Linéarise le DataFrame en regroupant les points sur des intervalles d'une durée de 'intervalle_sec' secondes.
    """
    df['temps_sec'] = df['temps_min'] * 60
    df['bin_sec'] = (df['temps_sec'] // intervalle_sec) * intervalle_sec
    df_linearise = df.groupby('bin_sec').mean().reset_index()
    df_linearise['temps_min'] = df_linearise['bin_sec'] / 60.0
    df_linearise = df_linearise.drop(columns=['temps_sec', 'bin_sec'])
    return df_linearise

def main():
    if len(sys.argv) != 3:
        print("Usage : python Calcul défenseur le plus proche.py <fichier_traitement> <fichier_defenseur>")
        sys.exit(1)
    
    fichier_entree = sys.argv[1]  # Fichier CSV issu de Code traitement
    fichier_export = sys.argv[2]  # Chemin pour le fichier CSV de sortie (par exemple, défenseur_le_plus_proche.csv)
    png_export = os.path.splitext(fichier_export)[0] + ".png"
    
    df_result = calculer_distance_defenseur(fichier_entree)
    # Optionnel : linéariser les données si besoin (par exemple, intervalle de 10 secondes)
    df_linearise = lineariser_dataframe(df_result, intervalle_sec=10)
    
    # On peut exporter et tracer le DataFrame linéarisé ou le DataFrame initial\n    # ici nous utilisons le DataFrame linéarisé\n    exporter_et_tracer(df_linearise, fichier_export, png_export)

if __name__ == "__main__":
    main()
