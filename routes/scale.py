"""
Routes untuk koneksi dan pembacaan timbangan SGW-3015P via Serial Port
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from services.connect import get_scale_connection

# Inisialisasi router
router = APIRouter(prefix="/api/scale", tags=["Scale/Timbangan"])


# =========================
# Pydantic Models
# =========================

class ScaleReadingResponse(BaseModel):
    """Model response untuk pembacaan timbangan"""
    ts: str
    type: str
    packet: int
    stability: Optional[str] = None
    mode: Optional[str] = None
    stable: bool
    weight: float
    unit: str
    raw: str


class ConnectionStatusResponse(BaseModel):
    """Model response untuk status koneksi"""
    connected: bool
    port: str
    baudrate: int
    active_config: Optional[Dict[str, Any]] = None
    packet_count: int
    last_reading: Optional[ScaleReadingResponse] = None


class AvailablePortResponse(BaseModel):
    """Model untuk port yang tersedia"""
    port: str
    description: str
    hwid: str


# =========================
# Endpoints
# =========================

@router.get("/status", response_model=ConnectionStatusResponse)
async def get_status():
    """
    Dapatkan status koneksi timbangan
    
    Returns:
        - connected: Status koneksi (True/False)
        - port: Serial port yang digunakan
        - baudrate: Kecepatan baud
        - active_config: Konfigurasi yang sedang aktif
        - packet_count: Jumlah paket yang diterima
        - last_reading: Pembacaan terakhir
    """
    scale = get_scale_connection()
    status = scale.get_status()
    
    return ConnectionStatusResponse(**status)


@router.get("/reading", response_model=Optional[ScaleReadingResponse])
async def get_reading():
    """
    Dapatkan pembacaan timbangan terbaru
    
    Returns:
        - weight: Nilai berat
        - unit: Satuan (kg, g, lb)
        - stable: Apakah pembacaan stabil
        - ts: Timestamp pembacaan
    """
    scale = get_scale_connection()
    reading = scale.get_last_reading()
    
    if reading is None:
        raise HTTPException(
            status_code=404,
            detail="Belum ada pembacaan. Pastikan timbangan terhubung."
        )
    
    return ScaleReadingResponse(**reading)


@router.post("/start")
async def start_connection():
    """
    Mulai koneksi ke timbangan
    
    Returns:
        - message: Pesan status
        - status: Status koneksi
    """
    scale = get_scale_connection()
    scale.start()
    
    return {
        "message": "Koneksi timbangan dimulai",
        "status": scale.get_status()
    }


@router.post("/stop")
async def stop_connection():
    """
    Hentikan koneksi ke timbangan
    
    Returns:
        - message: Pesan status
    """
    scale = get_scale_connection()
    scale.stop()
    
    return {
        "message": "Koneksi timbangan dihentikan"
    }


@router.get("/ports", response_model=List[AvailablePortResponse])
async def get_available_ports():
    """
    Dapatkan daftar serial port yang tersedia di sistem
    
    Returns:
        List serial port yang tersedia beserta deskripsi dan hardware ID
    """
    scale = get_scale_connection()
    ports = scale.get_available_ports()
    
    if not ports:
        raise HTTPException(
            status_code=404,
            detail="Tidak ada serial port yang ditemukan"
        )
    
    return [AvailablePortResponse(**port) for port in ports]


@router.get("/health")
async def scale_health():
    """
    Health check untuk timbangan
    
    Returns status koneksi dan informasi dasar
    """
    scale = get_scale_connection()
    status = scale.get_status()
    
    return {
        "healthy": status["connected"],
        "connected": status["connected"],
        "port": status["port"],
        "packet_count": status["packet_count"],
        "last_reading_available": status["last_reading"] is not None
    }


# =========================
# WebSocket untuk streaming readings (optional)
# =========================

@router.get("/readings/stream")
async def stream_readings():
    """
    Endpoint untuk informasi tentang streaming readings
    
    Note: Untuk implementasi WebSocket, lihat implementasi terpisah
    """
    return {
        "message": "Endpoint ini dapat dikembangkan untuk WebSocket streaming",
        "alternative": "Gunakan polling dengan /api/scale/reading"
    }
