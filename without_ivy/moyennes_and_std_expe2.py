import pandas as pd
import re



# Fonction pour remplacer les valeurs numériques par "number"
def categorize_animation_type(value):
    if re.match(r'^\d+$', str(value)):
        return 'number'
    return value



df_close = pd.read_csv('extracted_data/close.csv')

df_close_ok = df_close[(df_close['AnimationType'] == 'ok') & (df_close['Angle'].notna())]

df_close_survivor = df_close[(df_close['AnimationType'] == 'survivor') & (df_close['Angle'].notna())]

df_close_fire = df_close[(df_close['AnimationType'] == 'fire') & (df_close['Angle'].notna())]

df_close_hazardous_materials = df_close[(df_close['AnimationType'] == 'hazardous materials') & (df_close['Angle'].notna())]

df_close_mapping = df_close[(df_close['AnimationType'] == 'mapping') & (df_close['Angle'].notna())]

df_close_start_handover = df_close[(df_close['AnimationType'] == 'start handover') & (df_close['Angle'].notna())]

df_close_validate_handover = df_close[(df_close['AnimationType'] == 'validate handover') & (df_close['Angle'].notna())]

results_close = {}

for name, filtered_df_close in [
                          ('survivor', df_close_ok), 
                          ('survivor', df_close_survivor), 
                          ('fire', df_close_fire), 
                          ('hazardous materials', df_close_hazardous_materials), 
                          ('mapping', df_close_mapping), 
                          ('start handover', df_close_start_handover), 
                          ('validate handover', df_close_validate_handover)]:
    mean_angle = filtered_df_close['Angle'].mean()
    std_angle = filtered_df_close['Angle'].std()
    results_close[name] = {'mean': mean_angle, 'std': std_angle}

# Afficher les résultats
for name, stats in results_close.items():
    print(f"{name} - Mean Angle: {stats['mean']}, Std Dev Angle: {stats['std']}")





df_far = pd.read_csv('extracted_data/far.csv')

df_far_survivor = df_far[(df_far['AnimationType'] == 'survivor') & (df_far['Angle'].notna())]

df_far_fire = df_far[(df_far['AnimationType'] == 'fire') & (df_far['Angle'].notna())]

df_far_hazardous_materials = df_far[(df_far['AnimationType'] == 'hazardous materials') & (df_far['Angle'].notna())]

df_far_mapping = df_far[(df_far['AnimationType'] == 'mapping') & (df_far['Angle'].notna())]

df_far_start_handover = df_far[(df_far['AnimationType'] == 'start handover') & (df_far['Angle'].notna())]

df_far_validate_handover = df_far[(df_far['AnimationType'] == 'validate handover') & (df_far['Angle'].notna())]

results_far = {}

for name, filtered_df_far in [('survivor', df_far_survivor), 
                          ('fire', df_far_fire), 
                          ('hazardous materials', df_far_hazardous_materials), 
                          ('mapping', df_far_mapping), 
                          ('start handover', df_far_start_handover), 
                          ('validate handover', df_far_validate_handover)]:
    mean_angle = filtered_df_far['Angle'].mean()
    std_angle = filtered_df_far['Angle'].std()
    results_far[name] = {'mean': mean_angle, 'std': std_angle}

# Afficher les résultats
for name, stats in results_far.items():
    print(f"{name} - Mean Angle: {stats['mean']}, Std Dev Angle: {stats['std']}")