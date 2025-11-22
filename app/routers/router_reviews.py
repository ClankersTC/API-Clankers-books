from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore
from datetime import datetime, timezone
from app.models.review_model import ReviewCreate, ReviewResponse, ReviewUpdate
from app.core.security import get_current_user, get_current_admin

router = APIRouter()

@router.post("/{book_id}/reviews", response_model=ReviewResponse)
async def create_review(
    book_id: str,
    review: ReviewCreate,
    current_user: dict = Depends(get_current_user)
):
    if not current_user: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )
    
    db = firestore.client()

    book_ref = db.collection("books").document(book_id)
    if not book_ref.get().exists:
        raise HTTPException(status_code=404, detail="Book not found")

    review_data = review.model_dump()
    review_data.update({
        "bookId": book_id,
        "userId": current_user['id'],
        "reviewerName": current_user.get('username', 'Anonymous'), 
        "avatar": current_user.get('fotoPerfilURL'),
        "createdAt": datetime.now(timezone.utc)
    })

    try:
        
        new_review_ref = book_ref.collection("reviews").document()
        new_review_ref.set(review_data)
        
        return {
            "id": new_review_ref.id,
            **review_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{book_id}/reviews", response_model=list[ReviewResponse])
async def get_book_reviews(
    book_id: str,
    current_user: dict = Depends(get_current_user) 
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )

    db = firestore.client()

    reviews_ref = db.collection("books").document(book_id).collection("reviews")
    docs = reviews_ref.order_by("createdAt", direction=firestore.Query.DESCENDING).stream()
    
    results = []
    for doc in docs:
        data = doc.to_dict()
        results.append({"id": doc.id, **data})
        
    return results


@router.patch("/{book_id}/reviews/{review_id}", response_model=ReviewResponse)
async def update_review(
    book_id: str,
    review_id: str,
    updates: ReviewUpdate,
    current_user: dict = Depends(get_current_user)
):
    if not current_user: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )

    db = firestore.client()
    
    review_ref = db.collection("books").document(book_id).collection("reviews").document(review_id)
    review_doc = review_ref.get()

    if not review_doc.exists:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    review_data = review_doc.to_dict()

    if review_data["userId"] != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para editar esta reseña"
        )

    data_to_update = {k: v for k, v in updates.dict().items() if v is not None}
    
    if data_to_update:
        review_ref.update(data_to_update)
        
        updated_review = {**review_data, **data_to_update, "id": review_id}
        return updated_review
    
    return {**review_data, "id": review_id}

@router.delete("/{book_id}/reviews/{review_id}")
async def delete_review(
    book_id: str,
    review_id: str,
    current_user: dict = Depends(get_current_user) or Depends(get_current_admin)
):
    if not current_user: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede realizar esa accion"
        )


    db = firestore.client()
    
    review_ref = db.collection("books").document(book_id).collection("reviews").document(review_id)
    review_doc = review_ref.get()

    if not review_doc.exists:
        raise HTTPException(status_code=404, detail="Reseña no encontrada")

    is_owner = review_doc.to_dict()["userId"] == current_user["id"]
    is_admin = current_user.get("role") == "admin"

    if not (is_owner or is_admin):
        raise HTTPException(status_code=403, detail="No autorizado para borrar esto")

    review_ref.delete()
    
    return {"message": "Reseña eliminada correctamente"}

@router.get("/me/reviews", response_model=list[ReviewResponse])
async def get_my_reviews(current_user: dict = Depends(get_current_user)):
    
    if not current_user: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )

    uid = current_user['id']

    db = firestore.client()


    reviews_query = db.collection_group("reviews").where("userId", "==", uid).stream()

    results = []
    for doc in reviews_query:
        data = doc.to_dict()
        results.append({"id": doc.id, **data})
        
    return results