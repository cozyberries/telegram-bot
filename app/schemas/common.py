"""Common Pydantic schemas used across the application"""

from typing import Optional, Generic, TypeVar, List, Any
from pydantic import BaseModel, Field
from datetime import datetime


class MessageResponse(BaseModel):
    """Standard message response"""
    message: str
    parse_mode: str = "Markdown"


class SuccessResponse(BaseModel):
    """Standard success response"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    success: bool = False
    error: str
    details: Optional[str] = None


class ListMetadata(BaseModel):
    """Metadata for list responses"""
    total: int
    limit: int
    offset: int = 0
    has_more: bool = False


T = TypeVar('T')


class ListResponse(BaseModel, Generic[T]):
    """Generic list response with metadata"""
    items: List[T]
    metadata: ListMetadata


class CommandInput(BaseModel):
    """Base class for command inputs"""
    user_id: str
    username: Optional[str] = None
    
    class Config:
        frozen = False
        validate_assignment = True


class TimestampMixin(BaseModel):
    """Mixin for timestamp fields"""
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
