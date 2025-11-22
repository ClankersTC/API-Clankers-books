from fastapi import APIRouter, HTTPException, status
from firebase_admin import firestore,auth
from app.db import db as DataBase
from app.models import UsuarioCreate, UsuarioPublic

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

        DataBase.collection("users").document(user_record.uid).set(user_data)

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
