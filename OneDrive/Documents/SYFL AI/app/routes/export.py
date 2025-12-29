from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from io import BytesIO
from fastapi.responses import StreamingResponse
from datetime import datetime

from ..database import get_db
from ..models import User, Conversation, Message
from ..auth import get_current_user

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/conversation/{conversation_id}/pdf")
async def export_conversation_pdf(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a conversation to PDF format
    """
    if not REPORTLAB_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="PDF export not available. Install reportlab: pip install reportlab"
        )
    
    # Get conversation
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.asc()).all()
    
    if not messages:
        raise HTTPException(status_code=400, detail="No messages to export")
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
    )
    
    user_message_style = ParagraphStyle(
        'UserMessage',
        parent=styles['BodyText'],
        fontSize=11,
        leftIndent=20,
        rightIndent=0,
        spaceAfter=10,
    )
    
    assistant_message_style = ParagraphStyle(
        'AssistantMessage',
        parent=styles['BodyText'],
        fontSize=11,
        leftIndent=0,
        rightIndent=20,
        spaceAfter=10,
    )
    
    # Add title
    elements.append(Paragraph("SYFL AI - Consultation Juridique", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Add conversation info
    info_data = [
        ["Type de cas:", conversation.case_type or "Non spécifié"],
        ["Date:", conversation.created_at.strftime("%d/%m/%Y à %H:%M")],
        ["Utilisateur:", current_user.username],
        ["Nombre de messages:", str(len(messages))]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db'))
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Add messages
    elements.append(Paragraph("Conversation", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    for msg in messages:
        # Message header
        role_label = "👤 Vous" if msg.role == "user" else "🤖 Assistant SYFL AI"
        time_str = msg.created_at.strftime("%H:%M")
        
        header = f"<b>{role_label}</b> - {time_str}"
        elements.append(Paragraph(header, styles['Normal']))
        
        # Message content
        content = msg.content.replace('\n', '<br/>')
        style = user_message_style if msg.role == "user" else assistant_message_style
        elements.append(Paragraph(content, style))
        elements.append(Spacer(1, 0.15*inch))
    
    # Add footer
    elements.append(Spacer(1, 0.3*inch))
    footer_text = f"""
    <para align=center>
    <font size=8 color="#6b7280">
    Document généré par SYFL AI le {datetime.now().strftime("%d/%m/%Y à %H:%M")}<br/>
    Système d'assistance juridique pour le droit du travail togolais<br/>
    <b>Note:</b> Ce document est fourni à titre informatif uniquement et ne constitue pas un avis juridique.
    </font>
    </para>
    """
    elements.append(Paragraph(footer_text, styles['Normal']))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    buffer.seek(0)
    
    # Generate filename
    filename = f"conversation_{conversation_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )
