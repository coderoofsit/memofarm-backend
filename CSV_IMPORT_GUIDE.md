# CSV Import Guide

## Import Italian Medicines Data to MongoDB

This guide shows how to import Italian medicine data from CSV files to your MongoDB database.

---

## Prerequisites

✅ Backend environment set up (.env file with MongoDB connection)  
✅ CSV file with Italian medicines data (confezioni.csv)  
✅ Python installed with required packages

---

## CSV Format

The CSV file should be **semicolon-separated** (`;`) with the following columns:

```
codice_aic;cod_farmaco;cod_confezione;denominazione;descrizione;codice_ditta;ragione_sociale;stato_amministrativo;tipo_procedura;forma;codice_atc;pa_associati;link
```

**Example rows:**
```
000367045;000367;045;TISANA KELEMATA;10 BUSTINE FILTRO G 2;2934;KELEMATA S.R.L.;Autorizzata;Procedura Nazionale;Tisana;A06AB06;SENNA FOGLIA;
000527061;000527;061;MAGNESIA EFFERVESCENTE SELLA;MENTA-POLVERE EFF. FLAC.115 G;3399;LABORATORIO CHIMICO FARMACEUTICO A. SELLA S.R.L.;Autorizzata;Procedura Nazionale;Polvere effervescente;A02AA04;MAGNESIO IDROSSIDO;
```

---

## How to Import

### Step 1: Prepare CSV File

1. Place your CSV file somewhere accessible
2. Note the full path, for example:
   - `G:\data\confezioni.csv`
   - `C:\Users\YourName\Downloads\confezioni.csv`

### Step 2: Run Import Script

Open terminal in backend folder and run:

```bash
cd G:\companyproject\memofarm\backend

python import_csv.py path/to/your/confezioni.csv
```

**Example:**
```bash
python import_csv.py G:\data\confezioni.csv
```

### Step 3: Follow Prompts

The script will show:
```
📡 Connecting to MongoDB...
✅ Connected to MongoDB

📂 Reading CSV file: G:\data\confezioni.csv

📊 Current medicines in database: 0

⚠️  Clear existing data before import? (yes/no):
```

**Type:**
- `yes` - Delete existing data and import fresh
- `no` - Keep existing data and add new records

### Step 4: Wait for Import

The script will show progress:
```
📥 Importing data...
   📦 Processed 1000 records...
   ✅ Inserted 5000 medicines
   📦 Processed 5000 records...
   ✅ Inserted 5000 medicines
   ...
```

### Step 5: Verify Success

After completion, you'll see:
```
✅ Import completed successfully!
   📊 Total records processed: 158423
   ⚠️  Skipped (invalid): 12
   💾 Total in database: 158411

🔍 Creating index on codice_aic...
   ✅ Indexes created

📋 Sample data (first 3 medicines):
   🔹 000367045 - TISANA KELEMATA
      Manufacturer: KELEMATA S.R.L.
      Form: Tisana
      Active: SENNA FOGLIA
```

---

## Script Features

### ✅ Automatic Features

1. **Progress Tracking** - Shows progress every 1000 records
2. **Bulk Insert** - Inserts 5000 records at a time for performance
3. **Data Validation** - Skips rows with missing required fields
4. **Index Creation** - Creates indexes for fast searching:
   - `codice_aic` (unique)
   - `denominazione` (medicine name)
   - `ragione_sociale` (manufacturer)
   - `pa_associati` (active ingredients)
5. **Sample Display** - Shows first 3 medicines after import

### ⚠️ Safety Features

- Asks before clearing existing data
- Validates file exists before starting
- Tests MongoDB connection before import
- Shows detailed error messages if something fails

---

## Testing the Import

After importing, test the API:

### 1. Check Total Count
```bash
curl http://192.168.1.5:5000/api/italian-medicines/stats
```

**Expected response:**
```json
{
  "success": true,
  "total_medicines": 158411,
  "unique_manufacturers": 1234,
  "unique_forms": 56
}
```

### 2. Search by Name
```bash
curl "http://192.168.1.5:5000/api/italian-medicines/search?q=ASPIRINA"
```

### 3. Get by AIC Code
```bash
curl http://192.168.1.5:5000/api/italian-medicines/aic/000367045
```

---

## Common Issues & Solutions

### Issue 1: "File not found"
**Solution:** Check file path is correct and use full path with drive letter

### Issue 2: "Failed to connect to MongoDB"
**Solution:** 
- Make sure `.env` file has correct `MONGODB_URI`
- Check MongoDB Atlas IP whitelist includes your IP
- Test connection with: `python -c "from app.database import Database; Database.get_db()"`

### Issue 3: "Duplicate key error"
**Solution:** 
- Clear existing data first (answer `yes` when prompted)
- Or manually clear: 
```python
from pymongo import MongoClient
client = MongoClient("your-mongodb-uri")
db = client["memofarm"]
db["italian_medicines"].delete_many({})
```

### Issue 4: "Encoding error"
**Solution:** 
- Make sure CSV is UTF-8 encoded
- Open CSV in Notepad++, check encoding, convert if needed

---

## Performance Notes

- **Small files (< 10,000 records):** Instant
- **Medium files (10,000 - 50,000):** 1-2 minutes
- **Large files (50,000 - 200,000):** 5-10 minutes

**Tip:** The script uses bulk insert for optimal performance!

---

## Re-importing Data

To update the database with new CSV data:

1. Run the import script again
2. Answer `yes` to clear existing data
3. New data will be imported fresh

**Or** keep existing data and add more:
1. Answer `no` when prompted
2. New records will be added (duplicates may occur)

---

## Where is the Data?

**Database:** MongoDB Atlas (Cloud)  
**Collection:** `italian_medicines`  
**Total Size:** ~158,000+ medicines from AIFA registry

Access via:
- Backend API: `http://192.168.1.5:5000/api/italian-medicines/*`
- Flutter app: `ItalianMedicineApiService()`

---

## Next Steps After Import

1. ✅ Test search functionality in Flutter app
2. ✅ Barcode scanner will auto-fill medicine names
3. ✅ Users can search 158k+ Italian medicines
4. ✅ Medicine suggestions when adding new medicines

---

## Need Help?

**Check logs:** The script shows detailed progress and errors

**Test MongoDB connection:**
```bash
cd backend
python -c "from app.database import Database; print('✅ Connected' if Database.get_db() else '❌ Failed')"
```

**Check collection manually:**
```python
from pymongo import MongoClient
client = MongoClient("your-uri")
db = client["memofarm"]
print(f"Total: {db['italian_medicines'].count_documents({})}")
print(f"Sample: {db['italian_medicines'].find_one()}")
```

---

*Last Updated: February 17, 2026*
