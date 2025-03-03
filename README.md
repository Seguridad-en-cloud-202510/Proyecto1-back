# 📖 API REST para Gestión de Blogs

Esta API REST permite la gestión de blogs, incluyendo la creación de usuarios, autenticación con JWT, publicaciones con etiquetas, calificación de contenido y protección de rutas con autenticación.

## 🚀 Tecnologías Utilizadas

- **FastAPI** → Framework web rápido y moderno para Python.  
- **PostgreSQL** → Base de datos relacional utilizada para almacenar datos.  
- **asyncpg** → Cliente asincrónico para PostgreSQL.  
- **Pydantic** → Validación de datos y esquemas de respuesta.  
- **Passlib (bcrypt)** → Hashing seguro de contraseñas.  
- **JWT (JSON Web Tokens)** → Autenticación y autorización segura.

---

## 🎯 Características de la API

✅ **Gestión de Usuarios**  
- Registro de usuarios con almacenamiento seguro de contraseñas.  
- Autenticación con JWT.  
- Recuperación de información del usuario autenticado.  

✅ **Gestión de Publicaciones**  
- Creación, actualización, eliminación y consulta de publicaciones.  
- Paginación en la lista de publicaciones.  
- Asociación de etiquetas a las publicaciones.  

✅ **Sistema de Etiquetas**  
- Creación y asignación de etiquetas a publicaciones.  
- Filtro de publicaciones por etiqueta.  

✅ **Calificación de Publicaciones**  
- Permitir a los usuarios calificar publicaciones.  
- Obtener el promedio de calificación de una publicación.  

✅ **Autenticación y Seguridad**  
- Protección de endpoints sensibles con JWT.  
- Hashing de contraseñas con bcrypt.  
- Validación estricta de datos de entrada.

---

## 🔧 Instalación y Configuración

### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```
### 2️⃣ Crear un Entorno Virtual
```bash
python -m venv fastapi-env
source fastapi-env/bin/activate  # En Linux/macOS
fastapi-env\Scripts\activate     # En Windows
```
### 3️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```
### 4️⃣ Configurar Variables de Entorno
Crear un archivo .env en la raíz del proyecto con basado en el archivo .env.example
### 5️⃣ Ejecutar la Aplicación
```bash
uvicorn main:app --reload
```
La API estará disponible en: http://127.0.0.1:8000
---

## 📖 Documentación Interactiva
FastAPI genera automáticamente la documentación de la API en los siguientes endpoints:

- **Swagger UI** → [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  
- **Redoc UI** → [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

## 🔑 Uso del JWT en Postman
1. Autenticarse con el endpoint **POST /usuarios/login/** usando un usuario registrado.  
2. Copiar el **access_token** del response.  
3. En Postman, ir a la pestaña **Authorization** y seleccionar **Bearer Token**.  
4. Pegar el token en el campo de autenticación.  
5. Realizar peticiones a los endpoints protegidos.

---

## 🛠️ Endpoints Principales

### **Usuarios**
- `POST /usuarios/` → Registrar un nuevo usuario.  
- `POST /usuarios/login/` → Iniciar sesión y obtener un JWT.  
- `GET /usuarios/{id_usuario}` → Obtener información de un usuario.

### **Publicaciones**
- `POST /publicaciones/` → Crear una publicación (**Requiere autenticación**).  
- `GET /publicaciones/{id_post}` → Obtener una publicación por ID.  
- `GET /publicaciones/` → Listar publicaciones con paginación.  
- `PUT /publicaciones/{id_post}` → Actualizar una publicación (**Requiere autenticación**).  
- `DELETE /publicaciones/{id_post}` → Eliminar una publicación (**Requiere autenticación**).

### **Etiquetas**
- `POST /etiquetas/` → Crear una nueva etiqueta (**Requiere autenticación**).  
- `POST /publicaciones/{id_post}/etiquetas/` → Asignar etiquetas a una publicación (**Requiere autenticación**).  
- `GET /etiquetas/` → Listar todas las etiquetas.

### **Calificaciones**
- `POST /calificaciones/` → Calificar una publicación (**Requiere autenticación**).  
- `GET /calificaciones/{id_publicacion}` → Obtener la calificación promedio de una publicación.
