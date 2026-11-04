import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .config import DB_PATH, COMMITTEE_MAPPING
from .database import (
    init_db,
    create_grievance,
    get_all_grievances,
    get_grievance_by_ticket_id,
    update_grievance_status
)
from .schemas import (
    AnalyzeRequest,
    AnalyzeResponse,
    ConversationChatRequest,
    ConversationChatResponse,
    GrievanceCreate,
    GrievanceStatusUpdate,
    GrievanceResponse,
    EmergingIncident,
    CampusPulseNode,
    SettingsUpdateRequest
)
from .classifier import (
    classify_complaint,
    handle_conversation_turn,
    set_runtime_key,
    get_runtime_key,
    get_runtime_model
)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="CampusVoice Incident Intelligence Platform API",
    description="Speak. Detect. Resolve. AI Campus Operations & Incident Intelligence",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Conversational AI Concierge ---
@app.post("/api/conversation/chat", response_model=ConversationChatResponse)
async def conversation_chat(body: ConversationChatRequest):
    message = body.message.strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    
    result = handle_conversation_turn(message, body.conversationState)
    return result

# --- Core Grievance Endpoints ---
@app.post("/api/grievances/analyze", response_model=AnalyzeResponse)
async def analyze_grievance(request: AnalyzeRequest):
    complaint_text = request.complaint.strip()
    if not complaint_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Complaint text cannot be empty."
        )
    result = classify_complaint(complaint_text)
    return result

@app.post("/api/grievances", response_model=GrievanceResponse, status_code=status.HTTP_201_CREATED)
async def submit_grievance(data: GrievanceCreate):
    created = create_grievance(data.model_dump())
    if not created:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register grievance."
        )
    return created

@app.get("/api/grievances", response_model=List[GrievanceResponse])
async def list_grievances():
    return get_all_grievances()

@app.get("/api/grievances/{ticket_id}", response_model=GrievanceResponse)
async def get_grievance(ticket_id: str):
    ticket = get_grievance_by_ticket_id(ticket_id)
    if not ticket:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found."
        )
    return ticket

@app.patch("/api/grievances/{ticket_id}/status", response_model=GrievanceResponse)
async def update_status(ticket_id: str, body: GrievanceStatusUpdate):
    updated = update_grievance_status(ticket_id, body.status, body.actionTakenReport)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket '{ticket_id}' not found or update failed."
        )
    return updated

# --- SIGNATURE FEATURE 1: AI Incident Intelligence (Clustering & Emerging Incidents) ---
@app.get("/api/incidents/emerging", response_model=List[EmergingIncident])
async def get_emerging_incidents():
    all_tickets = get_all_grievances()
    
    # Filter active/recent tickets (not resolved or recently updated)
    active_tickets = [t for t in all_tickets if t["status"] != "RESOLVED"]
    
    # Group by (location, category)
    clusters = defaultdict(list)
    for t in active_tickets:
        loc = t.get("location") or "General Campus"
        cat = t.get("category") or "OTHER"
        clusters[(loc, cat)].append(t)
        
    emerging = []
    idx = 1
    for (loc, cat), t_list in clusters.items():
        count = len(t_list)
        # Cluster threshold: count >= 2 or any CRITICAL/HIGH priority item
        has_critical = any(t["priority"] in ["CRITICAL", "HIGH"] for t in t_list)
        
        if count >= 2 or (count >= 1 and has_critical and loc != "General Campus"):
            ticket_ids = [t["ticketId"] for t in t_list]
            dept_name = cat.replace("_", " ").title()
            
            # Formulate AI recommendation based on category
            if cat == "ELECTRICITY":
                rec = "Recommend immediate circuit isolation and emergency electrical maintenance team inspection."
            elif cat == "WATER_SUPPLY":
                rec = "Recommend water valve shutdown, emergency tanker dispatch, and plumbing audit."
            elif cat == "MESS_CANTEEN":
                rec = "Recommend food safety inspector audit and temporary vendor meal quarantine."
            elif cat == "SECURITY":
                rec = "Recommend deployment of proctorial security post and perimeter check."
            elif cat == "NETWORK_IT":
                rec = "Recommend network gateway reboot and core switch diagnostics."
            else:
                rec = f"Recommend expedited committee inspection by {COMMITTEE_MAPPING.get(cat, 'Estates Department')}."

            severity = "CRITICAL" if any(t["priority"] == "CRITICAL" for t in t_list) else "HIGH"

            emerging.append(EmergingIncident(
                incidentId=f"INC-2026-0{idx}",
                title=f"{loc} – {dept_name} Disruption ({count} related reports)",
                category=cat,
                location=loc,
                reportCount=count,
                severity=severity,
                status="ACTIVE_INVESTIGATION",
                relatedTicketIds=ticket_ids,
                aiRecommendation=rec,
                detectedAt=t_list[0]["createdAt"]
            ))
            idx += 1

    return emerging

