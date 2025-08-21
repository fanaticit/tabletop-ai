# main.py - Truly minimal working version (no routes yet)
import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta

# Import routes and auth
from app.database import connect_to_mongo, close_mongo_connection
from app.config import settings
from app.routes import games, admin, chat
from app.services.auth_service import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    print("Basic API ready")
    yield
    # Shutdown
    await close_mongo_connection()
    print("Disconnected from MongoDB")

app = FastAPI(
    title="Tabletop Game Rules API",
    description="AI-powered tabletop game rules query service",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login endpoint to get admin token"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Include routers
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
async def root():
    return {
        "message": "Tabletop Game Rules API is running!",
        "status": "minimal_version",
        "database_configured": bool(settings.mongodb_uri and "your-username" not in settings.mongodb_uri),
        "next_steps": [
            "Add your .env file with MongoDB URI and OpenAI API key",
            "Test this endpoint to verify basic functionality"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "environment": settings.environment,
        "mongodb_uri_configured": bool(settings.mongodb_uri and settings.mongodb_uri != "mongodb+srv://your-username:your-password@your-cluster.mongodb.net/"),
        "openai_key_configured": bool(settings.openai_api_key and settings.openai_api_key != "your-openai-api-key-here")
    }

# Simple test endpoint
@app.get("/test")
async def test_endpoint():
    return {
        "message": "Basic FastAPI is working!",
        "settings": {
            "database_name": settings.database_name,
            "environment": settings.environment,
            "mongodb_configured": "Yes" if settings.mongodb_uri and "your-username" not in settings.mongodb_uri else "No - update .env file"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)