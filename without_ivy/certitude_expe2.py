import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re

# Charger le fichier CSV dans un DataFrame
df = pd.read_csv('extracted_data/answers_far_corrected.csv')

# Fonction pour remplacer les valeurs numériques par "number" et les lettres uniques par "letter"
def categorize_animation_type(value):
    if re.match(r'^\d+$', str(value)):
        return 'number'
    elif re.match(r'^[A-Za-z]$', str(value)):
        return 'letter'
    return value

# Appliquer la fonction sur les colonnes d'animation
animation_types = ['number', 'static_text', 'scrolling_text', 
                   'signification_1', 'signification_2', 
                   'signification_3', 'signification_4', 
                   'signification_5', 'signification_6']

for anim_type in animation_types:
    df[anim_type] = df[anim_type].apply(categorize_animation_type)

# Convertir les colonnes de certitude en format numérique
for col in df.columns:
    if 'certitude' in col:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Préparer les données pour les graphiques
certainty_data = pd.DataFrame(columns=['AnimationType', 'Certainty'])

# Ajouter les certitudes au DataFrame
for anim_type in animation_types:
    cert_col = f'{anim_type}_certitude'
    temp_df = df[['Participant_ID', anim_type, cert_col]].copy()
    temp_df.columns = ['Participant_ID', 'AnimationType', 'Certainty']
    certainty_data = pd.concat([certainty_data, temp_df], ignore_index=True)

# Renommer les types d'animation pour qu'ils correspondent aux colonnes d'origine
certainty_data['AnimationType'].replace({
    'number': 'number',
    'static_text': 'letter',
    'scrolling_text': 'helicopter text',
    'signification_1': 'survivor',
    'signification_2': 'fire',
    'signification_3': 'hazardous materials',
    'signification_4': 'mapping',
    'signification_5': 'start handover',
    'signification_6': 'validate handover'
}, inplace=True)

# Calculer les moyennes des certitudes
mean_certainty = certainty_data.groupby('AnimationType')['Certainty'].mean().reset_index()

# Visualisation des moyennes des certitudes avec un graphique à barres
plt.figure(figsize=(14, 8))
sns.barplot(x='AnimationType', y='Certainty', data=mean_certainty)
plt.title('Moyenne des certitudes par type d\'animation')
plt.xticks(rotation=45)
plt.show()

# Visualisation avec boxplot pour la distribution des certitudes
plt.figure(figsize=(14, 8))
sns.boxplot(x='AnimationType', y='Certainty', data=certainty_data)
plt.title('Distribution des certitudes par type d\'animation')
plt.xticks(rotation=45)
plt.show()
