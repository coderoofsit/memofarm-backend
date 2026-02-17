import csv
import os
from datetime import datetime
from app.models.italian_medicine import ItalianMedicine


def import_confezioni_csv(csv_path, batch_size=1000):
    """
    Import Italian medicines from confezioni.csv file
    
    Args:
        csv_path: Path to the CSV file
        batch_size: Number of records to insert at once
    
    Returns:
        dict with import statistics
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    total_records = 0
    skipped_records = 0
    batch = []
    
    print(f"🚀 Starting import from: {csv_path}")
    start_time = datetime.now()
    
    with open(csv_path, 'r', encoding='utf-8') as file:
        # Read CSV with semicolon delimiter
        csv_reader = csv.DictReader(file, delimiter=';')
        
        for row in csv_reader:
            try:
                # Skip if missing required fields
                if not row.get('codice_aic'):
                    skipped_records += 1
                    continue
                
                medicine_data = {
                    "codice_aic": row.get('codice_aic', '').strip(),
                    "cod_farmaco": row.get('cod_farmaco', '').strip(),
                    "cod_confezione": row.get('cod_confezione', '').strip(),
                    "denominazione": row.get('denominazione', '').strip(),
                    "descrizione": row.get('descrizione', '').strip(),
                    "codice_ditta": row.get('codice_ditta', '').strip(),
                    "ragione_sociale": row.get('ragione_sociale', '').strip(),
                    "stato_amministrativo": row.get('stato_amministrativo', '').strip(),
                    "tipo_procedura": row.get('tipo_procedura', '').strip(),
                    "forma": row.get('forma', '').strip(),
                    "codice_atc": row.get('codice_atc', '').strip(),
                    "pa_associati": row.get('pa_associati', '').strip(),
                    "link": row.get('link', '').strip(),
                    "created_at": datetime.utcnow(),
                }
                
                batch.append(medicine_data)
                
                # Insert batch when it reaches batch_size
                if len(batch) >= batch_size:
                    inserted = ItalianMedicine.bulk_create(batch)
                    total_records += inserted
                    print(f"✅ Imported {total_records} records...")
                    batch = []
                    
            except Exception as e:
                print(f"⚠️ Error processing row: {e}")
                skipped_records += 1
                continue
        
        # Insert remaining records
        if batch:
            inserted = ItalianMedicine.bulk_create(batch)
            total_records += inserted
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    result = {
        "total_imported": total_records,
        "skipped": skipped_records,
        "duration_seconds": duration,
        "records_per_second": total_records / duration if duration > 0 else 0
    }
    
    print(f"\n🎉 Import completed!")
    print(f"📊 Total imported: {total_records}")
    print(f"⏭️ Skipped: {skipped_records}")
    print(f"⏱️ Duration: {duration:.2f} seconds")
    print(f"⚡ Speed: {result['records_per_second']:.2f} records/second")
    
    return result


def clear_italian_medicines():
    """Clear all Italian medicines from database"""
    count = ItalianMedicine.delete_all()
    print(f"🗑️ Deleted {count} Italian medicine records")
    return count
