# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 17:07:00 2025

# -*- coding: utf-8 -*-
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def extraire_temps(col_str): #ajt extraction timestamp eventuellement en les ignorant à la lecture
    """
    Extrait le temps en millisecondes à partir du premier élément
    de la chaîne (avant la première virgule).
    Exemple : "0,1,0:0" -> retourne 0.
    """
    try:
        return np.array(int(col_str.split(';')[0]), int(col_str.split(',')[0]))
    except Exception:
        return np.zero

def extraire_info_joueur(champ):
    """
    Extrait le numéro d'équipe et la coordonnée X à partir d'une chaîne représentant un joueur.
    Format attendu : "team,ID,numero,x,y"
    Exemple : "0,615385,12,44.96,40.174" -> retourne ("0", 44.96)
    """
    try:
        parts = champ.split(',')
        if len(parts) >= 5:
            team = parts[0].strip()
            x = float(parts[3])  # On prend la coordonnée X
            return team, x
        else:
            return None, None
    except Exception:
        return None, None

def traiter_fichier(fichier):
    """
    Lit le fichier filtré (colonnes séparées par ;) et retourne un DataFrame contenant :
      - 'temps_min' : le temps extrait de la première colonne (converti en minutes)
      - Pour chaque équipe (autre que 3 et 4), la moyenne des coordonnées X (hauteur moyenne)
        des joueurs à cet instant.
    La moyenne est calculée en sommant les coordonnées X des joueurs d'une équipe et en
    divisant par leur nombre.
    """
    data = []  # Liste de tuples (temps_min, team, x)
    
    with open(fichier, 'r') as f:
        lignes = f.readlines()
    
    for ligne in lignes:
        colonnes = ligne.strip().split(';')
        if len(colonnes) < 2:
            continue
        
        # Extraire le temps depuis la première colonne et le convertir en minutes
        temps_ms = extraire_temps(colonnes[0])
        if np.isnan(temps_ms):
            continue
        temps_min = temps_ms / 60000.0
        
        # Parcourir les colonnes à partir de la deuxième
        for champ in colonnes[1:]:
            champ = champ.strip()
            if not champ or champ.startswith(':'):
                continue  # Ignorer les colonnes vides ou celles commençant par ":" (ballon)
            team, x = extraire_info_joueur(champ)
            if team is None or x is None:
                continue
            # Ignorer les gardiens (équipes 3 et 4)
            if team in ['3', '4']:
                continue
            data.append((temps_min, team, x))
    
    # Créer un DataFrame à partir de la liste des tuples
    df = pd.DataFrame(data, columns=['temps_min', 'team', 'x'])
    # Calculer la moyenne pour chaque instant et chaque équipe
    df_grouped = df.groupby(['temps_min', 'team'], as_index=False)['x'].mean()
    # Faire un pivot pour avoir une colonne par équipe
    df_pivot = df_grouped.pivot(index='temps_min', columns='team', values='x')
    # Renommer les colonnes
    df_pivot.columns = [f"Equipe {col}" for col in df_pivot.columns]
    df_pivot = df_pivot.reset_index().sort_values(by='temps_min')
    return df_pivot

def exporter_et_tracer(df, fichier_export):
    # Exporter le tableau dans un fichier texte (CSV avec séparateur ;)
    df.to_csv(fichier_export, sep=';', index=False)
    print(f"Tableau exporté dans {fichier_export}")
    
    # Tracer les courbes
    plt.figure(figsize=(10, 6))
    for col in df.columns:
        if col != 'temps_min':
            plt.plot(df['temps_min'], df[col], label=col)
    plt.xlabel("Temps (min)")
    plt.ylabel("Hauteur moyenne (coordonnée X)")
    plt.title("Hauteur moyenne (coordonnée X) des joueurs par équipe au cours du temps")
    plt.legend()
    plt.tight_layout()
    plt.show()

# Exemple d'utilisation
fichier_entree = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM filtré.txt"
fichier_export = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM resultats.txt"
df_resultats = traiter_fichier(fichier_entree)
exporter_et_tracer(df_resultats, fichier_export)
