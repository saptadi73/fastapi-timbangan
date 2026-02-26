# Database Setup & Migrations Guide

## Konfigurasi Database PostgreSQL

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Dependencies yang diinstall:
- `sqlalchemy==2.0.23` - ORM
- `psycopg2-binary==2.9.9` - PostgreSQL adapter
- `alembic==1.12.1` - Database migrations

### 2. Konfigurasi PostgreSQL

Edit file `.env` dengan credential PostgreSQL Anda:

```env
DATABASE_URL=postgresql://opnpg:openpgpwd@localhost:5432/timbangan
SQLALCHEMY_ECHO=False
```

Pastikan:
- PostgreSQL sudah running
- Database `timbangan` sudah dibuat atau akan dibuat otomatis
- User `opnpg` memiliki akses ke database

**Membuat database jika belum ada:**
```sql
CREATE DATABASE timbangan OWNER opnpg;
```

### 3. Menjalankan Migrations

#### Pertama kali (Setup awal)

```bash
# Jalankan semua pending migrations
alembic upgrade head
```

#### Lihat status migrations

```bash
# Lihat revision history dan status
alembic current
alembic history

# Lihat detail migration tertentu
alembic show 001_initial
```

#### Buat migration baru (setelah ubah models)

```bash
# Generate migration otomatis berdasarkan perubahan models
alembic revision --autogenerate -m "Deskripsi perubahan"

# Atau buat migration manual
alembic revision -m "Deskripsi perubahan"
```

#### Upgrade/Downgrade

```bash
# Upgrade ke revision tertentu
alembic upgrade 001_initial

# Downgrade ke revision sebelumnya
alembic downgrade -1

# Downgrade ke revision tertentu
alembic downgrade 001_initial
```

## Struktur Database

### Table: timbangan

Menyimpan data pembacaan timbangan SGW-3015P

| Field | Type | Constraint | Deskripsi |
|-------|------|-----------|-----------|
| uuid | UUID | PRIMARY KEY | Unique identifier |
| no_urut | INTEGER | AUTO INCREMENT, UNIQUE | Nomor urut pembacaan |
| nopol | VARCHAR(20) | NOT NULL | Nomor plat nomor kendaraan |
| sopir | VARCHAR(100) | NOT NULL | Nama sopir/pengemudi |
| gross | NUMERIC(10,2) | NOT NULL | Berat kotor (kg) |
| rate | NUMERIC(10,2) | NULLABLE | Tarif per unit |
| nett | NUMERIC(10,2) | NOT NULL | Berat bersih (kg) |
| tanggalwaktu | TIMESTAMP | NOT NULL | Waktu pencatatan |
| petugas | VARCHAR(100) | NOT NULL | Nama petugas |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Waktu dibuat di DB |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Waktu terakhir update |
| catatan | TEXT | NULLABLE | Catatan tambahan |

### Indexes

- `ix_timbangan_no_urut` - Untuk no_urut (unique)
- `ix_timbangan_nopol` - Untuk fast query berdasarkan nopol
- `ix_timbangan_tanggalwaktu` - Untuk time range queries
- `ix_timbangan_created_at` - Untuk audit trail

## Menggunakan di Aplikasi

### 1. Dependency Injection

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Timbangan

@app.get("/api/timbangan/")
def get_timbangan(db: Session = Depends(get_db)):
    records = db.query(Timbangan).all()
    return records
```

### 2. Membuat Record

```python
from models import Timbangan
from datetime import datetime

new_record = Timbangan(
    nopol="B 1234 CD",
    sopir="Budi",
    gross=5000.00,
    nett=3000.00,
    petugas="Admin",
    tanggalwaktu=datetime.utcnow(),
    rate=500.00
)
db.add(new_record)
db.commit()
db.refresh(new_record)
```

### 3. Query Data

```python
# Get all
all_records = db.query(Timbangan).all()

# Get by UUID
record = db.query(Timbangan).filter(Timbangan.uuid == uuid_value).first()

# Get by nopol
records = db.query(Timbangan).filter(Timbangan.nopol == "B 1234 CD").all()

# Filter by date range
from datetime import datetime, timedelta

start_date = datetime(2026, 2, 25)
end_date = datetime(2026, 2, 26)
records = db.query(Timbangan).filter(
    Timbangan.tanggalwaktu.between(start_date, end_date)
).all()
```

### 4. Update Record

```python
record = db.query(Timbangan).filter(Timbangan.uuid == uuid_value).first()
if record:
    record.nett = 3500.00
    db.commit()
    db.refresh(record)
```

### 5. Delete Record

```python
record = db.query(Timbangan).filter(Timbangan.uuid == uuid_value).first()
if record:
    db.delete(record)
    db.commit()
```

## Troubleshooting

### Error: "psycopg2: could not translate host name"

**Solusi:** Pastikan PostgreSQL berjalan dan settings DATABASE_URL benar

```bash
# Test koneksi
psql -h localhost -U opnpg -d timbangan
```

### Error: "relation 'timbangan' does not exist"

**Solusi:** Jalankan migrations

```bash
alembic upgrade head
```

### Error saat auto-generate migration

Pastikan models.py di-import dengan benar di alembic/env.py. Edit `alembic/env.py`:

```python
from database import Base
from models import Timbangan  # Explicit import

target_metadata = Base.metadata
```

## Best Practices

1. **Selalu gunakan Alembic untuk schema changes** - Jangan modify schema langsung di database
2. **Write descriptive migration messages** - Jelaskan apa yang diubah
3. **Test migrations di dev dulu** - Sebelum apply ke production
4. **Keep migrations small** - Satu logical change per migration
5. **Use proper field types** - Gunakan Numeric untuk money/weight, DateTime untuk timestamps
6. **Add indexes** - Untuk kolom yang sering di-query (nopol, tanggalwaktu)

## Refs

- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [PostgreSQL UUID Type](https://www.postgresql.org/docs/current/uuid-ossp.html)
