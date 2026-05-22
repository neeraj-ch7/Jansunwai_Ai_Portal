import os
import json
import re
import base64
import google.generativeai as genai

# Setup Gemini API key
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def decode_base64_image(image_data: str) -> dict:
    """
    Parses a base64 image data URI string and returns a dictionary
    with raw binary data and the appropriate mime_type for the Gemini API.
    """
    if not image_data:
        return None
    try:
        pattern = r"^data:(image\/[a-zA-Z+.-]+);base64,(.+)$"
        match = re.match(pattern, image_data)
        if match:
            mime_type = match.group(1)
            base64_data = match.group(2)
            raw_bytes = base64.b64decode(base64_data)
            return {"mime_type": mime_type, "data": raw_bytes}
    except Exception as e:
        print(f"Error decoding base64 image: {e}")
    return None

DEPARTMENTS = {
    "Sanitation": "Municipal Solid Waste & Sanitation Division",
    "Water Supply": "Jal Sansthan (Water Board)",
    "Electricity": "State Electricity Distribution Corporation (UPPCL)",
    "Roads": "Public Works Department (PWD)",
    "Health": "Chief Medical Officer (CMO) Office",
    "Public Safety": "Local Police & Traffic Control",
    "Other": "General Administration Department"
}

def clean_json_string(text):
    """Strip code blocks and formatting from JSON response."""
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def fallback_classify(title: str, description: str) -> dict:
    """Keyword-based classification fallback when API key is missing."""
    text = (title + " " + description).lower()
    
    # Priority defaults to Low
    priority = "Low"
    category = "Other"
    sentiment = "Neutral"
    
    # Simple heuristics
    if any(k in text for k in ["power", "electricity", "voltage", "current", "wire", "light", "transformer", "uppcl", "meter"]):
        category = "Electricity"
    elif any(k in text for k in ["water", "sewer", "drain", "drainage", "overflow", "leak", "pipe", "tap", "jal"]):
        # Disambiguate water vs sewage
        if any(k in text for k in ["sewer", "drain", "drainage", "overflow"]):
            category = "Sanitation"
        else:
            category = "Water Supply"
    elif any(k in text for k in ["garbage", "trash", "clean", "sweeper", "dustbin", "waste", "filth", "dump", "smell"]):
        category = "Sanitation"
    elif any(k in text for k in ["road", "pothole", "highway", "street", "repair", "tar", "asphalt", "pwd"]):
        category = "Roads"
    elif any(k in text for k in ["hospital", "doctor", "health", "disease", "medicine", "dengue", "malaria", "cmo", "clinic"]):
        category = "Health"
    elif any(k in text for k in ["police", "safety", "theft", "harassment", "danger", "crime", "robbery", "scam"]):
        category = "Public Safety"
        
    # Urgency keyword indicators for Priority
    if any(k in text for k in ["danger", "hazard", "life", "accident", "emergency", "immediate", "urgent", "sparking", "child", "injured"]):
        priority = "High"
    elif any(k in text for k in ["broken", "leak", "week", "days", "blocked", "foul", "fever"]):
        priority = "Medium"
        
    # Sentiment heuristics
    if any(k in text for k in ["worst", "angry", "terrible", "useless", "disaster", "impossible"]):
        sentiment = "Angry"
    elif any(k in text for k in ["frustrated", "delay", "waiting", "please help", "sad"]):
        sentiment = "Frustrated"
    elif any(k in text for k in ["scared", "fear", "unsafe", "threat"]):
        sentiment = "Anxious"
        
    department = DEPARTMENTS.get(category, DEPARTMENTS["Other"])
    
    # Create brief summary (first 80 chars + ...)
    summary = title if len(title) < 80 else title[:80] + "..."
    
    return {
        "category": category,
        "department": department,
        "priority": priority,
        "sentiment": sentiment,
        "summary": f"[Local Heuristic] {summary}",
        "reasoning": f"Local rule-based agent analyzed keyword markers for '{category}' and priority '{priority}'."
    }

def classify_complaint(title: str, description: str, image_data: str = None) -> dict:
    """Classify the complaint category, department, priority, sentiment, and summary."""
    if not api_key:
        return fallback_classify(title, description)
        
    prompt = f"""
    You are an expert AI Classifier for the Indian Government's Jansunwai Grievance portal.
    Analyze the following grievance:
    Title: {title}
    Description: {description}
    
    Categorize it into one of these: Sanitation, Water Supply, Electricity, Roads, Health, Public Safety, Other.
    Assign the appropriate department from the following map:
    - Sanitation -> Municipal Solid Waste & Sanitation Division
    - Water Supply -> Jal Sansthan (Water Board)
    - Electricity -> State Electricity Distribution Corporation (UPPCL)
    - Roads -> Public Works Department (PWD)
    - Health -> Chief Medical Officer (CMO) Office
    - Public Safety -> Local Police & Traffic Control
    - Other -> General Administration Department
    
    Determine priority (High, Medium, Low) based on public safety, duration, and severity.
    Analyze citizen's sentiment (Angry, Frustrated, Anxious, Neutral, Hopeful).
    Provide a concise, 1-sentence executive summary of the issue.
    Explain the reasoning behind your decisions in a brief paragraph.
    
    You MUST respond with a valid JSON object ONLY. Do not include any other markdown formatting outside of JSON.
    Format your response EXACTLY like this:
    {{
      "category": "CategoryName",
      "department": "DepartmentName",
      "priority": "High/Medium/Low",
      "sentiment": "SentimentName",
      "summary": "Short 1-sentence summary",
      "reasoning": "Explain the category and priority reasoning"
    }}
    """
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Build contents array for multimodal request
        contents = []
        img_dict = decode_base64_image(image_data)
        if img_dict:
            contents.append(img_dict)
            photo_note = "\n\nCRITICAL: A supporting photo has been uploaded with this grievance. Carefully analyze this image along with the text details. Verify whether the image visually corresponds to the citizen's text description (e.g. validating a sparking wire, pothole, overflowing garbage, or low-hanging power line). Reference this image analysis directly in your 'reasoning' response field to confirm visual verification."
            contents.append(prompt + photo_note)
        else:
            contents.append(prompt)
            
        response = model.generate_content(contents)
        cleaned_text = clean_json_string(response.text)
        data = json.loads(cleaned_text)
        # Ensure fallback safety for keys
        data["category"] = data.get("category", "Other")
        data["department"] = DEPARTMENTS.get(data["category"], DEPARTMENTS["Other"])
        data["priority"] = data.get("priority", "Medium")
        data["sentiment"] = data.get("sentiment", "Neutral")
        data["summary"] = data.get("summary", title[:100])
        data["reasoning"] = data.get("reasoning", "Classified using Gemini AI model.")
        return data
    except Exception as e:
        print(f"Gemini API Exception, falling back: {e}")
        return fallback_classify(title, description)
