from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(...,min_length=1, max_length=100, description="User Full Name")
    email: EmailStr = Field(..., description="User Full Name")
    password: str = Field(...,min_length=6, description="User Password (Minimal 6 Characters)")
    role: str = Field(default='user', pattern='^(admin|user)$', description="User role: 'admin' or 'user'")
    parent_id: Optional[int] = Field(None, description="Parent user ID (for hierarchy)")
    is_active: bool = Field(True, description="Is user active?")

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100, description="User full name")
    email: Optional[EmailStr] = Field(None, description="User email address")
    password: Optional[str] = Field(None, min_length=6, description="User password")
    role: Optional[str] = Field(None, pattern='^(admin|user)$', description="User role")
    parent_id: Optional[int] = Field(None, description="Parent user ID")
    is_active: Optional[bool] = Field(None, description="Is user active?")