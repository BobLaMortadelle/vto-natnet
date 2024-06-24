import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('animation_evaluation.csv')
df = df.iloc[:, 2:]
df = df.loc[:, ~df.columns.str.startswith("Observation supplémentaire :")]
df = df.loc[:, ~df.columns.str.startswith("Que vous évoque ")]
df = df.loc[:, ~df.columns.str.startswith("Avez-vous des idées d'animation ")]
df.columns = ["carto" if "cartographie" in col else col for col in df.columns]
df.columns = ["fire" if "feu" in col else col for col in df.columns]
df.columns = ["materials" if "dangereux" in col else col for col in df.columns]
df.columns = ["survivor" if "survivant" in col else col for col in df.columns]
df.columns = ["demand" if "demandée" in col else col for col in df.columns]
df.columns = ["valid" if "validée" in col else col for col in df.columns]

df = df.replace("Pas du tout d’accord", 1)
df = df.replace("Pas d’accord", 2)
df = df.replace("Ni d’accord, ni pas d’accord", 3)
df = df.replace("J'accepte", 4)
df = df.replace("Tout à fait d’accord", 5)

unique_columns = ['fire', 'survivor', 'materials', 'carto', 'demand', 'valid']
positions_fire = [i for i, col in enumerate(df.columns) if col == 'fire']

animations = ["smiley", "fire", "zoom map", "red triangle", "blinking hand", "thumb riseup", "opening hand", "snail", 
              "Chemical", "blinking thumb", "blinking leak", "replay map", "warning picto", "tall waving hand", "water leak", "purple guy", "heart", "med kit"]

dataframes = []

# Diviser le DataFrame à chaque nouvelle colonne "fire"
for start_idx in positions_fire:
    end_idx = start_idx + len(unique_columns)
    # Créer un DataFrame avec les colonnes sélectionnées
    new_df = df.iloc[:, start_idx:end_idx]
    new_df.columns = unique_columns  # Renommer les colonnes pour les rendre uniques
    dataframes.append(new_df)
    
for idx, df_part in enumerate(dataframes):
    # print(animations[idx])
    # print(df_part)
    # somme_colonnes = df_part.sum()
    # somme_df = pd.DataFrame(somme_colonnes, columns=["Sum"])
    # print("Somme de chaque colonne:")
    # print(somme_df)
    count_dict = {}
    for col in df_part.columns:
        count_dict[col] = df_part[col].value_counts().reindex([1, 2, 3, 4, 5], fill_value=0)
        count_df = pd.DataFrame(count_dict).T
        count_df.columns = ['Count of 1', 'Count of 2', 'Count of 3', 'Count of 4', 'Count of 5']
    print(f"Nombre de 1, 2, 3, 4, 5 pour chaque colonne de " + animations[idx])
    print(count_df)
    
    # plt.figure(figsize=(8, 8))
    # plt.pie(somme_df["Sum"], labels=somme_df.index, autopct='%1.1f%%', startangle=140)
    # plt.title(f'Diagramme Camembert des sommes pour '+ animations[idx])
    # plt.show()
    # print(animations[idx])
    # somme_colonnes = df_part.sum()
    # # Convertir la série de sommes en DataFrame pour une meilleure présentation
    # somme_df = pd.DataFrame(somme_colonnes, columns=["Sum"])
    # print(somme_df.to_string(header=False))