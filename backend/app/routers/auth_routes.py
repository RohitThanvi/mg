from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, models, auth, ai, debate, matchmaking
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed = auth.get_password_hash(user.password)
    
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = auth.authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = auth.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@router.post("/match")
def match(user_id: int, db: Session = Depends(database.get_db)):
    opponent_id = matchmaking.add_to_queue(user_id)
    return {"opponent_id": opponent_id}


@router.post("/debate")
def start_debate(
    debate_data: schemas.DebateCreate,
    user_id: int,
    db: Session = Depends(database.get_db)
):
    saved = debate.create_debate(db, user_id, debate_data)

    prompt = f"Debate on '{debate_data.topic}' with stance '{debate_data.stance}'"
    ai_response = ai.get_ai_response(prompt)

    return {
        "ai_response": ai_response,
        "debate": saved
    }
