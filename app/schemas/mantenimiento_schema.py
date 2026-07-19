from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MantenimientoBase(BaseModel):
    tipo_mantenimiento: str
    fecha_ultimo: Optional[datetime] = None
    fecha_proximo: datetime
    estado: Optional[str] = "Activo"

class MantenimientoCreate(MantenimientoBase):
    pass

class MantenimientoResponse(MantenimientoBase):
    id: int
    id_vehiculo: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
