# Memofarm Admin API Documentation

**Base URL:** `http://localhost:5000/api/admin`  
**Authentication:** API Key in header: `X-Admin-Key: memofarm_admin_2026_secure_key`  
**Response Format:** JSON  
**Date Format:** ISO 8601

---

## Authentication

All endpoints require admin API key:

```
X-Admin-Key: memofarm_admin_2026_secure_key
```

---

## Endpoints

### Statistics

#### `GET /stats`

Returns system-wide statistics.

**Response 200:**
```json
{
  "data": {
    "users": {
      "total": 150,
      "active": 145,
      "paused": 5
    },
    "medicines": {
      "total": 2450,
      "expired": 120,
      "by_category": [
        {"_id": "Painkillers", "count": 850}
      ]
    },
    "italian_medicines": {
      "total": 158078
    }
  },
  "status": 200
}
```

---

### Italian Medicines (158k+ AIFA Database)

#### `GET /italian-medicines`

List Italian medicines with filtering and pagination.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Results per page |
| `skip` | integer | 0 | Offset for pagination |
| `search` | string | - | Search by medicine name (denominazione) |
| `manufacturer` | string | - | Filter by manufacturer (ragione_sociale) |
| `aic` | string | - | Filter by AIC code |

**Response 200:**
```json
{
  "data": {
    "medicines": [
      {
        "id": "65f1234567890abcdef12345",
        "codice_aic": "027912010",
        "cod_farmaco": "027912",
        "cod_confezione": "010",
        "denominazione": "ASPIRINA 20 compresse 500 mg",
        "descrizione": "500 MG COMPRESSE RIVESTITE",
        "codice_ditta": "01234",
        "ragione_sociale": "Bayer SpA",
        "stato_amministrativo": "Autorizzato",
        "tipo_procedura": "Nazionale",
        "forma": "compressa",
        "codice_atc": "N02BA01",
        "pa_associati": "acido acetilsalicilico",
        "link": "",
        "created_at": "2024-01-15T10:30:00.000Z"
      }
    ],
    "total": 158078,
    "limit": 50,
    "skip": 0
  },
  "status": 200
}
```

---

#### `GET /italian-medicines/{id}`

Get single Italian medicine by ID.

**Response 200:**
```json
{
  "data": {
    "id": "65f1234567890abcdef12345",
    "codice_aic": "027912010",
    "denominazione": "ASPIRINA 20 compresse 500 mg",
    "ragione_sociale": "Bayer SpA",
    "forma": "compressa",
    "pa_associati": "acido acetilsalicilico",
    "codice_atc": "N02BA01",
    "stato_amministrativo": "Autorizzato",
    "created_at": "2024-01-15T10:30:00.000Z"
  },
  "status": 200
}
```

**Response 404:**
```json
{
  "message": "Italian medicine not found",
  "status": 404
}
```

---

#### `POST /italian-medicines`

Create new Italian medicine.

**Request Body:**
```json
{
  "codice_aic": "099999999",           // Required, must be unique
  "denominazione": "MEDICINE NAME",    // Required
  "cod_farmaco": "099999",
  "cod_confezione": "001",
  "descrizione": "Description",
  "codice_ditta": "12345",
  "ragione_sociale": "Manufacturer SpA",
  "stato_amministrativo": "Autorizzato",
  "tipo_procedura": "Nazionale",
  "forma": "compressa",
  "codice_atc": "N02BA01",
  "pa_associati": "active ingredient",
  "link": ""
}
```

**Response 201:**
```json
{
  "data": {
    "id": "65f9999999999abcdef99999",
    "codice_aic": "099999999",
    "denominazione": "MEDICINE NAME",
    "created_at": "2026-02-17T10:30:00.000Z"
  },
  "message": "Italian medicine created successfully",
  "status": 201
}
```

**Response 400:**
```json
{
  "message": "codice_aic is required",
  "status": 400
}
```

---

