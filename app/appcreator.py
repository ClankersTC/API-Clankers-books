from fastapi import FastAPI
from contextlib import asynccontextmanager
#from .routers import libros, auth  
from .db.firebase_config import init_firebase
from .services.cache_config import init_cache, close_cache

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- AL ARRANCAR (Startup) ---
    print("INFO:     Iniciando servicios externos...")
    
    # 1. Inicializar Firebase
    try:
        init_firebase()
        print("INFO:     Conexión con Firebase establecida.")
    except Exception as e:
        print(f"ERROR:    No se pudo conectar a Firebase: {e}")
        
    # 2. Inicializar el Cache de Redis
    try:
        await init_cache()
        print("INFO:     Conexión con Cache (Redis) establecida.")
    except Exception as e:
        print(f"ERROR:    No se pudo conectar a Redis: {e}")

    print("INFO:     Aplicación lista para recibir peticiones.")
    
    yield 
    
    # --- AL APAGAR (Shutdown) ---
    print("INFO:     Cerrando conexiones...")
    await close_cache()
    print("INFO:     Conexiones cerradas. Adiós.")

app = FastAPI(
    title="API-BooksClankers",
    description="API de Clankers.",
    version="1.0",
    lifespan=lifespan  
)

#app.include_router(libros.router, prefix="/api/v1/libros", tags=["Libros"])
#app.include_router(auth.router, prefix="/api/v1/auth", tags=["Autenticación"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"status": "¡Servidor en línea!", "docs_url": "/docs"}