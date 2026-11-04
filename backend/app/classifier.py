import re
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
import requests
from .config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    ALLOWED_CATEGORIES,
    ALLOWED_PRIORITIES,
    COMMITTEE_MAPPING
)

logger = logging.getLogger(__name__)

# In-memory runtime override if user updates key via API / Settings UI
RUNTIME_GEMINI_KEY = GEMINI_API_KEY
RUNTIME_GEMINI_MODEL = GEMINI_MODEL

def set_runtime_key(key: str, model: Optional[str] = None):
    global RUNTIME_GEMINI_KEY, RUNTIME_GEMINI_MODEL
    RUNTIME_GEMINI_KEY = key.strip() if key else ""
    if model:
        RUNTIME_GEMINI_MODEL = model.strip()

def get_runtime_key() -> str:
    return RUNTIME_GEMINI_KEY

def get_runtime_model() -> str:
    return RUNTIME_GEMINI_MODEL

CATEGORY_KEYWORDS = {
    "WATER_SUPPLY": [
        "water", "leak", "leaking", "tap", "pipe", "pipes", "drinking water", "geyser",
        "washroom", "toilet", "plumbing", "drain", "drainage", "sewage", "flush", "water supply",
        "water cooler", "filter", "ro plant", "purifier", "no water", "dry tap"
    ],
    "ELECTRICITY": [
        "electric", "electricity", "power", "wire", "wires", "socket", "spark", "sparks",
        "switch", "switchboard", "light", "lights", "fan", "blackout", "breaker", "shock",
        "current", "short circuit", "voltage", "plug", "inverter", "generator", "bulb",
        "tube light", "phase", "mcb", "power outage", "electricity disruption"
    ],
    "MESS_CANTEEN": [
        "mess", "food", "canteen", "cafeteria", "lunch", "dinner", "breakfast", "meal",
        "meals", "cooking", "taste", "stale", "rotten", "hygiene", "caterer", "catering",
        "food quality", "chapati", "curry", "rice", "dal", "snack", "hair in food",
        "insect in food", "cold food", "mess hall", "tea", "coffee"
    ],
    "NETWORK_IT": [
        "wifi", "wi-fi", "internet", "network", "lan", "ethernet", "router", "signal",
        "bandwidth", "speed", "portal", "erp", "login", "student portal", "server down",
        "connection", "disconnected", "firewall", "captive portal", "ip address"
    ],
    "LABORATORY": [
        "lab", "laboratory", "machine", "apparatus", "pc", "computer", "multimeter",
        "oscilloscope", "microscope", "chemicals", "test tube", "practical", "terminal",
        "soldering", "workbench", "workstation", "sensor", "arduino", "matlab",
        "compiler", "operating system"
    ],
    "LIBRARY": [
        "library", "book", "books", "librarian", "journal", "borrow", "return",
        "due date", "fine", "study hall", "reading hall", "reference book", "e-resource",
        "card", "library card", "barcode", "newspaper", "magazine"
    ],
    "EXAMINATION": [
        "exam", "exams", "examination", "hall ticket", "admit card", "invigilator", "marksheet",
        "grade", "grades", "cgpa", "revaluation", "rechecking", "midterm", "endsem",
        "semester exam", "results", "schedule", "clash", "marks", "score", "supplementary", "arrear"
    ],
    "SECURITY": [
        "security", "security guard", "guard", "gate", "cctv", "camera", "theft", "stolen", "lost",
        "id card", "curfew", "harassment", "unauthorized", "trespass", "boundary wall",
        "parking pass", "entry", "night patrol", "campus safety", "intruder"
    ],
    "SPORTS": [
        "gym", "gymnasium", "ground", "court", "pitch", "badminton", "cricket", "football",
        "basketball", "volleyball", "table tennis", "track", "sports equipment", "fitness",
        "dumbbells", "treadmill", "treadmills", "sports complex", "indoor sports complex",
        "gym equipment", "coach", "tournament"
    ],
    "HEALTH_CARE": [
        "doctor", "nurse", "clinic", "dispensary", "health center", "medical", "first aid",
        "medicine", "bandage", "fever", "emergency", "ambulance", "pharmacy", "sick room",
        "physician", "tablets"
    ],
    "INFRASTRUCTURE": [
        "projector", "desk", "bench", "chair", "door", "window", "board", "whiteboard",
        "blackboard", "elevator", "lift", "stairs", "staircase", "building", "classroom",
        "hall", "ac", "air conditioner", "cooling", "podium", "mic in hall", "crack",
        "leakage from roof", "ceiling", "tiles", "lock"
    ],
    "HOSTEL": [
        "hostel", "warden", "room", "roommate", "bed", "mattress", "cupboard", "wardrobe",
        "almirah", "curfew", "dorm", "corridor", "hostel block", "laundry", "washing machine",
        "cloth line", "ironing", "balcony"
    ],
    "CLEANLINESS": [
        "garbage", "dirty", "trash", "waste", "dust", "cleaning", "clean", "sweep",
        "smell", "stink", "stinking", "odor", "foul", "pest", "insects", "cockroach",
        "litter", "dustbin", "waste bin", "sanitation", "housekeeping", "spill", "unhygienic"
    ],
    "TRANSPORT": [
        "bus", "shuttle", "transport", "parking", "vehicle", "driver", "route", "van",
        "bus stop", "college bus", "punctuality", "rash driving", "fare", "commute",
        "bicycle stand", "helmet"
    ],
    "ACADEMICS": [
        "syllabus", "professor", "teacher", "lecture", "class", "classes", "attendance",
        "assignment", "course", "faculty", "tutorial", "hod", "department", "curriculum",
        "teaching", "timetable"
    ]
}

