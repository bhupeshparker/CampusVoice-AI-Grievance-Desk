import sqlite3
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from .config import DB_PATH, COMMITTEE_MAPPING

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS grievances (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE NOT NULL,
                student_name TEXT,
                roll_no TEXT,
                is_confidential INTEGER DEFAULT 0,
                complaint TEXT NOT NULL,
                summary TEXT NOT NULL,
                category TEXT NOT NULL,
                assigned_committee TEXT NOT NULL,
                grievance_type TEXT NOT NULL,
                priority TEXT NOT NULL,
                location TEXT,
                description TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                recurrence TEXT DEFAULT 'First-Time Occurrence',
                affected_scope TEXT DEFAULT 'Individual Student',
                relief_sought TEXT DEFAULT 'Immediate Inspection & Rectification',
                prior_reported INTEGER DEFAULT 0,
                status TEXT NOT NULL DEFAULT 'SUBMITTED',
                action_taken_report TEXT,
                sla_hours INTEGER DEFAULT 48,
                ai_processed INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM grievances")
        count = cursor.fetchone()[0]
        if count == 0:
            seed_data = [
                (
                    "CV-1030",
                    "Rohan Sharma",
                    "2023-CS-042",
                    0,
                    "The dinner served yesterday in Hostel Mess was cold and the paneer curry was sour and stale.",
                    "Substandard & Unhygienic Meal Served in Mess",
                    "MESS_CANTEEN",
                    "Food Quality & Mess Supervisory Committee",
                    "Living Conditions Failure",
                    "HIGH",
                    "Cafeteria",
                    "Quality and hygiene failure in dinner preparation; multiple residents reported nausea.",
                    "2026-11-01T20:00",
                    "2026-11-02T10:00",
                    "Repeated / Unresolved Negligence",
                    "Entire Block / Community",
                    "Caterer penalization, food batch audit, and replacement of catering supervisor",
                    1,
                    "RESOLVED",
                    "Food safety inspector seized batch samples. Catering contractor penalized. Fresh hygiene protocol implemented.",
                    24,
                    1,
                    "2026-11-01T20:15:00Z",
                    "2026-11-02T10:00:00Z"
                ),
                (
                    "CV-1031",
                    "Ananya Iyer",
                    "2024-EC-018",
                    0,
                    "Power surge caused laboratory computers to reboot and lights are flickering in Block A.",
                    "Power Fluctuation & Voltage Drop in Block A",
                    "ELECTRICITY",
                    "Electrical Engineering & Power Utility Services",
                    "Facility Breakdown",
                    "MEDIUM",
                    "Block A",
                    "Voltage fluctuation on 2nd floor causing system reboots during practical sessions.",
                    "2026-11-02T08:30",
                    "2026-11-02T14:00",
                    "First-Time Occurrence",
                    "Entire Block / Community",
                    "Substation transformer inspection and voltage stabilizer check",
                    0,
                    "UNDER_INVESTIGATION",
                    None,
                    48,
                    1,
                    "2026-11-02T09:30:00Z",
                    "2026-11-02T14:00:00Z"
                ),
                (
                    "CV-1032",
                    "Karthik Nair",
                    "2023-ME-089",
                    0,
                    "Computer terminal 18 in Lab Complex has a malfunctioning keyboard and blue screen crash.",
                    "Hardware Malfunction on Workstation #18",
                    "LABORATORY",
                    "Laboratory Standards, Equipment & Safety Committee",
                    "Facility Breakdown",
                    "LOW",
                    "Lab Complex",
                    "Hardware fault: multiple keys unresponsive and kernel panic during computational mechanics session.",
                    "2026-11-02T11:00",
                    "2026-11-02T17:30",
                    "First-Time Occurrence",
                    "Individual Student",
                    "Peripheral replacement and system disk diagnostic repair",
                    0,
                    "RESOLVED",
                    "Faulty keyboard replaced. RAM reseated and system re-imaged.",
                    72,
                    0,
                    "2026-11-02T11:45:00Z",
                    "2026-11-02T17:30:00Z"
                ),
                (
                    "CV-1033",
                    "Pooja Patel",
                    "2022-IT-105",
                    0,
                    "Unable to download semester end hall ticket from student portal, showing internal server error.",
                    "Portal Authentication Failure Generating Hall Ticket",
                    "EXAMINATION",
                    "Office of the Controller of Examinations (COE)",
                    "Academic Evaluation Dispute",
                    "CRITICAL",
                    "Auditorium",
                    "Examination portal 500 server error preventing admit card download 24 hours prior to semester finals.",
                    "2026-11-02T14:00",
                    "2026-11-02T18:00",
                    "Repeated / Unresolved Negligence",
                    "Entire Block / Community",
                    "Emergency hall ticket generation and database clearance sync",
                    1,
                    "RESOLVED",
                    "COE cleared database lock and issued official stamped PDF admit card.",
                    12,
                    1,
                    "2026-11-02T15:20:00Z",
                    "2026-11-02T18:00:00Z"
                ),
                (
                    "CV-1034",
                    "Protected Disclosure",
                    "CONFIDENTIAL",
                    1,
                    "The floodlights along Hostel pathway are completely dark since two days.",
                    "High-Risk Perimeter Lighting Failure on Residential Pathway",
                    "SECURITY",
                    "Campus Security, Safety & Proctorial Board",
                    "Safety & Security Hazard",
                    "CRITICAL",
                    "Hostel",
                    "Dark stretch along the pathway after 7 PM poses immediate safety hazard for female residents.",
                    "2026-11-01T19:00",
                    "2026-11-03T11:30",
                    "Repeated / Unresolved Negligence",
                    "Entire Block / Community",
                    "Emergency floodlight replacement and deployment of dedicated patrol guard",
                    1,
                    "RESOLVED",
                    "Burnt LED driver replaced. Security proctor deployed stationary guard post from 18:00 to 06:00.",
                    12,
                    1,
                    "2026-11-03T07:10:00Z",
                    "2026-11-03T11:30:00Z"
                ),
                (
                    "CV-1035",
                    "Aditya Roy",
                    "2024-CV-051",
                    0,
                    "Both motorized treadmills in Sports Complex have broken safety belts and loose handles.",
                    "Hazardous Mechanical Wear on Cardio Equipment",
                    "SPORTS",
                    "Physical Education & Sports Directorate",
                    "Facility Breakdown",
                    "LOW",
                    "Sports Complex",
                    "Physical wear on motor belts and emergency stop magnets posing tripping risks during training.",
                    "2026-11-03T07:30",
                    "2026-11-03T16:00",
                    "First-Time Occurrence",
                    "Individual Student",
                    "Preventative maintenance service and emergency strap replacement",
                    0,
                    "RESOLVED",
                    "OEM technician serviced both units, replaced tension belts and emergency magnetic keys.",
                    72,
                    0,
                    "2026-11-03T08:30:00Z",
                    "2026-11-03T16:00:00Z"
                ),
                (
                    "CV-1036",
                    "Varun Sen",
                    "2023-ME-112",
                    0,
                    "First aid box in Lab Complex workshop is empty and missing antiseptic bandages.",
                    "OSHA Non-Compliance: Depleted First Aid Supplies",
                    "HEALTH_CARE",
                    "Campus Medical Board & Health Center",
                    "Safety & Security Hazard",
                    "HIGH",
                    "Lab Complex",
                    "Depleted medical supplies near heavy machining lathes where laceration risks are severe.",
                    "2026-11-03T08:00",
                    None,
                    "First-Time Occurrence",
                    "Individual Student",
                    "Emergency replenishment of trauma dressings, antiseptic ointment, and burn gel",
                    0,
                    "ACTION_TAKEN",
                    "Medical dispensary dispatched emergency trauma pack. Permanent monthly inventory audit established.",
                    24,
                    1,
                    "2026-11-03T09:10:00Z",
                    "2026-11-03T10:00:00Z"
                ),
                (
                    "CV-1037",
                    "Siddharth Rao",
                    "2024-BT-033",
                    0,
                    "Broken window latch in Block B causing water seepage during rain.",
                    "Window Frame Failure & Rain Seepage in Block B",
                    "INFRASTRUCTURE",
                    "Campus Works, Estates & Physical Infrastructure Cell",
                    "Facility Breakdown",
                    "MEDIUM",
                    "Block B",
                    "Classroom 204 window latch broken, allowing rain water inside.",
                    "2026-11-03T08:15",
                    None,
                    "First-Time Occurrence",
                    "Individual Student",
                    "Carpentry repair and window latch replacement",
                    0,
                    "UNDER_INVESTIGATION",
                    None,
                    48,
                    1,
                    "2026-11-03T10:00:00Z",
                    "2026-11-03T11:00:00Z"
                ),
                (
                    "CV-1038",
                    "Meera Kulkarni",
                    "2023-EE-077",
                    0,
                    "The self-checkout scanner in Main Library is repeatedly failing to read RFID book tags.",
                    "RFID Checkout Kiosk Hardware Failure",
                    "LIBRARY",
                    "Central Library Advisory & Digital Resources Council",
                    "Facility Breakdown",
                    "LOW",
                    "Main Library",
                    "Automated kiosk scanner failing leading to circulation queue congestion at manual desk.",
                    "2026-11-03T10:30",
                    None,
                    "First-Time Occurrence",
                    "Individual Student",
                    "RFID antenna recalibration and kiosk software patch",
                    0,
                    "UNDER_INVESTIGATION",
                    None,
                    72,
                    0,
                    "2026-11-03T12:00:00Z",
                    "2026-11-03T13:00:00Z"
                ),
                (
                    "CV-1039",
                    "Demo Student",
                    "2023-CS-104",
                    0,
                    "The AC in Main Library 2nd floor study area is not cooling and making loud rattling noises.",
                    "HVAC Blower Motor Failure in Silent Reading Hall",
                    "INFRASTRUCTURE",
                    "Campus Works, Estates & Physical Infrastructure Cell",
                    "Facility Breakdown",
                    "MEDIUM",
                    "Main Library",
                    "Excessive compressor noise exceeding 75dB disrupting study hall during exam preparation.",
                    "2026-11-03T13:00",
                    "2026-11-03T17:00",
                    "First-Time Occurrence",
                    "Entire Block / Community",
                    "HVAC blower bearing replacement and refrigerant recharge",
                    0,
                    "RESOLVED",
                    "Estates engineer replaced worn pulley belt and recharged refrigerant.",
                    48,
                    1,
                    "2026-11-03T14:30:00Z",
                    "2026-11-03T17:00:00Z"
                ),
                (
                    "CV-1040",
                    "Demo Student",
                    "2023-CS-104",
                    0,
                    "Broken electrical socket in Block A Room 302 with exposed wires near PC 14.",
                    "Exposed High-Voltage Wiring in Block A",
                    "ELECTRICITY",
                    "Electrical Engineering & Power Utility Services",
                    "Safety & Security Hazard",
                    "CRITICAL",
                    "Block A",
                    "230V live wire exposed on shared workbench in Block A posing severe shock hazard.",
                    "2026-11-04T07:00",
                    None,
                    "Repeated / Unresolved Negligence",
                    "Entire Block / Community",
                    "Immediate circuit isolation and industrial modular socket replacement",
                    1,
                    "SUBMITTED",
                    None,
                    12,
                    1,
                    "2026-11-04T07:15:00Z",
                    "2026-11-04T07:15:00Z"
                ),
                (
                    "CV-1041",
                    "Demo Student",
                    "2023-CS-104",
                    0,
                    "Water supply in Hostel Block B has been unavailable since yesterday.",
                    "Severe Water Shortage in Hostel Block B",
                    "WATER_SUPPLY",
                    "Public Health & Campus Sanitation Division",
                    "Living Conditions Failure",
                    "HIGH",
                    "Hostel",
                    "Hostel Block B taps dry since yesterday, affecting over 50 resident students.",
                    "2026-11-04T06:30",
                    None,
                    "Repeated / Unresolved Negligence",
                    "Entire Block / Community",
                    "Emergency water tanker dispatch and main pipeline valve repair",
                    1,
                    "SUBMITTED",
                    None,
                    12,
                    1,
                    "2026-11-04T08:00:00Z",
                    "2026-11-04T08:00:00Z"
                )
            ]
            cursor.executemany("""
                INSERT INTO grievances (
                    ticket_id, student_name, roll_no, is_confidential,
                    complaint, summary, category, assigned_committee,
                    grievance_type, priority, location, description,
                    start_time, end_time, recurrence, affected_scope,
                    relief_sought, prior_reported, status, action_taken_report,
                    sla_hours, ai_processed, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, seed_data)
        conn.commit()

def get_next_ticket_id() -> str:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ticket_id FROM grievances WHERE ticket_id LIKE 'CV-%' ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return "CV-1042"
        last_id = row["ticket_id"]
        try:
            num = int(last_id.split("-")[1])
            return f"CV-{num + 1}"
        except (IndexError, ValueError):
            return "CV-1042"

def row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    keys = row.keys()
    category = row["category"]
    committee = row["assigned_committee"] if "assigned_committee" in keys and row["assigned_committee"] else COMMITTEE_MAPPING.get(category, "Central Grievance Redressal Cell")
    
    return {
        "ticketId": row["ticket_id"],
        "studentName": row["student_name"] if "student_name" in keys else "Demo Student",
        "rollNo": row["roll_no"] if "roll_no" in keys else "2023-CS-104",
        "isConfidential": bool(row["is_confidential"]) if "is_confidential" in keys else False,
        "complaint": row["complaint"],
        "summary": row["summary"],
        "category": category,
        "assignedCommittee": committee,
        "grievanceType": row["grievance_type"] if "grievance_type" in keys and row["grievance_type"] else "Facility Breakdown",
        "priority": row["priority"],
        "location": row["location"],
        "description": row["description"],
        "startTime": row["start_time"] if "start_time" in keys else None,
        "endTime": row["end_time"] if "end_time" in keys else None,
        "recurrence": row["recurrence"] if "recurrence" in keys and row["recurrence"] else "First-Time Occurrence",
        "affectedScope": row["affected_scope"] if "affected_scope" in keys and row["affected_scope"] else "Individual Student",
        "reliefSought": row["relief_sought"] if "relief_sought" in keys and row["relief_sought"] else "Immediate Inspection & Rectification",
        "priorReported": bool(row["prior_reported"]) if "prior_reported" in keys else False,
        "status": row["status"],
        "actionTakenReport": row["action_taken_report"] if "action_taken_report" in keys else None,
        "slaHours": row["sla_hours"] if "sla_hours" in keys and row["sla_hours"] else 48,
        "aiProcessed": bool(row["ai_processed"]),
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }

def get_all_grievances() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM grievances ORDER BY id DESC")
        rows = cursor.fetchall()
        return [row_to_dict(r) for r in rows]

def get_grievance_by_ticket_id(ticket_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM grievances WHERE ticket_id = ?", (ticket_id,))
        row = cursor.fetchone()
        return row_to_dict(row) if row else None

def create_grievance(data: Dict[str, Any]) -> Dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    ticket_id = get_next_ticket_id()
    category = data["category"]
    committee = data.get("assignedCommittee") or COMMITTEE_MAPPING.get(category, "Central Student Grievance Redressal Committee (CGRC)")
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO grievances (
                ticket_id, student_name, roll_no, is_confidential,
                complaint, summary, category, assigned_committee,
                grievance_type, priority, location, description,
                start_time, end_time, recurrence, affected_scope,
                relief_sought, prior_reported, status, action_taken_report,
                sla_hours, ai_processed, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticket_id,
            "Protected Disclosure" if data.get("isConfidential") else data.get("studentName", "Demo Student"),
            "CONFIDENTIAL" if data.get("isConfidential") else data.get("rollNo", "2023-CS-104"),
            1 if data.get("isConfidential") else 0,
            data.get("complaint", ""),
            data["summary"],
            category,
            committee,
            data.get("grievanceType", "Facility Breakdown"),
            data["priority"],
            data.get("location"),
            data["description"],
            data.get("startTime"),
            data.get("endTime"),
            data.get("recurrence", "First-Time Occurrence"),
            data.get("affectedScope", "Individual Student"),
            data.get("reliefSought", "Immediate Inspection & Rectification"),
            1 if data.get("priorReported") else 0,
            "SUBMITTED",
            None,
            24 if data["priority"] in ["HIGH", "CRITICAL"] else 48,
            1 if data.get("aiProcessed") else 0,
            now,
            now
        ))
        conn.commit()
    return get_grievance_by_ticket_id(ticket_id)

def update_grievance_status(ticket_id: str, status: str, action_taken_report: Optional[str] = None) -> Optional[Dict[str, Any]]:
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        cursor = conn.cursor()
        if action_taken_report:
            cursor.execute("""
                UPDATE grievances
                SET status = ?, action_taken_report = ?, updated_at = ?
                WHERE ticket_id = ?
            """, (status, action_taken_report, now, ticket_id))
        else:
            cursor.execute("""
                UPDATE grievances
                SET status = ?, updated_at = ?
                WHERE ticket_id = ?
            """, (status, now, ticket_id))
        conn.commit()
        if cursor.rowcount == 0:
            return None
    return get_grievance_by_ticket_id(ticket_id)
