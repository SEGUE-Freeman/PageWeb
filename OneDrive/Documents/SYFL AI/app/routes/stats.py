from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from ..database import get_db
from ..models import User, Conversation, Message
from ..auth import get_current_user

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("")
async def get_user_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get statistics for the current user
    """
    # Total conversations
    total_conversations = db.query(func.count(Conversation.id)).filter(
        Conversation.user_id == current_user.id
    ).scalar()
    
    # Total messages
    total_messages = db.query(func.count(Message.id)).join(
        Conversation, Message.conversation_id == Conversation.id
    ).filter(
        Conversation.user_id == current_user.id
    ).scalar()
    
    # Messages by role
    user_messages = db.query(func.count(Message.id)).join(
        Conversation, Message.conversation_id == Conversation.id
    ).filter(
        Conversation.user_id == current_user.id,
        Message.role == "user"
    ).scalar()
    
    assistant_messages = db.query(func.count(Message.id)).join(
        Conversation, Message.conversation_id == Conversation.id
    ).filter(
        Conversation.user_id == current_user.id,
        Message.role == "assistant"
    ).scalar()
    
    # Cases distribution
    cases_distribution = db.query(
        Conversation.case_type,
        func.count(Conversation.id).label('count')
    ).filter(
        Conversation.user_id == current_user.id,
        Conversation.case_type.isnot(None)
    ).group_by(Conversation.case_type).all()
    
    # Format cases distribution
    cases_dict = {case_type: count for case_type, count in cases_distribution}
    
    # Most recent conversation
    recent_conversation = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).first()
    
    recent_conversation_data = None
    if recent_conversation:
        recent_conversation_data = {
            "id": recent_conversation.id,
            "case_type": recent_conversation.case_type,
            "created_at": recent_conversation.created_at.isoformat(),
            "message_count": db.query(func.count(Message.id)).filter(
                Message.conversation_id == recent_conversation.id
            ).scalar()
        }
    
    # Average messages per conversation
    avg_messages_per_conversation = 0
    if total_conversations > 0:
        avg_messages_per_conversation = round(total_messages / total_conversations, 2)
    
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "member_since": current_user.created_at.isoformat()
        },
        "conversations": {
            "total": total_conversations,
            "average_messages": avg_messages_per_conversation
        },
        "messages": {
            "total": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages
        },
        "cases": {
            "distribution": cases_dict,
            "total_cases_consulted": len(cases_dict)
        },
        "recent_activity": recent_conversation_data
    }
