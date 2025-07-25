from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth_routes, leaderboard_routes, dashboard_routes
from . import debate, matchmaking
from .socketio_instance import sio
import socketio

# Define the list of allowed origins explicitly
origins = [
    "http://localhost:5173"
]

# Create FastAPI instance
fastapi_app = FastAPI()

# Enable CORS



fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Your frontend dev port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Log incoming requests for debugging
@fastapi_app.middleware("http")
async def log_requests(request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

# Include routers
fastapi_app.include_router(auth_routes.router)
fastapi_app.include_router(debate.router)
fastapi_app.include_router(leaderboard_routes.router)
fastapi_app.include_router(dashboard_routes.router)
fastapi_app.include_router(matchmaking.router)

# Combine Socket.IO and FastAPI into a single ASGI app
app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
