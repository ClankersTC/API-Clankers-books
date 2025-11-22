from fastapi import APIRouter, HTTPException, status, Depends, Query
from firebase_admin import firestore
from fastapi_cache.decorator import cache
from fastapi_cache import FastAPICache
from typing import List

from app.models.libro_model import BookCreate, BookUpdate, BookResponse
from app.core.security import get_current_user, get_current_admin
from app.utils import build_book_key
router = APIRouter()


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    current_user: dict = Depends(get_current_admin) 
):
    db = firestore.client()
    await FastAPICache.clear(namespace="todos_libros")

    book_dict = book.model_dump(exclude_unset=True)
    custom_id = book_dict.pop("id", None)
    
    defaults = {
        "rating": 0.0,
        "reviewCount": 0,
        "reviews": [],
        "createdBy": current_user['id'] 
    }
    final_data = {**book_dict, **defaults}

    try:
        if custom_id:
            doc_ref = db.collection("books").document(custom_id)
            if doc_ref.get().exists:
                raise HTTPException(status_code=409, detail="Ya existe un libro con este ID")
            doc_ref.set(final_data)
        else:
            doc_ref = db.collection("books").document()
            doc_ref.set(final_data)

        return {"id": doc_ref.id, **final_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/", response_model=List[BookResponse])
@cache(expire=1800, namespace="todos_libros")
async def get_books(
    current_user: dict = Depends(get_current_user) 
):
    if not current_user: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )

    db = firestore.client()

    docs = db.collection("books").stream()
    
    books_list = []
    for doc in docs:
        data = doc.to_dict()
        books_list.append({
            "id": doc.id, 
            **data,
            "reviewCount": data.get("reviewCount", 0) 
        })
        
    return books_list

@router.get("/genre/{genero}", response_model=List[BookResponse])
@cache(expire=1800) 
async def get_books_by_genre(
    genero: str,
    current_user: dict = Depends(get_current_user) 
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )
    
    db = firestore.client()
    genre_query_object = {"genre": genero}
    
    try:
        query = db.collection("books").where("genres", "array_contains", genre_query_object)
        docs = query.stream()
        
        results = []
        for doc in docs:
            data = doc.to_dict()
            results.append({"id": doc.id, **data, "reviews": data.get("reviews", [])})
            
        return results
    except Exception as e:
        print(f"Error buscando genero: {e}")
        return []

@router.get("/{book_id}", response_model=BookResponse)
@cache(
    expire=1800,
    key_builder=build_book_key
)
async def get_book_by_id(
    book_id: str,
    current_user: dict = Depends(get_current_user) 
):
    if not current_user: 
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )
    
    db = firestore.client()

    doc_ref = db.collection("books").document(book_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    data = doc.to_dict()
    return {"id": doc.id, **data, "reviews": data.get("reviews", [])}

@router.patch("/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str, 
    updates: BookUpdate,
    current_user: dict = Depends(get_current_admin) 
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario administrador autenticado puede acceder a esos recursos"
        )


    db = firestore.client()
    doc_ref = db.collection("books").document(book_id)
    
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    data_to_update = {k: v for k, v in updates.model_dump().items() if v is not None}
    
    if not data_to_update:
        current_data = doc_ref.get().to_dict()
        return {"id": book_id, **current_data}

    try:
        doc_ref.update(data_to_update)
        
        await FastAPICache.get_backend().delete(f"book:{book_id}")
        await FastAPICache.clear(namespace="todos_libros")

        new_data = doc_ref.get().to_dict()
        return {"id": book_id, **new_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(
    book_id: str,
    current_user: dict = Depends(get_current_admin) 
):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo un usuario autenticado puede acceder a esos recursos"
        )

    db = firestore.client()

    doc_ref = db.collection("books").document(book_id)
    
    if not doc_ref.get().exists:
        raise HTTPException(status_code=404, detail="Libro no encontrado")

    try:
        doc_ref.delete()

        await FastAPICache.get_backend().delete(f"book:{book_id}")
        await FastAPICache.clear(namespace="todos_libros")
        
        return None 

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))