#### `PUT /italian-medicines/{id}`

Update Italian medicine.

**Request Body:**
```json
{
  "denominazione": "Updated name",
  "ragione_sociale": "Updated manufacturer",
  "stato_amministrativo": "Revocato"
}
```

**Response 200:**
```json
{
  "data": {
    "id": "65f1234567890abcdef12345",
    "denominazione": "Updated name",
    "ragione_sociale": "Updated manufacturer"
  },
  "message": "Italian medicine updated successfully",
  "status": 200
}
```

**Response 404:**
```json
{
  "message": "Italian medicine not found",
  "status": 404
}
```

---

#### `DELETE /italian-medicines/{id}`

Delete Italian medicine.

**Response 200:**
```json
{
  "message": "Italian medicine deleted successfully",
  "status": 200
}
```

**Response 404:**
```json
{
  "message": "Italian medicine not found",
  "status": 404
}
```

---

#### `POST /italian-medicines/bulk-delete`

Delete multiple Italian medicines.

**Request Body:**
```json
{
  "ids": [
    "65f1234567890abcdef12345",
    "65f9876543210abcdef54321"
  ]
}
```

**Response 200:**
```json
{
  "data": {
    "deleted_count": 2
  },
  "message": "Successfully deleted 2 medicines",
  "status": 200
}
```

---

#### `POST /italian-medicines/bulk-upload`

Bulk upload Italian medicines from CSV or Excel file. Headers are auto-mapped.

**Content-Type:** `multipart/form-data`

**Form Fields:**
| Field | Type | Description |
|-------|------|-------------|
| `file` | file | CSV or XLSX file (required) |
| `skip_duplicates` | string | `"true"` (default) or `"false"` |

**Recognized CSV/Excel Headers:**
- `codice_aic` / `aic` / `aic_code`
- `denominazione` / `nome` / `name` / `medicine name`
- `descrizione` / `description`
- `ragione_sociale` / `manufacturer` / `produttore`
- `stato_amministrativo` / `stato` / `status`
- `forma` / `form` / `dosage form`
- `codice_atc` / `atc` / `atc_code`
- `pa_associati` / `principio attivo` / `active ingredient`
- `cod_farmaco`, `cod_confezione`, `codice_ditta`, `tipo_procedura`, `link`

**Response 200:**
```json
{
  "data": {
    "inserted": 150,
    "skipped": 10,
    "errors_count": 2,
    "errors": ["Row 5: missing codice_aic", "Row 12: missing denominazione"],
    "total_rows": 162,
    "mapped_fields": ["codice_aic", "denominazione", "ragione_sociale", "forma"]
  },
  "message": "Uploaded 150 medicines (10 duplicates skipped, 2 errors)",
  "status": 200
}
```

**Response 400:**
```json
{
  "message": "No file provided",
  "status": 400
}
```

---

### User Management

#### `GET /users`

List all users with pagination and filtering.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Results per page |
| `skip` | integer | 0 | Offset for pagination |
| `status` | string | - | Filter: `active`, `paused` |
| `search` | string | - | Search by email or name |

**Response 200:**
```json
{
  "data": {
    "users": [
      {
        "id": "65f1234567890abcdef12345",
        "firebase_uid": "abc123xyz",
        "email": "john@example.com",
        "name": "John Doe",
        "provider": "google",
        "status": "active",
        "medicine_count": 15,
        "created_at": "2024-01-15T10:30:00.000Z",
        "updated_at": "2024-01-20T14:25:00.000Z"
      }
    ],
    "total": 150,
    "limit": 50,
    "skip": 0
  },
  "status": 200
}
```

---

#### `GET /users/{id}`

Get user details including their medicines.

