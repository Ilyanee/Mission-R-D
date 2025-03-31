#!/usr/bin/env python3
import csv
import math

def conv_float(s):
    """Convertit une chaîne avec une virgule en décimal."""
    return float(s.replace(',', '.'))

def lire_donnees_porteur(filename):
    """
    Lit le fichier converti contenant les informations du porteur.
    Chaque ligne doit avoir le format :
       porteur_team;porteur_x;porteur_y;temps_min
    Retourne une liste de tuples (temps_min, porteur_team, porteur_x, porteur_y).
    """
    donnees = []
    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            try:
                team = int(row["porteur_team"])
                x = float(row["porteur_x"])
                y = float(row["porteur_y"])
                temps_min = float(row["temps_min"])
                donnees.append((temps_min, team, x, y))
            except ValueError:
                continue
    # On trie par temps au cas où
    donnees.sort(key=lambda rec: rec[0])
    return donnees

def distance(x1, y1, x2, y2):
    """Calcule la distance euclidienne entre deux points."""
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

def calculer_distance_defenseur(match_filename, porteur_data):
    """
    Pour chaque instant du match (fichier complet avec toutes les positions des joueurs),
    utilise la position du porteur issue du fichier converti (porteur_data) pour déterminer :
      - Parmi les joueurs de l’équipe adverse, qui est le défenseur le plus proche du porteur,
      - La distance correspondante.
    
    Le fichier complet est supposé avoir pour chaque ligne le format suivant :
      timestamp;periode;player_1;player_2;...;player_22;ball
    Chaque segment joueur est au format "team,?, ?, x, y".
    Le dernier champ "ball" est ignoré ici.
    
    On suppose que les enregistrements du fichier complet et du fichier converti sont alignés (même ordre).
    
    Retourne une liste de tuples :
      (temps_min, porteur_team, porteur_x, porteur_y,
       defenseur_team, defenseur_x, defenseur_y, distance)
    """
    resultats = []
    ref_timestamp = None
    porteur_index = 0  # pour accéder aux enregistrements de porteur_data
    with open(match_filename, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=';')
        # Optionnel : ignorer l'en-tête s'il existe
        header = next(reader, None)
        # Si la première colonne de l'en-tête n'est pas numérique, on le considère comme un header
        if header and not header[0].isdigit():
            pass
        else:
            # Le premier enregistrement fait partie des données
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

            # Vérification que nous avons un enregistrement porteur correspondant
            if porteur_index >= len(porteur_data):
                break
            # On suppose que l'enregistrement dans porteur_data correspond (ou est très proche) à temps_min
            porteur_rec = porteur_data[porteur_index]
            porteur_index += 1
            temps_porteur, porteur_team, porteur_x, porteur_y = porteur_rec
            # (On peut ajouter ici une vérification ou interpolation si les temps divergent)

            # Extraction des joueurs à partir du 3ème champ jusqu'à l'avant-dernier (le dernier étant le ballon)
            joueurs = []
            for p in row[2:-1]:
                p = p.strip()
                if not p:
                    continue
                parts = p.split(',')
                # On attend au moins 5 valeurs : team, id, numéro, x, y
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

            # Parmi les joueurs de l'équipe adverse du porteur, on cherche celui le plus proche du porteur
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
            # Si aucun défenseur n'est trouvé, on ignore cet instant
            if defenseur is None:
                continue
            defenseur_team, defenseur_x, defenseur_y = defenseur

            resultats.append((temps_min, porteur_team, porteur_x, porteur_y,
                              defenseur_team, defenseur_x, defenseur_y, min_dist_def))
    return resultats

def main():
    # Fichiers d'entrée
    fichier_porteur = "output.txt"  # Nouveau format : porteur_team;porteur_x;porteur_y;temps_min
    fichier_match = "match.txt"       # Fichier complet avec toutes les positions des joueurs

    # Lecture du fichier converti avec les informations du porteur à chaque instant
    porteur_data = lire_donnees_porteur(fichier_porteur)
    print("Données du porteur (nouveau format) :")
    for rec in porteur_data:
        temps_min, team, x, y = rec
        print(f"  Temps {temps_min:.3f} min – Équipe {team} – Position ({x:.3f}, {y:.3f})")

    # Calcul pour chaque instant du match du défenseur le plus proche du porteur
    resultats = calculer_distance_defenseur(fichier_match, porteur_data)
    print("\nDéfenseur le plus proche pour chaque instant :")
    for res in resultats:
        (temps_min, porteur_team, porteur_x, porteur_y,
         defenseur_team, defenseur_x, defenseur_y, dist) = res
        print(f"À {temps_min:.3f} min – Porteur (équipe {porteur_team} @ {porteur_x:.3f}, {porteur_y:.3f}) / "
              f"Défenseur (équipe {defenseur_team} @ {defenseur_x:.3f}, {defenseur_y:.3f}) : distance = {dist:.2f}")

if __name__ == "__main__":
    main()
