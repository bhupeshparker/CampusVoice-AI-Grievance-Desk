import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "campusvoice.db"

# Formal Institutional Grievance Redressal Categories (Jurisdictions)
ALLOWED_CATEGORIES = [
    "HOSTEL",
    "INFRASTRUCTURE",
    "ELECTRICITY",
    "WATER_SUPPLY",
    "CLEANLINESS",
    "MESS_CANTEEN",
    "NETWORK_IT",
    "LABORATORY",
    "LIBRARY",
    "ACADEMICS",
    "EXAMINATION",
    "SECURITY",
    "SPORTS",
    "HEALTH_CARE",
    "TRANSPORT",
    "OTHER",
]

COMMITTEE_MAPPING = {
    "HOSTEL": "Hostel Administration & Residence Oversight Committee",
    "INFRASTRUCTURE": "Campus Works, Estates & Physical Infrastructure Cell",
    "ELECTRICITY": "Electrical Engineering & Power Utility Services",
    "WATER_SUPPLY": "Public Health & Campus Sanitation Division",
    "CLEANLINESS": "Sanitation, Waste Management & Environment Committee",
    "MESS_CANTEEN": "Food Quality & Mess Supervisory Committee",
    "NETWORK_IT": "Campus IT, Network & Computing Resource Center",
    "LABORATORY": "Laboratory Standards, Equipment & Safety Committee",
    "LIBRARY": "Central Library Advisory & Digital Resources Council",
    "ACADEMICS": "Dean of Academic Affairs & Faculty Grievance Board",
    "EXAMINATION": "Office of the Controller of Examinations (COE)",
    "SECURITY": "Campus Security, Safety & Proctorial Board",
    "SPORTS": "Physical Education & Sports Directorate",
    "HEALTH_CARE": "Campus Medical Board & Health Center",
    "TRANSPORT": "Commute, Transport Operations & Bus Fleet Desk",
    "OTHER": "Central Student Grievance Redressal Committee (CGRC)"
}

ALLOWED_PRIORITIES = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

# Standard institutional grievance workflow statuses (CPGRAMS / UGC model)
ALLOWED_STATUSES = [
    "SUBMITTED",
    "UNDER_INVESTIGATION",
    "ACTION_TAKEN",
    "RESOLVED"
]

ALLOWED_GRIEVANCE_TYPES = [
    "Facility Breakdown",
    "Living Conditions Failure",
    "Academic Evaluation Dispute",
    "Safety & Security Hazard",
    "Sanitation & Hygiene Violation",
    "Administrative Delay",
    "Code of Conduct / Harassment",
    "Service Outage"
]

ALLOWED_SCOPES = [
    "Individual Student",
    "Group / Class of Students",
    "Floor / Wing of Hostel",
    "Department-wide",
    "Campus-wide"
]
