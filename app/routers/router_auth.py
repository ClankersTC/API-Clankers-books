from fastapi import APIRouter, HTTPException, status
from firebase_admin import firestore,auth
import requests
from app.models import (
    UsuarioPublic,
    UsuarioCreate,
    UsuarioLogin,
    TokenResponse
)
from app.core import settings

router = APIRouter()

@router.post("/register", response_model=UsuarioPublic, status_code=status.HTTP_201_CREATED)
async def register_user(user: UsuarioCreate):
    """
    Registra un nuevo usuario en Firebase Auth 
    Crea su perfil en Firestore
    """

    try:
        user_record = auth.create_user(
            email = user.email,
            password = user.password,
            display_name= user.username
        )

        user_data = {
            "id" : user_record.uid,
            "username": user.username,
            "email": user.email,
            "rol": "lector",
            "preferencias": [],
            "fechaRegistro": firestore.SERVER_TIMESTAMP
        }

        db = firestore.client()

        db.collection("users").document(user_record.uid).set(user_data)

        return user_data
    
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=400,
            detail=f"El correo {user.email}"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error de validación: {str(e)}"
        )
    
    except Exception as e:
        print(f"Error no controlado: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocurrió un error interno al procesar el registro."
        )


@router.post("/login", response_model=TokenResponse)
async def login_user(user: UsuarioLogin):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_API_KEY}"
    
    payload = {
        "email": user.email,
        "password": user.password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)
    
    if response.status_code != 200:
        error_data = response.json()
        error_msg = error_data.get("error", {}).get("message", "Login failed")
        
        if "INVALID_PASSWORD" in error_msg or "EMAIL_NOT_FOUND" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Credenciales incorrectas"
            )
        elif "USER_DISABLED" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Cuenta deshabilitada"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=error_msg
            )

    auth_data = response.json()
    
    
    db = firestore.client() 
    user_doc = db.collection("users").document(auth_data["localId"]).get()
    
    user_info = None
    if user_doc.exists:
        user_info = user_doc.to_dict()
        user_info['id'] = auth_data["localId"]

    return {
        "idToken": auth_data["idToken"],           # El Token JWT para usar la API
        "refreshToken": auth_data["refreshToken"], # Para renovar sesión
        "expiresIn": auth_data["expiresIn"],
        "localId": auth_data["localId"],
        "userData": user_info 
    }