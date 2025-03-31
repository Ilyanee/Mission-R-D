# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 15:36:22 2025

@author: Luis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def parse_score_code(score_str):
    """
    Convertit un code de score sur 2 chiffres en label "A-B".
    Exemple : "10" -> "1-0".
    """
    score_str = score_str.strip()
    if len(score_str) == 2 and score_str.isdigit():
        return f"{score_str[0]}-{score_str[1]}"
    return score_str

def lire_fichier_scores(fichier_txt):
    """
    Lit un fichier texte contenant des lignes du type :
      temps_min;score_code
    Exemple : "15.1245;10" signifie qu'à 15.1245 minutes, le score devient 1-0.
    Retourne un DataFrame trié avec les colonnes : score_time, score_code et score_label.
    """
    df = pd.read_csv(fichier_txt, sep=';', header=None, names=['score_time', 'score_code'])
    df['score_time'] = pd.to_numeric(df['score_time'], errors='coerce')
    df['score_label'] = df['score_code'].apply(parse_score_code)
    df = df.sort_values('score_time').reset_index(drop=True)
    return df

def associer_score(df_data, df_score):
    """
    Associe à chaque ligne de df_data (basé sur 'temps_min') le score courant,
    en utilisant merge_asof (join temporel backward).
    """
    df_data = df_data.sort_values('temps_min').reset_index(drop=True)
    df_score = df_score.sort_values('score_time').reset_index(drop=True)
    df_merged = pd.merge_asof(
        df_data, 
        df_score, 
        left_on='temps_min', 
        right_on='score_time', 
        direction='backward'
    )
    return df_merged

def tracer_boxplots(df, param_cols, group_col='score_label'):
    """
    Trace des boxplots pour les colonnes indiquées dans param_cols,
    groupées par la colonne group_col.
    """
    for param in param_cols:
        plt.figure(figsize=(8, 5))
        groups = []
        labels = []
        for score, group in df.groupby(group_col):
            s = group[param].dropna()
            groups.append(s)
            labels.append(score)
        plt.boxplot(groups, labels=labels)
        plt.xlabel("Score")
        plt.ylabel(param)
        plt.title(f"Boxplot de {param} par score")
        plt.tight_layout()
        plt.show()

# ---------------------------
# Exécution directe du script
# ---------------------------

# Remplacez les chemins ci-dessous par vos chemins réels
fichier_csv_calcul = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM hauteur_bloc.csv"  # Fichier CSV issu du calcul de hauteur de bloc
fichier_txt_scores = r"C:\Users\Luis\Documents\Fichiers matchs\scores.txt"  # Fichier TXT contenant les scores
fichier_export = r"C:\Users\Luis\Documents\Fichiers matchs\boxplots.csv"  # Fichier CSV de sortie pour le DataFrame fusionné

# Lecture du fichier CSV de hauteur de bloc
df_data = pd.read_csv(fichier_csv_calcul, sep=';', encoding='utf-8')
# On suppose que df_data contient une colonne "temps_min" et des colonnes comme "Equipe 0", "Equipe 1", etc.

# Lecture du fichier de scores
df_score = lire_fichier_scores(fichier_txt_scores)

# Association du score à chaque instant
df_merged = associer_score(df_data, df_score)

# Exportation du DataFrame fusionné dans un fichier CSV
df_merged.to_csv(fichier_export, sep=';', index=False, encoding='utf-8')
print(f"Le DataFrame fusionné a été exporté dans {fichier_export}")

# Définition des colonnes à tracer (toutes sauf celles utilisées pour le merge)
param_cols = [col for col in df_merged.columns if col not in ['temps_min', 'score_time', 'score_code', 'score_label']]

# Tracé des boxplots groupés par score
tracer_boxplots(df_merged, param_cols, group_col='score_label')
