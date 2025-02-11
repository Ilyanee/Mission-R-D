# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 09:53:40 2025

@author: Luis
"""
import pandas as pd

def traiter_donnees(fichier_entree, fichier_sortie, intervalle_ms=520):
    # Lire les lignes du fichier d'entrée
    with open(fichier_entree, 'r') as f:
        lignes = f.readlines()

    lignes_filtrees = []
    
    for ligne in lignes:
        champs = ligne.strip().split(';')
        if len(champs) < 2:
            continue  # Ignorer les lignes mal formatées
        
        # La deuxième colonne est attendue au format "A:B"
        if ':' in champs[1]:
            A, B = champs[1].split(':', 1)
        else:
            continue  # Si le format n'est pas celui attendu, on passe à la ligne suivante
        
        # Extraire le premier nombre de A (avant la première virgule)
        first_number = A.split(',')[0]
        if not first_number.isdigit():
            continue
        temps_ms = int(first_number)
        
        # Conserver la ligne uniquement si le temps (en ms) est un multiple de intervalle_ms (500 ms)
        if temps_ms % intervalle_ms != 0:
            continue
        
        # Construire la nouvelle valeur pour la deuxième colonne :
        # Conserver le premier nombre, puis un ";" puis tout ce qu'il y a après le ":"
        nouvelle_valeur = first_number + ";" + B
        champs[1] = nouvelle_valeur
        
        # Recomposer la ligne en supprimant la première colonne (timestamp)
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




