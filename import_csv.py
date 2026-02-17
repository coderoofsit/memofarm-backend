"""
Import Italian medicines from CSV to MongoDB
Usage: python import_csv.py path/to/confezioni.csv
"""

import sys
import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient

# Load environment variables
load_dotenv()

def connect_to_mongodb():
    """Connect to MongoDB"""
    try:
        mongodb_uri = os.getenv("MONGODB_URI")
        db_name = os.getenv("DB_NAME", "memofarm")
        
        print(f"📡 Connecting to MongoDB...")
        print(f"   URI: {mongodb_uri[:50]}...")
        print(f"   Database: {db_name}")
        
        client = MongoClient(mongodb_uri)
        db = client[db_name]
        
        # Test connection
        client.server_info()
        print("✅ Connected to MongoDB\n")
        
        return db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)


def import_csv(csv_file_path, db):
    """Import CSV data to MongoDB"""
    
    if not os.path.exists(csv_file_path):
        print(f"❌ File not found: {csv_file_path}")
        sys.exit(1)
    
    print(f"📂 Reading CSV file: {csv_file_path}\n")
    
    collection = db["italian_medicines"]
    
    # Ask if user wants to clear existing data
    print(f"📊 Current medicines in database: {collection.count_documents({})}")
    clear = input("\n⚠️  Clear existing data before import? (yes/no): ").strip().lower()
    
    if clear == "yes":
        print("🗑️  Deleting existing data...")
        result = collection.delete_many({})
        print(f"   Deleted {result.deleted_count} documents\n")
    
    # Read and parse CSV
    medicines = []
    skipped = 0
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # CSV is semicolon-separated
            csv_reader = csv.DictReader(file, delimiter=';')
            
            print("📥 Importing data...")
            print("=" * 80)
            
            for i, row in enumerate(csv_reader, 1):
                # Skip rows with missing required fields
                if not row.get('codice_aic') or not row.get('denominazione'):
                    skipped += 1
                    continue
                
                medicine = {
                    "codice_aic": row['codice_aic'].strip(),
                    "cod_farmaco": row['cod_farmaco'].strip(),
                    "cod_confezione": row['cod_confezione'].strip(),
                    "denominazione": row['denominazione'].strip(),
                    "descrizione": row['descrizione'].strip(),
                    "codice_ditta": row['codice_ditta'].strip(),
                    "ragione_sociale": row['ragione_sociale'].strip(),
                    "stato_amministrativo": row['stato_amministrativo'].strip(),
                    "tipo_procedura": row['tipo_procedura'].strip(),
                    "forma": row['forma'].strip(),
                    "codice_atc": row['codice_atc'].strip(),
                    "pa_associati": row['pa_associati'].strip(),
                    "link": row.get('link', '').strip(),
                    "created_at": datetime.utcnow(),
                }
                
                medicines.append(medicine)
                
                # Print progress every 1000 records
                if i % 1000 == 0:
                    print(f"   📦 Processed {i} records...")
                
                # Bulk insert every 5000 records for performance
                if len(medicines) >= 5000:
                    collection.insert_many(medicines)
                    print(f"   ✅ Inserted {len(medicines)} medicines")
                    medicines = []
            
            # Insert remaining medicines
            if medicines:
                collection.insert_many(medicines)
                print(f"   ✅ Inserted {len(medicines)} medicines")
            
            print("=" * 80)
            print(f"\n✅ Import completed successfully!")
            print(f"   📊 Total records processed: {i}")
            print(f"   ⚠️  Skipped (invalid): {skipped}")
            print(f"   💾 Total in database: {collection.count_documents({})}")
            
            # Create index on codice_aic for faster lookups
            print("\n🔍 Creating index on codice_aic...")
            collection.create_index("codice_aic", unique=True)
            collection.create_index("denominazione")
            collection.create_index("ragione_sociale")
            collection.create_index("pa_associati")
            print("   ✅ Indexes created")
            
            # Show sample data
            print("\n📋 Sample data (first 3 medicines):")
            print("-" * 80)
            for med in collection.find().limit(3):
                print(f"   🔹 {med['codice_aic']} - {med['denominazione']}")
                print(f"      Manufacturer: {med['ragione_sociale']}")
                print(f"      Form: {med['forma']}")
                print(f"      Active: {med['pa_associati']}")
                print()
            
    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    """Main function"""
    print("\n" + "=" * 80)
    print("🇮🇹 ITALIAN MEDICINES CSV IMPORT TOOL")
    print("=" * 80 + "\n")
    
    if len(sys.argv) < 2:
        print("Usage: python import_csv.py <path_to_csv_file>")
        print("\nExample:")
        print("  python import_csv.py data/confezioni.csv")
        print("  python import_csv.py G:\\data\\confezioni.csv")
        sys.exit(1)
    
    csv_file_path = sys.argv[1]
    
    # Connect to MongoDB
    db = connect_to_mongodb()
    
    # Import CSV
    import_csv(csv_file_path, db)
    
    print("\n" + "=" * 80)
    print("✨ All done!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
