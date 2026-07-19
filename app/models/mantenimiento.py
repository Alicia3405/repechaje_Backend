from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class Mantenimiento(Base):
    __tablename__ = "mantenimiento"

    id = Column(Integer, primary_key=True, index=True)
    id_vehiculo = Column(Integer, ForeignKey("vehiculo.id_vehiculo"), nullable=False, index=True)
    tipo_mantenimiento = Column(String(100), nullable=False)
    fecha_ultimo = Column(DateTime(timezone=True), nullable=True)
    fecha_proximo = Column(DateTime(timezone=True), nullable=False)
    estado = Column(String(50), nullable=False, default="Activo")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    vehiculo = relationship("Vehiculo", back_populates="mantenimientos")
