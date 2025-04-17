#!/usr/bin/env python3
"""
main.py
Archivo principal de la API usando FastAPI.
Se han modificado:
  • El endpoint de login para que, al autenticar, se envíe el token en una cookie.
  • La obtención del usuario autenticado, leyendo la cookie "access_token".
"""

from fastapi import FastAPI, HTTPException, Query, Depends, Security, Response, Request
from models import (CalificacionCreate, CalificacionResponse, EtiquetaCreate, EtiquetaResponse,
                    EtiquetasPublicacion, PublicacionCreate, PublicacionUpdate, UsuarioCreate, 
                    UsuarioLogin, UsuarioResponse, Token)
from crud import (assign_tags_to_post, create_calificacion, create_post, create_tag, 
                  get_calificacion_promedio, get_post, get_user_by_id, list_posts, list_tags, 
                  update_post, delete_post, create_user, login_user)
from database import connect_to_db, close_db_connection
from security import decode_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from contextlib import asynccontextmanager
from typing import List
from fastapi.middleware.cors import CORSMiddleware

# Configuración del ciclo de vida de la aplicación
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await connect_to_db()
    yield
    await close_db_connection(app.state.pool)

app = FastAPI(title="API de Blogs", lifespan=lifespan)

# Configuración del middleware CORS para que funcione con cookies
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Dominio del frontend (React)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Nueva dependencia para obtener el usuario desde la cookie "access_token"
async def get_current_user_from_cookie(request: Request) -> int:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Token no encontrado en la cookie")
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")
    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token corrupto")

# ────────────── Endpoints de Publicaciones ─────────────────────────────
@app.post("/publicaciones/")
async def crear_publicacion(publicacion: PublicacionCreate, user_id: int = Depends(get_current_user_from_cookie)):
    try:
        # Se fuerza que la publicación se cree con el id del usuario autenticado
        publicacion.id_usuario = user_id  
        post_id = await create_post(app.state.pool, publicacion)
        return {"id_post": post_id, "mensaje": "Publicación creada con éxito"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/publicaciones/{id_post}")
async def obtener_publicacion(id_post: int):
    post = await get_post(app.state.pool, id_post)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return post

@app.get("/publicaciones/")
async def listar_publicaciones(skip: int = Query(0, alias="pagina"), limit: int = Query(10, alias="limite")):
    return await list_posts(app.state.pool, skip, limit)

@app.put("/publicaciones/{id_post}")
async def actualizar_publicacion(id_post: int, post_update: PublicacionUpdate, user_id: int = Depends(get_current_user_from_cookie)):
    post = await update_post(app.state.pool, id_post, post_update)
    if not post:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return post

@app.delete("/publicaciones/{id_post}")
async def eliminar_publicacion(id_post: int, user_id: int = Depends(get_current_user_from_cookie)):
    if not await delete_post(app.state.pool, id_post):
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return {"mensaje": "Publicación eliminada exitosamente"}

# ────────────── Endpoints de Usuarios ─────────────────────────────
@app.post("/usuarios/", response_model=UsuarioResponse)
async def registrar_usuario(usuario: UsuarioCreate):
    try:
        user = await create_user(app.state.pool, usuario)
        return user
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

# Endpoint de login modificado para enviar el token en una cookie HTTP segura
@app.post("/usuarios/login/", response_model=Token)
async def login(usuario: UsuarioLogin, response: Response):
    token = await login_user(app.state.pool, usuario)
    if not token:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,          # No accesible via JavaScript
        secure=False,
        samesite="lax",         # Ajustar según necesidades (“lax” o “strict”)
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Tiempo de expiración en segundos
    )
    
    return {"access_token": token, "token_type": "bearer"}

@app.get("/usuarios/{id_usuario}", response_model=UsuarioResponse)
async def obtener_usuario(id_usuario: int):
    user = await get_user_by_id(app.state.pool, id_usuario)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# ────────────── Endpoints de Calificaciones ─────────────────────────────
@app.post("/calificaciones/")
async def calificar_publicacion(calificacion: CalificacionCreate, user_id: int = Depends(get_current_user_from_cookie)):
    try:
        # Se asigna el usuario autenticado a la calificación
        calificacion.id_usuario = user_id  
        return await create_calificacion(app.state.pool, calificacion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/calificaciones/{id_publicacion}", response_model=CalificacionResponse)
async def obtener_calificacion_promedio(id_publicacion: int):
    calificacion = await get_calificacion_promedio(app.state.pool, id_publicacion)
    if not calificacion:
        raise HTTPException(status_code=404, detail="Publicación no encontrada")
    return calificacion

# ────────────── Endpoints de Etiquetas ─────────────────────────────
@app.post("/etiquetas/", response_model=EtiquetaResponse)
async def crear_etiqueta(etiqueta: EtiquetaCreate, user_id: int = Depends(get_current_user_from_cookie)):
    tag = await create_tag(app.state.pool, etiqueta)
    if not tag:
        raise HTTPException(status_code=400, detail="La etiqueta ya existe")
    return tag

@app.post("/publicaciones/{id_post}/etiquetas/")
async def asignar_etiquetas(id_post: int, etiquetas: List[str], user_id: int = Depends(get_current_user_from_cookie)):
    try:
        etiquetas_publicacion = EtiquetasPublicacion(id_publicacion=id_post, etiquetas=etiquetas)
        return await assign_tags_to_post(app.state.pool, etiquetas_publicacion)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/etiquetas/", response_model=List[EtiquetaResponse])
async def listar_etiquetas():
    return await list_tags(app.state.pool)