import os
import google.generativeai as genai

# Setup Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

TEMPLATES = {
    "Submitted": {
        "en": "Grievance received successfully. Tracking ID is {id}. AI agent is evaluating category and routing.",
        "hi": "शिकायत सफलतापूर्वक प्राप्त हुई। ट्रैकिंग आईडी {id} है। एआई एजेंट श्रेणी और विभाग मैपिंग का मूल्यांकन कर रहा है।"
    },
    "Assigned": {
        "en": "Your complaint has been assigned to {department}.",
        "hi": "आपकी शिकायत {department} को सौंप दी गई है।"
    },
    "In Progress": {
        "en": "Department team acknowledged the grievance. Investigation and on-site resolution are in progress.",
        "hi": "विभाग की टीम ने शिकायत स्वीकार कर ली है। जांच और ऑन-साइट समाधान प्रगति पर है।"
    },
    "Escalated": {
        "en": "Escalation Warning: Complaint escalated to District Magistrate / Commissioner's division due to delay.",
        "hi": "चेतावनी: समय सीमा पार होने के कारण शिकायत को जिलाधिकारी / आयुक्त मंडल स्तर पर अग्रेषित किया गया है।"
    },
    "Resolved": {
        "en": "Grievance resolved successfully. Resolution action verified by inspector: {action}",
        "hi": "शिकायत का समाधान सफलतापूर्वक हो गया है। निरीक्षक द्वारा सत्यापित कार्रवाई: {action}"
    }
}

def generate_vernacular_messages(status: str, details: dict) -> tuple:
    """
    Returns (message_en, message_hi) based on status and details.
    Uses Gemini API if available, else template lookups.
    """
    # Grab template defaults
    temp = TEMPLATES.get(status, TEMPLATES["Submitted"])
    d_id = details.get("id", "N/A")
    dept = details.get("department", "General Administration")
    action = details.get("action", "Standard action taken")
    
    default_en = temp["en"].format(id=d_id, department=dept, action=action)
    default_hi = temp["hi"].format(id=d_id, department=dept, action=action)
    
    if not api_key:
        return default_en, default_hi
        
    prompt = f"""
    You are an AI Communications officer for the Government.
    Your task is to write a citizen-friendly SMS update for a grievance.
    Status of grievance: {status}
    Ticket ID: {d_id}
    Department: {dept}
    Additional details/actions: {action}
    
    Write two brief SMS messages (under 160 characters each):
    1. In plain English (clear, professional)
    2. In clear Hindi (vernacular, easily understood by common citizens in UP, using Devanagari script)
    
    You must output exactly two lines and nothing else:
    EN: [English message here]
    HI: [Hindi message here]
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        lines = response.text.strip().split("\n")
        
        en_msg, hi_msg = default_en, default_hi
        for line in lines:
            if line.upper().startswith("EN:"):
                en_msg = line[3:].strip()
            elif line.upper().startswith("HI:"):
                hi_msg = line[3:].strip()
                
        return en_msg, hi_msg
    except Exception as e:
        print(f"Gemini Translation Exception, using template: {e}")
        return default_en, default_hi
