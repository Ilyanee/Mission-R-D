# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 11:34:25 2025

@author: Luis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

def extraire_temps(col_str):
    """
    Extrait le temps en millisecondes à partir du premier élément
    de la chaîne (avant la première virgule).
    Exemple : "0,1,0:0" -> retourne 0.
    """
    try:
        return int(col_str.split(',')[0])
    except Exception:
        return np.nan

def extraire_info_joueur(champ):
    """
    Extrait les informations d'un joueur.
    Format attendu : "team,ID,numero,x,y"
    Retourne un tuple (team, id, x)
    Exemple : "0,540100,9,52.607,33.316" -> ("0", "540100", 52.607)
    """
    try:
        parts = champ.split(',')
        if len(parts) >= 5:
            team = parts[0].strip()
            player_id = parts[1].strip()
            x = float(parts[3])
            return team, player_id, x
        else:
            return None, None, np.nan
    except Exception:
        return None, None, np.nan

def lire_donnees(fichier, equipe_cible="0"):
    """
    Lit le fichier filtré et retourne un dictionnaire où chaque clé est un temps (ms)
    et la valeur est un dictionnaire pour l'équipe cible qui associe l'ID du joueur à sa coordonnée x.
    On ignore les colonnes commençant par ":" (ballon) et on ne prend en compte que les joueurs de l'équipe cible.
    """
    data = {}
    with open(fichier, 'r') as f:
        lignes = f.readlines()
    
    for ligne in lignes:
        colonnes = ligne.strip().split(';')
        if len(colonnes) < 2:
            continue
        temps_ms = extraire_temps(colonnes[0])
        if np.isnan(temps_ms):
            continue
        # On ignore le timestamp d'origine, la ligne contient ensuite les infos des joueurs
        # On parcourt les colonnes à partir de la deuxième (index 1)
        joueurs = {}
        for champ in colonnes[1:]:
            champ = champ.strip()
            if not champ or champ.startswith(':'):
                continue
            team, player_id, x = extraire_info_joueur(champ)
            if team is None:
                continue
            # Ne prendre que l'équipe cible
            if team == equipe_cible:
                joueurs[player_id] = x
        data[temps_ms] = joueurs
    return data

def calculer_course(data):
    """
    À partir du dictionnaire data (clé = temps en ms, valeur = {player_id: x}),
    calcule pour l'équipe la somme des déplacements (distance absolue sur x) entre instants consécutifs.
    Retourne un DataFrame avec le temps en minutes et le cumul de course.
    """
    # Trier les clés (temps) par ordre croissant
    temps_trie = sorted(data.keys())
    cumul = 0.0
    resultats = []
    prev = None
    
    for t in temps_trie:
        joueurs_actuels = data[t]
        if prev is None:
            # Premier instant, aucun déplacement
            resultats.append((t/60000.0, cumul))
        else:
            # Pour chaque joueur présent dans les deux instants, calculer la différence absolue
            deplacement = 0.0
            for pid in joueurs_actuels:
                if pid in prev:
                    deplacement += abs(joueurs_actuels[pid] - prev[pid])
            cumul += deplacement
            resultats.append((t/60000.0, cumul))
        prev = joueurs_actuels
    df_course = pd.DataFrame(resultats, columns=["temps_min", "cumul_course"])
    return df_course

def exporter_et_tracer_course(df, fichier_export):
    # Exporter le DataFrame dans un fichier texte (CSV avec séparateur ;)
    df.to_csv(fichier_export, sep=';', index=False)
    print(f"Tableau exporté dans {fichier_export}")
    
    # Tracer la courbe du cumul de course en fonction du temps
    plt.figure(figsize=(10, 6))
    plt.plot(df["temps_min"], df["cumul_course"], label="Cumul de course", marker='o')
    plt.xlabel("Temps (min)")
    plt.ylabel("Cumul de course (m)")
    plt.title("Cumul des courses de l'équipe selon la coordonnée X au cours du temps")
    plt.legend()
    plt.tight_layout()
    plt.show()

# Exemple d'utilisation :
fichier_filtre = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM filtré.txt"
fichier_export = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM course.txt"

# Lire les données pour l'équipe "0" (peut être modifié pour une autre équipe)
data = lire_donnees(fichier_filtre, equipe_cible="0")
# Calculer le cumul de course (déplacements sur x) sur le temps
df_course = calculer_course(data)
# Exporter le tableau et tracer le graphique
exporter_et_tracer_course(df_course, fichier_export)
