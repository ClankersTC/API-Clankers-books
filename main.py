from fastapi import FastAPI
from google.cloud import firestore
import json

app= FastAPI()

db = firestore.Client.from_service_account_json('serviceAccountKey.json')

@app.get("/")
async def read_root():
    return {"Hello": "from clankers-books API"}

@app.get("/books")
async def get_books():
    books_ref = db.collection('books')
    docs = books_ref.stream()
    books = []
    for doc in docs:
        book = doc.to_dict()
        book['id'] = doc.id
        books.append(book)
    return books
