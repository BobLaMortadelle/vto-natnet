import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns

# Fonction pour remplacer les valeurs numériques par "number" et les lettres uniques par "letter"
def categorize_animation_type(value):
    if re.match(r'^\d+$', str(value)):
        return 'number'
    elif re.match(r'^[A-Za-z]$', str(value)):
        return 'letter'
    return value

# Fonction pour analyser les angles par type d'animation
def analyze_angles(input_file_path):
    # Lire le DataFrame depuis le fichier CSV
    df = pd.read_csv(input_file_path)

    # Appliquer la fonction sur la colonne 'AnimationType'
    df['AnimationType'] = df['AnimationType'].apply(categorize_animation_type)

    # Filtrer les DataFrames pour les angles valides et les différents types d'animation
    types_of_animation = df['AnimationType'].unique()

    results = {}

    for animation_type in types_of_animation:
        filtered_df = df[(df['AnimationType'] == animation_type) & (df['Angle'].notna())]
        mean_angle = filtered_df['Angle'].mean()
        std_angle = filtered_df['Angle'].std()
        results[animation_type] = {'mean': mean_angle, 'std': std_angle}

    # Afficher les résultats
    for name, stats in results.items():
        print(f"{input_file_path} - {name} - Mean Angle: {stats['mean']}, Std Dev Angle: {stats['std']}")

    # Order for visualization
    ordered_categories = ['survivor', 'fire', 'hazardous materials', 'mapping', 'start handover', 'validate handover']
    # Add the other animation types to the order
    for animation_type in types_of_animation:
        if animation_type not in ordered_categories:
            ordered_categories.insert(0, animation_type)

    df['AnimationType'] = pd.Categorical(df['AnimationType'], categories=ordered_categories, ordered=True)

    # Visualisation avec boxplot
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='AnimationType', y='Angle', data=df)
    plt.title(f'Distribution des angles par type d\'animation - {input_file_path}')
    plt.xticks(rotation=45)
    plt.show()

    # Visualisation avec histogramme et KDE
    plt.figure(figsize=(12, 6))
    sns.histplot(df, x='Angle', hue='AnimationType', kde=True, element='step', palette="tab10")
    plt.title(f'Histogramme et KDE des angles par type d\'animation - {input_file_path}')
    plt.show()

    # Calcul des quartiles
    quartiles = df.groupby('AnimationType')['Angle'].quantile([0.25, 0.5, 0.75]).unstack()
    print(f"Quartiles des angles par type d'animation - {input_file_path}:")
    print(quartiles)

# Analyser le fichier angle_close.csv
analyze_angles('extracted_data/angle_close.csv')

# Analyser le fichier angle_close_corrected.csv
analyze_angles('extracted_data/angle_close_corrected.csv')

# Analyser le fichier angle_far.csv
analyze_angles('extracted_data/angle_far.csv')

# Analyser le fichier angle_far_corrected.csv
analyze_angles('extracted_data/angle_far_corrected.csv')
