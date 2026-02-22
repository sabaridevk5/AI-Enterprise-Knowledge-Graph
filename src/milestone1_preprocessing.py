# milestone1_preprocessing.py - FIXED for Windows

import json
import pandas as pd
import os

def process_huge_json(input_file, output_csv):
    # 1. Load the raw data (Ingestion)
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        print(f"Current directory: {os.getcwd()}")
        print(f"Looking for file at: {os.path.abspath(input_file)}")
        return

    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    all_emails = []

    # 2. Handle Data Variety (Transformation)
    if isinstance(data, dict):
        for thread_id, messages in data.items():
            for msg in messages:
                msg['thread_id'] = thread_id
                all_emails.append(msg)
    else:
        all_emails = data

    # 3. Data Quality & Cleaning
    df = pd.DataFrame(all_emails)

    # Drop rows where critical fields are NaN or empty
    df = df.dropna(subset=['From', 'To', 'Body'])
    df = df[(df['From'] != "") & (df['To'] != "")]
    
    # 4. Save to CSV
    df.to_csv(output_csv, index=False, encoding='utf-8')
    print(f"Milestone 1 Complete: {output_csv} created with {len(df)} cleaned rows.")
    print(f"File saved at: {os.path.abspath(output_csv)}")

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, 'data')
    
    # Ensure the data directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"Created data directory: {data_dir}")
    
    input_file = os.path.join(data_dir, 'cleaned_enron_emails.json')
    output_file = os.path.join(data_dir, 'processed_emails.csv')
    
    print(f"Looking for input file: {input_file}")
    process_huge_json(input_file, output_file)