"""
Routes de chat
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, Conversation, Message
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationResponse,
    ConversationDetailResponse,
    MessageResponse
)
from app.auth import get_current_active_user

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Variable globale pour l'AIEngine (sera initialisée dans main.py)
ai_engine = None


def set_ai_engine(engine):
    """Configure l'AIEngine pour ce module"""
    global ai_engine
    ai_engine = engine


@router.post("/send", response_model=ChatResponse)
def send_message(
    chat_request: ChatRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Envoie un message et reçoit une réponse de l'IA"""
    
    # Récupérer ou créer la conversation
    if chat_request.conversation_id:
        conversation = db.query(Conversation).filter(
            Conversation.id == chat_request.conversation_id,
            Conversation.user_id == current_user.id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation non trouvée"
            )
    else:
        # Créer une nouvelle conversation
        conversation = Conversation(
            user_id=current_user.id,
            title="Nouvelle consultation"
        )
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
    
    # Sauvegarder le message utilisateur
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=chat_request.message
    )
    db.add(user_message)
    db.commit()
    
    # Récupérer l'historique de la conversation (pour le contexte)
    messages = db.query(Message).filter(
        Message.conversation_id == conversation.id
    ).order_by(Message.created_at).all()
    
    # Préparer l'historique pour l'IA (exclure le dernier message)
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages[:-1]
    ]
    
    # Détecter le cas si c'est le premier message
    case_detected = conversation.case_type
    confidence = None
    
    if len(messages) == 1:  # Premier message
        case_detected = ai_engine.detect_case(chat_request.message)
        
        if case_detected:
            confidence = 0.85
            conversation.case_type = case_detected
            conversation.title = case_detected.replace("_", " ").title()
            db.commit()
    
    # Générer la réponse de l'IA
    response_text = ai_engine.generate_response(
        user_message=chat_request.message,
        case_id=case_detected,
        conversation_history=conversation_history
    )
    
    # Sauvegarder la réponse de l'assistant
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=response_text,
        extra_data={
            "case_detected": case_detected,
            "confidence": confidence
        }
    )
    db.add(assistant_message)
    db.commit()
    
    return ChatResponse(
        message=response_text,
        conversation_id=conversation.id,
        case_detected=case_detected,
        confidence=confidence
    )


@router.get("/conversations", response_model=List[ConversationResponse])
def get_conversations(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère toutes les conversations de l'utilisateur"""
    conversations = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.updated_at.desc()).all()
    
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationDetailResponse)
def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Récupère une conversation avec tous ses messages"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée"
        )
    
    return conversation


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Supprime une conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation non trouvée"
        )
    
    db.delete(conversation)
    db.commit()
    
    return None


@router.get("/cases")
def get_legal_cases():
    """
    Retourne la liste de tous les cas juridiques disponibles
    """
    if not ai_engine:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI Engine non initialisé"
        )
    
    cases_list = []
    for case_id, case_data in ai_engine.knowledge_base.items():
        cases_list.append({
            "id": case_id,
            "titre": case_data.get("titre", ""),
            "description": case_data.get("description", ""),
            "type": case_data.get("type", ""),
            "faits": case_data.get("faits", []),
            "articles_applicables": case_data.get("articles_applicables", []),
            "conseils_juridiques": case_data.get("conseils_juridiques", [])
        })
    
    return {
        "total": len(cases_list),
        "cases": cases_list
    }
