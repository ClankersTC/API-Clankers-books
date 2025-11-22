from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional, List, Literal
from uuid import UUID, uuid4
from datetime import datetime
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
        if not re.search(r'[A-Z]', v): raise ValueError('La contraseña debe contener al menos una letra mayúscula')
    
        # 2. Verificar minúscula
        if not re.search(r'[a-z]', v): raise ValueError('La contraseña debe contener al menos una letra minúscula')
        
        # 3. Verificar número
        if not re.search(r'[0-9]', v): raise ValueError('La contraseña debe contener al menos un número')
            
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v): raise ValueError('Falta un caracter especial')
            
        return v

class UsuarioPublic(UsuarioBase):
    """
    Modelo SEGURO para devolver al cliente.
    """
    id: str = Field(..., description="Firebase Auth User ID (UID)") 
    profileImgURL: Optional[str] = None
    role: Literal["lector", "admin"] = "lector"
    preferences: List[str] = []

    lastConection: Optional[datetime] = None
    dateRegister: Optional[datetime] = None  

    class Config:
        from_attributes = True


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    idToken: str
    refreshToken: str
    expiresIn: str
    localId: str 
    userData: Optional[UsuarioPublic] = None

class UsuarioUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=6, max_length=50)
    profileImgURL: Optional[str] = None
    preferences: Optional[List[str]] = None

class PasswordChange(BaseModel):
    password: str = Field(..., min_length=12)

    @field_validator('password')
    def validar_complejidad_password(cls, v):
        # 1. Verificar mayúscula
        if not re.search(r'[A-Z]', v): raise ValueError('La contraseña debe contener al menos una letra mayúscula')
        # 2. Verificar minúscula
        if not re.search(r'[a-z]', v): raise ValueError('La contraseña debe contener al menos una letra minúscula')
        # 3. Verificar número
        if not re.search(r'[0-9]', v): raise ValueError('La contraseña debe contener al menos un número')    
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v): raise ValueError('Falta un caracter especial')
            
        return v