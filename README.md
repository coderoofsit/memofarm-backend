# Memofarm Backend API

Flask backend for Memofarm - Italian Medicine Management App

## Features
- Google OAuth Authentication
- Apple Sign In Authentication
- MongoDB Database
- User Management
- Medicine Management with AIC codes
- Italian Medicine Database (AIFA confezioni.csv with 158k+ medicines)
- Barcode/AIC code search
- RESTful API endpoints

## Setup

### Prerequisites
- Python 3.8+
- MongoDB
- Google OAuth credentials
- Apple Sign In credentials

### Installation

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file with:
```
MONGODB_URI=mongodb://localhost:27017/memofarm
SECRET_KEY=your-secret-key-here
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
APPLE_TEAM_ID=your-apple-team-id
APPLE_KEY_ID=your-apple-key-id
```

4. Import Italian medicine database:
```bash
# First time import
python import_medicines.py

# Re-import (clears existing data first)
python import_medicines.py --clear
```

5. Run the application:
```bash
python run.py
```

## API Endpoints

### Authentication
- `POST /api/auth/google` - Google OAuth login
- `POST /api/auth/apple` - Apple Sign In login
- `GET /api/auth/me` - Get current user info

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update user profile
- `DELETE /api/users/account` - Delete user account

### Medicines (User's Personal Collection)
- `GET /api/medicines` - Get all user medicines
- `POST /api/medicines` - Add new medicine
- `GET /api/medicines/:id` - Get medicine by ID
- `PUT /api/medicines/:id` - Update medicine
- `DELETE /api/medicines/:id` - Delete medicine
- `GET /api/medicines/barcode/:code` - Search by barcode
- `GET /api/medicines/aic/:code` - Search by AIC code

### Italian Medicines (AIFA Database - 158k+ medicines)
- `GET /api/italian-medicines/search?q=<query>&type=<name|aic|manufacturer|ingredient>&limit=<20>` - Search medicines
- `GET /api/italian-medicines/aic/:codice_aic` - Get medicine by AIC code
- `GET /api/italian-medicines/stats` - Get database statistics
- `GET /api/italian-medicines/list?limit=<100>&skip=<0>` - Get paginated list

## Database Schema

### Users Collection
```json
{
  "_id": "ObjectId",
  "firebase_uid": "string",
  "email": "string",
  "name": "string",
  "photo_url": "string",
  "provider": "google|apple",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Medicines Collection
```json
{
  "_id": "ObjectId",
  "user_id": "ObjectId",
  "aic_code": "string",
  "barcode": "string",
  "name": "string",
  "description": "string",
  "manufacturer": "string",
  "batch_number": "string",
  "serial_number": "string",
  "expiry_date": "datetime",
  "quantity": "number",
  "category": "string",
  "notes": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Italian Medicines Collection (AIFA Database)
```json
{
  "_id": "ObjectId",
  "codice_aic": "string (unique)",
  "cod_farmaco": "string",
  "cod_confezione": "string",
  "denominazione": "string (medicine name)",
  "descrizione": "string (package description)",
  "codice_ditta": "string",
  "ragione_sociale": "string (manufacturer)",
  "stato_amministrativo": "string",
  "tipo_procedura": "string",
  "forma": "string (form: tablet, capsule, etc.)",
  "codice_atc": "string",
  "pa_associati": "string (active ingredients)",
  "link": "string",
  "created_at": "datetime"
}
```

## CSV Import

The backend includes an Italian medicine database from AIFA (Agenzia Italiana del Farmaco) with 158,000+ medicines.

### CSV Format
The `confezioni.csv` file contains Italian medicines with semicolon-separated values:
- **codice_aic**: Unique AIC code (Autorizzazione all'Immissione in Commercio)
- **cod_farmaco**: Drug code
- **cod_confezione**: Package code
- **denominazione**: Medicine name
- **descrizione**: Package description
- **ragione_sociale**: Manufacturer name
- **forma**: Medicine form (tablet, capsule, etc.)
- **pa_associati**: Active pharmaceutical ingredients

### Import Process
```bash
# Import for the first time
python import_medicines.py

# Clear and re-import
python import_medicines.py --clear
```

The import script:
- Processes ~158,000 records
- Batch inserts for performance (1000 records at a time)
- Creates indexes for fast searching
- Provides progress updates and statistics
