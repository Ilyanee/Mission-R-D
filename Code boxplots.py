import pandas as pd
import matplotlib.pyplot as plt
import sys

def lire_fichier_scores(fichier_txt):
    """Lit un fichier texte contenant des lignes de score et retourne un DataFrame trié."""
    try:
        df = pd.read_csv(fichier_txt, sep=';', header=None, names=['score_time', 'score_label'], dtype={'score_label': str})
        df['score_time'] = pd.to_numeric(df['score_time'], errors='coerce')
        df = df.sort_values('score_time').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier des scores ({fichier_txt}) : {e}")
        sys.exit(1)

def associer_score(df_data, df_score):
    """Associe à chaque ligne du DataFrame df_data le score courant (score connu avant cet événement)."""
    try:
        df_data = df_data.sort_values('temps_min').reset_index(drop=True)
        df_score = df_score.sort_values('score_time').reset_index(drop=True)

        df_data['temps_min'] = df_data['temps_min'].astype(float)
        df_score['score_time'] = df_score['score_time'].astype(float)

        # Associer chaque événement au dernier score connu (avant l'événement)
        df_merged = pd.merge_asof(df_data, df_score, left_on='temps_min', right_on='score_time', direction='backward')
        return df_merged
    except Exception as e:
        print(f"Erreur lors de l'association des scores aux données : {e}")
        sys.exit(1)

def tracer_boxplots(df, param_cols, group_col='score_label', output_prefix='boxplot'):
    """Trace et sauvegarde des boxplots pour les colonnes numériques."""
    for param in param_cols:
        try:
            plt.figure(figsize=(8, 5))
            groups = [group[param].dropna() for _, group in df.groupby(group_col) if not group[param].dropna().empty]
            labels = [score for score, group in df.groupby(group_col) if not group[param].dropna().empty]

            if groups:
                plt.boxplot(groups, labels=labels)
                plt.xlabel("Score")
                plt.ylabel(param)
                plt.title(f"Boxplot de {param} par score")
                plt.tight_layout()
                output_file = f"{output_prefix}_{param}.png"
                plt.savefig(output_file)
                plt.close()
                print(f"Boxplot généré et sauvegardé : {output_file}")
            else:
                print(f"Aucune donnée pour le paramètre {param}, boxplot non généré.")
        except Exception as e:
            print(f"Erreur lors de la génération du boxplot pour {param} : {e}")

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print("Utilisation : python CodeBoxplots.py <fichier_csv_calcul> <fichier_txt_scores> <output_prefix>")
        sys.exit(1)
    
    fichier_csv_calcul, fichier_txt_scores, output_prefix = sys.argv[1], sys.argv[2], sys.argv[3]

    # Lecture du fichier CSV des calculs
    try:
        df_data = pd.read_csv(fichier_csv_calcul, sep=';', encoding='utf-8')
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier CSV ({fichier_csv_calcul}) : {e}")
        sys.exit(1)
    
    # Lecture des scores
    df_score = lire_fichier_scores(fichier_txt_scores)

    # Association des scores aux données
    df_merged = associer_score(df_data, df_score)

    # Sauvegarde du DataFrame fusionné
    try:
        merged_csv_file = f"{output_prefix}_merged.csv"
        df_merged.to_csv(merged_csv_file, sep=';', index=False, encoding='utf-8')
        print(f"DataFrame fusionné sauvegardé dans {merged_csv_file}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde du DataFrame fusionné : {e}")

    # Sélection des colonnes numériques pour les boxplots
    param_cols = [col for col in df_merged.columns if col not in ['temps_min', 'score_time', 'score_label']]
    
    # Génération des boxplots
    tracer_boxplots(df_merged, param_cols, group_col='score_label', output_prefix=output_prefix)
