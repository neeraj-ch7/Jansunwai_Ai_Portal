import os
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

# Load env variables
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    masked_key = api_key[:7] + "..." + api_key[-4:] if len(api_key) > 10 else "..."
    print(f"\n🟢 [Jansathi AI Engine] Loaded GEMINI_API_KEY ({masked_key}) successfully.")
    print("🟢 [Jansathi AI Engine] Multimodal Classifier fully active!\n")
else:
    print("\n⚠️  [Jansathi AI Engine] GEMINI_API_KEY not found in .env! Local rule heuristics loaded.\n")

from database import engine, SessionLocal, init_db, Complaint, StatusLog
from agents.classifier import classify_complaint
from agents.router import generate_ticket_id, route_complaint
from agents.vernacular import generate_vernacular_messages
from agents.escalator import check_and_escalate_complaints

# Initialize Database tables and seeds
init_db()

app = FastAPI(title="Jansathi AI Backend", version="1.0.0")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Open for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class ComplaintCreate(BaseModel):
    title: str
    description: str
    location: str
    preferred_language: str = "en"
    image_data: Optional[str] = None

class StatusUpdate(BaseModel):
    status: str # In Progress, Resolved
    action_taken: Optional[str] = None

class ComplaintResponse(BaseModel):
    id: str
    title: str
    description: str
    location: str
    category: Optional[str]
    department: Optional[str]
    priority: Optional[str]
    sentiment: Optional[str]
    summary: Optional[str]
    status: str
    preferred_language: str
    image_data: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LogResponse(BaseModel):
    id: int
    complaint_id: str
    status: str
    message_en: str
    message_hi: str
    agent_reasoning: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ComplaintDetailResponse(BaseModel):
    complaint: ComplaintResponse
    history: List[LogResponse]

# API Endpoints
@app.post("/api/complaints", response_model=ComplaintResponse)
def create_complaint_endpoint(data: ComplaintCreate, db: Session = Depends(get_db)):
    """
    Submits a new citizen grievance.
    1. Generates Ticket ID.
    2. Runs AI Agent to Classify (Category, Dept, Priority, Summary, Sentiment).
    3. Saves record.
    4. Logs ingestion.
    5. Routes automatically (creates 'Assigned' log).
    """
    ticket_id = generate_ticket_id()
    
    # Run AI Classification Agent
    ai_results = classify_complaint(data.title, data.description, data.image_data)
    
    now = datetime.utcnow()
    new_complaint = Complaint(
        id=ticket_id,
        title=data.title,
        description=data.description,
        location=data.location,
        category=ai_results.get("category", "Other"),
        department=ai_results.get("department", "General Administration Department"),
        priority=ai_results.get("priority", "Medium"),
        sentiment=ai_results.get("sentiment", "Neutral"),
        summary=ai_results.get("summary", data.title),
        status="Submitted",
        preferred_language=data.preferred_language,
        image_data=data.image_data,
        created_at=now,
        updated_at=now
    )
    
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    
    # Log Submission history
    details = {"id": ticket_id, "department": new_complaint.department}
    msg_en, msg_hi = generate_vernacular_messages("Submitted", details)
    
    submit_log = StatusLog(
        complaint_id=ticket_id,
        status="Submitted",
        message_en=msg_en,
        message_hi=msg_hi,
        agent_reasoning="Citizen submission captured. File upload verified (if any). Real-time ingestion complete.",
        created_at=now
    )
    db.add(submit_log)
    db.commit()
    
    # Auto-Route (Changes state to Assigned immediately for demo purposes)
    new_complaint.status = "Assigned"
    db.commit()
    
    route_complaint(
        db_session=db,
        complaint_id=ticket_id,
        category=new_complaint.category,
        department=new_complaint.department,
        reasoning=ai_results.get("reasoning", "Autonomous routing triggered by classification metadata.")
    )
    
    return new_complaint

@app.get("/api/complaints", response_model=List[ComplaintResponse])
def get_complaints(
    search: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List complaints with filters for admin dashboard search."""
    query = db.query(Complaint)
    
    if search:
        query = query.filter(
            (Complaint.title.like(f"%{search}%")) |
            (Complaint.description.like(f"%{search}%")) |
            (Complaint.id.like(f"%{search}%")) |
            (Complaint.location.like(f"%{search}%"))
        )
    if category:
        query = query.filter(Complaint.category == category)
    if status:
        query = query.filter(Complaint.status == status)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if department:
        query = query.filter(Complaint.department == department)
        
    return query.order_by(Complaint.created_at.desc()).all()

@app.get("/api/complaints/{complaint_id}", response_model=ComplaintDetailResponse)
def get_complaint_details(complaint_id: str, db: Session = Depends(get_db)):
    """Retrieve full details of a single ticket along with its history log."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    history = db.query(StatusLog).filter(
        StatusLog.complaint_id == complaint_id
    ).order_by(StatusLog.created_at.asc()).all()
    
    return {"complaint": complaint, "history": history}

