#!/usr/bin/env python3
import math

def calculer_distance(x1, y1, x2, y2):
    """Calcule la distance euclidienne entre deux points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def parser_ligne_joueurs(ligne):
    """
    Analyse une ligne de données du match.
    
    Format de la ligne :
      <temps_match> ; <segment_joueur> ; ... ; <segment_joueur> ; :<porteur_x>,<porteur_y>,<temps_porteur> ;
      
    Chaque segment joueur est de la forme :
      equipe,identifiant,numero,x,y
      
    Le segment commençant par ':' contient les données du porteur (ici on récupère uniquement x et y).
    """
    ligne = ligne.strip()
    if not ligne:
        return None
    elements = ligne.split(';')
    temps_match = elements[0]
    joueurs = []
    porteur_inclus = None  # données du porteur telles qu'incluses dans la ligne (peuvent être remplacées)
    for elem in elements[1:]:
        elem = elem.strip()
        if not elem:
            continue
        if elem.startswith(':'):
            # Segment du porteur de balle
            parties = elem[1:].split(',')
            try:
                x_porteur = float(parties[0])
                y_porteur = float(parties[1])
                # On ignore le temps ici (partie[2])
                porteur_inclus = (x_porteur, y_porteur)
            except (ValueError, IndexError):
                print("Erreur lors de l'analyse du porteur :", elem)
        else:
            # Segment joueur
            parties = elem.split(',')
            if len(parties) < 5:
                continue
            try:
                equipe = int(parties[0])
                # Les deux champs suivants (identifiant et numéro) sont ignorés
                x = float(parties[3])
                y = float(parties[4])
                joueurs.append((equipe, x, y))
            except ValueError:
                print("Erreur lors de l'analyse d'un joueur :", elem)
    return temps_match, joueurs, porteur_inclus

def lire_donnees_porteur(contenu):
    """
    Lit les données du porteur de balle à partir d'une chaîne de caractères.
    
    Chaque ligne doit être de la forme : equipe;x;y;temps
    Si les trois premiers champs sont vides, la ligne est ignorée.
    
    Retourne une liste de tuples (temps, equipe, x, y).
    """
    donnees = []
    for ligne in contenu.splitlines():
        ligne = ligne.strip()
        if not ligne:
            continue
        champs = ligne.split(';')
        if len(champs) < 4:
            continue
        try:
            temps = float(champs[3])
        except ValueError:
            continue
        # On ignore les lignes où les trois premiers champs sont vides
        if champs[0] == '' or champs[1] == '' or champs[2] == '':
            continue
        try:
            equipe = int(champs[0])
            x = float(champs[1])
            y = float(champs[2])
        except ValueError:
            continue
        donnees.append((temps, equipe, x, y))
    return donnees

def calculer_distance_defenseur(temps_match, joueurs, porteur):
    """
    Détermine de quel côté se trouve le porteur (en fonction de la proximité avec un coéquipier)
    puis calcule la distance minimale entre le porteur et un joueur de l'équipe adverse.
    
    Retourne un tuple (equipe_porteur, equipe_defense, distance_minimale) ou None si les données sont insuffisantes.
    """
    if porteur is None:
        return None
    bx, by = porteur

    # Calcul de la distance minimale entre le porteur et les joueurs des équipes 0 et 1
    distances_par_equipe = {0: float('inf'), 1: float('inf')}
    for equipe, x, y in joueurs:
        if equipe in distances_par_equipe:
            d = calculer_distance(bx, by, x, y)
            if d < distances_par_equipe[equipe]:
                distances_par_equipe[equipe] = d

    # On suppose que le porteur est proche d'un coéquipier
    if distances_par_equipe[0] < distances_par_equipe[1]:
        equipe_porteur = 0
    else:
        equipe_porteur = 1

    # L'équipe adverse est celle des défenseurs
    equipe_defense = 1 if equipe_porteur == 0 else 0

    # Recherche du défenseur le plus proche (dans l'équipe adverse)
    distance_min = float('inf')
    for equipe, x, y in joueurs:
        if equipe == equipe_defense:
            d = calculer_distance(bx, by, x, y)
            if d < distance_min:
                distance_min = d

    if distance_min == float('inf'):
        distance_min = None
    return equipe_porteur, equipe_defense, distance_min

def main():
    # --- Exemple de données du match (positions des joueurs + données porteur intégrées) ---
    donnees_match = """0;0,540100,9,52.607,33.316;0,615385,12,44.96,40.174;0,656168,25,52.042,23.946;0,831112,10,52.335,57.354;0,838039,6,45.768,57.055;0,1064775,31,45.506,11.244;0,1088286,26,26.779,34.311;0,1162824,13,44.95,29.049;0,1260555,21,52.189,13.823;0,1283143,34,29.163,25.955;1,347822,10,52.428,43.403;1,847084,8,63.404,44.694;1,947732,17,52.663,17.73;1,956887,6,55.415,24.344;1,968133,4,66.915,16.95;1,972474,14,67.818,44.611;1,1050211,22,61.597,33.009;1,1106097,5,68.218,34.621;1,1131291,2,67.486,24.161;1,1159139,20,58.331,53.197;3,869970,16,5.07,33.046;4,397826,30,98.025,33.757;:52.5,34,0;
