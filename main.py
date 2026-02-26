from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging
from contextlib import asynccontextmanager
from config import settings
from routes import scale
from services.connect import get_scale_connection
from database import engine, init_db, close_db
from models import Base

# Setup logging
logging.basicConfig(
    level=settings.log_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =========================
# Lifecycle Events
# =========================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager untuk startup dan shutdown
    """
    # Startup event
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} berjalan di {settings.server_host}:{settings.server_port}")
    logger.info(f"📦 Database: {settings.database_url}")
    logger.info(f"🔐 Debug Mode: {settings.debug}")
    
    # Inisialisasi database tables (jika belum ada)
    logger.info("📊 Inisialisasi database...")
    try:
        init_db()
        logger.info("✓ Database tables initialized")
    except Exception as e:
        logger.error(f"✗ Database initialization error: {e}")
    
    # Inisialisasi dan mulai koneksi timbangan jika auto_start enabled
    if settings.scale_auto_start:
        logger.info(f"⚖️  Menemukan timbangan di port {settings.scale_port}...")
        scale_connection = get_scale_connection()
        scale_connection.start()
        logger.info("✓ Koneksi timbangan dimulai")
    
    yield
    
    # Shutdown event
    logger.info("🛑 Menghentikan aplikasi...")
    scale_connection = get_scale_connection()
    scale_connection.stop()
    close_db()
    logger.info("✓ Aplikasi dihentikan")


# Inisialisasi FastAPI app dengan konfigurasi dari .env dan lifespan management
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    description="API untuk mengelola koneksi Timbangan SGW-3015P via Serial Port dan Database"
)


# =========================
# Include Routes
# =========================

app.include_router(scale.router)


# =========================
# Default Routes
# =========================

@app.get("/")
async def read_root():
    """Root endpoint - informasi aplikasi"""
    return {
        "message": f"Selamat datang di {settings.app_name}",
        "version": settings.app_version,
        "endpoints": {
            "api_docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "scale_api": "/api/scale"
        },
        "scale": {
            "model": "SGW-3015P",
            "connection": f"Serial Port {settings.scale_port}"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint - status aplikasi dan timbangan"""
    scale_connection = get_scale_connection()
    scale_status = scale_connection.get_status()
    
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "debug": settings.debug,
        "scale": {
            "connected": scale_status["connected"],
            "port": scale_status["port"],
            "packet_count": scale_status["packet_count"]
        }
    }


@app.get("/config")
async def get_config():
    """
    Endpoint untuk melihat konfigurasi (hanya untuk debug)
    
    ⚠️ Caution: Endpoint ini hanya tersedia di debug mode
    """
    if not settings.debug:
        return JSONResponse(
            status_code=403,
            content={"detail": "Endpoint ini hanya tersedia di debug mode"}
        )
    
    return {
        "app": {
            "name": settings.app_name,
            "version": settings.app_version,
            "debug": settings.debug,
        },
        "server": {
            "host": settings.server_host,
            "port": settings.server_port,
        },
        "database": {
            "url": settings.database_url,
        },
        "scale": {
            "port": settings.scale_port,
            "baudrate": settings.scale_baudrate,
            "bytesize": settings.scale_bytesize,
            "stopbits": settings.scale_stopbits,
            "parity": settings.scale_parity,
            "reconnect_ms": settings.scale_reconnect_ms,
            "poll_ms": settings.scale_poll_ms,
            "enable_poll": settings.scale_enable_poll,
            "auto_start": settings.scale_auto_start,
        },
        "logging": {
            "level": settings.log_level,
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