**Response 200:**
```json
{
  "data": {
    "id": "65f1234567890abcdef12345",
    "firebase_uid": "abc123xyz",
    "email": "john@example.com",
    "name": "John Doe",
    "provider": "google",
    "status": "active",
    "created_at": "2024-01-15T10:30:00.000Z",
    "updated_at": "2024-01-20T14:25:00.000Z",
    "medicine_count": 2,
    "medicines": [
      {
        "id": "65f9876543210abcdef54321",
        "name": "Aspirina",
        "category": "Painkillers",
        "quantity": 20,
        "expiry_date": "2025-12-31T00:00:00.000Z",
        "aic_code": "027912010",
        "notes": "Take with food"
      }
    ]
  },
  "status": 200
}
```

**Response 404:**
```json
{
  "message": "User not found",
  "status": 404
}
```

---

#### `PUT /users/{id}/pause`

Pause or unpause user account.

**Request Body:**
```json
{
  "paused": true,                      // Required: true to pause, false to unpause
  "reason": "Suspicious activity"      // Optional: reason for pausing
}
```

**Response 200:**
```json
{
  "data": {
    "id": "65f1234567890abcdef12345",
    "email": "john@example.com",
    "status": "paused",
    "paused_at": "2024-01-25T09:15:00.000Z",
    "pause_reason": "Suspicious activity"
  },
  "message": "User paused successfully",
  "status": 200
}
```

**Response 404:**
```json
{
  "message": "User not found",
  "status": 404
}
```

---

#### `DELETE /users/{id}`

Delete user and all associated medicines.

**Response 200:**
```json
{
  "message": "User and all associated data deleted successfully",
  "status": 200
}
```

**Response 404:**
```json
{
  "message": "User not found",
  "status": 404
}
```

---

### User Medicines Management

#### `GET /medicines`

List all medicines across all users.

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | integer | 50 | Results per page |
| `skip` | integer | 0 | Offset for pagination |
| `category` | string | - | Filter by category |
| `expired` | boolean | - | Filter: `true` (expired), `false` (valid) |
| `user_id` | string | - | Filter by user ID |
| `search` | string | - | Search by medicine name |

**Response 200:**
```json
{
  "data": {
    "medicines": [
      {
        "id": "65f9876543210abcdef54321",
        "user_id": "65f1234567890abcdef12345",
        "user_email": "john@example.com",
        "name": "Augmentin",
        "category": "Antibiotics",
        "quantity": 14,
        "expiry_date": "2024-01-10T00:00:00.000Z",
        "aic_code": "027912010",
        "manufacturer": "GSK",
        "notes": "Expired",
        "created_at": "2024-01-15T10:30:00.000Z"
      }
    ],
    "total": 250,
    "limit": 50,
    "skip": 0
  },
  "status": 200
}
```

---

#### `GET /medicines/{id}`

Get medicine details (admin access - no user restriction).

**Response 200:**
```json
{
  "data": {
    "id": "65f9876543210abcdef54321",
    "user_id": "65f1234567890abcdef12345",
    "name": "Aspirina",
    "description": "500mg tablets",
    "category": "Painkillers",
    "quantity": 20,
    "expiry_date": "2025-12-31T00:00:00.000Z",
    "aic_code": "027912010",
    "barcode": "8012345678901",
    "manufacturer": "Bayer",
    "batch_number": "LOT12345",
    "serial_number": "SN98765",
    "notes": "Take with food",
    "user": {
      "id": "65f1234567890abcdef12345",
      "email": "john@example.com",
      "name": "John Doe"
    }
  },
  "status": 200
}
```

---

#### `POST /medicines`

Create medicine for specific user.

**Request Body:**
```json
{
  "user_id": "65f1234567890abcdef12345",  // Required
  "name": "Tachipirina 500mg",            // Required
  "description": "Paracetamol tablets",
  "category": "Painkillers",
  "quantity": 20,
  "expiry_date": "2025-12-31T00:00:00.000Z",  // ISO 8601 format
  "aic_code": "027912010",
  "barcode": "8012345678901",
  "manufacturer": "Angelini",
  "batch_number": "LOT2024A",
  "serial_number": "SN123456",
  "notes": "Take before meals"
}
```

