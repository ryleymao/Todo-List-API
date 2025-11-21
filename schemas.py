from pydantic import BaseModel, EmailStr
from typing import List

# Schema for creating a user (what we receive during registration)
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

# Schema for returning user data (what we send back - no password!)
class UserResponse(BaseModel):
    id: int
    name: str
    email: str

    class Config:
        from_attributes = True # Allows Pydantic to work with SQLAlchemy models

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    token: str

class TodoCreate(BaseModel):
    title: str
    description: str

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str

    class Config:
        from_attributes = True

class TodoListResponse(BaseModel):
    data: List[TodoResponse]
    page: int
    limit: int
    total: int