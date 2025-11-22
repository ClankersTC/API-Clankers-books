from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Literal
from uuid import UUID, uuid4
import re


class UsuarioBase(BaseModel):
    """
    Campos base que todos los usuarios tienen.
    """
    username: str = Field(..., min_length=6, max_length=50)
    email: EmailStr

class UsuarioCreate(UsuarioBase):
    """
    Modelo para el endpoint de registro (/auth/register).
    Recibimos la contraseña en texto plano.
    """
    password: str = Field(..., min_length=12)

    @field_validator('password')
    def validar_complejidad_password(cls, v):
        # 1. Verificar mayúscula
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        
        # 2. Verificar minúscula
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        # 3. Verificar número
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Falta un caracter especial')
            
        return v

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

