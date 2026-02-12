import json
import pandas as pd
import os

def process_huge_json(input_file, output_csv):
    # 1. Load the raw data (Ingestion)
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    with open(input_file, 'r') as f:
        data = json.load(f)
    
    all_emails = []

    # 2. Handle Data Variety (Transformation)
    # Check if data is threaded_emails.json (dict) or cleaned_enron_emails.json (list)
    if isinstance(data, dict):
        for thread_id, messages in data.items():
            for msg in messages:
                msg['thread_id'] = thread_id
                all_emails.append(msg)
    else:
        all_emails = data

    # 3. Data Quality & Cleaning
    df = pd.DataFrame(all_emails)

    # CRITICAL FIX: Drop rows where critical fields are NaN or empty
    # This prevents the "Cannot merge node because of NaN" error in Milestone 2
    df = df.dropna(subset=['From', 'To', 'Body'])
    df = df[(df['From'] != "") & (df['To'] != "")]
    
    # 4. Save to Staging (Medallion 'Silver' Layer)
    df.to_csv(output_csv, index=False)
    print(f"Milestone 1 Complete: {output_csv} created with {len(df)} cleaned rows.")

if __name__ == "__main__":
    # Ensure the data directory exists
    if not os.path.exists('data'):
        os.makedirs('data')
        
    process_huge_json('data/cleaned_enron_emails.json', 'data/processed_emails.csv')