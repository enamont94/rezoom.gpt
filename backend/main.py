from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv
import sqlite3
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Import route modules
from routes.parse import router as parse_router
from routes.transform import router as transform_router
from routes.ats_score import router as ats_score_router
from routes.export import router as export_router
from routes.email import router as email_router
from routes.activity import router as activity_router

# Initialize FastAPI app
app = FastAPI(
    title="Rezoom.ai API",
    description="AI Resume Builder that Beats the ATS Filters",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://rezoom.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(parse_router, prefix="/api/parse", tags=["parse"])
app.include_router(transform_router, prefix="/api/transform", tags=["transform"])
app.include_router(ats_score_router, prefix="/api/ats-score", tags=["ats-score"])
app.include_router(export_router, prefix="/api/export", tags=["export"])
app.include_router(email_router, prefix="/api/email", tags=["email"])
app.include_router(activity_router, prefix="/api/activity", tags=["activity"])

# Database initialization
def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('db/rezoom.db')
    cursor = conn.cursor()
    
    # Create user_activity table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            job_title TEXT,
            ats_score INTEGER,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create resume_cache table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            original_text TEXT,
            optimized_text TEXT,
            job_description TEXT,
            tone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and create necessary directories"""
    # Create directories
    os.makedirs("db", exist_ok=True)
    os.makedirs("tmp", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    
    # Initialize database
    init_db()
    
    print("🚀 Rezoom.ai API is ready!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("👋 Rezoom.ai API shutting down...")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Rezoom.ai API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# API status endpoint
@app.get("/api/status")
async def api_status():
    """Get API status and system information"""
    return {
        "status": "operational",
        "version": "1.0.0",
        "features": [
            "Resume parsing (PDF/DOCX)",
            "AI-powered optimization",
            "ATS scoring",
            "PDF generation",
            "Email delivery"
        ],
        "ai_model": "Mistral (via Ollama)",
        "database": "SQLite",
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