# --- SIGNATURE FEATURE 2: Campus Pulse Schematic Map Telemetry ---
CAMPUS_NODES = [
    {"id": "block-a", "name": "Block A", "shortName": "Block A (CS/ECE)"},
    {"id": "block-b", "name": "Block B", "shortName": "Block B (Mech/Civil)"},
    {"id": "block-c", "name": "Block C", "shortName": "Block C (Science)"},
    {"id": "library", "name": "Main Library", "shortName": "Central Library"},
    {"id": "hostel", "name": "Hostel", "shortName": "Hostel Residence"},
    {"id": "cafeteria", "name": "Cafeteria", "shortName": "Main Cafeteria & Mess"},
    {"id": "auditorium", "name": "Auditorium", "shortName": "Main Auditorium / SAC"},
    {"id": "lab-complex", "name": "Lab Complex", "shortName": "Computing & Robotics Lab"},
    {"id": "sports-complex", "name": "Sports Complex", "shortName": "Indoor Gym & Arena"},
]

@app.get("/api/campus/pulse", response_model=List[CampusPulseNode])
async def get_campus_pulse():
    all_tickets = get_all_grievances()
    active_tickets = [t for t in all_tickets if t["status"] != "RESOLVED"]
    
    pulse_nodes = []
    for node in CAMPUS_NODES:
        name_lower = node["name"].lower()
        node_tickets = [
            t for t in active_tickets
            if name_lower in (t.get("location") or "").lower() or (t.get("location") or "").lower() in name_lower
        ]
        
        active_count = len(node_tickets)
        critical_count = sum(1 for t in node_tickets if t.get("priority") == "CRITICAL")
        high_count = sum(1 for t in node_tickets if t.get("priority") == "HIGH")
        
        cat_counts = defaultdict(int)
        for t in node_tickets:
            cat_counts[t.get("category", "OTHER")] += 1
            
        if critical_count > 0 or active_count >= 3:
            status_val = "CRITICAL"
        elif active_count >= 1 or high_count > 0:
            status_val = "ELEVATED"
        else:
            status_val = "NORMAL"
            
        recent_ids = [t["ticketId"] for t in node_tickets[:4]]
        
        pulse_nodes.append(CampusPulseNode(
            id=node["id"],
            name=node["name"],
            shortName=node["shortName"],
            activeTickets=active_count,
            criticalCount=critical_count,
            highCount=high_count,
            status=status_val,
            categoryCounts=dict(cat_counts),
            recentTicketIds=recent_ids
        ))
        
    return pulse_nodes

# --- Settings & Dynamic API Key Configuration ---
@app.get("/api/settings")
async def get_settings():
    key = get_runtime_key()
    model = get_runtime_model()
    masked_key = ""
    if key:
        masked_key = key[:4] + "..." + key[-4:] if len(key) > 8 else "CONFIGURED"
    return {
        "geminiConfigured": bool(key),
        "hasGeminiKey": bool(key),
        "geminiApiKeyMasked": masked_key,
        "geminiModel": model,
        "activeEngine": "Google Gemini 2.5 Flash" if key else "Institutional Neural Fallback"
    }

@app.post("/api/settings")
async def update_settings(body: SettingsUpdateRequest):
    if body.geminiApiKey is not None:
        set_runtime_key(body.geminiApiKey, body.geminiModel)
    key = get_runtime_key()
    model = get_runtime_model()
    return {
        "status": "success",
        "geminiConfigured": bool(key),
        "hasGeminiKey": bool(key),
        "geminiModel": model,
        "activeEngine": "Google Gemini 2.5 Flash" if key else "Institutional Neural Fallback",
        "message": "AI configuration updated successfully."
    }

# --- Static Files & Client Routes ---
if FRONTEND_DIR.exists():
    css_dir = FRONTEND_DIR / "css"
    js_dir = FRONTEND_DIR / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")

@app.get("/")
async def root():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"message": "CampusVoice API running"}

@app.get("/index.html")
async def student_portal():
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="index.html not found")

@app.get("/dashboard.html")
async def admin_dashboard():
    dashboard_file = FRONTEND_DIR / "dashboard.html"
    if dashboard_file.exists():
        return FileResponse(dashboard_file)
    raise HTTPException(status_code=404, detail="dashboard.html not found")
