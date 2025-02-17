from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import date

####################################################################################################
#Publicaciones

# Modelo para crear una nueva publicación
class PublicacionBase(BaseModel):
    id_usuario: int
    titulo: str
    contenido: str
    fecha_publicacion: Optional[date] = None
    portada: Optional[str] = None
    publicado: bool = False

class PublicacionCreate(PublicacionBase):
    etiquetas: List[str] = []  # Lista de etiquetas (nombres, no IDs)

class PublicacionUpdate(BaseModel):
    titulo: Optional[str] = None
    contenido: Optional[str] = None
    portada: Optional[str] = None
    publicado: Optional[bool] = None

class PublicacionResponse(PublicacionBase):
    id_post: int
    etiquetas: List[str] = []  # Lista de etiquetas asignadas a la publicación

    class Config:
        from_attributes = True

# Modelo para listar publicaciones con paginación
class PublicacionesResponse(BaseModel):
    total: int
    publicaciones: List[PublicacionResponse]

# Modelo para filtrado por etiqueta
class FiltrarPorEtiqueta(BaseModel):
    etiqueta: str

####################################################################################################
#Usuarios

# Modelo para registrar un usuario
class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    contrasenia: str

# Modelo para respuesta de usuario (sin contraseña)
class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre: str
    email: EmailStr


    class Config:
        from_attributes = True

# Modelo para inicio de sesión
class UsuarioLogin(BaseModel):
    email: EmailStr
    contrasenia: str

# Modelo para el token de acceso
class Token(BaseModel):
    access_token: str
    token_type: str

####################################################################################################
#Calificaciones

# Modelo para registrar una calificación
class CalificacionCreate(BaseModel):
    id_usuario: int
    id_publicacion: int
    calificacion: float = Field(ge=0, le=5)  # ✅ Calificación entre 0 y 5

# Modelo para devolver la calificación promedio de una publicación
class CalificacionResponse(BaseModel):
    id_publicacion: int
    promedio: float
    cantidad: int

####################################################################################################
# Etiqueta

# Modelo para crear una etiqueta
class EtiquetaCreate(BaseModel):
    tag: str  # Nombre único de la etiqueta

# Modelo para asociar etiquetas a publicaciones
class EtiquetasPublicacion(BaseModel):
    id_publicacion: int
    etiquetas: List[str]  # Lista de nombres de etiquetas

# Modelo para devolver una etiqueta
class EtiquetaResponse(BaseModel):
    id_tag: int
    tag: str
