#!/usr/bin/env python3
"""
Script to import Italian medicines from confezioni.csv into MongoDB
Usage: python import_medicines.py [--clear]
"""
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app import create_app
from app.utils.csv_importer import import_confezioni_csv, clear_italian_medicines


def main():
    """Main import function"""
    # Initialize Flask app (to load config and DB connection)
    app = create_app()
    
    with app.app_context():
        # Check if --clear flag is provided
        if "--clear" in sys.argv:
            print("🗑️ Clearing existing Italian medicine data...")
            clear_italian_medicines()
            print("✅ Database cleared\n")
        
        # Path to CSV file
        csv_path = os.path.join(os.path.dirname(__file__), "confezioni.csv")
        
        if not os.path.exists(csv_path):
            print(f"❌ Error: CSV file not found at {csv_path}")
            print("Please ensure confezioni.csv is in the backend/ directory")
            sys.exit(1)
        
        try:
            # Import the CSV
            result = import_confezioni_csv(csv_path)
            
            print("\n" + "="*60)
            print("✅ Import Summary:")
            print("="*60)
            print(f"Total Records Imported: {result['total_imported']}")
            print(f"Skipped Records: {result['skipped']}")
            print(f"Time Taken: {result['duration_seconds']:.2f} seconds")
            print(f"Import Speed: {result['records_per_second']:.2f} records/sec")
            print("="*60)
            
        except Exception as e:
            print(f"❌ Import failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    main()
