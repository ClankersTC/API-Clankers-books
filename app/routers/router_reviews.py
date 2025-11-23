from fastapi import APIRouter, Depends, HTTPException, status
from firebase_admin import firestore
from datetime import datetime, timezone
from app.models.review_model import ReviewCreate, ReviewResponse, ReviewUpdate
from app.core.security import get_current_user, get_current_admin
from app.utils import get_review_simple

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

    transaction = db.transaction()


    @firestore.transactional
    def add_review_in_transaction(transaction, book_ref, review_data):
        book_snapshot = book_ref.get(transaction=transaction)

        if not book_snapshot.exists:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book_data = book_snapshot.to_dict()

        current_rating = book_data.get("rating", 0)
        current_count = book_data.get("reviewCount", 0)

    
        new_count = current_count + 1
        new_total_score = (current_rating * current_count) + review.rating
        new_rating = new_total_score / new_count

        new_review_ref = book_ref.collection("reviews").document()
        
        transaction.set(new_review_ref, review_data)
        
        transaction.update(book_ref, {
            "rating": new_rating,
            "reviewCount": new_count
        })

        return new_review_ref.id

    try:
        review_id = add_review_in_transaction(transaction, book_ref, review_data)
        
        return {
            "id": review_id,
            **review_data
        }
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error en transacción: {e}")
        raise HTTPException(status_code=500, detail="Error al procesar la reseña")

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
    
    book_ref = db.collection("books").document(book_id)
    review_ref = book_ref.collection("reviews").document(review_id)
    
    transaction = db.transaction()


    @firestore.transactional
    def update_in_transaction(transaction, book_ref, review_ref, updates_dict):
        book_snap = book_ref.get(transaction=transaction)
        review_snap = review_ref.get(transaction=transaction)

        if not review_snap.exists:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        if not book_snap.exists:
            raise HTTPException(status_code=404, detail="Libro no encontrado")

        review_data = review_snap.to_dict()

        if review_data["userId"] != current_user["id"]:
            raise HTTPException(status_code=403, detail="No eres el dueño de esta reseña")

        if "rating" in updates_dict and updates_dict["rating"] is not None:
            old_rating = review_data.get("rating", 0)
            new_individual_rating = updates_dict["rating"]
            
            if old_rating != new_individual_rating:
                book_data = book_snap.to_dict()
                current_avg = book_data.get("rating", 0)
                current_count = book_data.get("reviewCount", 1) 

        
                current_total_score = current_avg * current_count
                new_total_score = current_total_score - old_rating + new_individual_rating
                
                new_avg = new_total_score / current_count
                
                transaction.update(book_ref, {"rating": new_avg})

        transaction.update(review_ref, updates_dict)
        
        return {**review_data, **updates_dict, "id": review_id}

    try:
        data_to_update = {k: v for k, v in updates.model_dump().items() if v is not None}
        
        if not data_to_update:
            return await get_review_simple(review_id, book_id)

        updated_data = update_in_transaction(transaction, book_ref, review_ref, data_to_update)
        return updated_data

    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error update transaction: {e}")
        raise HTTPException(status_code=500, detail="Error actualizando reseña")

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
    
    book_ref = db.collection("books").document(book_id)
    review_ref = book_ref.collection("reviews").document(review_id)

    transaction = db.transaction()

    @firestore.transactional
    def delete_in_transaction(transaction, book_ref, review_ref):
        book_snap = book_ref.get(transaction=transaction)
        review_snap = review_ref.get(transaction=transaction)

        if not review_snap.exists:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")

        review_data = review_snap.to_dict()
        
        is_owner = review_data["userId"] == current_user["id"]
        is_admin = current_user.get("role") == "admin"
        
        if not (is_owner or is_admin):
            raise HTTPException(status_code=403, detail="No autorizado")

        if book_snap.exists:
            book_data = book_snap.to_dict()
            current_avg = book_data.get("rating", 0)
            current_count = book_data.get("reviewCount", 0)
            rating_to_remove = review_data.get("rating", 0)

            if current_count > 1:
                current_total = current_avg * current_count
                new_total = current_total - rating_to_remove
                new_count = current_count - 1
                new_avg = new_total / new_count
            else:
                new_count = 0
                new_avg = 0

            transaction.update(book_ref, {
                "rating": new_avg,
                "reviewCount": new_count
            })

        transaction.delete(review_ref)

    try:
        delete_in_transaction(transaction, book_ref, review_ref)
        return {"message": "Reseña eliminada y estadísticas actualizadas"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Error delete transaction: {e}")
        raise HTTPException(status_code=500, detail="Error eliminando reseña")

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