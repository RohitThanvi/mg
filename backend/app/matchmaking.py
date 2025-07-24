# backend/app/matchmaking.py

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from threading import Lock

router = APIRouter()

queue = []
lock = Lock()

class QueueRequest(BaseModel):
    user_id: int

@router.post("/match")
def add_to_queue(request: QueueRequest):
    user_id = request.user_id
    with lock:
        if queue and queue[0] != user_id:
            opponent_id = queue.pop(0)
            return {"opponent_id": opponent_id}
        queue.append(user_id)
        return {"opponent_id": None}

@router.post("/leave")
def remove_from_queue(request: QueueRequest):
    user_id = request.user_id
    with lock:
        if user_id in queue:
            queue.remove(user_id)
    return {"message": "User removed from queue"}
