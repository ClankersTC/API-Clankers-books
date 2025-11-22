from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .routers import (
    auth_router,
    user_router,
    review_router,
    book_router
)  
from app.db.firebase_config import init_firebase
from app.services.cache_config import init_cache

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
        print("INFO:    Inicializando el Cache")
    except Exception as e:
        print(f"ERROR:    No se pudo iniciar el Cache: {e}")

    print("INFO:     Aplicación lista para recibir peticiones.")
    
    yield 

app = FastAPI(
    title="API-BooksClankers",
    description="API de Clankers.",
    version="1.0",
    lifespan=lifespan  
)

origins = [
    "http://localhost:3000",         # Frontend local
    "http://localhost:8000/docs"     # Swagger Test
    "https://mis-libros.vercel.app", # Frontend en producción
    "https://clankers-reading.com"   # Dominio Real
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/clankers/auth", tags=["Auth"])
app.include_router(user_router, prefix="/clankers/users", tags=["Users"])
app.include_router(review_router, prefix="/clankers/reviews", tags=["Reseñas"])
app.include_router(book_router, prefix="/clankers/books", tags=["Libros"])

@app.get("/", tags=["Root"])
async def read_root():
    return {"status": "¡Servidor en línea!", "docs_url": "/docs"}