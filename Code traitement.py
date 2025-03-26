import pandas as pd
import sys

TOTAL_PLAYERS = 22  # Nombre fixe de joueurs

def parse_line(ligne):
    """
    Extrait depuis une ligne :
      - timestamp (premier élément)
      - période (seconde colonne, extraite de la partie avant le ':', on prend le 2ème nombre)
      - positions des joueurs (les champs situés après le ':' dans le 2ème champ puis les suivants, sauf le dernier)
      - position du ballon (dernier champ, on retire le ':' initial s'il existe)
    
    La fonction retourne une liste de la forme :
       [timestamp, période, player_1, player_2, ..., player_22, ball]
       
    Seules les lignes dont le timestamp est un multiple de 520 ms sont conservées.
    Si le nombre de joueurs est inférieur à 22, la liste est complétée avec des chaînes vides.
    Si le nombre de joueurs est supérieur à 22, seuls les 22 premiers sont conservés.
    """
    ligne = ligne.strip()
    if not ligne:
        return None
    # Séparer les champs par ";" et supprimer les éventuels champs vides (ex : causés par un ";" final)
    champs = [champ for champ in ligne.split(';') if champ != ""]
    if len(champs) < 3:
        return None

    # 1. Timestamp
    timestamp = champs[0]
    try:
        t = int(timestamp)
    except Exception:
        return None
    # Filtrer : ne conserver que si t est un multiple de 520 ms
    if t % 520 != 0:
        return None

    # 2. Extraction de la période et du premier joueur
    if ':' not in champs[1]:
        return None
    partie_gauche, right = champs[1].split(':', 1)
    left_parts = partie_gauche.split(',')
    if len(left_parts) < 2:
        return None
    periode = left_parts[1]
    
    # 3. Récupération des positions des joueurs
    players = [right]
    if len(champs) > 2:
        additional_players = champs[2:-1]
        players.extend(additional_players)
    
    # 4. Récupération de la position du ballon (dernier champ)
    ball = champs[-1].lstrip(':')

    # Ajuster la liste des joueurs pour qu'elle comporte exactement TOTAL_PLAYERS éléments
    if len(players) < TOTAL_PLAYERS:
        players.extend([""] * (TOTAL_PLAYERS - len(players)))
    elif len(players) > TOTAL_PLAYERS:
        players = players[:TOTAL_PLAYERS]
    
    return [timestamp, periode] + players + [ball]

def construire_dataframe(fichier_entree):
    """
    Lit le fichier d'entrée, traite chaque ligne filtrée et retourne un DataFrame.
    La structure du DataFrame est :
      [timestamp, période, player_1, ..., player_22, ball]
    """
    donnees = []
    with open(fichier_entree, 'r', encoding='utf-8') as f:
        lignes = f.readlines()
    
    for ligne in lignes:
        ligne_traitee = parse_line(ligne)
        if ligne_traitee is not None:
            donnees.append(ligne_traitee)
    
    if not donnees:
        return pd.DataFrame()
    
    colonnes = ['timestamp', 'periode'] + [f'player_{i+1}' for i in range(TOTAL_PLAYERS)] + ['ball']
    return pd.DataFrame(donnees, columns=colonnes)

def traiter_donnees(fichier_entree, fichier_sortie):
    df = construire_dataframe(fichier_entree)
    if df.empty:
        print("Aucune donnée valide trouvée.")
        return
    df.to_csv(fichier_sortie, sep=';', index=False, encoding='utf-8')
    print(f"Les données ont été sauvegardées dans {fichier_sortie}.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Utilisation : python code_traitement.py <fichier_entree> <fichier_sortie>")
        sys.exit(1)
    
    fichier_entree = sys.argv[1]
    fichier_sortie = sys.argv[2]
    
    traiter_donnees(fichier_entree, fichier_sortie)
