from sqlalchemy import Column, Integer, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base


class TallerFavorito(Base):
    __tablename__ = "taller_favorito"
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_taller", name="uq_usuario_taller_favorito"),
    )

    id_favorito = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuario.id_usuario"), nullable=False, index=True)
    id_taller = Column(Integer, ForeignKey("taller.id_taller"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    usuario = relationship("Usuario")
    taller = relationship("Taller")