**Response 201:**
```json
{
  "data": {
    "id": "65f9999999999abcdef99999",
    "user_id": "65f1234567890abcdef12345",
    "name": "Tachipirina 500mg",
    "category": "Painkillers",
    "quantity": 20,
    "created_at": "2024-01-25T10:30:00.000Z"
  },
  "message": "Medicine created successfully",
  "status": 201
}
```

---

#### `PUT /medicines/{id}`

Update any medicine without user restriction.

**Request Body:**
```json
{
  "name": "Tachipirina 1000mg",
  "quantity": 15,
  "notes": "Updated dosage"
}
```

**Response 200:**
```json
{
  "data": {
    "id": "65f9876543210abcdef54321",
    "name": "Tachipirina 1000mg",
    "quantity": 15,
    "updated_at": "2024-01-25T11:45:00.000Z"
  },
  "message": "Medicine updated successfully",
  "status": 200
}
```

---

#### `DELETE /medicines/{id}`

Delete any medicine without user restriction.

**Response 200:**
```json
{
  "message": "Medicine deleted successfully",
  "status": 200
}
```

---

## Data Models

### ItalianMedicine
```typescript
{
  id: string
  codice_aic: string           // Required, unique
  cod_farmaco?: string
  cod_confezione?: string
  denominazione: string        // Required
  descrizione?: string
  codice_ditta?: string
  ragione_sociale?: string
  stato_amministrativo?: string
  tipo_procedura?: string
  forma?: string
  codice_atc?: string
  pa_associati?: string
  link?: string
  created_at: string
}
```

### User
```typescript
{
  id: string
  firebase_uid: string
  email: string
  name: string
  provider: "google" | "apple"
  status?: "active" | "paused"
  medicine_count: number
  paused_at?: string
  pause_reason?: string
  created_at: string
  updated_at: string
  medicines?: Medicine[]  // Only in GET /users/{id}
}
```

### Medicine
```typescript
{
  id: string
  user_id: string
  name: string
  description?: string
  category: string
  quantity: number
  expiry_date?: string
  aic_code?: string
  barcode?: string
  manufacturer?: string
  batch_number?: string
  serial_number?: string
  notes?: string
  user_email?: string  // Only in admin endpoints
  created_at: string
  updated_at: string
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "message": "Error description",
  "status": 400 | 401 | 404 | 500
}
```

### Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request (missing/invalid parameters)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `500` - Internal Server Error

---

## Notes

- All dates are in ISO 8601 format
- All IDs are MongoDB ObjectId strings (24 hex characters)
- Pagination uses `limit` and `skip` parameters
- Search parameters are case-insensitive regex matches
- API key must be changed in production: `backend/app/routes/admin.py` line 8

**API Version:** 1.0  
**Last Updated:** February 17, 2026

// Production API Configuration
const API_BASE = 'https://memofarmbackend.onrender.com/api/admin';
const ADMIN_API_KEY = 'a9Ue1UGEWuycSHdkeDTxzNrrdW2yBXE7eXQJ7AwWpPQ';


curl -H "X-Admin-Key: a9Ue1UGEWuycSHdkeDTxzNrrdW2yBXE7eXQJ7AwWpPQ" \
  https://memofarmbackend.onrender.com/api/admin/stats


  # Public endpoints
curl https://memofarmbackend.onrender.com/health
curl https://memofarmbackend.onrender.com/api/italian-medicines/stats

# Admin endpoints (with your key)
curl -H "X-Admin-Key: a9Ue1UGEWuycSHdkeDTxzNrrdW2yBXE7eXQJ7AwWpPQ" \
  https://memofarmbackend.onrender.com/api/admin/stats

curl -H "X-Admin-Key: a9Ue1UGEWuycSHdkeDTxzNrrdW2yBXE7eXQJ7AwWpPQ" \
  "https://memofarmbackend.onrender.com/api/admin/italian-medicines?limit=10"