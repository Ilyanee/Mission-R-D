# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:53:40 2025

@author: Luis
"""

import pandas as pd

def traiter_donnees(fichier_entree, fichier_sortie, intervalle_ms=500):
    # Lire les lignes du fichier d'entrée
    with open(fichier_entree, 'r') as f:
        lignes = f.readlines()

    # Initialiser une liste pour stocker les lignes filtrées
    lignes_filtrees = []
    
    for ligne in lignes:
        champs = ligne.strip().split(';')
        
        if len(champs) < 2:
            continue  # Ignorer les lignes mal formatées
        
        # Extraire la première valeur avant la virgule dans la deuxième colonne
        premiere_valeur = champs[1].split(',')[0]
        
        if premiere_valeur.isdigit():
            temps_ms = int(premiere_valeur)
            
            # Garder la ligne si le temps est un multiple de 500 ms
            if temps_ms % intervalle_ms == 0:
                # Supprimer la première colonne (timestamp) avant d'ajouter la ligne
                ligne_filtre = ';'.join(champs[1:]) + '\n'
                lignes_filtrees.append(ligne_filtre)
    
    # Sauvegarder les lignes filtrées dans le fichier de sortie
    with open(fichier_sortie, 'w') as f:
        f.writelines(lignes_filtrees)
    
    print(f"Les données ont été filtrées et sauvegardées dans {fichier_sortie}.")

# Exemple d'utilisation
fichier_entree = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM 2.0 PUIS 2.3 08.08.2021\données match MHSC OM.txt"
fichier_sortie = r"C:\Users\Luis\Documents\Fichiers matchs\L1 J1 MHSC OM filtré.txt"
traiter_donnees(fichier_entree, fichier_sortie)


