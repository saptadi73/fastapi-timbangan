# FastAPI Timbangan dengan Konfigurasi .env

Aplikasi FastAPI yang dikonfigurasi melalui file `.env` untuk kemudahan pengaturan environment variables. Dilengkapi dengan koneksi ke timbangan SGW-3015P via Serial Port.

## Setup Awal

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Buat file `.env`
Copy dari `.env.example`:
```bash
copy .env.example .env
```

### 3. Edit file `.env`
Sesuaikan nilai-nilai di `.env` sesuai kebutuhan Anda:
```env
APP_NAME=FastAPI Timbangan
SERVER_PORT=8000
DATABASE_URL=sqlite:///./timbangan.db
SECRET_KEY=your-secret-key-here
DEBUG=False

# Konfigurasi Timbangan
SCALE_PORT=COM3
SCALE_BAUDRATE=2400
SCALE_AUTO_START=true
```

### 4. Jalankan Aplikasi
```bash
python main.py
```

Atau dengan uvicorn:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Setup Database PostgreSQL

### 1. Pastikan PostgreSQL Sudah Running

Pastikan PostgreSQL sudah berjalan di `localhost:5432` dengan credential:
- Username: `opnpg`
- Password: `openpgpwd`

Jika belum ada database, buat dengan:
```sql
CREATE DATABASE timbangan OWNER opnpg;
```

### 2. Jalankan Migrations

Aplikasi akan otomatis membuat tables saat startup. Tapi untuk kontrol penuh, gunakan:

```bash
# Jalankan semua pending migrations
python db_migrate.py upgrade

# Atau langsung dengan alembic
alembic upgrade head

# Lihat status migrations
python db_migrate.py current
python db_migrate.py history
```

Lihat [DATABASE.md](DATABASE.md) untuk panduan lengkap migrations.

## Struktur File

```
fastapi-timbangan/
├── main.py                  # Aplikasi FastAPI utama
├── config.py                # Konfigurasi (load dari .env)
├── database.py              # Database configuration & session
├── models.py                # SQLAlchemy models
├── schemas.py               # Pydantic schemas untuk API
├── requirements.txt         # Dependencies Python
├── .env                     # File environment variables (JANGAN commit)
├── .env.example             # Template .env (untuk dokumentasi)
├── .gitignore              # Git ignore rules
├── README.md               # File ini
├── DATABASE.md             # Database setup & migration guide
├── db_migrate.py           # Migration helper script
├── services/
│   ├── __init__.py
│   └── connect.py          # Service untuk koneksi timbangan
├── routes/
│   ├── __init__.py
│   └── scale.py            # Routes/API endpoints timbangan
└── alembic/                # Database migrations (Alembic)
    ├── env.py              # Alembic environment config
    ├── script.py.mako      # Migration template
    └── versions/
        ├── __init__.py
        └── 001_initial.py  # Initial migration (create table)
```

## Konfigurasi Environment Variables

### API & Server
- **APP_NAME** - Nama aplikasi
- **APP_VERSION** - Versi aplikasi  
- **DEBUG** - Mode debug (True/False)
- **SERVER_HOST** - Host server (default: 0.0.0.0)
- **SERVER_PORT** - Port server (default: 8000)

### Database
- **DATABASE_URL** - Connection string database

### Security
- **SECRET_KEY** - Secret key untuk security
- **ALGORITHM** - Algoritma enkripsi (default: HS256)
- **ACCESS_TOKEN_EXPIRE_MINUTES** - Durasi token (default: 30)

### Scale/Timbangan SGW-3015P
- **SCALE_PORT** - Serial port timbangan (default: COM3)
- **SCALE_BAUDRATE** - Kecepatan baud (default: 2400)
- **SCALE_BYTESIZE** - Ukuran byte (default: 8)
- **SCALE_STOPBITS** - Stop bits (default: 1)
- **SCALE_PARITY** - Parity (N/E/O, default: N)
- **SCALE_RECONNECT_MS** - Delay reconnect (default: 3000ms)
- **SCALE_POLL_MS** - Interval polling (default: 1000ms)
- **SCALE_ENABLE_POLL** - Enable polling (default: true)
- **SCALE_AUTO_START** - Auto-start koneksi saat app mulai (default: true)

### Logging
- **LOG_LEVEL** - Level logging (INFO, DEBUG, ERROR, etc)

## API Endpoints

