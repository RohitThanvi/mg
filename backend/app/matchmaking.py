from .socketio_instance import sio
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from . import database, models, schemas
from .ai import get_ai_response
from .services.evaluation_service import evaluate_debate, get_debate_analysis

router = APIRouter()

# In-memory store for online users
# In a production app, you'd use Redis or a similar store
online_users = {}

@router.post("/match")
def match(user_id: int, db: Session = Depends(database.get_db)):
    # This is a placeholder for the old match endpoint.
    # The new matchmaking logic is handled by websockets.
    return {"message": "This endpoint is deprecated. Please use websockets."}

@sio.event
async def connect(sid, environ):
    print(f"connect {sid}")

@sio.event
async def disconnect(sid):
    print(f"disconnect {sid}")
    user_id_to_remove = None
    for user_id, user_data in online_users.items():
        if user_data['sid'] == sid:
            user_id_to_remove = user_id
            break
    if user_id_to_remove:
        del online_users[user_id_to_remove]
    await sio.emit('online_users', list(online_users.values()))

@sio.event
async def user_online(sid, data):
    user_id = data.get('userId')
    online_users[str(user_id)] = {
        'id': user_id,
        'sid': sid,
        'username': data.get('username'),
        'elo': data.get('elo')
    }
    await sio.emit('online_users', list(online_users.values()))

@sio.event
async def user_offline(sid, data):
    user_id = data.get('userId')
    if user_id in online_users:
        del online_users[user_id]
    await sio.emit('online_users', list(online_users.values()))

@sio.event
async def challenge_user(sid, data):
    opponent_id = data.get('opponentId')
    challenger = data.get('challenger')
    topic = data.get('topic')

    if opponent_id == 'ai':
        with Session(bind=database.get_db.engine) as db:
            # Create a new debate
            db_debate = models.Debate(
                user_id=challenger['id'],
                topic=topic,
                stance="pro"  # Add a default stance
            )
            db.add(db_debate)
            db.commit()
            db.refresh(db_debate)
            debate_id = db_debate.id
        # Create an AI opponent
        ai_opponent = {
            'id': 'ai',
            'username': 'AI Challenger',
            'elo': 1200,
            'is_ai': True
        }
        await sio.emit('challenge_accepted', {'opponent': ai_opponent, 'topic': topic, 'debateId': debate_id}, room=sid)
    elif str(opponent_id) in online_users:
        opponent_sid = online_users[str(opponent_id)]['sid']
        await sio.emit('challenge_received', {'challenger': challenger, 'topic': topic}, room=opponent_sid)


@sio.event
async def accept_challenge(sid, data):
    challenger_id = data.get('challengerId')
    opponent = data.get('opponent')
    topic = data.get('topic')
    print(f"Challenge accepted by {opponent['username']} from {challenger_id}")

    with Session(bind=database.get_db.engine) as db:
        # Create a new debate
        db_debate = models.Debate(
            user_id=challenger_id,
            topic=topic,
            stance="pro"  # Add a default stance
        )
        db.add(db_debate)
        db.commit()
        db.refresh(db_debate)
        debate_id = db_debate.id

    print(f"Debate created with id: {debate_id}")

    challenger_sid = online_users[str(challenger_id)]['sid']
    print(f"Sending challenge accepted to {challenger_sid}")
    await sio.emit('challenge_accepted', {'opponent': opponent, 'topic': topic, 'debateId': debate_id}, room=challenger_sid)

    # Notify the user who accepted the challenge
    challenger_user = online_users[str(challenger_id)]
    await sio.emit('challenge_accepted', {'opponent': challenger_user, 'topic': topic, 'debateId': debate_id}, room=sid)


@sio.event
async def decline_challenge(sid, data):
    challenger_id = data.get('challengerId')
    challenger_sid = online_users[str(challenger_id)]['sid']
    await sio.emit('challenge_declined', {}, room=challenger_sid)

import logging

logging.basicConfig(level=logging.INFO)

@sio.event
async def join_debate(sid, data):
    debate_id = data.get('debate_id')
    sio.enter_room(sid, f"debate_{debate_id}")

@sio.event
async def human_message(sid, data):
    logging.info(f"Received human message: {data}")
    debate_id = data.get('debate_id')
    user_id = data.get('user_id')
    content = data.get('content')

    # Use a database session from the pool
    with Session(bind=database.get_db.engine) as db:
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

        # 2. Broadcast the message to the other user in the debate
        await sio.emit('new_message', schemas.MessageOut.from_orm(user_message).dict(), room=f"debate_{debate_id}")

@sio.event
async def forfeit_debate(sid, data):
    debate_id = data.get('debate_id')
    await sio.emit('debate_forfeited', {}, room=f"debate_{debate_id}", skip_sid=sid)

@sio.event
async def end_debate(sid, data):
    debate_id = data.get('debate_id')
    print(f"Ending debate with ID: {debate_id}")
    with Session(bind=database.get_db.engine) as db:
        messages = db.query(models.Message).filter(models.Message.debate_id == debate_id).all()
        winner = evaluate_debate(messages)

        user_ids = [m.user_id for m in messages if m.user_id is not None]

        if len(user_ids) == 2:
            user1_id, user2_id = user_ids
            user1 = db.query(models.User).filter(models.User.id == user1_id).first()
            user2 = db.query(models.User).filter(models.User.id == user2_id).first()

            if winner == 'user':
                user1.elo += 10
                user1.mind_tokens += 5
                user2.elo -= 10
                db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
                db_debate.winner = user1.username
            elif winner == 'opponent':
                user2.elo += 10
                user2.mind_tokens += 5
                user1.elo -= 10
                db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
                db_debate.winner = user2.username
            else:
                db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
                db_debate.winner = "draw"
        elif len(user_ids) == 1:
            user_id = user_ids[0]
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if winner == 'user':
                user.elo += 10
                user.mind_tokens += 5
                db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
                db_debate.winner = user.username
            elif winner == 'opponent':
                user.elo -= 10
                db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
                db_debate.winner = "AI"
            else:
                db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
                db_debate.winner = "draw"

        analysis = get_debate_analysis(messages)
        db_debate = db.query(models.Debate).filter(models.Debate.id == debate_id).first()
        db_debate.analysis = analysis
        db.commit()

        await sio.emit('debate_ended', {'winner': winner}, room=f"debate_{debate_id}")
