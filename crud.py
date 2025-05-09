import asyncpg
from fastapi import HTTPException
from models import (CalificacionCreate, CalificacionResponse, EtiquetaCreate, EtiquetaResponse,
                    EtiquetasPublicacion, PublicacionCreate, PublicacionUpdate, PublicacionResponse,
                    UsuarioCreate, UsuarioLogin, UsuarioResponse)
from security import hash_password, verify_password, create_access_token
import json

####################################################################################################
# Usuarios

async def create_user(pool: asyncpg.Pool, usuario: UsuarioCreate):
    async with pool.acquire() as connection:
        query = """
        INSERT INTO Usuario (nombre, email, contrasenia)
        VALUES ($1, $2, $3)
        RETURNING id_usuario, nombre, email;
        """
        hashed_password = hash_password(usuario.contrasenia)
        row = await connection.fetchrow(query, usuario.nombre, usuario.email, hashed_password)
        return UsuarioResponse(id_usuario=row["id_usuario"], nombre=row["nombre"], email=row["email"])

async def get_user_by_email(pool: asyncpg.Pool, email: str):
    async with pool.acquire() as connection:
        query = "SELECT * FROM Usuario WHERE email = $1;"
        return await connection.fetchrow(query, email)

async def login_user(pool: asyncpg.Pool, usuario: UsuarioLogin):
    # Obtener el usuario por email
    user = await get_user_by_email(pool, usuario.email)
    if not user or not verify_password(usuario.contrasenia, user["contrasenia"]):
        return None
    # Se crea el token usando el id del usuario en lugar del email
    return create_access_token({"sub": str(user["id_usuario"])})

async def get_user_by_id(pool: asyncpg.Pool, id_usuario: int):
    async with pool.acquire() as connection:
        query = "SELECT id_usuario, nombre, email FROM Usuario WHERE id_usuario = $1;"
        row = await connection.fetchrow(query, id_usuario)
        if row:
            return UsuarioResponse(id_usuario=row["id_usuario"], nombre=row["nombre"], email=row["email"])
        return None

####################################################################################################
# Publicaciones

async def create_post(pool: asyncpg.Pool, publicacion: PublicacionCreate):
    async with pool.acquire() as connection:
        async with connection.transaction():
            query = """
            INSERT INTO Publicacion (id_usuario, titulo, contenido, fecha_publicacion, portada, publicado)
            VALUES ($1, $2, $3, COALESCE($4, CURRENT_DATE), $5, $6)
            RETURNING id_post;
            """
            post_id = await connection.fetchval(query, publicacion.id_usuario, publicacion.titulo,
                                                publicacion.contenido, publicacion.fecha_publicacion,
                                                publicacion.portada, publicacion.publicado)
            for tag in publicacion.etiquetas:
                tag_id = await connection.fetchval("""
                    INSERT INTO Etiquetas (tag) 
                    VALUES ($1) 
                    ON CONFLICT (tag) DO UPDATE SET tag = EXCLUDED.tag
                    RETURNING id_tag;
                """, tag)
                if tag_id:
                    await connection.execute("""
                        INSERT INTO Publicacion_Etiquetas (id_publicacion, id_tag) 
                        VALUES ($1, $2)
                        ON CONFLICT DO NOTHING;
                    """, post_id, tag_id)
            return post_id

async def get_post(pool: asyncpg.Pool, id_post: int):
    async with pool.acquire() as connection:
        query = """
        SELECT p.id_post, p.id_usuario, p.titulo, p.contenido, p.fecha_publicacion, 
               p.portada, p.publicado, 
               COALESCE(json_agg(e.tag) FILTER (WHERE e.tag IS NOT NULL), '[]'::json) AS etiquetas
        FROM Publicacion p
        LEFT JOIN Publicacion_Etiquetas pe ON p.id_post = pe.id_publicacion
        LEFT JOIN Etiquetas e ON pe.id_tag = e.id_tag
        WHERE p.id_post = $1
        GROUP BY p.id_post;
        """
        post = await connection.fetchrow(query, id_post)
        if not post:
            return None
        return PublicacionResponse(
            id_post=post["id_post"],
            id_usuario=post["id_usuario"],
            titulo=post["titulo"],
            contenido=post["contenido"],
            fecha_publicacion=post["fecha_publicacion"],
            portada=post["portada"],
            publicado=post["publicado"],
            etiquetas=json.loads(post["etiquetas"]) if post["etiquetas"] else []
        )

