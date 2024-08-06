import pandas as pd
import re
import os

# Expressions régulières ajustées
pattern_displayed = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (.*?) displayed')
pattern_angle = re.compile(r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - .*User rises the hand up : animation readable wit angle ([\d.]+)')

data_close = []
angles_close = []

# Comptage des lignes pour le débogage
total_lines_close = 0
matched_lines_displayed_close = 0
matched_lines_angle_close = 0

for i in range(1, 13):
    if os.path.exists(f'expe2_{i}_corrected.log'):
        log_file_path = f'expe2_{i}_corrected.log'
    else:
        log_file_path = f'expe2_{i}.log'
    
    print(log_file_path)
    with open(log_file_path, 'r') as file:
        participant_data = {'Participant_ID': i, 'number': None, 'static_text': None, 'scrolling_text': None,
                            'signification_1': None, 'signification_2': None, 'signification_3': None, 
                            'signification_4': None, 'signification_5': None, 'signification_6': None}
        animation_count = 0
        
        for line in file:
            total_lines_close += 1
            match_displayed = pattern_displayed.search(line)
            match_angle = pattern_angle.search(line)
            
            if match_displayed:
                matched_lines_displayed_close += 1
                datetime_str_displayed = match_displayed.group(1)
                animation_type = match_displayed.group(2)
                
                if animation_count == 0:
                    participant_data['number'] = animation_type
                elif animation_count == 1:
                    participant_data['static_text'] = animation_type
                elif animation_count == 2:
                    participant_data['scrolling_text'] = animation_type
                elif animation_count < 9:
                    participant_data[f'signification_{animation_count-2}'] = animation_type
                
                animation_count += 1
                
            if match_angle:
                matched_lines_angle_close += 1
                datetime_str_angle = match_angle.group(1)
                angle = float(match_angle.group(2))
                angles_close.append([i, datetime_str_angle, animation_type, angle])

        data_close.append(participant_data)

df_close = pd.DataFrame(data_close)
output_file_path_close = 'extracted_data/close.csv'
df_close.to_csv(output_file_path_close, index=False)
print(df_close)

df_angles_close = pd.DataFrame(angles_close, columns=['Participant_ID', 'Timestamp', 'AnimationType', 'Angle'])
output_file_path_angles_close = 'extracted_data/angle_close.csv'
df_angles_close.to_csv(output_file_path_angles_close, index=False)
print(df_angles_close)

print(f"Total lines processed: {total_lines_close}")
print(f"Total matching 'displayed' lines: {matched_lines_displayed_close}")
print(f"Total matching 'angle' lines: {matched_lines_angle_close}")

data_far = []
angles_far = []

total_lines_far = 0
matched_lines_displayed_far = 0
matched_lines_angle_far = 0

for i in range(1, 13):
    if os.path.exists(f'expe2_far_{i}_corrected.log'):
        log_file_path = f'expe2_far_{i}_corrected.log'
    else:
        log_file_path = f'expe2_far_{i}.log'
    
    print(log_file_path)
    with open(log_file_path, 'r') as file:
        participant_data = {'Participant_ID': i, 'number': None, 'static_text': None, 'scrolling_text': None,
                            'signification_1': None, 'signification_2': None, 'signification_3': None, 
                            'signification_4': None, 'signification_5': None, 'signification_6': None}
        animation_count = 0
        
        for line in file:
            total_lines_far += 1
            match_displayed = pattern_displayed.search(line)
            match_angle = pattern_angle.search(line)
            
            if match_displayed:
                matched_lines_displayed_far += 1
                datetime_str_displayed = match_displayed.group(1)
                animation_type = match_displayed.group(2)
                
                if animation_count == 0:
                    participant_data['number'] = animation_type
                elif animation_count == 1:
                    participant_data['static_text'] = animation_type
                elif animation_count == 2:
                    participant_data['scrolling_text'] = animation_type
                elif animation_count < 9:
                    participant_data[f'signification_{animation_count-2}'] = animation_type
                
                animation_count += 1
                
            if match_angle:
                matched_lines_angle_far += 1
                datetime_str_angle = match_angle.group(1)
                angle = float(match_angle.group(2))
                angles_far.append([i, datetime_str_angle, animation_type, angle])

        data_far.append(participant_data)

df_far = pd.DataFrame(data_far)
output_file_path_far = 'extracted_data/far.csv'
df_far.to_csv(output_file_path_far, index=False)
print(df_far)

df_angles_far = pd.DataFrame(angles_far, columns=['Participant_ID', 'Timestamp', 'AnimationType', 'Angle'])
output_file_path_angles_far = 'extracted_data/angle_far.csv'
df_angles_far.to_csv(output_file_path_angles_far, index=False)
print(df_angles_far)

print(f"Total lines processed: {total_lines_far}")
print(f"Total matching 'displayed' lines: {matched_lines_displayed_far}")
print(f"Total matching 'angle' lines: {matched_lines_angle_far}")
