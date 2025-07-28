from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class User(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserInDB(User):
    hashed_password: str

class FileMetadata(BaseModel):
    filename: str
    user_id: str
    timestamp: datetime
    num_chunks: int
