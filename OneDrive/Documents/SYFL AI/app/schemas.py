"""
Schémas Pydantic pour validation des données
"""
from pydantic import BaseModel, EmailStr, field_validator, Field
from typing import Optional, List
from datetime import datetime
import re


# === AUTHENTIFICATION ===

class UserCreate(BaseModel):
    """Schéma pour créer un utilisateur"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Valide que le mot de passe contient des caractères variés"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'[0-9]', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        return v


class UserLogin(BaseModel):
    """Schéma pour la connexion"""
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=100)


class Token(BaseModel):
    """Schéma pour le token JWT"""
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Schéma pour la réponse utilisateur"""
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


# === CHAT ===

class ChatRequest(BaseModel):
    """Schéma pour envoyer un message"""
    message: str = Field(..., min_length=1, max_length=5000)
    conversation_id: Optional[int] = None


class ChatResponse(BaseModel):
    """Schéma pour la réponse du chat"""
    message: str
    conversation_id: int
    case_detected: Optional[str] = None
    confidence: Optional[float] = None


class MessageResponse(BaseModel):
    """Schéma pour un message"""
    id: int
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Schéma pour une conversation"""
    id: int
    title: str
    case_type: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ConversationDetailResponse(ConversationResponse):
    """Schéma pour une conversation avec ses messages"""
    messages: List[MessageResponse]


# === CAS JURIDIQUES ===

class CaseResponse(BaseModel):
    """Schéma pour un cas juridique"""
    id: int
    case_id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    
    class Config:
        from_attributes = True
