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

    lignes_filtrees = []
    
    for ligne in lignes:
        champs = ligne.strip().split(';')
        if len(champs) < 2:
            continue  # Ignorer les lignes mal formatées
        
        # Vérifier si la deuxième colonne contient un deux-points
        if ':' in champs[1]:
            # Séparer la partie gauche et droite de la deuxième colonne
            left, right = champs[1].split(':', 1)
            # Extraire le premier nombre depuis la partie gauche
            first_num = left.split(',')[0]
            # Vérifier que ce nombre est numérique
            if first_num.isdigit():
                temps_ms = int(first_num)
            else:
                continue
            # Dans la partie droite, on supprime le premier élément
            right_parts = right.split(',')
            if len(right_parts) > 1:
                nouvelle_valeur = first_num + ',' + ','.join(right_parts[1:])
            else:
                nouvelle_valeur = first_num
            # Remplacer la deuxième colonne par la nouvelle valeur
            champs[1] = nouvelle_valeur
        else:
            # S'il n'y a pas de deux-points, on utilise le premier élément de la deuxième colonne
            first_num = champs[1].split(',')[0]
            if first_num.isdigit():
                temps_ms = int(first_num)
            else:
                continue

        # Filtrer la ligne si le temps est un multiple de l'intervalle (500 ms)
        if temps_ms % intervalle_ms == 0:
            # Supprimer la première colonne (timestamp) et reconstruire la ligne
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



