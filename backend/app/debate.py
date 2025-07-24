from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db
from .ai import get_ai_response
from .socketio_instance import sio

router = APIRouter(
    prefix="/debate",
    tags=["Debates"]
)

# ----------------- CREATE DEBATE -----------------
@router.post("/", response_model=schemas.DebateOut)
def create_debate_route(debate: schemas.DebateCreate, db: Session = Depends(get_db)):
    db_debate = models.Debate(**debate.dict())
    db.add(db_debate)
    db.commit()
    db.refresh(db_debate)
    return db_debate

# ----------------- GET DEBATE BY ID -----------------
@router.get("/{debate_id}", response_model=schemas.DebateOut)
def get_debate_route(debate_id: int, db: Session = Depends(get_db)):
    db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
    if not db_debate:
        raise HTTPException(status_code=404, detail="Debate not found")
    return db_debate

# ----------------- CREATE MESSAGE IN DEBATE -----------------
@router.post("/{debate_id}/messages", response_model=schemas.MessageOut)
def create_message_route(debate_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    # Ensure debate exists
    if not db.query(models.Debate).filter(models.Debate.id == debate_id).first():
        raise HTTPException(status_code=404, detail="Debate not found")
    
    db_message = models.Message(**message.dict(), debate_id=debate_id)
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

# ----------------- GET ALL MESSAGES IN A DEBATE -----------------
@router.get("/{debate_id}/messages", response_model=list[schemas.MessageOut])
def get_messages_route(debate_id: int, db: Session = Depends(get_db)):
    return (
        db.query(models.Message)
        .filter(models.Message.debate_id == debate_id)
        .order_by(models.Message.timestamp)
        .all()
    )

# ----------------- AI DEBATE ENDPOINT -----------------
@router.post("/{debate_id}/ai-message", response_model=schemas.MessageOut)
async def create_ai_message_route(debate_id: int, message: schemas.MessageCreate, db: Session = Depends(get_db)):
    # 1. Save user's message
    user_message = models.Message(**message.dict(), debate_id=debate_id)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)
    await sio.emit('new_message', schemas.MessageOut.from_orm(user_message).dict())

    # 2. Get AI response
    ai_prompt = f"The user in a debate said: '{message.content}'. Respond to this argument."
    ai_content = get_ai_response(ai_prompt)

    # 3. Save AI's message
    ai_message = models.Message(
        content=ai_content,
        user_id=None, # Or a specific AI user ID
        debate_id=debate_id,
        sender_type='ai'
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)
    await sio.emit('new_message', schemas.MessageOut.from_orm(ai_message).dict())

    return user_message
