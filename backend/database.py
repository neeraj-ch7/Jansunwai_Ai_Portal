import os
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./jansathi.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Complaint(Base):
    __tablename__ = "complaints"
    
    id = Column(String, primary_key=True, index=True) # e.g. TKT-123456
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    location = Column(String, nullable=False)
    category = Column(String, nullable=True)
    department = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    status = Column(String, default="Submitted") # Submitted, Assigned, In Progress, Escalated, Resolved
    preferred_language = Column(String, default="en") # en, hi
    image_data = Column(Text, nullable=True) # Base64 image data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class StatusLog(Base):
    __tablename__ = "status_logs"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    complaint_id = Column(String, ForeignKey("complaints.id"), index=True)
    status = Column(String, nullable=False)
    message_en = Column(Text, nullable=False)
    message_hi = Column(Text, nullable=False)
    agent_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
    seed_data()

def seed_data():
    db = SessionLocal()
    # Check if we already have complaints
    if db.query(Complaint).count() > 0:
        db.close()
        return

    # Seed list of departments and sample complaints
    sample_complaints = [
        {
            "id": "TKT-582910",
            "title": "Low hanging power lines posing danger",
            "description": "High voltage electricity wires are hanging very low near the playground in Gomti Nagar Sector 3. It is extremely hazardous for children playing in the park. Please tighten them immediately.",
            "location": "Gomti Nagar, Lucknow",
            "category": "Electricity",
            "department": "State Electricity Distribution Corporation (UPPCL)",
            "priority": "High",
            "sentiment": "Frustrated",
            "summary": "High voltage electricity wires hanging low near playground in Gomti Nagar park, posing danger to children.",
            "status": "Escalated",
            "preferred_language": "hi",
            "age_days": 5
        },
        {
            "id": "TKT-192837",
            "title": "Severe garbage accumulation and foul smell",
            "description": "Uncontrolled heap of waste has accumulated in Sector 12 near the main market. Municipal staff has not visited for a week. Strays are scattering the trash, and it smells terrible.",
            "location": "Sector 12, Noida",
            "category": "Sanitation",
            "department": "Municipal Solid Waste & Sanitation Division",
            "priority": "Medium",
            "sentiment": "Angry",
            "summary": "Garbage dump accumulated in Noida Sector 12 market with no municipal pickup for a week, causing foul odors.",
            "status": "In Progress",
            "preferred_language": "hi",
            "age_days": 2
        },
        {
            "id": "TKT-847291",
            "title": "Yellow muddy water supplied in mornings",
            "description": "For the past three days, the tap water supplied in the morning has a yellowish color and contains mud particles. We cannot drink or cook with it.",
            "location": "Kakadeo, Kanpur",
            "category": "Water Supply",
            "department": "Jal Sansthan (Water Board)",
            "priority": "High",
            "sentiment": "Anxious",
            "summary": "Tap water supply contains mud and yellow discolouration in Kakadeo area for three consecutive days.",
            "status": "Submitted",
            "preferred_language": "en",
            "age_days": 0
        },
        {
            "id": "TKT-463829",
            "title": "Massive potholes on main crossing road",
            "description": "The main crossing near Hazratganj has developed huge potholes after the rains. Multiple motorists have fallen off their two-wheelers. Urgent repair required.",
            "location": "Hazratganj, Lucknow",
            "category": "Roads",
            "department": "Public Works Department (PWD)",
            "priority": "High",
            "sentiment": "Angry",
            "summary": "Hazardous large potholes at Hazratganj crossing following rain, causing vehicle accidents.",
            "status": "Resolved",
            "preferred_language": "hi",
            "age_days": 8
        },
        {
            "id": "TKT-304958",
            "title": "Street lights not functioning for 2 weeks",
            "description": "The entire lane of Block B has non-functional street lights. It gets completely dark by 7 PM, making it unsafe for residents and senior citizens walking in the evening.",
            "location": "Indira Nagar, Lucknow",
            "category": "Electricity",
            "department": "State Electricity Distribution Corporation (UPPCL)",
            "priority": "Medium",
            "sentiment": "Neutral",
            "summary": "Streetlights off for two weeks in Indira Nagar Block B lane, causing safety concerns.",
            "status": "Assigned",
            "preferred_language": "en",
            "age_days": 3
        },
        {
            "id": "TKT-758493",
            "title": "Sewer overflow onto main road",
            "description": "A manhole is overflowing constantly near the government primary school. The dirty water is flooding the street, and children have to step through it to enter school.",
            "location": "Aliganj, Lucknow",
            "category": "Sanitation",
            "department": "Municipal Solid Waste & Sanitation Division",
            "priority": "High",
            "sentiment": "Frustrated",
            "summary": "Sewer leakage and overflow near public school in Aliganj, flooding the street.",
            "status": "In Progress",
            "preferred_language": "hi",
            "age_days": 1
        }
    ]

    for item in sample_complaints:
        age_days = item.pop("age_days")
        created_time = datetime.utcnow() - timedelta(days=age_days)
        complaint = Complaint(
            **item,
            created_at=created_time,
            updated_at=created_time
        )
        db.add(complaint)
        
        # Log history
        # Create Submitted Log
        submit_time = created_time
        db.add(StatusLog(
            complaint_id=complaint.id,
            status="Submitted",
            message_en=f"Grievance filed successfully. Tracking ID: {complaint.id}",
            message_hi=f"शिकायत सफलतापूर्वक दर्ज कर ली गई है। ट्रैकिंग आईडी: {complaint.id}",
            agent_reasoning="AI classification triggered on ingestion. Intent classified as public infrastructure grievance.",
            created_at=submit_time
        ))

        # Create Assigned Log
        if complaint.status in ["Assigned", "In Progress", "Escalated", "Resolved"]:
            assign_time = created_time + timedelta(hours=2)
            db.add(StatusLog(
                complaint_id=complaint.id,
                status="Assigned",
                message_en=f"Assigned to {complaint.department} for investigation.",
                message_hi=f"जांच के लिए इसे {complaint.department} को सौंप दिया गया है।",
                agent_reasoning=f"Routing Agent automatically mapped category '{complaint.category}' to '{complaint.department}'.",
                created_at=assign_time
            ))

        # Create In Progress Log
        if complaint.status in ["In Progress", "Escalated", "Resolved"]:
            progress_time = created_time + timedelta(days=1)
            db.add(StatusLog(
                complaint_id=complaint.id,
                status="In Progress",
                message_en=f"Official field investigation initiated. Officer assigned to site.",
                message_hi=f"आधिकारिक मैदानी जांच शुरू की गई। अधिकारी को स्थल पर नियुक्त किया गया है।",
                agent_reasoning="Follow-up Agent recorded acknowledgement from local division desk.",
                created_at=progress_time
            ))

        # Create Escalated Log
        if complaint.status == "Escalated":
            escalation_time = created_time + timedelta(days=4)
            db.add(StatusLog(
                complaint_id=complaint.id,
                status="Escalated",
                message_en="Escalated to Division Commissioner due to delay in resolution.",
                message_hi="नियत समय में समाधान न होने के कारण संभागीय आयुक्त को शिकायत अग्रेषित की गई है।",
                agent_reasoning="Escalation trigger: High priority ticket remained in progress for more than 72 hours.",
                created_at=escalation_time
            ))

        # Create Resolved Log
        if complaint.status == "Resolved":
            resolved_time = created_time + timedelta(days=3)
            db.add(StatusLog(
                complaint_id=complaint.id,
                status="Resolved",
                message_en="Resolution complete. Potholes filled and road patch repair verified by inspector.",
                message_hi=f"समाधान पूरा हो गया है। गड्ढों को भर दिया गया है और निरीक्षक द्वारा सड़क मरम्मत का सत्यापन किया गया है।",
                agent_reasoning="Resolution agent confirmed closure with site photos upload and inspector clearance.",
                created_at=resolved_time
            ))

    db.commit()
    db.close()
