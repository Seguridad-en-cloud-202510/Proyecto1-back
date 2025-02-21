from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date

####################################################################################################
# Publicaciones

class PublicacionBase(BaseModel):
    id_usuario: int
    titulo: str
    contenido: str
    fecha_publicacion: Optional[date] = None
    portada: Optional[str] = None
    publicado: bool = False

class PublicacionCreate(PublicacionBase):
    etiquetas: List[str] = []

class PublicacionUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    portada: Optional[str] = None
    publicado: Optional[bool] = None

class PublicacionResponse(PublicacionBase):
    id_post: int
    etiquetas: List[str] = []

    class Config:
        from_attributes = True

class PublicacionesResponse(BaseModel):
    total: int
    publicaciones: List[PublicacionResponse]

class FiltrarPorEtiqueta(BaseModel):
    etiqueta: str

####################################################################################################
# Usuarios

class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    contrasenia: str

class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr

    class Config:
        from_attributes = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    contrasenia: str

class Token(BaseModel):
    access_token: str
    token_type: str

####################################################################################################
# Calificaciones

class CalificacionCreate(BaseModel):
    id_usuario: int
    id_publicacion: int
    calificacion: float = Field(ge=0, le=5)

class CalificacionResponse(BaseModel):
    id_publicacion: int
    promedio: float
    cantidad: int

####################################################################################################
# Etiqueta

class EtiquetaCreate(BaseModel):
    tag: str

class EtiquetasPublicacion(BaseModel):
    id_publicacion: int
    etiquetas: List[str]

class EtiquetaResponse(BaseModel):
    id_tag: int
    tag: str