CRITICAL_PRIORITY_CUES = [
    "fire", "spark", "sparks", "shock", "danger", "electrocution", "severe injury",
    "food poisoning", "accident", "theft", "harassment", "emergency", "critical"
]

HIGH_PRIORITY_CUES = [
    "exam tomorrow", "presentation tomorrow", "since yesterday", "days", "no water",
    "overflowing", "not working at all", "hall ticket missing", "dispute", "repeatedly", "urgent",
    "entire block", "whole block", "blackout", "since morning"
]

LOW_PRIORITY_CUES = [
    "suggestion", "minor", "request", "whenever possible", "feedback", "slowly", "not urgent"
]

LOCATION_PATTERNS = [
    r"(Block\s+[A-C])",
    r"(Hostel\s+Block\s+[A-D])",
    r"(Main\s+Library|Central\s+Library)",
    r"(Cafeteria|Main\s+Cafeteria|Food\s+Court)",
    r"(Auditorium|Main\s+Auditorium)",
    r"(Lab\s+Complex|Computer\s+Lab\s+[0-9]+|Robotics\s+Lab|Mechanical\s+Workshop)",
    r"(Sports\s+Complex|Gymnasium|Indoor\s+Sports)",
    r"(Hostel(?:\s+Complex|\s+Mess)?)",
    r"(Academic\s+Block\s+[0-9]+)",
    r"(Science\s+Block)",
    r"(Admin\s+Block)",
    r"(Room\s+[0-9]+)"
]

def normalize_campus_location(location: Optional[str]) -> str:
    if not location:
        return "General Campus"
    loc_lower = location.lower()
    if "block a" in loc_lower or "academic block 1" in loc_lower:
        return "Block A"
    if "block b" in loc_lower or "academic block 2" in loc_lower or "engineering block 2" in loc_lower:
        return "Block B"
    if "block c" in loc_lower or "science block" in loc_lower:
        return "Block C"
    if "library" in loc_lower:
        return "Main Library"
    if "cafeteria" in loc_lower or "canteen" in loc_lower or "food court" in loc_lower:
        return "Cafeteria"
    if "auditorium" in loc_lower or "sac" in loc_lower:
        return "Auditorium"
    if "hostel" in loc_lower or "mess" in loc_lower or "residence" in loc_lower:
        return "Hostel"
    if "lab" in loc_lower or "workshop" in loc_lower:
        return "Lab Complex"
    if "gym" in loc_lower or "sports" in loc_lower:
        return "Sports Complex"
    return location.title()