520;0,540100,9,53.265,33.058;0,615385,12,45.506,40.271;0,656168,25,52.141,24.203;0,831112,10,53.402,57.661;0,838039,6,46.374,57.16;0,1064775,31,45.556,11.536;0,1088286,26,28.517,39.586;0,1162824,13,45.032,29.252;0,1260555,21,52.561,13.787;0,1283143,34,29.341,25.658;1,347822,10,51.195,41.75;1,847084,8,63.682,44.966;1,947732,17,54.287,16.132;1,956887,6,55.416,24.497;1,968133,4,67.056,16.713;1,972474,14,67.959,44.634;1,1050211,22,61.317,34.204;1,1106097,5,68.331,34.886;1,1131291,2,67.551,24.427;1,1159139,20,58.858,53.367;3,869970,16,5.639,33.76;4,397826,30,97.394,33.548;:44,35.63,0;
1040;0,540100,9,54.941,31.999;0,615385,12,46.044,40.192;0,656168,25,52.816,24.832;0,831112,10,55.199,58.027;0,838039,6,46.895,57.513;0,1064775,31,45.651,11.69;0,1088286,26,28.939,39.697;0,1162824,13,45.31,29.657;0,1260555,21,53.787,13.846;0,1283143,34,29.653,25.973;1,347822,10,49.661,40.313;1,847084,8,63.968,45.435;1,947732,17,54.174,16.532;1,956887,6,55.547,24.868;1,968133,4,67.204,16.491;1,972474,14,68.363,44.891;1,1050211,22,60.999,35.423;1,1106097,5,68.704,34.897;1,1131291,2,67.35,24.894;1,1159139,20,59.362,53.729;3,869970,16,6.026,34.214;4,397826,30,96.603,33.855;:37.54,37.21,0;
"""

    # --- Exemple de données du porteur de balle dans le nouveau format ---
    donnees_porteur_str = """;;;0.0
;;;0.0
;;;0.008666666666666666
;;;0.008666666666666666
;;;0.017333333333333333
;;;0.017333333333333333
;;;0.026
1;44.349;40.522;0.026
1;44.886;40.84;0.034666666666666665
;;;0.034666666666666665
1;45.483;40.263;0.043333333333333335
;;;0.043333333333333335
1;45.979;39.483;0.052
;;;0.052
1;46.383;38.759;0.06066666666666667
;;;0.06066666666666667
1;46.708;38.179;0.06933333333333333
;;;0.06933333333333333
;;;0.078
;;;0.078
"""
    # Lecture des données du porteur à partir du nouveau fichier
    liste_porteur = lire_donnees_porteur(donnees_porteur_str)
    
    # Lecture des données du match (chaque ligne représente un instant)
    lignes_match = donnees_match.splitlines()
    donnees_match_parsees = []
    for ligne in lignes_match:
        resultat = parser_ligne_joueurs(ligne)
        if resultat is not None:
            donnees_match_parsees.append(resultat)
    
    # Pour cet exemple, on va utiliser le premier enregistrement du match.
    # Les données incluses dans la ligne sont celles qui figuraient initialement (après ':')
    temps_match, joueurs, porteur_inclus = donnees_match_parsees[0]
    print("Temps de match :", temps_match)
    print("Nombre de joueurs :", len(joueurs))
    print("Porteur initial :", porteur_inclus)
    
    # --- Remplacement des données du porteur par celles du fichier porteur si disponibles ---
    # Ici, les temps des enregistrements ne sont pas forcément comparables (les échelles diffèrent)
    # Pour l'exemple, nous prenons le premier enregistrement valide du fichier porteur.
    if liste_porteur:
        temps_porteur, equipe_porteur, x_porteur, y_porteur = liste_porteur[0]
        nouveau_porteur = (x_porteur, y_porteur)
        print("Données du porteur depuis le fichier :", nouveau_porteur, " (équipe", equipe_porteur, ", temps", temps_porteur,")")
    else:
        nouveau_porteur = porteur_inclus
    
    # Calcul de la distance au défenseur le plus proche
    resultat = calculer_distance_defenseur(temps_match, joueurs, nouveau_porteur)
    if resultat is None:
        print("Impossible de calculer la distance (données manquantes).")
    else:
        equipe_du_porteur, equipe_defense, distance_min = resultat
        if distance_min is None:
            print("Aucun défenseur trouvé.")
        else:
            print(f"Au temps {temps_match} : le porteur (équipe {equipe_du_porteur}) est à {distance_min:.2f} unités du défenseur le plus proche (équipe {equipe_defense}).")

if __name__ == "__main__":
    main()
