from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
from uuid import UUID, uuid4

# Importamos el helper
from .helpers_model import LectorEmbedded

class ResenaBase(BaseModel):
    """
    Lo mínimo que envía un usuario para crear una reseña.
    """
    comentario: str = Field(..., min_length=5, max_length=5000)
    # ge = 'greater or equal', le = 'less or equal'
    calificacion: int = Field(..., ge=1, le=5) 


class ResenaCreate(ResenaBase):
    """
    Modelo para el endpoint POST /libros/{libroId}/resenas
    """
    pass


class ResenaUpdate(BaseModel):
    """
    Modelo para PATCH /.../resenas/{id}
    (Ej. un admin moderando o un usuario editando)
    """
    comentario: Optional[str] = None
    calificacion: Optional[int] = None
    estado: Optional[Literal["pendiente", "aprobado", "rechazado"]] = None


class ResenaInDB(ResenaBase):
    """
    El documento completo de la reseña como vive en Firestore.
    """
    id: str = Field(..., description="ID del documento de la reseña")
    fecha: datetime = Field(default_factory=datetime.now)
    estado: Literal["pendiente", "aprobado", "rechazado"] = "pendiente"

    lectorInfo: LectorEmbedded
    
    libroId: str 

    class Config:
        from_attributes = True