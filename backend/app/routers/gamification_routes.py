from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import database, models, schemas, auth

router = APIRouter(
    prefix="/gamification",
    tags=["Gamification"]
)

@router.get("/badges", response_model=list[schemas.Badge])
def get_badges(db: Session = Depends(database.get_db)):
    return db.query(models.Badge).all()

@router.get("/streaks", response_model=schemas.Streak)
def get_streaks(db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Streak).filter(models.Streak.user_id == current_user.id).first()
