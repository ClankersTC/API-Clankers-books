import uvicorn

from app import app  

if __name__ == "__main__":
    print("INFO:   Ejecutando API")
    uvicorn.run(
        app,  
        host="127.0.0.1",
        port=8000,
        log_level="info"
    )