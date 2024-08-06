import pandas as pd

# Load the DataFrame from the CSV file
file_path = 'extracted_data/form_answers.csv'
df = pd.read_csv(file_path)

# Define the mapping dictionary for standardizing responses
response_mapping = {
    'feu': 'fire', 'feu ': 'fire', 'Fire': 'fire', 'fire': 'fire', 'Fire spot': 'fire', 'fire spot': 'fire',
    'survivor': 'survivor', 'survivor ': 'survivor','Survivor': 'survivor', 'survivant': 'survivor',
    'hazardous_materials': 'hazardous materials', 'hazardous materials': 'hazardous materials', 'hazardous materials ': 'hazardous materials',
    'mapping': 'mapping', 'Mapping': 'mapping',
    'start_handover': 'start handover', 'start handover': 'start handover', 'initiating handover': 'start handover', 'demande handover': 'start handover',
    'confimation of handover': 'validate handover', 'confirm_handover': 'validate handover', 'confirm handover': 'validate handover', 'cofirm handover': 'validate handover', 'validate handover': 'validate handover', 'accepter handover' : 'validate handover',
    'ok': 'ok', 'OK': 'ok',
    'Handover': 'handover text', 'handover': 'handover text', 
    'helicopter': 'heliocpter text', 'helicoptere': 'heliocpter text', 'Helicopter': 'heliocpter text',
    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9
}

# Function to standardize responses based on the mapping dictionary
def standardize_response(value):
    return response_mapping.get(value, value)

# List of keywords to exclude
exclude_keywords = ['observation', 'Describe', 'Modification']

# Create a list of columns to keep by excluding columns that contain the keywords
columns_to_keep = [col for col in df.columns if not any(keyword in col for keyword in exclude_keywords)]

#sort according to participant ID
df_sorted = df.sort_values(by='Participant_ID')

# Create a new DataFrame with the filtered columns
filtered_df = df_sorted[columns_to_keep]

# Apply the function to relevant columns
columns_to_standardize = filtered_df.columns 

for col in columns_to_standardize:
    filtered_df[col] = filtered_df[col].apply(standardize_response)

# Display the filtered DataFrame
# print(filtered_df)

output_file_path = 'extracted_data/filtered and_standardized_form_data.csv'
filtered_df.to_csv(output_file_path, index=False)

df_far = filtered_df[filtered_df['distance'] == 'Far']
output_file_path = 'extracted_data/answers_far.csv'
df_far.to_csv(output_file_path, index=False)

df_close = filtered_df[filtered_df['distance'] == 'Close']
output_file_path = 'extracted_data/answers_close.csv'
df_close.to_csv(output_file_path, index=False)