async def list_posts(pool: asyncpg.Pool, skip: int = 0, limit: int = 10):
    async with pool.acquire() as connection:
        total_query = "SELECT COUNT(*) FROM Publicacion;"
        total = await connection.fetchval(total_query)
        query = """
        SELECT p.id_post, p.id_usuario, p.titulo, p.contenido, p.fecha_publicacion, 
               p.portada, p.publicado, 
               COALESCE(json_agg(e.tag) FILTER (WHERE e.tag IS NOT NULL), '[]'::json) AS etiquetas
        FROM Publicacion p
        LEFT JOIN Publicacion_Etiquetas pe ON p.id_post = pe.id_publicacion
        LEFT JOIN Etiquetas e ON pe.id_tag = e.id_tag
        GROUP BY p.id_post
        ORDER BY p.fecha_publicacion DESC
        OFFSET $1 LIMIT $2;
        """
        rows = await connection.fetch(query, skip, limit)
        return {
            "total": total,
            "publicaciones": [
                PublicacionResponse(
                    id_post=row["id_post"],
                    id_usuario=row["id_usuario"],
                    titulo=row["titulo"],
                    contenido=row["contenido"],
                    fecha_publicacion=row["fecha_publicacion"],
                    portada=row["portada"],
                    publicado=row["publicado"],
                    etiquetas=json.loads(row["etiquetas"]) if row["etiquetas"] else []
                ) for row in rows
            ]
        }

async def update_post(pool: asyncpg.Pool, id_post: int, post_update: PublicacionUpdate):
    async with pool.acquire() as connection:
        query = """
        UPDATE Publicacion
        SET titulo = COALESCE($1, titulo),
            contenido = COALESCE($2, contenido),
            portada = COALESCE($3, portada),
            publicado = COALESCE($4, publicado)
        WHERE id_post = $5
        RETURNING *;
        """
        post = await connection.fetchrow(query, post_update.titulo, post_update.contenido,
                                         post_update.portada, post_update.publicado, id_post)
        return post if post else None

async def delete_post(pool: asyncpg.Pool, id_post: int):
    async with pool.acquire() as connection:
        await connection.execute("DELETE FROM Publicacion_Etiquetas WHERE id_publicacion = $1;", id_post)
        await connection.execute("DELETE FROM Calificaciones_Publicacion WHERE id_publicacion = $1;", id_post)
        result = await connection.execute("DELETE FROM Publicacion WHERE id_post = $1;", id_post)
        return result == "DELETE 1"

####################################################################################################
# Calificaciones

async def create_calificacion(pool: asyncpg.Pool, calificacion: CalificacionCreate):
    async with pool.acquire() as connection:
        async with connection.transaction():
            query = """
            INSERT INTO Calificaciones (calificacion)
            VALUES ($1)
            RETURNING id_calificacion;
            """
            id_calificacion = await connection.fetchval(query, calificacion.calificacion)
            query_asociacion = """
            INSERT INTO Calificaciones_Publicacion (id_calificacion, id_publicacion)
            VALUES ($1, $2);
            """
            await connection.execute(query_asociacion, id_calificacion, calificacion.id_publicacion)
            return {"mensaje": "Calificación registrada correctamente"}

async def get_calificacion_promedio(pool: asyncpg.Pool, id_publicacion: int):
    async with pool.acquire() as connection:
        query = """
        SELECT p.id_post AS id_publicacion, 
               COALESCE(AVG(c.calificacion), 0) AS promedio, 
               COUNT(c.id_calificacion) AS cantidad
        FROM Publicacion p
        LEFT JOIN Calificaciones_Publicacion cp ON p.id_post = cp.id_publicacion
        LEFT JOIN Calificaciones c ON cp.id_calificacion = c.id_calificacion
        WHERE p.id_post = $1
        GROUP BY p.id_post;
        """
        row = await connection.fetchrow(query, id_publicacion)
        if not row:
            return None
        return CalificacionResponse(
            id_publicacion=row["id_publicacion"],
            promedio=float(row["promedio"]),
            cantidad=row["cantidad"]
        )

####################################################################################################
# Etiqueta

async def create_tag(pool: asyncpg.Pool, etiqueta: EtiquetaCreate):
    async with pool.acquire() as connection:
        query = """
        INSERT INTO Etiquetas (tag)
        VALUES ($1)
        ON CONFLICT (tag) DO NOTHING
        RETURNING id_tag, tag;
        """
        row = await connection.fetchrow(query, etiqueta.tag)
        if row:
            return EtiquetaResponse(id_tag=row["id_tag"], tag=row["tag"])
        else:
            return None

async def assign_tags_to_post(pool: asyncpg.Pool, etiquetas_publicacion: EtiquetasPublicacion):
    async with pool.acquire() as connection:
        async with connection.transaction():
            for tag in etiquetas_publicacion.etiquetas:
                tag_id = await connection.fetchval(
                    "INSERT INTO Etiquetas (tag) VALUES ($1) ON CONFLICT (tag) DO NOTHING RETURNING id_tag;",
                    tag
                )
                if not tag_id:
                    tag_id = await connection.fetchval("SELECT id_tag FROM Etiquetas WHERE tag = $1;", tag)
                await connection.execute(
                    "INSERT INTO Publicacion_Etiquetas (id_publicacion, id_tag) VALUES ($1, $2) ON CONFLICT DO NOTHING;",
                    etiquetas_publicacion.id_publicacion, tag_id
                )
            return {"mensaje": "Etiquetas asignadas correctamente"}

async def list_tags(pool: asyncpg.Pool):
    async with pool.acquire() as connection:
        query = "SELECT id_tag, tag FROM Etiquetas ORDER BY tag;"
        rows = await connection.fetch(query)
        return [EtiquetaResponse(id_tag=row["id_tag"], tag=row["tag"]) for row in rows]
