import csv
import math

"""
Dictionnaires  but_i <-> [minute, seconde, id_buteur, team]
"""

buts_rcl_mhsc = { "but_1": [15, 4, 154048, 1], "but_2": [25, 11, 106821, 1], "but_3" : [35, 23, 186796, 0], "but_4" : [49, 55, 59325, 0], "but_5" : [68, 10, 167443, 1] }
buts_mhsc_metz = { "but_1": [23, 50, 98826, 1], "but_2": [69, 46, 442793, 1], "but_3" : [79, 3, 78275, 0], "but_4" : [90, 50, 477724, 0] }
buts_rcsa_mhsc = { "but_1": [35, 15, 167443, 1], "but_2": [45, 36, 73965, 1], "but_3" : [48, 51, 167443, 1], "but_4" : [68, 32, 168539, 0], "but_5" : [94, 38, 433640, 0] }


def convertir_temps(buts):
    """
    Conversion en ms des timers de buts
    """
    timers_buts = []
    for value in buts.values() :
        timers_buts.append((value[0]*60+value[1])*1000)
    return timers_buts

def convertir_temps(buts):
    """
    Conversion en minutes
    """
    timers_buts = []
    for value in buts.values() :
        timers_buts.append(value[0]+1)
    return timers_buts


def arrondir_temps_500ms(temps_ms):
    """
    Arrondit le temps (en ms) au multiple de 500 ms supérieur.
    """
    return int(math.ceil(temps_ms / 500.0) * 500)

def generer_fichier_buts(buts, output_filename):
    """
    Pour un dictionnaire de buts (où chaque valeur est une liste : [minute, seconde, id_buteur, team]),
    génère un fichier texte dont chaque ligne indique :
       - le temps du but en ms (converti en multiple de 500 ms, arrondi au supérieur si besoin)
       - l'évolution du score sous la forme "buts équipe 0 : buts équipe 1"
       
    Les buts sont traités par ordre chronologique.
    """
    # Convertir chaque but en temps en ms
    buts_list = []
    for key, value in buts.items():
        try:
            minute = value[0]
            seconde = value[1]
            team = int(value[3])
        except (IndexError, ValueError):
            continue
        # Calcul du temps en ms
        temps_ms = (minute * 60 + seconde) * 1000
        temps_arrondi = arrondir_temps_500ms(temps_ms)
        buts_list.append((temps_arrondi, team))
    
    # Tri des buts par temps croissant
    buts_list.sort(key=lambda x: x[0])
    
    score_equipe0 = 0
    score_equipe1 = 0
    lignes = []
    for temps_arrondi, team in buts_list:
        if team == 0:
            score_equipe0 += 1
        else:
            score_equipe1 += 1
        # Format de la ligne : temps_arrondi ; score_equipe0 : score_equipe1
        lignes.append(f"{temps_arrondi};{score_equipe0}:{score_equipe1}")
    
    # Écriture dans le fichier de sortie
    with open(output_filename, "w", encoding="utf-8") as f:
        for ligne in lignes:
            f.write(ligne + "\n")

generer_fichier_buts(buts_rcl_mhsc, "buts_rcl_mhsc.txt")
generer_fichier_buts(buts_mhsc_metz, "buts_mhsc_metz.txt")
generer_fichier_buts(buts_rcsa_mhsc, "buts_rcsa_mhsc.txt")
print("\nFichiers de buts générés pour chaque dictionnaire.")
