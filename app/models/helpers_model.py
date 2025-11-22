from pydantic import BaseModel, Field

class AuthorEmbedded(BaseModel):
    idAuthor: str = Field(..., description="ID del documento del autor")
    nombreCompleto: str

class LectorEmbedded(BaseModel):
    idUsuario: str = Field(..., description="ID del usuario lector")
    nombreUsuario: str = Field(..., description="Nombre del usuario a mostrar")