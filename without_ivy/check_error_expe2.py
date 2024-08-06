import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix

def load_and_prepare_answers(file_path):
    df = pd.read_csv(file_path)
    return df[['Participant_ID', 'number', 'number_certitude', 'static_text', 'static_text_certitude', 
               'scrolling_text', 'scrolling_text_certitude', 'signification_1', 'signification_1_certitude', 
               'signification_2', 'signification_2_certitude', 'signification_3', 'signification_3_certitude', 
               'signification_4', 'signification_4_certitude', 'signification_5', 'signification_5_certitude', 
               'signification_6', 'signification_6_certitude']]

def categorize_value(value):
    predefined_labels = {'number', 'letter', 'ok', 'handover text', 'helicopter text', 'survivor', 
                         'fire', 'hazardous materials', 'mapping', 'start handover', 'validate handover'}
    if isinstance(value, str) and value.isdigit():
        return 'number'
    elif isinstance(value, str) and value.isalpha() and len(value) == 1:
        return 'letter'
    elif value in predefined_labels:
        return value
    else:
        return 'cannot read'

def prepare_combined_data(df_corrected, df_answers):
    combined_corrected = []
    combined_answers = []

    for col in df_corrected.columns:
        if col != 'Participant_ID' and not col.endswith('_certitude'):
            combined_corrected.extend(df_corrected[col].astype(str).apply(categorize_value).tolist())
            combined_answers.extend(df_answers[col].astype(str).apply(categorize_value).tolist())

    return combined_corrected, combined_answers

def plot_combined_confusion_matrix(corrected, answers, labels):
    cm = confusion_matrix(corrected, answers, labels=labels)
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(cm, annot=True, fmt='d', xticklabels=labels, yticklabels=labels, cmap='Blues')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.title('Combined Confusion Matrix')
    plt.show()

# Charger les fichiers CSV
df_corrected_close = pd.read_csv('extracted_data/close_corrected.csv')
df_answers_close = load_and_prepare_answers('extracted_data/answers_close.csv')
df_corrected_far = pd.read_csv('extracted_data/far_corrected.csv')
df_answers_far = load_and_prepare_answers('extracted_data/answers_far.csv')

# Préparer les données combinées pour les fichiers close
combined_corrected_close, combined_answers_close = prepare_combined_data(df_corrected_close, df_answers_close)

# Préparer les données combinées pour les fichiers far
combined_corrected_far, combined_answers_far = prepare_combined_data(df_corrected_far, df_answers_far)

# Combiner les données close et far
combined_corrected = combined_corrected_close + combined_corrected_far
combined_answers = combined_answers_close + combined_answers_far

# Étiquettes spécifiques
labels = ['number', 'letter', 'ok', 'handover text', 'helicopter text', 'survivor', 'fire', 
          'hazardous materials', 'mapping', 'start handover', 'validate handover', 'cannot read']

# Afficher la matrice de confusion combinée
plot_combined_confusion_matrix(combined_corrected, combined_answers, labels)

# Fonction pour comparer les colonnes et inclure les niveaux de certitude, en ignorant les chiffres identiques
def compare_columns_with_certainty(df1, df2):
    differences = []
    low_certainty = []
    for col in df1.columns:
        if col != 'Participant_ID' and not col.endswith('_certitude'):
            cert_col = col + '_certitude'
            for idx in df1.index:
                # Ignore identical numbers
                if (isinstance(df1.loc[idx, col], (int, float)) or (isinstance(df1.loc[idx, col], str) and df1.loc[idx, col].isdigit())) and df1.loc[idx, col] == df2.loc[idx, col]:
                    continue
                if df1.loc[idx, col] != df2.loc[idx, col]:
                    differences.append((idx, df1.loc[idx, 'Participant_ID'], col, df1.loc[idx, col], df2.loc[idx, col], df2.loc[idx, cert_col]))
                if df2.loc[idx, cert_col] != 5:
                    low_certainty.append((idx, df1.loc[idx, 'Participant_ID'], col, df1.loc[idx, col], df2.loc[idx, col], df2.loc[idx, cert_col]))
    return differences, low_certainty

# Comparer les fichiers close
differences_close, low_certainty_close = compare_columns_with_certainty(df_corrected_close, df_answers_close)
# Comparer les fichiers far
differences_far, low_certainty_far = compare_columns_with_certainty(df_corrected_far, df_answers_far)

# Créer les DataFrames pour les différences
diff_close_df = pd.DataFrame(differences_close, columns=['Index', 'Participant_ID', 'Column', 'Corrected', 'Answer', 'Certainty'])
diff_far_df = pd.DataFrame(differences_far, columns=['Index', 'Participant_ID', 'Column', 'Corrected', 'Answer', 'Certainty'])

# Créer les DataFrames pour les certitudes < 5 dans les réponses
low_certainty_close_df = pd.DataFrame(low_certainty_close, columns=['Index', 'Participant_ID', 'Column', 'Corrected', 'Answer', 'Certainty'])
low_certainty_far_df = pd.DataFrame(low_certainty_far, columns=['Index', 'Participant_ID', 'Column', 'Corrected', 'Answer', 'Certainty'])

# Afficher les différences sous forme de tableau
print("\nDifferences found in extracted_data/close_corrected.csv vs extracted_data/answers_close.csv:")
print(diff_close_df)

print("\nDifferences found in extracted_data/far_corrected.csv vs extracted_data/answers_far.csv:")
print(diff_far_df)

# Afficher les différences avec certitudes < 5 dans les réponses
print("\nLow Certainty Answers in extracted_data/close_corrected.csv vs extracted_data/answers_close.csv:")
print(low_certainty_close_df)

print("\nLow Certainty Answers in extracted_data/far_corrected.csv vs extracted_data/answers_far.csv:")
print(low_certainty_far_df)

# Sauvegarder les DataFrames dans des fichiers CSV
diff_close_df.to_csv('differences_close.csv', index=False)
diff_far_df.to_csv('differences_far.csv', index=False)
low_certainty_close_df.to_csv('low_certainty_close.csv', index=False)
low_certainty_far_df.to_csv('low_certainty_far.csv', index=False)
