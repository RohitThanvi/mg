from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes
from . import debate
import socketio

# Define the list of allowed origins explicitly
origins = [
    "http://127.0.0.1:8080",
    "http://localhost:8080"
]

# Create FastAPI instance
fastapi_app = FastAPI()

# Enable CORS
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log incoming requests for debugging
@fastapi_app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# Include routers
fastapi_app.include_router(auth_routes.router)
fastapi_app.include_router(debate.router)

# Setup Socket.IO server with CORS
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=origins  # Match this to frontend
)

# Combine Socket.IO and FastAPI into a single ASGI app
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
