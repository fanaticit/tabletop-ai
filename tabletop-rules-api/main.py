# main.py - Truly minimal working version (no routes yet)
import os
from dotenv import load_dotenv

# Load environment variables before any other imports
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import asyncio
from contextlib import asynccontextmanager
from datetime import timedelta

# Import routes and auth
from app.database import connect_to_mongo, close_mongo_connection
from app.config import settings
from app.routes import games, admin, chat
from app.services.auth_service import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token

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
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Database connection
client = None
database = None

@app.on_event("startup")
async def startup_db_client():
    global client, database
    client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
    database = client[os.getenv("DATABASE_NAME", "tabletop_rules")]

@app.on_event("shutdown") 
async def shutdown_db_client():
    if client:
        client.close()

async def get_database() -> AsyncIOMotorDatabase:
    return database

# Authentication setup
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token."""
    try:
        payload = verify_token(token)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"username": username}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth endpoints
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Legacy token endpoint for OAuth2 compatibility."""
    # Simple admin authentication for demo
    if form_data.username == "admin" and form_data.password == "secret":
        access_token = create_access_token(data={"sub": form_data.username})
        return {
            "access_token": access_token, 
            "token_type": "bearer",
            "user": {
                "id": "admin",
                "username": "admin",
                "email": "admin@example.com"
            }
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@app.post("/api/auth/register")
async def register_user(user_data: dict, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Register a new user."""
    from passlib.context import CryptContext
    from datetime import datetime
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        # Validate required fields
        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if not user_data.get(field):
                raise HTTPException(
                    status_code=400,
                    detail=f"{field.capitalize()} is required"
                )
        
        # Check if user already exists
        existing_user = await db.users.find_one({
            "$or": [
                {"username": user_data["username"]},
                {"email": user_data["email"]}
            ]
        })
        
        if existing_user:
            if existing_user["username"] == user_data["username"]:
                raise HTTPException(status_code=400, detail="Username already exists")
            else:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password
        hashed_password = pwd_context.hash(user_data["password"])
        
        # Create user document
        user_doc = {
            "username": user_data["username"],
            "email": user_data["email"],
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "preferences": {
                "selected_game_id": None,
                "theme": "light"
            }
        }
        
        # Insert user
        result = await db.users.insert_one(user_doc)
        
        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": str(result.inserted_id),
                "username": user_data["username"],
                "email": user_data["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/api/auth/login")
async def login_user(login_data: dict, db: AsyncIOMotorDatabase = Depends(get_database)):
    """Login user with username/password."""
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    try:
        username = login_data.get("username")
        password = login_data.get("password")
        
        if not username or not password:
            raise HTTPException(status_code=400, detail="Username and password required")
        
        # Find user in database
        user = await db.users.find_one({"username": username})
        
        if not user or not pwd_context.verify(password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create access token
        access_token = create_access_token(data={"sub": username})
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user["_id"]),
                "username": user["username"],
                "email": user["email"]
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

# Include routers
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Health check
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
    try:
        # Test database connection
        await database.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

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