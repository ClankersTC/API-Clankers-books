from pydantic import BaseModel, Field, computed_field
from typing import Optional
from datetime import date, datetime
from app.utils.time_utils import calculate_time_ago 
from datetime import datetime
class ReviewCreate(BaseModel):
    rating: float = Field(..., ge=1, le=10)
    reviewText: str = Field(..., min_length=1, max_length=5000)
    hasSpoilers: bool = False
    startedDate: Optional[datetime] = None
    finishedDate: Optional[datetime] = None

class ReviewResponse(ReviewCreate):
    id: str
    bookId: str
    userId: str 
    reviewerName: str
    avatar: Optional[str] = None
    createdAt: datetime

    @computed_field
    def timeAgo(self) -> str:
        return calculate_time_ago(self.createdAt)

    class Config:
        from_attributes = True

class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1, le=10)
    reviewText: Optional[str] = Field(None, min_length=1, max_length=5000)
    hasSpoilers: Optional[bool] = None
    finishedDate: Optional[str] = None 