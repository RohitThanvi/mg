# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes
from . import debate, matchmaking  # Include both
from .socketio_instance import sio  # Use the shared socketio instance

import socketio

# Define allowed origins for CORS
origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080",
    "http://localhost:5173"
]

# Create FastAPI app
fastapi_app = FastAPI()

# Add CORS middleware
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: log all incoming requests
@fastapi_app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# Include routers
fastapi_app.include_router(auth_routes.router)
fastapi_app.include_router(debate.router)

# Combine Socket.IO and FastAPI into one ASGI app
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
