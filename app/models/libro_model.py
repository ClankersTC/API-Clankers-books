from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from uuid import UUID, uuid4

class Genre(BaseModel):
    genre: str = Field(..., min_length=1, max_length=100)
class ReviewEmbedded(BaseModel):
    reviewerName: str
    timeAgo: str  
    rating: float = Field(..., ge=0, le=5, description="Debe estar entre 0 y 5")
    reviewText: str = Field(..., min_length=1, max_length=5000)
    avatar: Optional[str] = None

class BookBase(BaseModel):
    title: str = Field(..., min_length=1 ,max_length=500)
    author: str = Field(..., min_length=1, max_length=500) 
    coverImage: str
    coverAlt: str
    description: str = Field(..., min_length=1, max_length=5000)
    genres: List[Genre]
class BookCreate(BookBase):
    id: Optional[str] = None 

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    coverImage: Optional[str] = None
    coverAlt: Optional[str] = None
    description: Optional[str] = None
    genres: Optional[List[Genre]] = None
    
class BookResponse(BookBase):
    id: str
    rating: float = 0.0
    reviewCount: int = 0    
    reviews: Optional[List[ReviewEmbedded]] = []    

    class Config:
        from_attributes = True