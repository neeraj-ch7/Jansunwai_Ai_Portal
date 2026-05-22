from datetime import datetime
from sqlalchemy.orm import Session
from database import Complaint, StatusLog
from agents.vernacular import generate_vernacular_messages

def check_and_escalate_complaints(db: Session) -> list:
    """
    Simulates checks for delay thresholds and auto-escalates.
    Returns a list of ticket IDs that were escalated.
    """
    escalated_tickets = []
    now = datetime.utcnow()
    
    # We load all complaints that are not resolved and not already escalated
    active_complaints = db.query(Complaint).filter(
        Complaint.status.in_(["Assigned", "In Progress"])
    ).all()
    
    for complaint in active_complaints:
        # Calculate mock delay in days
        delta = now - complaint.created_at
        days_old = delta.days
        
        should_escalate = False
        reason = ""
        
        if complaint.priority == "High" and days_old >= 3:
            should_escalate = True
            reason = f"High priority grievance exceeded 3-day SLA (Age: {days_old} days) without resolution."
        elif complaint.priority == "Medium" and days_old >= 7:
            should_escalate = True
            reason = f"Medium priority grievance exceeded 7-day SLA (Age: {days_old} days) without resolution."
        elif complaint.priority == "Low" and days_old >= 14:
            should_escalate = True
            reason = f"Low priority grievance exceeded 14-day SLA (Age: {days_old} days) without resolution."
            
        if should_escalate:
            complaint.status = "Escalated"
            complaint.updated_at = now
            
            # Generate logs
            details = {
                "id": complaint.id,
                "department": complaint.department,
                "action": "Escalated to Special Desk Officer"
            }
            msg_en, msg_hi = generate_vernacular_messages("Escalated", details)
            
            log = StatusLog(
                complaint_id=complaint.id,
                status="Escalated",
                message_en=msg_en,
                message_hi=msg_hi,
                agent_reasoning=f"Autonomous Escalation Engine triggered: {reason}",
                created_at=now
            )
            db.add(log)
            escalated_tickets.append(complaint.id)
            
    if escalated_tickets:
        db.commit()
        
    return escalated_tickets
