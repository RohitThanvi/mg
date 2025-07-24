from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db
from .ai import get_ai_response
from .socket_io import sio

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

# ----------------- SOCKET.IO AI DEBATE EVENTS -----------------
@sio.event
async def user_message(sid, data):
    debate_id = data.get('debate_id')
    user_id = data.get('user_id')
    content = data.get('content')

    # Use a database session from the pool
    with Session(bind=get_db.engine) as db:
        # 1. Save user's message
        user_message = models.Message(
            content=content,
            user_id=user_id,
            debate_id=debate_id,
            sender_type='user'
        )
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

        # Optionally, emit the user message back to the room if needed
        # await sio.emit('new_message', schemas.MessageOut.from_orm(user_message).dict())

    # 2. Notify clients that AI is "typing"
    await sio.emit('ai_typing', {'is_typing': True, 'debateId': debate_id})

    # 3. Get AI response
    ai_prompt = f"The user in a debate said: '{content}'. Respond to this argument."
    ai_content = get_ai_response(ai_prompt)

    # 4. Notify clients that AI is done "typing"
    await sio.emit('ai_typing', {'is_typing': False, 'debateId': debate_id})

    # 5. Save AI's message
    with Session(bind=get_db.engine) as db:
        ai_message = models.Message(
            content=ai_content,
            user_id=None,  # Or a specific AI user ID
            debate_id=debate_id,
            sender_type='ai'
        )
        db.add(ai_message)
        db.commit()
        db.refresh(ai_message)

        # 6. Broadcast AI's message to the room
        await sio.emit('new_message', schemas.MessageOut.from_orm(ai_message).dict())
