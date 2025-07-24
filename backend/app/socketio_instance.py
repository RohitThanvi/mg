# app/socketio_instance.py
import socketio

origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080"
]

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins
)
