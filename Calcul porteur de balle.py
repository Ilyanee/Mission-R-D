# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 14:32:20 2025

@author: Luis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def extraire_coords_joueur(champ):
    """
    Extrait le numéro d'équipe et la coordonnée x d'un joueur.
    Format attendu : "team,ID,numero,x,y"
    Exemple : "0,540100,9,52.607,33.316" -> retourne ("0", 52.607)
    """
    try:
        parts = champ.split(',')
        if len(parts) >= 4:
            team = parts[0].strip()
            x = float(parts[3])
            return team, x
        else:
            return None, np.nan
    except Exception:
        return None, np.nan

def calculer_courses_algebriques_x(fichier):
    """
    Lit le fichier filtré et calcule la somme des courses algébriques en x à chaque instant
    pour chaque équipe (hors gardiens). Retourne un DataFrame.
    """
    with open(fichier, 'r') as f:
        lignes = f.readlines()

    # Listes pour stocker les données
    temps = []
    equipes_x = {}

    for ligne in lignes:
        colonnes = ligne.strip().split(';')
        if len(colonnes) < 2:
            continue

        try:
            t_ms = int(colonnes[0])
        except:
            continue
        
        temps_min = t_ms / 60000.0
        temps.append(temps_min)
        
        courses_x = {}

        # Parcourir les colonnes de joueurs
        for col in range(1, len(colonnes)-2):  # Exclure la colonne ballon
            cell = colonnes[col].strip()
            team, x = extraire_coords_joueur(cell)
            
            if team in ['3', '4']:  # Ignorer les gardiens
                continue

            # Stocker les positions x dans une liste par équipe
            if team not in courses_x:
                courses_x[team] = []
            courses_x[team].append(x)

        # Ajouter la somme des déplacements en x par équipe
        for equipe, positions_x in courses_x.items():
            somme_courses = sum(positions_x)  # Somme des courses algébriques
            if equipe not in equipes_x:
                equipes_x[equipe] = []
            equipes_x[equipe].append(somme_courses)

    # Création du DataFrame
    df = pd.DataFrame({"temps_min": temps})

    for equipe, values in equipes_x.items():
        df[f"Equipe {equipe}"] = pd.Series(values).diff()  # Différence entre instants

    df = df.dropna()  # Suppression de la première ligne avec NaN

    return df

def exporter_et_tracer_courses(df, fichier_export):
    """
    Exporte le DataFrame et trace l'évolution des courses algébriques en x.
    """
    df.to_csv(fichier_export, sep=';', index=False)
    print(f"Tableau exporté dans {fichier_export}")

    # Tracé
    plt.figure(figsize=(10, 6))
    for col in df.columns[1:]:  # Ignorer la colonne "temps_min"
        plt.plot(df["temps_min"], df[col], label=col, marker='o')

    plt.xlabel("Temps (min)")
    plt.ylabel("Courses algébriques en x")
    plt.title("Évolution des courses algébriques en x par équipe")
    plt.legend()
    plt.grid()
    plt.show()

# Exemple d'utilisation :
fichier_filtre = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM filtré.txt"
fichier_export = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM courses_x.txt"

df_courses = calculer_courses_algebriques_x(fichier_filtre)
exporter_et_tracer_courses(df_courses, fichier_export)
