from fastapi import FastAPI, HTTPException, Query, Depends, Security
from models import CalificacionCreate, CalificacionResponse, EtiquetaCreate, EtiquetaResponse, EtiquetasPublicacion, PublicacionCreate, PublicacionUpdate, UsuarioCreate, UsuarioLogin, UsuarioResponse, Token
from crud import assign_tags_to_post, create_calificacion, create_post, create_tag, get_calificacion_promedio, get_post, list_posts, list_tags, update_post, delete_post, create_user, login_user
from database import connect_to_db, close_db_connection
from security import get_current_user
from contextlib import asynccontextmanager
from typing import List

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await connect_to_db()
    yield
    await close_db_connection(app.state.pool)

app = FastAPI(title="API de Blogs", lifespan=lifespan)

####################################################################################################
#Publicaciones

# Crear una publicación
@app.post("/publicaciones/")
async def crear_publicacion(publicacion: PublicacionCreate, user: str = Depends(get_current_user)):
    try:
        post_id = await create_post(app.state.pool, publicacion)
        return {"id_post": post_id, "mensaje": "Publicación creada con éxito"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Obtener una publicación por ID
@app.get("/publicaciones/{id_post}")
async def obtener_publicacion(id_post: int):
    post = await get_post(app.state.pool, id_post)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return post

# Listar publicaciones con paginación
@app.get("/publicaciones/")
async def listar_publicaciones(skip: int = Query(0, alias="pagina"), limit: int = Query(10, alias="limite")):
    return await list_posts(app.state.pool, skip, limit)

# Actualizar una publicación
@app.put("/publicaciones/{id_post}")
async def actualizar_publicacion(id_post: int, post_update: PublicacionUpdate, user: str = Depends(get_current_user)):
    post = await update_post(app.state.pool, id_post, post_update)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return post

# Eliminar una publicación
@app.delete("/publicaciones/{id_post}")
async def eliminar_publicacion(id_post: int, user: str = Depends(get_current_user)):
    if not await delete_post(app.state.pool, id_post):
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return {"mensaje": "Publicación eliminada exitosamente"}

####################################################################################################
#Usuarios

# Endpoint para registrar un usuario
@app.post("/usuarios/", response_model=UsuarioResponse)
async def registrar_usuario(usuario: UsuarioCreate):
    try:
        user = await create_user(app.state.pool, usuario)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Endpoint para iniciar sesión y obtener token
@app.post("/usuarios/login/", response_model=Token)
async def login(usuario: UsuarioLogin):
    token = await login_user(app.state.pool, usuario)
    if not token:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"access_token": token, "token_type": "bearer"}

####################################################################################################
#Calificaciones

# Endpoint para calificar una publicación
@app.post("/calificaciones/")
async def calificar_publicacion(calificacion: CalificacionCreate, user: str = Depends(get_current_user)):
    try:
        return await create_calificacion(app.state.pool, calificacion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Endpoint para obtener la calificación promedio de una publicación
@app.get("/calificaciones/{id_publicacion}", response_model=CalificacionResponse)
async def obtener_calificacion_promedio(id_publicacion: int):
    calificacion = await get_calificacion_promedio(app.state.pool, id_publicacion)
    if not calificacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return calificacion

####################################################################################################
#Etiquta

# Endpoint para crear una nueva etiqueta
@app.post("/etiquetas/", response_model=EtiquetaResponse)
async def crear_etiqueta(etiqueta: EtiquetaCreate, user: str = Depends(get_current_user)):
    tag = await create_tag(app.state.pool, etiqueta)
    if not tag:
        raise HTTPException(status_code=400, detail="La etiqueta ya existe")
    return tag

# Endpoint para asignar etiquetas a una publicación
@app.post("/publicaciones/{id_post}/etiquetas/")
async def asignar_etiquetas(id_post: int, etiquetas: List[str], user: str = Depends(get_current_user)):
    try:
        etiquetas_publicacion = EtiquetasPublicacion(id_publicacion=id_post, etiquetas=etiquetas)
        return await assign_tags_to_post(app.state.pool, etiquetas_publicacion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Endpoint para listar todas las etiquetas
@app.get("/etiquetas/", response_model=List[EtiquetaResponse])
async def listar_etiquetas():
    return await list_tags(app.state.pool)
