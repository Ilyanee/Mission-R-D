#!/usr/bin/env python3
import csv
import math

def conv_float(s):
    """Convertit une chaîne avec une virgule en décimal."""
    return float(s.replace(',', '.'))

def distance(x1, y1, x2, y2):
    """Calcule la distance euclidienne entre deux points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calcul_porteur(row):
    """
    Calcule le porteur de balle pour une ligne du fichier match.
    On utilise le dernier champ (ball) pour extraire la position du ballon,
    puis on parcourt les segments joueurs (colonnes 2 à avant-dernier) afin
    de déterminer le joueur le plus proche du ballon.
    
    Retourne un tuple (porteur_team, porteur_x, porteur_y) ou None si non trouvé.
    """
    # Extraction de la position du ballon depuis le dernier champ
    ball_field = row[-1]
    ball_parts = ball_field.split(',')
    if len(ball_parts) < 2:
        return None
    try:
        ball_x = conv_float(ball_parts[0])
        ball_y = conv_float(ball_parts[1])
    except ValueError:
        return None

    min_dist = float('inf')
    porteur = None

    # Parcours des segments joueurs (colonnes 2 à avant-dernier)
    for p in row[2:-1]:
        p = p.strip()
        if not p:
            continue
        parts = p.split(',')
        if len(parts) < 5:
            continue
        try:
            team = int(parts[0])
            x = conv_float(parts[3])
            y = conv_float(parts[4])
        except ValueError:
            continue
        d = distance(x, y, ball_x, ball_y)
        if d < min_dist:
            min_dist = d
            porteur = (team, x, y)
    return porteur

def calculer_distance_defenseur(match_filename):
    """
    Pour chaque instant du match (fichier complet avec toutes les positions des joueurs),
    détermine :
      - Le porteur de balle en calculant, pour la ligne courante, le joueur le plus proche du ballon.
      - Parmi les joueurs de l’équipe adverse, le défenseur le plus proche du porteur.
      - La distance correspondante entre le porteur et ce défenseur.
    
    Le fichier complet doit avoir pour chaque ligne le format :
       timestamp;periode;player_1;player_2;...;player_22;ball
    Chaque segment joueur est au format "team,ID,numero,x,y".
    
    Retourne une liste de tuples :
      (temps_min, porteur_team, porteur_x, porteur_y,
       defenseur_team, defenseur_x, defenseur_y, distance)
    """
    resultats = []
    ref_timestamp = None

    with open(match_filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        # Tenter d'ignorer un éventuel header
        header = next(reader, None)
        if header and not header[0].isdigit():
            pass
        else:
            f.seek(0)
            reader = csv.reader(f, delimiter=';')
        
        for row in reader:
            if not row:
                continue
            # Conversion du timestamp (premier champ) en minutes
            try:
                ts = int(row[0])
            except ValueError:
                continue
            if ref_timestamp is None:
                ref_timestamp = ts
            temps_min = (ts - ref_timestamp) / (60 * 1e9)  # conversion nanosecondes -> minutes

            # Calcul du porteur de balle pour la ligne actuelle
            porteur = calcul_porteur(row)
            if porteur is None:
                continue
            porteur_team, porteur_x, porteur_y = porteur

            # Extraction des joueurs pour le calcul du défenseur
            joueurs = []
            for p in row[2:-1]:
                p = p.strip()
                if not p:
                    continue
                parts = p.split(',')
                if len(parts) < 5:
                    continue
                try:
                    team = int(parts[0])
                    x = conv_float(parts[3])
                    y = conv_float(parts[4])
                except ValueError:
                    continue
                joueurs.append((team, x, y))
            if not joueurs:
                continue

            # Recherche du défenseur : parmi les joueurs de l'équipe opposée, on prend celui
            # le plus proche du porteur
            min_dist_def = float('inf')
            defenseur = None
            for joueur in joueurs:
                team, x, y = joueur
                if team == porteur_team:
                    continue
                d = distance(porteur_x, porteur_y, x, y)
                if d < min_dist_def:
                    min_dist_def = d
                    defenseur = joueur
            if defenseur is None:
                continue
            defenseur_team, defenseur_x, defenseur_y = defenseur

            resultats.append((temps_min, porteur_team, porteur_x, porteur_y,
                              defenseur_team, defenseur_x, defenseur_y, min_dist_def))
    return resultats

def main():
    # Nom du fichier complet du match
    match_filename = "match.txt"
    
    resultats = calculer_distance_defenseur(match_filename)
    
    print("Défenseur le plus proche pour chaque instant :")
    for res in resultats:
        (temps_min, porteur_team, porteur_x, porteur_y,
         defenseur_team, defenseur_x, defenseur_y, dist) = res
        print(f"À {temps_min:.3f} min – Porteur (équipe {porteur_team} @ {porteur_x:.3f}, {porteur_y:.3f}) / "
              f"Défenseur (équipe {defenseur_team} @ {defenseur_x:.3f}, {defenseur_y:.3f}) : distance = {dist:.2f}")

if __name__ == "__main__":
    main()
