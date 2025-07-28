from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth
from ..ai import get_ai_response

router = APIRouter(
    prefix="/ai-debate",
    tags=["AI Debate"]
)

@router.post("/{debate_id}", response_model=schemas.MessageOut)
async def create_ai_message_route(debate_id: int, message: schemas.MessageCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    # 1. Save user's message
    user_message = models.Message(**message.dict(), debate_id=debate_id, user_id=current_user.id)
    db.add(user_message)
    db.commit()
    db.refresh(user_message)

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

    return ai_message