### Default Endpoints
- **GET /** - Welcome message & info aplikasi
- **GET /health** - Health check aplikasi dan timbangan
- **GET /config** - Lihat konfigurasi (hanya saat DEBUG=True)
- **GET /docs** - Swagger UI
- **GET /redoc** - ReDoc UI

### Scale/Timbangan API Endpoints

#### Status & Health
- **GET /api/scale/status** - Status koneksi timbangan
- **GET /api/scale/health** - Health check timbangan
- **GET /api/scale/ports** - Daftar serial port yang tersedia

#### Pembacaan
- **GET /api/scale/reading** - Pembacaan timbangan terbaru
- **GET /api/scale/readings/stream** - Info streaming readings (future feature)

#### Kontrol Koneksi
- **POST /api/scale/start** - Mulai koneksi timbangan
- **POST /api/scale/stop** - Hentikan koneksi timbangan

### Timbangan Data API (Coming Soon)

Endpoints untuk management data pembacaan timbangan:
- **GET /api/timbangan** - Daftar semua pembacaan
- **GET /api/timbangan/{uuid}** - Detail pembacaan
- **POST /api/timbangan** - Tambah pembacaan baru
- **PUT /api/timbangan/{uuid}** - Update pembacaan
- **DELETE /api/timbangan/{uuid}** - Hapus pembacaan
- **GET /api/timbangan/summary** - Statistik pembacaan

## Contoh Penggunaan API

### Cek Status Timbangan
```bash
curl http://localhost:8000/api/scale/status
```

Response:
```json
{
  "connected": true,
  "port": "COM3",
  "baudrate": 2400,
  "active_config": {
    "port": "COM3",
    "baudrate": 2400,
    "bytesize": 8,
    "stopbits": 1,
    "parity": "N"
  },
  "packet_count": 45,
  "last_reading": {
    "ts": "2026-02-25T10:30:45.123456",
    "type": "weight",
    "packet": 45,
    "stability": "ST",
    "mode": "NT",
    "stable": true,
    "weight": 2.45,
    "unit": "kg",
    "raw": "ST,NT,2.45kg"
  }
}
```

### Dapatkan Pembacaan Terbaru
```bash
curl http://localhost:8000/api/scale/reading
```

### Lihat Serial Port Tersedia
```bash
curl http://localhost:8000/api/scale/ports
```

### Mulai Koneksi
```bash
curl -X POST http://localhost:8000/api/scale/start
```

### Hentikan Koneksi
```bash
curl -X POST http://localhost:8000/api/scale/stop
```

## Tips Keamanan

⚠️ **PENTING:**
- Jangan pernah commit file `.env` ke repository
- Gunakan `.env.example` untuk dokumentasi variabel yang diperlukan
- Ubah `SECRET_KEY` di production dengan nilai yang aman
- Set `DEBUG=False` di production
- Gunakan database yang aman di production (jangan SQLite)
- Protect `/config` endpoint di production (sudah dilindungi secara default)

## Development vs Production

**Development (.env):**
```env
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///./timbangan.db
SCALE_AUTO_START=true
```

**Production (.env):**
```env
DEBUG=False
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:password@prod-server/db
SECRET_KEY=<generate-secret-key>
SCALE_AUTO_START=true
```

## Menambah Variabel Baru

### 1. Update config.py
Tambahkan di class `Settings`:
```python
my_setting: str = "default_value"
```

### 2. Update .env dan .env.example
```env
MY_SETTING=actual_value
```

### 3. Gunakan di kode
```python
from config import settings
print(settings.my_setting)
```

## Troubleshooting

### Timbangan tidak terkoneksi
1. Cek serial port di Device Manager (Windows)
2. Sesuaikan `SCALE_PORT` di .env
3. Cek kabel USB/RS-232
4. Lihat log dengan `LOG_LEVEL=DEBUG`

### Pembacaan timbangan unstable
1. Pastikan timbangan sudah warm-up (dibiarkan on beberapa saat)
2. Letakkan timbangan di permukaan datar
3. Periksa setting baudrate di timbangan

### Port tidak ditemukan
Gunakan endpoint `/api/scale/ports` untuk melihat port yang tersedia:
```bash
curl http://localhost:8000/api/scale/ports
```

## Testing dengan Swagger UI

Buka browser ke:
```
http://localhost:8000/docs
```

Dari sana Anda bisa:
- Lihat semua API endpoints
- Test endpoints langsung dari browser
- Lihat contoh request dan response
- Download OpenAPI spec

## Referensi Timbangan SGW-3015P

- Format pembacaan: `ST,NT,1234.56kg`
  - ST/US = Stability (Stabil/Unstabil)
  - NT/GS = Mode (Normal/Gross)
  - 1234.56 = Nilai berat
  - kg = Satuan (kg, g, lb)

## Kontribusi

Untuk menambah fitur atau melaporkan bug, silakan buat issue atau pull request.

## License

MIT

#   f a s t a p i - t i m b a n g a n  
 