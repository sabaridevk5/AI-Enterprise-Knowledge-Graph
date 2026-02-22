"""
Auto-generated path configuration for Enterprise Knowledge Graph
"""

import os
import sys

# Project paths
PROJECT_ROOT = r'C:\Users\SABARI\Desktop\enterprise_kg'
SRC_DIR = r'C:\Users\SABARI\Desktop\enterprise_kg\src'
DATA_DIR = r'C:\Users\SABARI\Desktop\enterprise_kg\data'

# Add src to path for imports
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def get_data_path(filename):
    """Get full path to a file in data directory"""
    return os.path.join(DATA_DIR, filename)

def ensure_data_dir():
    """Ensure data directory exists"""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created data directory: {DATA_DIR}")
    return DATA_DIR

# Common file paths
PROCESSED_EMAILS_CSV = get_data_path('processed_emails.csv')
CLEANED_ENRON_JSON = get_data_path('cleaned_enron_emails.json')
THREADED_EMAILS_JSON = get_data_path('threaded_emails.json')

print(f"📁 Path config loaded - Data directory: {DATA_DIR}")
