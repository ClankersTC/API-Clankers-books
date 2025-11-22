from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth, firestore

security_scheme = HTTPBearer(auto_error=True)

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(security_scheme)):
    """
    1. Recibe el token 'Bearer ...' del Header.
    2. Lo decodifica con Firebase Admin.
    3. Busca los datos completos del usuario en Firestore.
    4. Retorna el diccionario del usuario o lanza error si algo falla.
    """
    try:
        decoded_token = auth.verify_id_token(token.credentials)
        uid = decoded_token['uid']

        db = firestore.client()
        user_ref = db.collection("users").document(uid)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuario válido en Auth pero no encontrado en Base de Datos."
            )

        user_data = user_doc.to_dict()
        
        user_data['id'] = uid
        
        if 'email' not in user_data:
            user_data['email'] = decoded_token.get('email')

        return user_data

    except auth.ExpiredIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado. Por favor inicia sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.InvalidIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o malformado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except auth.RevokedIdTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha sido revocado (el usuario cambió contraseña o se cerró sesión).",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error de autenticación: {e}") 
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al validar las credenciales."
        )
    

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos de administrador para realizar esta acción."
        )
    return current_user