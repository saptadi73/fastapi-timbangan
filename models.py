"""
Database models untuk aplikasi timbangan
"""

from decimal import Decimal
from typing import Optional
from sqlalchemy import String, Integer, DateTime, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
from database import Base


class Timbangan(Base):
    """
    Model untuk tabel pembacaan timbangan
    
    Menyimpan data pengukuran berat dari timbangan SGW-3015P
    """
    __tablename__ = "timbangan"
    
    # Primary Key
    uuid: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        doc="Unique identifier"
    )
    
    # Sequence
    no_urut: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        autoincrement=True,
        doc="Nomor urut pembacaan (auto increment)"
    )
    
    # Vehicle info
    nopol: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        doc="Nomer plat nomor kendaraan"
    )
    
    # Driver info
    sopir: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Nama sopir/pengemudi"
    )
    
    # Weight measurements
    gross: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
        doc="Berat kotor (gross) dalam kg"
    )
    
    rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=True,
        doc="Tarif/harga per unit peso"
    )
    
    nett: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2),
        nullable=False,
        doc="Berat bersih (nett) dalam kg"
    )
    
    # Timestamp
    tanggalwaktu: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Waktu pencatatan pembacaan"
    )
    
    # Officer
    petugas: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Nama petugas yang mencatat"
    )
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        doc="Waktu record dibuat di database"
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
        doc="Waktu record terakhir diupdate"
    )
    
    catatan: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        doc="Catatan tambahan"
    )
    
    def __repr__(self):
        return f"<Timbangan(no_urut={self.no_urut}, nopol={self.nopol}, gross={self.gross}kg, nett={self.nett}kg)>"
    
    def to_dict(self):
        """Convert model ke dictionary"""
        return {
            "uuid": str(self.uuid),
            "no_urut": self.no_urut,
            "nopol": self.nopol,
            "sopir": self.sopir,
            "gross": float(self.gross) if self.gross else None,
            "rate": float(self.rate) if self.rate else None,
            "nett": float(self.nett) if self.nett else None,
            "tanggalwaktu": self.tanggalwaktu.isoformat() if self.tanggalwaktu else None,
            "petugas": self.petugas,
            "catatan": self.catatan,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
