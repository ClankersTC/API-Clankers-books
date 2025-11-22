from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID, uuid4

# Importamos el helper que creamos
from .helpers_model import AutorEmbedded

class LibroBase(BaseModel):
    """
    Campos base para crear o actualizar un libro.
    """
    titulo: str = Field(..., min_length=1)
    sinopsis: str = Field(..., min_length=10)
    fechaPublicacion: date
    autor: AutorEmbedded
    generos: List[str] = []


class LibroCreate(LibroBase):
    """
    Modelo para el endpoint POST /libros
    """
    # Opcional: Si el ID lo generas tú y no la DB
    id: UUID = Field(default_factory=uuid4)
    urlPortada: Optional[str] = None


class LibroUpdate(BaseModel):
    """
    Modelo para el endpoint PATCH /libros/{id}
    Todos los campos son opcionales.
    """
    titulo: Optional[str] = None
    sinopsis: Optional[str] = None
    fechaPublicacion: Optional[date] = None
    autor: Optional[AutorEmbedded] = None
    generos: Optional[List[str]] = None
    urlPortada: Optional[str] = None


class LibroInDB(LibroBase):
    """
    El modelo completo del libro como se devuelve desde la API.
    """
    id: str = Field(..., description="ID del documento del libro")
    calificacionPromedio: float = 0.0 
    urlPortada: Optional[str] = None

    class Config:
        from_attributes = True