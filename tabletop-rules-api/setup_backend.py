#!/usr/bin/env python3
"""
Setup script for Tabletop Rules API Backend
This script helps verify and fix common setup issues.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(filepath):
    """Check if a file exists and return status."""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {filepath}")
    return exists

def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n📋 Checking .env configuration...")
    
    if not check_file_exists(".env"):
        print("⚠️  Creating sample .env file...")
        sample_env = """
# MongoDB Configuration
MONGODB_URI=mongodb+srv://your-username:your-password@your-cluster.mongodb.net/
DATABASE_NAME=tabletop_rules

# Authentication
SECRET_KEY=your-secret-key-change-this-in-production

# AI Service (optional for now)
OPENAI_API_KEY=sk-your-openai-key-here

# Environment
ENVIRONMENT=development
""".strip()
        
        with open(".env", "w") as f:
            f.write(sample_env)
        print("✅ Sample .env file created - please update with your values")
        return False
    
    # Check if .env has required variables
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["MONGODB_URI", "SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value or "your-" in value:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Please update these variables in .env: {', '.join(missing_vars)}")
        return False
    
    print("✅ .env file configured correctly")
    return True

def check_dependencies():
    """Check if all required dependencies are installed."""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "motor",
        "pymongo", 
        "python-dotenv",
        "pydantic",
        "passlib",
        "bcrypt",
        "python-jose",
        "python-frontmatter"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All dependencies installed")
    return True

def check_project_structure():
    """Check if all required files and directories exist."""
    print("\n📁 Checking project structure...")
    
    required_files = [
        "main.py",
        "app/__init__.py",
        "app/config.py",
        "app/database.py",
        "app/models.py",
        "app/services/__init__.py",
        "app/services/auth_service.py",
        "app/routes/__init__.py", 
        "app/routes/games.py",
        "app/routes/admin.py",
        "app/routes/chat.py"
    ]
    
    missing_files = []
    
    for filepath in required_files:
        if not check_file_exists(filepath):
            missing_files.append(filepath)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        return False
    
    print("✅ Project structure complete")
    return True

def test_imports():
    """Test if all imports work correctly."""
    print("\n🔍 Testing imports...")
    
    try:
        from app.config import settings
        print("✅ app.config")
    except ImportError as e:
        print(f"❌ app.config: {e}")
        return False
    
    try:
        from app.database import get_database
        print("✅ app.database")
    except ImportError as e:
        print(f"❌ app.database: {e}")
        return False
    
    try:
        from app.services.auth_service import create_access_token, verify_token
        print("✅ app.services.auth_service")
    except ImportError as e:
        print(f"❌ app.services.auth_service: {e}")
        return False
    
    try:
        from app.routes import games, admin, chat
        print("✅ app.routes")
    except ImportError as e:
        print(f"❌ app.routes: {e}")
        return False
    
    print("✅ All imports working")
    return True

def test_server_start():
    """Test if the server can start without errors."""
    print("\n🚀 Testing server startup...")
    
    try:
        # Try importing the main app
        import main
        print("✅ main.py imports successfully")
        
        # Check if app is defined
        if hasattr(main, 'app'):
            print("✅ FastAPI app created successfully")
            return True
        else:
            print("❌ FastAPI app not found in main.py")
            return False
            
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

def main():
    """Run all setup checks."""
    print("🎯 Tabletop Rules API Backend Setup Check")
    print("=" * 50)
    
    checks = [
        check_project_structure,
        check_dependencies,
        check_env_file,
        test_imports,
        test_server_start
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()  # Add spacing between checks
    
    print("=" * 50)
    print(f"📊 Setup Status: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your backend is ready to run.")
        print("\n🚀 To start the server:")
        print("uvicorn main:app --reload")
        print("\n📚 API Documentation:")
        print("http://localhost:8000/docs")
    else:
        print("⚠️  Please fix the issues above before starting the server.")
        print("\n📝 Common fixes:")
        print("1. pip install -r requirements.txt")
        print("2. Update your .env file with real values")
        print("3. Make sure all files are created with the correct content")

if __name__ == "__main__":
    main()