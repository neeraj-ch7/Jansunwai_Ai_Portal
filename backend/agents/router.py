import random
from sqlalchemy.orm import Session
from database import StatusLog

def generate_ticket_id() -> str:
    """Generate a unique 6-digit ticket reference."""
    return f"TKT-{random.randint(100000, 999999)}"

def route_complaint(db_session: Session, complaint_id: str, category: str, department: str, reasoning: str):
    """
    Simulates routing action:
    Generates a log entry showing successful routing to the assigned department.
    """
    message_en = f"Grievance auto-classified under '{category}' and routed to '{department}'."
    message_hi = f"शिकायत को '{category}' के अंतर्गत वर्गीकृत किया गया है और '{department}' को अग्रेषित किया गया है।"
    
    log_entry = StatusLog(
        complaint_id=complaint_id,
        status="Assigned",
        message_en=message_en,
        message_hi=message_hi,
        agent_reasoning=reasoning
    )
    db_session.add(log_entry)
    db_session.commit()
    return message_en
