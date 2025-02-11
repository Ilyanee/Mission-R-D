#!/usr/bin/env python3
import math

def compute_distance(x1, y1, x2, y2):
    """Calcule la distance euclidienne entre deux points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def parse_line(line):
    """
    Parse une ligne de données.
    
    Chaque ligne est de la forme :
      <temps_match> ; <segment_joueur> ; ... ; <segment_joueur> ; :<porteur_x>,<porteur_y>,<temps_min> ;
      
    Les segments joueurs sont de la forme :
      team,unused,joueur,x,y
    """
    line = line.strip()
    if not line:
        return None
    fields = line.split(';')
    
    # Le premier champ est le temps (exemple "0", "520", "1040")
    temps_match = fields[0]
    
    players = []
    ball_carrier = None  # porteur de balle : (x, y)
    
    # Parcours de tous les segments (on ignore les champs vides)
    for field in fields[1:]:
        field = field.strip()
        if not field:
            continue
        # Si le segment commence par ":" c'est le porteur de balle.
        if field.startswith(':'):
            # On enlève le caractère ":" et on découpe par la virgule.
            # On s’attend à obtenir [porteur_x, porteur_y, temps_min] (on n’utilise ici que les 2 premières valeurs)
            parts = field[1:].split(',')
            try:
                bx = float(parts[0])
                by = float(parts[1])
                ball_carrier = (bx, by)
            except (ValueError, IndexError):
                print("Erreur lors du parsing du porteur de balle:", field)
        else:
            # Segment joueur. On s'attend à avoir 5 valeurs séparées par des virgules.
            parts = field.split(',')
            if len(parts) < 5:
                continue
            try:
                team = int(parts[0])
                # On ne se sert pas de parts[1] et parts[2] (par exemple un identifiant ou le numéro du joueur)
                x = float(parts[3])
                y = float(parts[4])
                players.append((team, x, y))
            except ValueError:
                print("Erreur lors du parsing d'un joueur:", field)
                continue

    return temps_match, players, ball_carrier

def compute_defender_distance(temps_match, players, ball_carrier):
    """
    Détermine de quel côté se trouve le porteur (0 ou 1)
    en cherchant quel groupe possède un joueur très proche.
    
    Puis calcule la distance minimale entre le porteur et un joueur
    de l'équipe adverse (considéré ici comme le défenseur le plus proche).
    
    Retourne (ball_team, defender_team, distance_min) ou None si impossible.
    """
    if ball_carrier is None:
        return None
    bx, by = ball_carrier

    # On suppose que les équipes jouant sont 0 et 1.
    # Pour déterminer le camp du porteur, on calcule la plus petite distance
    # entre le porteur et les joueurs de chaque équipe.
    distances_by_team = {0: float('inf'), 1: float('inf')}
    for team, x, y in players:
        if team in distances_by_team:
            d = compute_distance(bx, by, x, y)
            if d < distances_by_team[team]:
                distances_by_team[team] = d

    # On considère que le porteur est du côté dont un joueur se trouve le plus près.
    if distances_by_team[0] < distances_by_team[1]:
        ball_team = 0
    else:
        ball_team = 1

    # L’équipe adverse sera considérée comme celle des défenseurs.
    defender_team = 1 if ball_team == 0 else 0

    # On parcourt les joueurs de l'équipe adverse pour trouver la distance minimale.
    min_distance = float('inf')
    for team, x, y in players:
        if team == defender_team:
            d = compute_distance(bx, by, x, y)
            if d < min_distance:
                min_distance = d

    if min_distance == float('inf'):
        min_distance = None

    return ball_team, defender_team, min_distance

def main():
    # Exemple de données (trois lignes) tel que fourni
    data = """0;0,540100,9,52.607,33.316;0,615385,12,44.96,40.174;0,656168,25,52.042,23.946;0,831112,10,52.335,57.354;0,838039,6,45.768,57.055;0,1064775,31,45.506,11.244;0,1088286,26,26.779,34.311;0,1162824,13,44.95,29.049;0,1260555,21,52.189,13.823;0,1283143,34,29.163,25.955;1,347822,10,52.428,43.403;1,847084,8,63.404,44.694;1,947732,17,52.663,17.73;1,956887,6,55.415,24.344;1,968133,4,66.915,16.95;1,972474,14,67.818,44.611;1,1050211,22,61.597,33.009;1,1106097,5,68.218,34.621;1,1131291,2,67.486,24.161;1,1159139,20,58.331,53.197;3,869970,16,5.07,33.046;4,397826,30,98.025,33.757;:52.5,34,0;
520;0,540100,9,53.265,33.058;0,615385,12,45.506,40.271;0,656168,25,52.141,24.203;0,831112,10,53.402,57.661;0,838039,6,46.374,57.16;0,1064775,31,45.556,11.536;0,1088286,26,28.517,39.586;0,1162824,13,45.032,29.252;0,1260555,21,52.561,13.787;0,1283143,34,29.341,25.658;1,347822,10,51.195,41.75;1,847084,8,63.682,44.966;1,947732,17,54.287,16.132;1,956887,6,55.416,24.497;1,968133,4,67.056,16.713;1,972474,14,67.959,44.634;1,1050211,22,61.317,34.204;1,1106097,5,68.331,34.886;1,1131291,2,67.551,24.427;1,1159139,20,58.858,53.367;3,869970,16,5.639,33.76;4,397826,30,97.394,33.548;:44,35.63,0;
1040;0,540100,9,54.941,31.999;0,615385,12,46.044,40.192;0,656168,25,52.816,24.832;0,831112,10,55.199,58.027;0,838039,6,46.895,57.513;0,1064775,31,45.651,11.69;0,1088286,26,28.939,39.697;0,1162824,13,45.31,29.657;0,1260555,21,53.787,13.846;0,1283143,34,29.653,25.973;1,347822,10,49.661,40.313;1,847084,8,63.968,45.435;1,947732,17,54.174,16.532;1,956887,6,55.547,24.868;1,968133,4,67.204,16.491;1,972474,14,68.363,44.891;1,1050211,22,60.999,35.423;1,1106097,5,68.704,34.897;1,1131291,2,67.35,24.894;1,1159139,20,59.362,53.729;3,869970,16,6.026,34.214;4,397826,30,96.603,33.855;:37.54,37.21,0;"""

    # Pour chaque ligne, on extrait les données et on calcule la distance minimale.
    for line in data.splitlines():
        parsed = parse_line(line)
        if parsed is None:
            continue
        temps_match, players, ball_carrier = parsed
        res = compute_defender_distance(temps_match, players, ball_carrier)
        if res is None:
            print(f"Temps {temps_match} : données du porteur manquantes.")
        else:
            ball_team, defender_team, min_dist = res
            if min_dist is None:
                print(f"Temps {temps_match} : aucun joueur adverse trouvé.")
            else:
                print(f"Temps {temps_match} : Le porteur (équipe {ball_team}) est confronté à un défenseur (équipe {defender_team}) à {min_dist:.2f} unités.")

if __name__ == "__main__":
    main()
