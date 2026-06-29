from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
import os
import asyncio
import traceback
import logging
from dotenv import load_dotenv
from sqlalchemy.orm import Session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from aws_scanner import AWSScanner
from groq_analyzer import GroqAnalyzer
from db import init_db, get_db, User, Analysis
from auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, authenticate_user
)

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="AI Cloud Cost Detective API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()


class AnalyzeRequest(BaseModel):
    region: str = "us-east-1"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Common AWS regions
AWS_REGIONS = [
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
    "eu-west-1",
    "eu-west-2",
    "eu-west-3",
    "eu-central-1",
    "ap-south-1",
    "ap-northeast-1",
    "ap-northeast-2",
    "ap-southeast-1",
    "ap-southeast-2",
    "ca-central-1",
    "sa-east-1",
]

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, analysis_id: str):
        await websocket.accept()
        self.active_connections[analysis_id] = websocket
    
    def disconnect(self, analysis_id: str):
        if analysis_id in self.active_connections:
            del self.active_connections[analysis_id]
    
    async def send_message(self, analysis_id: str, message: str):
        if analysis_id in self.active_connections:
            try:
                await self.active_connections[analysis_id].send_text(message)
            except:
                self.disconnect(analysis_id)

manager = ConnectionManager()


@app.get("/api/regions")
def get_regions():
    """Return list of common AWS regions"""
    return {"regions": AWS_REGIONS}


# Auth endpoints
@app.post("/api/auth/signup")
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    """Create a new user account"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(request.password)
    new_user = User(email=request.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": new_user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": new_user.id,
            "email": new_user.email
        }
    }


@app.post("/api/auth/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Login and get access token"""
    user = authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }


@app.get("/api/auth/me")
def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "created_at": current_user.created_at.isoformat()
    }


@app.post("/api/analyze")
async def analyze_resources(request: AnalyzeRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Scan AWS resources in the specified region and analyze them for cost optimization
    Returns resource data and AI-powered cost analysis
    Stores results in database and sends progress via WebSocket
    """
    # Validate region
    if request.region not in AWS_REGIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid region '{request.region}'. Must be one of: {', '.join(AWS_REGIONS)}"
        )
    
    # Create analysis record
    analysis = Analysis(
        user_id=current_user.id,
        region=request.region,
        status="pending"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    analysis_id = str(analysis.id)
    
    # Start analysis in background
    asyncio.create_task(run_analysis(analysis_id, request.region, current_user.id))
    
    return {
        "analysis_id": analysis_id,
        "status": "pending",
        "message": "Analysis started"
    }


async def run_analysis(analysis_id: str, region: str, user_id: int):
    db = next(get_db())
    try:
        analysis = db.query(Analysis).filter(Analysis.id == int(analysis_id)).first()
        if not analysis:
            logger.error(f"Analysis {analysis_id} not found in database")
            return
            
        analysis.status = "running"
        db.commit()
        
        await manager.send_message(analysis_id, "Connecting to AWS...")
        await manager.send_message(analysis_id, f"Scanning AWS resources in {region}...")
        
        scanner = AWSScanner(region=region)
        results = scanner.scan_all()
        
        all_resources = []
        for resource_type, resources in results.items():
            all_resources.extend(resources)
        
        await manager.send_message(analysis_id, "Analyzing costs with Groq AI...")
        analyzer = GroqAnalyzer()
        try:
            ai_analysis = analyzer.analyze_resources(all_resources, region)
        except Exception as e:
            logger.error(f"Groq analysis failed: {str(e)}")
            ai_analysis = {
                "summary": f"AI analysis unavailable: {str(e)}",
                "total_estimated_monthly_savings": 0,
                "issues": []
            }
        
        await manager.send_message(analysis_id, "Storing results in database...")
        analysis.resources_scanned = len(all_resources)
        analysis.issues_found = len(ai_analysis.get("issues", []))
        analysis.estimated_savings = float(ai_analysis.get("total_estimated_monthly_savings", 0))
        analysis.analysis_result = ai_analysis
        analysis.status = "completed"
        db.commit()
        
        await manager.send_message(analysis_id, "Analysis complete")
        logger.info(f"Analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {str(e)}")
        logger.error(traceback.format_exc())
        try:
            analysis = db.query(Analysis).filter(Analysis.id == int(analysis_id)).first()
            if analysis:
                analysis.status = "failed"
                db.commit()
        except:
            pass
        await manager.send_message(analysis_id, f"Analysis failed: {str(e)}")
    finally:
        db.close()


@app.get("/api/history")
def get_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get analysis history for the authenticated user"""
    analyses = db.query(Analysis).filter(
        Analysis.user_id == current_user.id
    ).order_by(Analysis.created_at.desc()).all()
    
    return {
        "analyses": [
            {
                "id": a.id,
                "region": a.region,
                "resources_scanned": a.resources_scanned,
                "issues_found": a.issues_found,
                "estimated_savings": a.estimated_savings,
                "status": a.status,
                "created_at": a.created_at.isoformat(),
                "summary": a.analysis_result.get("summary") if a.analysis_result else None
            }
            for a in analyses
        ]
    }


@app.get("/api/analysis/{analysis_id}")
def get_analysis(analysis_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed analysis by ID"""
    analysis = db.query(Analysis).filter(
        Analysis.id == analysis_id,
        Analysis.user_id == current_user.id
    ).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "id": analysis.id,
        "region": analysis.region,
        "resources_scanned": analysis.resources_scanned,
        "issues_found": analysis.issues_found,
        "estimated_savings": analysis.estimated_savings,
        "status": analysis.status,
        "created_at": analysis.created_at.isoformat(),
        "analysis_result": analysis.analysis_result
    }


@app.websocket("/ws/progress/{analysis_id}")
async def websocket_progress(websocket: WebSocket, analysis_id: str):
    """WebSocket endpoint for live progress updates"""
    await manager.connect(websocket, analysis_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(analysis_id)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "AI Cloud Cost Detective API",
        "endpoints": {
            "regions": "/api/regions",
            "auth_signup": "/api/auth/signup",
            "auth_login": "/api/auth/login",
            "auth_me": "/api/auth/me",
            "analyze": "/api/analyze",
            "history": "/api/history",
            "analysis": "/api/analysis/{analysis_id}",
            "websocket": "/ws/progress/{analysis_id}"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
