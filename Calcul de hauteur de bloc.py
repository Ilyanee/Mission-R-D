# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys

def extraire_temps(timestamp_str):
    """
    Extrait le temps en millisecondes à partir de la chaîne du timestamp.
    """
    try:
        return int(timestamp_str)
    except ValueError:
        return np.nan

def extraire_info_joueur(champ):
    """
    Extrait le numéro d'équipe et la coordonnée X à partir d'une chaîne représentant un joueur.
    Format attendu : "team,ID,numero,x,y"
    Exemple : "0,540100,9,52.607,33.316" -> retourne ("0", 52.607)
    """
    try:
        parts = champ.split(',')
        if len(parts) >= 5:
            team = parts[0].strip()
            x = float(parts[3])
            return team, x
        return None, None
    except ValueError:
        return None, None

def traiter_fichier(fichier_entree):
    """
    Lit le fichier filtré au format :
    timestamp;periode;player_1;player_2;...;player_22;ball
    et retourne un DataFrame contenant la hauteur moyenne des blocs.
    """
    df = pd.read_csv(fichier_entree, delimiter=';', encoding='utf-8')

    data = []
    
    for _, row in df.iterrows():
        timestamp_str = str(row['timestamp'])
        temps_ms = extraire_temps(timestamp_str)
        if np.isnan(temps_ms):
            continue
        temps_min = temps_ms / 60000.0
        
        for i in range(1, 23):
            champ = str(row[f'player_{i}']).strip()
            if not champ or champ.startswith(':'):
                continue
            team, x = extraire_info_joueur(champ)
            if team is None or x is None:
                continue
            if team in ['3', '4']:  # Ignorer les gardiens
                continue
            data.append((temps_min, team, x))
    
    df_data = pd.DataFrame(data, columns=['temps_min', 'team', 'x'])
    df_grouped = df_data.groupby(['temps_min', 'team'], as_index=False)['x'].mean()
    df_pivot = df_grouped.pivot(index='temps_min', columns='team', values='x')
    df_pivot.columns = [f"Equipe {col}" for col in df_pivot.columns]
    df_pivot = df_pivot.reset_index().sort_values(by='temps_min')
    df_pivot['temps_min'] = df_pivot['temps_min'] - df_pivot['temps_min'].min()

    return df_pivot

def exporter_et_tracer(df, fichier_export):
    """
    Exporte le DataFrame dans un fichier CSV et trace la hauteur moyenne des équipes.
    """
    df.to_csv(fichier_export, sep=';', index=False, encoding='utf-8')
    print(f"Résultats exportés dans {fichier_export}")
    
    plt.figure(figsize=(10, 6))
    for col in df.columns:
        if col != 'temps_min':
            plt.plot(df['temps_min'], df[col], label=col)
    plt.xlabel("Temps (min)")
    plt.ylabel("Hauteur moyenne (coordonnée X)")
    plt.title("Hauteur moyenne (coordonnée X) des joueurs par équipe")
    plt.legend()
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Utilisation : python calcul_hauteur_bloc.py <fichier_entree> <fichier_export>")
        sys.exit(1)

    fichier_entree = sys.argv[1]
    fichier_export = sys.argv[2]

    df_resultats = traiter_fichier(fichier_entree)
    exporter_et_tracer(df_resultats, fichier_export)
