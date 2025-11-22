# API Clankers Books

API REST para una plataforma de recomendaciones de libros donde los usuarios pueden descubrir, calificar y dejar reseñas sobre sus libros favoritos.

## Características

- **Autenticación y autorización** de usuarios
- **Gestión de libros** con información detallada
- **Sistema de reseñas** y calificaciones
- **Caché optimizado** para mejorar rendimiento
- **Integración con Firebase** para base de datos

## Stack Tecnológico

| Tecnología | Versión | Propósito |
|-----------|---------|----------|
| **FastAPI** | Latest | Framework web moderno y rápido |
| **Python** | 3.9+ | Lenguaje de programación |
| **Firebase Admin** | Latest | Base de datos y autenticación |
| **Redis** | Latest | Sistema de caché |
| **Uvicorn** | Latest | Servidor ASGI |
| **Pydantic** | Latest | Validación de datos |

## Instalación

### Requisitos previos
- Python 3.9 o superior
- pip (gestor de paquetes de Python)
- Redis (para caché)
- Firebase Project configurado

### Pasos de instalación

1. **Clona el repositorio**
   ```bash
   git clone <tu-repositorio>
   cd API-Clankers-books
   ```

2. **Crea un entorno virtual**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configura las variables de entorno**
   - Crea un archivo `.env` en la raíz del proyecto
   - Añade tus credenciales de Firebase y otras configuraciones necesarias
   ```env
   FIREBASE_PROJECT_ID=tu_proyecto_id
   REDIS_URL=redis://localhost:6379
   SECRET_KEY=tu_clave_secreta
   ```

5. **Inicia el servidor**
   ```bash
   python main.py
   ```

El servidor estará disponible en `http://127.0.0.1:8000`

## Documentación de la API

Una vez que el servidor esté corriendo, accede a:

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`

## Estructura del Proyecto

```
app/
├── core/              # Configuración principal y seguridad
├── db/                # Configuración de Firebase
├── models/            # Modelos de datos (User, Libro, Review)
├── routers/           # Rutas de la API
├── services/          # Lógica de caché
└── utils/             # Utilidades generales
```

### Módulos principales

- **routers**: 
  - `router_auth.py` - Autenticación de usuarios
  - `router_libro.py` - Gestión de libros
  - `router_reviews.py` - Sistema de reseñas
  - `router_user.py` - Perfil de usuario

- **models**: Definición de esquemas Pydantic para validación

- **services**: Configuración de caché con Redis

## Uso

### Endpoints principales

#### Libros
- `GET /libros` - Obtener lista de libros
- `GET /libros/{id}` - Obtener detalles de un libro
- `POST /libros` - Crear nuevo libro

#### Reseñas
- `GET /reviews` - Obtener reseñas
- `POST /reviews` - Crear reseña
- `GET /reviews/{libro_id}` - Reseñas de un libro específico

#### Autenticación
- `POST /auth/register` - Registrar usuario
- `POST /auth/login` - Iniciar sesión

#### Usuario
- `GET /users/me` - Obtener perfil actual
- `PUT /users/me` - Actualizar perfil


## Deployment

El proyecto está configurado para ejecutarse con Uvicorn. Para producción:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Variables de Entorno

Asegúrate de configurar las siguientes variables en tu archivo `.env`:

- `FIREBASE_PROJECT_ID` - ID del proyecto Firebase
- `FIREBASE_PRIVATE_KEY` - Clave privada de Firebase
- `FIREBASE_CLIENT_EMAIL` - Email del cliente de Firebase
- `REDIS_URL` - URL de conexión a Redis
- `SECRET_KEY` - Clave para JWT tokens




---
