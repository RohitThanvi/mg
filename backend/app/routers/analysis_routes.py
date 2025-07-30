from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth
from ..ai import get_ai_response

router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"]
)

from ..services.evaluation_service import get_debate_analysis, evaluate_debate

@router.get("/{debate_id}", response_model=schemas.Analysis)
def get_analysis(debate_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    messages = db.query(models.Message).filter(models.Message.debate_id == debate_id).all()

    analysis = get_debate_analysis(messages)

    winner = evaluate_debate(messages)
    score = 0
    if winner == 'user':
        score = 10
    elif winner == 'opponent':
        score = -10

    return {"analysis": analysis, "score": score}
