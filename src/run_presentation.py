#!/usr/bin/env python3
"""
Enterprise Knowledge Graph Builder - Complete Presentation Runner
Run this to demonstrate all milestones sequentially for Infosys review
"""

import subprocess
import sys
import os
import time
import shutil

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Get directories
SRC_DIR = os.path.dirname(os.path.abspath(__file__))  # This is src folder
BASE_DIR = os.path.dirname(SRC_DIR)                    # This is enterprise_kg folder
DATA_DIR = os.path.join(BASE_DIR, 'data')              # This is enterprise_kg/data

print(f"📁 Source folder: {SRC_DIR}")
print(f"📁 Base folder: {BASE_DIR}")
print(f"📁 Data folder: {DATA_DIR}")

def create_path_config():
    """Create a path configuration file that all scripts can import"""
    config_path = os.path.join(SRC_DIR, 'path_config.py')
    
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(f'''"""
Auto-generated path configuration for Enterprise Knowledge Graph
"""

import os
import sys

# Project paths
PROJECT_ROOT = r'{BASE_DIR}'
SRC_DIR = r'{SRC_DIR}'
DATA_DIR = r'{DATA_DIR}'

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
        print(f"Created data directory: {{DATA_DIR}}")
    return DATA_DIR

# Common file paths
PROCESSED_EMAILS_CSV = get_data_path('processed_emails.csv')
CLEANED_ENRON_JSON = get_data_path('cleaned_enron_emails.json')
THREADED_EMAILS_JSON = get_data_path('threaded_emails.json')

print(f"📁 Path config loaded - Data directory: {{DATA_DIR}}")
''')
    
    print(f"✅ Created path configuration at: {config_path}")
    return config_path

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*80)
    print(f" {text}")
    print("="*80)

def run_script(script_name, description):
    """Run a Python script from src folder"""
    print_header(f"Running: {description}")
    
    script_path = os.path.join(SRC_DIR, script_name)
    print(f"Script: {script_path}\n")
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found: {script_path}")
        return False
    
    try:
        # Set environment variable to tell scripts where data is
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['DATA_DIR'] = DATA_DIR
        env['PROJECT_ROOT'] = BASE_DIR
        env['PYTHONPATH'] = SRC_DIR + os.pathsep + env.get('PYTHONPATH', '')
        
        # Run the script
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, cwd=SRC_DIR,
                              env=env, encoding='utf-8', errors='replace')
        
        if result.stdout:
            # Replace emojis for Windows compatibility
            output = result.stdout.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('🚀', '[START]')
            print(output)
        
        if result.stderr:
            error_output = result.stderr.replace('✅', '[OK]').replace('❌', '[ERROR]').replace('🚀', '[START]')
            print("Warnings/Errors:")
            print(error_output)
            
        return True
    except Exception as e:
        print(f"❌ Failed to run {script_name}: {e}")
        return False

def check_files():
    """Check if all required files exist"""
    required_files = [
        'milestone1_preprocessing.py',
        'milestone2_graph_build.py',
        'milestone3_semantic_search.py', 
        'm4_upload_to_pinecone.py',
        'app.py',
        'graph_analytics.py'
    ]
    
    print("\n🔍 Checking for required files...")
    print(f"📁 Source files in: {SRC_DIR}")
    print(f"📁 Data files in: {DATA_DIR}\n")
    
    all_good = True
    
    # Check source files
    for file in required_files:
        file_path = os.path.join(SRC_DIR, file)
        if os.path.exists(file_path):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_good = False
    
    # Check data directory
    if os.path.exists(DATA_DIR):
        print(f"✅ data/ directory found at: {DATA_DIR}")
        
        # Check for input data file
        json_path = os.path.join(DATA_DIR, 'cleaned_enron_emails.json')
        if os.path.exists(json_path):
            size = os.path.getsize(json_path) / (1024*1024)
            print(f"✅ cleaned_enron_emails.json ({size:.1f} MB)")
        else:
            print(f"❌ cleaned_enron_emails.json not found in {DATA_DIR}")
            all_good = False
        
        # Check for processed emails
        csv_path = os.path.join(DATA_DIR, 'processed_emails.csv')
        if os.path.exists(csv_path):
            size = os.path.getsize(csv_path) / (1024*1024)
            print(f"✅ processed_emails.csv ({size:.2f} MB)")
    else:
        print(f"❌ data/ directory not found at: {DATA_DIR}")
        all_good = False
    
    return all_good

def patch_scripts():
    """Patch all milestone scripts to use the correct data path"""
    print("\n🔧 Patching scripts to use correct data paths...")
    
    # List of scripts to patch
    scripts_to_patch = [
        'milestone2_graph_build.py',
        'milestone3_semantic_search.py',
        'm4_upload_to_pinecone.py',
        'app.py'
    ]
    
    for script_name in scripts_to_patch:
        script_path = os.path.join(SRC_DIR, script_name)
        if not os.path.exists(script_path):
            print(f"❌ {script_name} not found, skipping...")
            continue
        
        # Read the script
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already patched
        if 'import path_config' in content:
            print(f"✅ {script_name} already patched")
            continue
        
        # Add import at the top (after any existing imports)
        lines = content.split('\n')
        new_lines = []
        import_added = False
        
        for line in lines:
            if not import_added and line.startswith('import ') or line.startswith('from '):
                new_lines.append(line)
                if 'import' in line and not import_added:
                    new_lines.append('import path_config  # Auto-added for path configuration')
                    import_added = True
            else:
                if not import_added and line.strip() and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                    new_lines.append('import path_config  # Auto-added for path configuration')
                    import_added = True
                new_lines.append(line)
        
        # Write back
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_lines))
        
        print(f"✅ Patched {script_name}")
    
    return True

