from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Literal
from uuid import UUID, uuid4


class UsuarioBase(BaseModel):
    """
    Campos base que todos los usuarios tienen.
    """
    nombreUsuario: str = Field(..., min_length=3, max_length=50)
    correoElectronico: EmailStr 

class UsuarioCreate(UsuarioBase):
    """
    Modelo para el endpoint de registro (/auth/register).
    Recibimos la contraseña en texto plano.
    """
    password: str = Field(..., min_length=8)

class UsuarioPublic(UsuarioBase):
    """
    Modelo SEGURO para devolver al cliente.
    """
    id: str = Field(..., description="Firebase Auth User ID (UID)") 
    fotoPerfilURL: Optional[str] = None
    rol: Literal["lector", "admin"] = "lector"
    
    # Campos específicos de Lector
    preferencias: List[str] = []

    # Campos específicos de Admin
    nivelAcceso: Optional[int] = None
    necesita2FA: Optional[bool] = None

    class Config:
        from_attributes = True

