from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import auth, firestore
from app.models.user_model import UsuarioPublic, UsuarioUpdate, PasswordChange
from app.core import get_current_user

router = APIRouter()

@router.get("/me", response_model=UsuarioPublic)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return current_user


@router.patch("/me", response_model=UsuarioPublic)
async def update_user_me(
    datos: UsuarioUpdate, 
    current_user: dict = Depends(get_current_user)
):
    db = firestore.client()
    
    uid = current_user['id']
    update_data = {k: v for k, v in datos.dict().items() if v is not None}
    
    if not update_data:
        return current_user
    
    try:
        user_ref = db.collection("users").document(uid)
        user_ref.update(update_data)
        
        if 'username' in update_data:
            auth.update_user(uid, display_name=update_data['username'])

        return {**current_user, **update_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al actualizar: {str(e)}")
    

@router.post("/me/change-password")
async def change_password(
    datos: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    db = firestore.client()

    uid = current_user['id']
    try:
        auth.update_user(uid, password=datos.password)
        return {"message": "Contraseña actualizada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.delete("/me")
async def delete_account(current_user: dict = Depends(get_current_user)):
    db = firestore.client()
    

    uid = current_user['id']
    try:
        auth.delete_user(uid)
        
        db.collection("users").document(uid).delete()
        
        return {"message": "Cuenta eliminada permanentemente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))