def run_milestone1_with_check():
    """Run milestone1 with correct data path"""
    print_header("Running Milestone 1: Data Ingestion & Cleaning")
    
    milestone1_path = os.path.join(SRC_DIR, 'milestone1_preprocessing.py')
    
    if not os.path.exists(milestone1_path):
        print(f"❌ milestone1_preprocessing.py not found")
        return False
    
    # Create a temporary wrapper that uses path_config
    temp_script = os.path.join(SRC_DIR, 'temp_m1_run.py')
    with open(temp_script, 'w', encoding='utf-8') as f:
        f.write(f'''
import os
import sys
import path_config

# Import the milestone1 function
sys.path.insert(0, r'{SRC_DIR}')
from milestone1_preprocessing import process_huge_json

# Use paths from config
input_file = path_config.CLEANED_ENRON_JSON
output_file = path_config.PROCESSED_EMAILS_CSV

print(f"Input file: {{input_file}}")
print(f"Output file: {{output_file}}")
print(f"Data directory: {{path_config.DATA_DIR}}")

if os.path.exists(input_file):
    process_huge_json(input_file, output_file)
    print(f"\\n✅ Milestone 1 completed successfully!")
else:
    print(f"❌ ERROR: Input file not found at {{input_file}}")
    print(f"Please place cleaned_enron_emails.json in: {{path_config.DATA_DIR}}")
''')
    
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONPATH'] = SRC_DIR + os.pathsep + env.get('PYTHONPATH', '')
    
    result = subprocess.run([sys.executable, temp_script], 
                          capture_output=True, text=True, cwd=SRC_DIR,
                          env=env, encoding='utf-8', errors='replace')
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    # Clean up
    if os.path.exists(temp_script):
        os.remove(temp_script)
    
    return True

def run_streamlit():
    """Launch the Streamlit app"""
    print_header("Launching Enterprise Dashboard")
    
    app_path = os.path.join(SRC_DIR, 'app.py')
    
    if not os.path.exists(app_path):
        print(f"❌ app.py not found in {SRC_DIR}")
        return False
    
    print("Starting Streamlit app...\n")
    print(f"📍 Dashboard will open at: http://localhost:8501")
    print(f"📍 Data directory: {DATA_DIR}")
    print("📍 Press Ctrl+C in terminal to stop the dashboard\n")
    
    # Set environment variables for the app
    env = os.environ.copy()
    env['DATA_DIR'] = DATA_DIR
    env['PROJECT_ROOT'] = BASE_DIR
    env['PYTHONPATH'] = SRC_DIR + os.pathsep + env.get('PYTHONPATH', '')
    
    subprocess.run(['streamlit', 'run', app_path], cwd=SRC_DIR, env=env)
    return True

def main():
    print_header("ENTERPRISE KNOWLEDGE GRAPH BUILDER")
    print("Complete Project Demonstration for Infosys Review\n")
    
    print(f"📁 Source folder: {SRC_DIR}")
    print(f"📁 Data folder: {DATA_DIR}")
    print(f"📁 Run command: python src/run_presentation.py\n")
    
    # Create path configuration
    create_path_config()
    
    # Check files
    if not check_files():
        print("\n" + "-"*60)
        response = input("⚠️ Some files are missing. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    # Patch scripts to use correct paths
    patch_scripts()
    
    print("\n" + "-"*60)
    print("Starting sequential milestone demonstration...")
    print("Press Enter at each step to continue")
    print("-"*60 + "\n")
    
    # Milestone 1
    input("\n👉 Press Enter to start Milestone 1: Data Ingestion...")
    run_milestone1_with_check()
    
    # Milestone 2
    input("\n👉 Press Enter to start Milestone 2: Graph Construction...")
    run_script('milestone2_graph_build.py', 'Milestone 2: Neo4j Graph Construction')
    
    # Milestone 3
    input("\n👉 Press Enter to start Milestone 3: Local Semantic Search Demo...")
    run_script('milestone3_semantic_search.py', 'Milestone 3: Semantic Search')
    
    # Milestone 4
    input("\n👉 Press Enter to start Milestone 4: Pinecone Cloud Upload...")
    run_script('m4_upload_to_pinecone.py', 'Milestone 4: Pinecone Upload')
    
    # Final Dashboard
    input("\n👉 Press Enter to launch the main application...")
    run_streamlit()
    
    print("\n" + "="*80)
    print("🎉 Presentation Complete! Thank you for watching!")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Presentation interrupted. Good luck with your Infosys review!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()