def extract_time_range(text: str) -> Tuple[str, Optional[str]]:
    now = datetime.now()
    text_lower = text.lower()
    start_time = now.strftime("%Y-%m-%dT%H:%M")
    end_time = None
    
    if "since yesterday" in text_lower or "from yesterday" in text_lower:
        start_time = (now - timedelta(days=1)).strftime("%Y-%m-%dT09:00")
    elif "since 2 days" in text_lower or "since two days" in text_lower:
        start_time = (now - timedelta(days=2)).strftime("%Y-%m-%dT09:00")
    elif "since 3 days" in text_lower or "since three days" in text_lower:
        start_time = (now - timedelta(days=3)).strftime("%Y-%m-%dT09:00")
    elif "since morning" in text_lower or "this morning" in text_lower:
        start_time = now.strftime("%Y-%m-%dT08:30")
    elif "last night" in text_lower:
        start_time = (now - timedelta(days=1)).strftime("%Y-%m-%dT21:00")
        
    if "until tomorrow" in text_lower or "by tomorrow" in text_lower:
        end_time = (now + timedelta(days=1)).strftime("%Y-%m-%dT18:00")
    elif "today evening" in text_lower:
        end_time = now.strftime("%Y-%m-%dT18:00")
        
    return start_time, end_time

def infer_formal_attributes(category: str, text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    if category in ["WATER_SUPPLY", "ELECTRICITY", "INFRASTRUCTURE"]:
        grievance_type = "Facility Breakdown"
    elif category in ["HOSTEL", "MESS_CANTEEN"]:
        grievance_type = "Living Conditions Failure"
    elif category in ["EXAMINATION", "ACADEMICS"]:
        grievance_type = "Academic Evaluation Dispute"
    elif category in ["SECURITY", "HEALTH_CARE"]:
        grievance_type = "Safety & Security Hazard"
    elif category == "CLEANLINESS":
        grievance_type = "Sanitation & Hygiene Violation"
    elif category == "TRANSPORT":
        grievance_type = "Administrative Delay"
    elif category == "NETWORK_IT":
        grievance_type = "Service Outage"
    else:
        grievance_type = "Operational Disruption"

    if any(k in text_lower for k in ["again", "repeatedly", "since yesterday", "days", "not fixed", "ignored"]):
        recurrence = "Repeated / Unresolved Negligence"
    else:
        recurrence = "First-Time Occurrence"

    if any(k in text_lower for k in ["entire block", "whole block", "all of us", "entire hostel", "floor", "class", "students", "everyone"]):
        affected_scope = "Entire Block / Community"
    elif any(k in text_lower for k in ["campus", "entire college"]):
        affected_scope = "Campus-wide"
    else:
        affected_scope = "Individual Student"

    prior_reported = any(k in text_lower for k in ["told", "informed", "reported", "warden", "complained before"])

    if "electricity" in text_lower or "power" in text_lower or "wire" in text_lower:
        relief = "Immediate inspection and restoration by the electrical maintenance team"
    elif "water" in text_lower or "leak" in text_lower:
        relief = "Emergency plumbing repair and water restoration"
    elif "food" in text_lower or "mess" in text_lower:
        relief = "Food safety audit and catering penalty enforcement"
    elif "wifi" in text_lower or "internet" in text_lower:
        relief = "Access point diagnosis and network gateway reboot"
    else:
        relief = "Immediate institutional inspection and verifiable corrective action report"

    return {
        "assignedCommittee": COMMITTEE_MAPPING.get(category, "Central Student Grievance Redressal Committee (CGRC)"),
        "grievanceType": grievance_type,
        "recurrence": recurrence,
        "affectedScope": affected_scope,
        "priorReported": prior_reported,
        "reliefSought": relief
    }

def rule_based_classify(text: str) -> Dict[str, Any]:
    text_lower = text.lower()
    
    # 1. Category
    matched_category = "OTHER"
    highest_score = 0
    for cat, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            pattern = r'\b' + re.escape(kw) + r'\b'
            if re.search(pattern, text_lower):
                score += (len(kw.split()) * 2) if " " in kw else 1
        if score > highest_score:
            highest_score = score
            matched_category = cat
            
    # 2. Priority
    if any(cue in text_lower for cue in CRITICAL_PRIORITY_CUES):
        priority = "CRITICAL"
    elif any(cue in text_lower for cue in HIGH_PRIORITY_CUES):
        priority = "HIGH"
    elif any(cue in text_lower for cue in LOW_PRIORITY_CUES):
        priority = "LOW"
    elif matched_category in ["WATER_SUPPLY", "ELECTRICITY", "HEALTH_CARE", "SECURITY", "EXAMINATION"]:
        priority = "HIGH"
    else:
        priority = "MEDIUM"
            
    # 3. Location
    raw_location = None
    for pattern in LOCATION_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw_location = match.group(1).strip()
            break
    location = normalize_campus_location(raw_location)
            
    # 4. Summary Title
    cleaned_first_sentence = text.strip().split(".")[0].strip()
    words = cleaned_first_sentence.split()
    if len(words) <= 8 and not any(w in cleaned_first_sentence.lower() for w in ["i want", "there is"]):
        summary = cleaned_first_sentence.capitalize()
    else:
        dept_name = matched_category.replace("_", " ").title()
        summary = f"{dept_name} Disruption at {location}"

    start_time, end_time = extract_time_range(text)
    formal_attrs = infer_formal_attributes(matched_category, text)

    return {
        "summary": summary,
        "category": matched_category,
        "assignedCommittee": formal_attrs["assignedCommittee"],
        "grievanceType": formal_attrs["grievanceType"],
        "priority": priority,
        "location": location,
        "description": text.strip(),
        "startTime": start_time,
        "endTime": end_time,
        "recurrence": formal_attrs["recurrence"],
        "affectedScope": formal_attrs["affectedScope"],
        "reliefSought": formal_attrs["reliefSought"],
        "priorReported": formal_attrs["priorReported"],
        "aiProcessed": False,
        "source": "CampusVoice Incident Engine"
    }

def call_gemini(text: str) -> Optional[Dict[str, Any]]:
    key = RUNTIME_GEMINI_KEY
    if not key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{RUNTIME_GEMINI_MODEL}:generateContent?key={key}"
    cats_str = " | ".join(f'"{c}"' for c in ALLOWED_CATEGORIES)
    prompt = f"""You are an advanced campus incident intelligence assistant.
Analyze this student complaint:
"{text}"

Return ONLY valid JSON matching this schema:
{{
  "summary": "Concise incident summary (max 7 words, e.g. 'Electricity Disruption at Block A')",
  "category": {cats_str},
  "assignedCommittee": "Responsible campus authority or committee",
  "grievanceType": "Facility Breakdown | Living Conditions Failure | Academic Evaluation Dispute | Safety & Security Hazard | Service Outage",
  "priority": "LOW | MEDIUM | HIGH | CRITICAL",
  "location": "Schematic block (Block A, Block B, Block C, Main Library, Hostel, Cafeteria, Auditorium, Lab Complex, Sports Complex)",
  "description": "Factual description of the incident",
  "startTime": "YYYY-MM-DDTHH:MM if mentioned, or null",
  "endTime": "YYYY-MM-DDTHH:MM if mentioned, or null",
  "recurrence": "First-Time Occurrence | Repeated / Unresolved Negligence",
  "affectedScope": "Individual Student | Entire Block / Community | Campus-wide",
  "reliefSought": "Immediate actionable remedy recommended",
  "priorReported": true or false
}}
"""

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"}
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            return None
        parts = candidates[0].get("content", {}).get("parts", [])
        if not parts:
            return None
        raw_json = parts[0].get("text", "").strip()
        if raw_json.startswith("```"):
            raw_json = re.sub(r"^```(?:json)?\s*", "", raw_json)
            raw_json = re.sub(r"\s*```$", "", raw_json)

        parsed = json.loads(raw_json)
        category = str(parsed.get("category", "OTHER")).upper()
        if category not in ALLOWED_CATEGORIES:
            category = "OTHER"
        priority = str(parsed.get("priority", "MEDIUM")).upper()
        if priority not in ALLOWED_PRIORITIES:
            priority = "MEDIUM"

        norm_loc = normalize_campus_location(parsed.get("location"))
        fallback_attrs = infer_formal_attributes(category, text)

        return {
            "summary": str(parsed.get("summary", "Incident at Campus")).strip(),
            "category": category,
            "assignedCommittee": str(parsed.get("assignedCommittee") or fallback_attrs["assignedCommittee"]),
            "grievanceType": str(parsed.get("grievanceType") or fallback_attrs["grievanceType"]),
            "priority": priority,
            "location": norm_loc,
            "description": str(parsed.get("description", text)).strip(),
            "startTime": parsed.get("startTime") or extract_time_range(text)[0],
            "endTime": parsed.get("endTime") or extract_time_range(text)[1],
            "recurrence": str(parsed.get("recurrence") or fallback_attrs["recurrence"]),
            "affectedScope": str(parsed.get("affectedScope") or fallback_attrs["affectedScope"]),
            "reliefSought": str(parsed.get("reliefSought") or fallback_attrs["reliefSought"]),
            "priorReported": bool(parsed.get("priorReported", fallback_attrs["priorReported"])),
            "aiProcessed": True,
            "source": "Gemini Incident Intelligence"
        }
    except Exception as e:
        logger.warning(f"Gemini call failed: {e}")
        return None

def classify_complaint(text: str) -> Dict[str, Any]:
    gemini_res = call_gemini(text)
    if gemini_res:
        return gemini_res
    return rule_based_classify(text)

def handle_conversation_turn(message: str, conversation_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Conversational AI Concierge: Handles follow-up questions when details are ambiguous or missing.
    Matches exact demo scenario:
    Student: "Electricity has been unavailable in Block A since morning."
    AI: "Is the entire block affected or just one classroom?"
    Student: "The entire block."
    AI: "Understood. I'll register this as an electricity disruption affecting Block A."
    """
    state = conversation_state or {}
    message_clean = message.strip()
    msg_lower = message_clean.lower()

    # Case 1: Student is answering an active follow-up question
    if state.get("waitingForScope"):
        orig = state.get("initialComplaint", "")
        # Merge follow-up clarification into full grievance context
        combined_text = f"{orig} Affecting: {message_clean}."
        analysis = classify_complaint(combined_text)
        
        # Determine scope phrasing
        if any(w in msg_lower for w in ["entire", "whole", "all", "block", "yes"]):
            analysis["affectedScope"] = "Entire Block / Community"
            analysis["priority"] = "HIGH"
            scope_phrase = f"an electricity disruption affecting {analysis['location']}" if analysis["category"] == "ELECTRICITY" else f"an incident affecting {analysis['location']}"
        else:
            analysis["affectedScope"] = "Classroom / Room"
            scope_phrase = f"a local issue in {analysis['location']}"

        ai_response = f"Understood. I'll register this as {scope_phrase}."

        return {
            "needsFollowUp": False,
            "aiMessage": ai_response,
            "followUpQuestion": None,
            "partialState": None,
            "analysis": analysis
        }

    # Case 2: Missing location check
    analysis = classify_complaint(message_clean)
    
    # Check if this is the signature electricity/block issue that needs scope follow-up
    has_block = bool(re.search(r'\b(block\s+[a-c]|hostel|library|cafeteria)\b', msg_lower))
    is_utility = analysis["category"] in ["ELECTRICITY", "WATER_SUPPLY", "NETWORK_IT"]
    has_scope_cues = any(w in msg_lower for w in ["entire", "whole", "room", "floor", "classroom", "only"])

    if is_utility and has_block and not has_scope_cues:
        question = "Is the entire block affected or just one classroom?"
        return {
            "needsFollowUp": True,
            "aiMessage": question,
            "followUpQuestion": question,
            "partialState": {
                "waitingForScope": True,
                "initialComplaint": message_clean,
                "category": analysis["category"],
                "location": analysis["location"]
            },
            "analysis": None
        }

    # Case 3: Completely clear statement upfront
    location_desc = f" at {analysis['location']}" if analysis.get("location") else ""
    return {
        "needsFollowUp": False,
        "aiMessage": f"Understood. I've compiled your incident report for {analysis['category'].replace('_', ' ').title()}{location_desc}.",
        "followUpQuestion": None,
        "partialState": None,
        "analysis": analysis
    }
