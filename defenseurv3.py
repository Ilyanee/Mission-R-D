#!/usr/bin/env python3
import csv
import math
import os

def conv_float(s):
    """Convertit une chaîne avec une virgule en décimal."""
    return float(s.replace(',', '.'))

def distance(x1, y1, x2, y2):
    """Calcule la distance euclidienne entre deux points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calcul_porteur(row):
    """
    Calcule le porteur de balle pour une ligne du fichier match.
    Pour ce faire, il extrait la position du ballon depuis le dernier champ de la ligne,
    puis parcourt les segments joueurs (colonnes 2 à avant-dernier) afin de déterminer
    le joueur le plus proche du ballon.
    
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
    Pour chaque instant du match (fichier complet contenant toutes les positions des joueurs),
    détermine :
      - Le porteur de balle en calculant, pour la ligne courante, le joueur le plus proche du ballon.
      - Parmi les joueurs de l’équipe adverse, le défenseur le plus proche du porteur.
      - La distance correspondante entre le porteur et ce défenseur.
    
    Le fichier complet doit avoir pour chaque ligne le format :
      timestamp;periode;player_1;player_2;...;player_22;ball
    Chaque segment joueur est au format "team,ID,numero,x,y".
    
    Le timestamp (premier champ) est converti en minutes (en utilisant le premier timestamp comme référence).
    
    Les résultats sont enregistrés dans un fichier texte nommé :
         defenseur_nomDuMatch.txt
    où nomDuMatch est extrait du nom du fichier match sans l'extension.
    
    Chaque ligne du fichier résultat est au format :
      temps_min ; porteur_team ; porteur_x ; porteur_y ; defenseur_team ; defenseur_x ; defenseur_y ; distance
    """
    resultats = []
    ref_timestamp = None

    with open(match_filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        # Vérifier si la première ligne est un header
        header = next(reader, None)
        if header and not header[0].isdigit():
            # On garde le header et on continue la lecture
            pass
        else:
            # Le header n'existe pas, on revient au début
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
            temps_min = (ts - ref_timestamp) / (60 * 1e9)  # Conversion nanosecondes -> minutes

            # Calcul du porteur de balle à partir de la ligne
            porteur = calcul_porteur(row)
            if porteur is None:
                continue
            porteur_team, porteur_x, porteur_y = porteur

            # Extraction de la liste des joueurs (colonnes 2 à avant-dernier)
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

            # Recherche du défenseur le plus proche parmi les joueurs de l'équipe adverse
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

    # Générer le nom du fichier de sortie à partir du nom du match
    match_name = os.path.basename(match_filename).replace(".txt", "")
    output_filename = f"defenseur_{match_name}.txt"

    # Enregistrement des résultats dans le fichier de sortie
    with open(output_filename, "w", encoding="utf-8") as f_out:
        for res in resultats:
            # Format : temps_min;porteur_team;porteur_x;porteur_y;defenseur_team;defenseur_x;defenseur_y;distance
            ligne = f"{res[0]:.3f};{res[1]};{res[2]:.3f};{res[3]:.3f};{res[4]};{res[5]:.3f};{res[6]:.3f};{res[7]:.2f}"
            f_out.write(ligne + "\n")

    print(f"Résultats enregistrés dans {output_filename}")
    return output_filename

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: python defenseurv2.py <match_filename>")
        return

    match_filename = sys.argv[1]
    output_file = calculer_distance_defenseur(match_filename)
    print(f"Fichier généré : {output_file}")

if __name__ == "__main__":
    main()
