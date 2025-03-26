#!/usr/bin/env python3
import csv
import math

# Pour faciliter la conversion des nombres avec des virgules en décimaux
def conv_float(s):
    return float(s.replace(',', '.'))

# Fonction pour calculer la distance euclidienne entre deux points (x1, y1) et (x2, y2)
def distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# On suppose que le premier timestamp lu correspond au temps zéro (en minutes)
ref_timestamp = None

# Fonction pour convertir un timestamp en minutes par rapport au temps de référence
def timestamp_to_minutes(ts, ref):
    return (ts - ref) / (60 * 1e9)  # Conversion nanosecondes → minutes

# Fonction pour extraire les informations du porteur de balle
def extract_porteur(row):
    global ref_timestamp

    # Extraction du timestamp et de la période
    timestamp_str = row[0]
    periode = row[1]

    # Conversion du timestamp
    ts = int(timestamp_str)
    if ref_timestamp is None:
        ref_timestamp = ts
    temps_min = timestamp_to_minutes(ts, ref_timestamp)

    # Récupération de la position du ballon (dernier champ)
    ball_field = row[-1]
    ball_parts = ball_field.split(',')
    ball_x = conv_float(ball_parts[0])
    ball_y = conv_float(ball_parts[1])

    # Initialisation du porteur de balle
    min_distance = float('inf')
    porteur_team = None
    porteur_x = None
    porteur_y = None

    # Les joueurs sont dans les colonnes 2 à -2
    players = row[2:-1]

    for p in players:
        parts = p.split(',')
        if len(parts) < 5:
            continue
        team = parts[0]
        x = conv_float(parts[3])
        y = conv_float(parts[4])

        # Calcul de la distance joueur-ballon
        dist = distance(x, y, ball_x, ball_y)

        # Mise à jour si ce joueur est plus proche du ballon
        if dist < min_distance:
            min_distance = dist
            porteur_team = team
            porteur_x = x
            porteur_y = y

    return (porteur_team, porteur_x, porteur_y, temps_min)

# Nom des fichiers d'entrée et de sortie
input_filename = "input.txt"
output_filename = "output.txt"

with open(input_filename, "r", encoding="utf-8") as fin, \
     open(output_filename, "w", newline='', encoding="utf-8") as fout:
    
    reader = csv.reader(fin, delimiter=';')
    writer = csv.writer(fout, delimiter=';')
    
    # Écrire l'en-tête dans le fichier de sortie
    writer.writerow(["porteur_team", "porteur_x", "porteur_y", "temps_min"])
    
    # Pour chaque ligne du fichier d'entrée
    for row in reader:
        if not row or row[0].lower() == "timestamp":
            continue
        porteur_team, porteur_x, porteur_y, temps_min = extract_porteur(row)
        writer.writerow([porteur_team, f"{porteur_x:.3f}", f"{porteur_y:.3f}", f"{temps_min:.3f}"])
