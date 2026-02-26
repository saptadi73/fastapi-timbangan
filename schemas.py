"""
Pydantic schemas untuk Timbangan API
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class TimbanganBase(BaseModel):
    """Base schema dengan semua field yang diperlukan"""
    nopol: str = Field(..., min_length=1, max_length=20, description="Nomor plat nomor kendaraan")
    sopir: str = Field(..., min_length=1, max_length=100, description="Nama sopir/pengemudi")
    gross: float = Field(..., gt=0, description="Berat kotor (gross) dalam kg")
    nett: float = Field(..., gt=0, description="Berat bersih (nett) dalam kg")
    petugas: str = Field(..., min_length=1, max_length=100, description="Nama petugas yang mencatat")
    rate: Optional[float] = Field(None, ge=0, description="Tarif/harga per unit peso")
    catatan: Optional[str] = Field(None, description="Catatan tambahan")


class TimbanganCreate(TimbanganBase):
    """Schema untuk create timbangan"""
    tanggalwaktu: Optional[datetime] = Field(None, description="Waktu pencatatan pembacaan (opsional, default sekarang)")


class TimbanganUpdate(BaseModel):
    """Schema untuk update timbangan"""
    nopol: Optional[str] = Field(None, max_length=20)
    sopir: Optional[str] = Field(None, max_length=100)
    gross: Optional[float] = Field(None, gt=0)
    nett: Optional[float] = Field(None, gt=0)
    rate: Optional[float] = Field(None, ge=0)
    petugas: Optional[str] = Field(None, max_length=100)
    catatan: Optional[str] = None


class TimbanganResponse(TimbanganBase):
    """Schema untuk response timbangan (dari database)"""
    uuid: UUID
    no_urut: int
    tanggalwaktu: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TimbanganListResponse(BaseModel):
    """Schema untuk list timbangan dengan pagination"""
    total: int = Field(..., description="Total records")
    page: int = Field(..., description="Halaman saat ini")
    page_size: int = Field(..., description="Jumlah records per halaman")
    total_pages: int = Field(..., description="Total halaman")
    data: list[TimbanganResponse]


class TimbanganSummary(BaseModel):
    """Schema untuk summary statistik timbangan"""
    total_records: int
    total_gross: float
    total_nett: float
    average_gross: float
    average_nett: float
    date_from: datetime
    date_to: datetime