@app.post("/api/complaints/{complaint_id}/status", response_model=ComplaintResponse)
def update_complaint_status(complaint_id: str, data: StatusUpdate, db: Session = Depends(get_db)):
    """Allows admins to move complaints to 'In Progress' or 'Resolved' states manually."""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
        
    if data.status not in ["In Progress", "Resolved", "Escalated"]:
        raise HTTPException(status_code=400, detail="Invalid status transition")
        
    now = datetime.utcnow()
    complaint.status = data.status
    complaint.updated_at = now
    
    details = {
        "id": complaint.id,
        "department": complaint.department,
        "action": data.action_taken or "Administrative status update"
    }
    
    # Generate messages in vernacular
    msg_en, msg_hi = generate_vernacular_messages(data.status, details)
    
    log = StatusLog(
        complaint_id=complaint_id,
        status=data.status,
        message_en=msg_en,
        message_hi=msg_hi,
        agent_reasoning=f"Manual action logged by department administrator. Detail: {data.action_taken or 'None'}",
        created_at=now
    )
    
    db.add(log)
    db.commit()
    db.refresh(complaint)
    
    return complaint

@app.post("/api/simulate-tick")
def simulate_timeline_tick(db: Session = Depends(get_db)):
    """
    Cron simulation helper:
    1. Ages all non-resolved complaints by 2 days.
    2. Runs follow-up agent to check and trigger auto-escalations.
    """
    complaints = db.query(Complaint).filter(Complaint.status != "Resolved").all()
    for comp in complaints:
        # Subtract 2 days from creation to simulate time lapse
        comp.created_at = comp.created_at - timedelta(days=2)
        
    db.commit()
    
    # Trigger autonomous escalator checks
    escalated_ids = check_and_escalate_complaints(db)
    
    return {
        "message": f"Time simulated forward by 2 days. Processed {len(complaints)} complaints.",
        "escalated_count": len(escalated_ids),
        "escalated_tickets": escalated_ids
    }

@app.get("/api/stats")
def get_dashboard_statistics(department: Optional[str] = None, db: Session = Depends(get_db)):
    """Computes stats and chart data for the Admin Dashboard."""
    query = db.query(Complaint)
    if department:
        query = query.filter(Complaint.department == department)
        
    total = query.count()
    pending = query.filter(Complaint.status != "Resolved").count()
    resolved = query.filter(Complaint.status == "Resolved").count()
    escalated = query.filter(Complaint.status == "Escalated").count()
    
    # Category distribution
    categories = ["Sanitation", "Water Supply", "Electricity", "Roads", "Health", "Public Safety", "Other"]
    cat_counts = {}
    for c in categories:
        cat_query = db.query(Complaint).filter(Complaint.category == c)
        if department:
            cat_query = cat_query.filter(Complaint.department == department)
        cat_counts[c] = cat_query.count()
        
    # Priority counts
    priorities = ["High", "Medium", "Low"]
    prio_counts = {}
    for p in priorities:
        prio_query = db.query(Complaint).filter(Complaint.priority == p)
        if department:
            prio_query = prio_query.filter(Complaint.department == department)
        prio_counts[p] = prio_query.count()
        
    # Average resolution time estimate
    # Simple simulation calculation: average difference of resolved complaints
    res_query = db.query(Complaint).filter(Complaint.status == "Resolved")
    if department:
        res_query = res_query.filter(Complaint.department == department)
    resolved_tickets = res_query.all()
    avg_hours = 0
    if resolved_tickets:
        durations = []
        for t in resolved_tickets:
            diff = t.updated_at - t.created_at
            durations.append(diff.total_seconds() / 3600.0)
        avg_hours = sum(durations) / len(durations)
    else:
        avg_hours = 36.5 # Demo placeholder average
        
    return {
        "total_complaints": total,
        "pending_complaints": pending,
        "resolved_complaints": resolved,
        "escalated_complaints": escalated,
        "category_data": cat_counts,
        "priority_data": prio_counts,
        "avg_resolution_hours": round(avg_hours, 1)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
