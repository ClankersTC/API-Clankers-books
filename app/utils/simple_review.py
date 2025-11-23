from firebase_admin import firestore
from fastapi import  HTTPException, Depends, status

async def get_review_simple(review_id: str, book_id: str):
    
    db = firestore.client()
    
    review_ref = db.collection("books").document(book_id).collection("reviews").document(review_id)
    doc = review_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reseña no encontrada")

    return {**doc.to_dict(), "id": doc.id}