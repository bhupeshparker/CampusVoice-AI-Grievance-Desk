from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator
from .config import ALLOWED_CATEGORIES, ALLOWED_PRIORITIES, ALLOWED_STATUSES, COMMITTEE_MAPPING


class AnalyzeRequest(BaseModel):
    complaint: str = Field(..., min_length=2, description="Raw complaint voice transcript or typed statement")


class AnalyzeResponse(BaseModel):
    summary: str
    category: str
    assignedCommittee: str
    grievanceType: str
    priority: str
    location: Optional[str] = None
    description: str
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    recurrence: str
    affectedScope: str
    reliefSought: str
    priorReported: bool
    aiProcessed: bool
    source: str


class ConversationChatRequest(BaseModel):
    message: str
    conversationState: Optional[Dict[str, Any]] = None


class ConversationChatResponse(BaseModel):
    needsFollowUp: bool
    aiMessage: str
    followUpQuestion: Optional[str] = None
    partialState: Optional[Dict[str, Any]] = None
    analysis: Optional[Dict[str, Any]] = None


class GrievanceCreate(BaseModel):
    summary: str = Field(..., min_length=2)
    category: str
    assignedCommittee: Optional[str] = None
    grievanceType: Optional[str] = "Facility Breakdown"
    priority: str
    location: Optional[str] = None
    description: str = Field(..., min_length=2)
    complaint: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    recurrence: Optional[str] = "First-Time Occurrence"
    affectedScope: Optional[str] = "Individual Student"
    reliefSought: Optional[str] = "Immediate Inspection & Rectification"
    priorReported: Optional[bool] = False
    studentName: Optional[str] = "Demo Student"
    rollNo: Optional[str] = "2023-CS-104"
    isConfidential: Optional[bool] = False
    aiProcessed: Optional[bool] = False

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in ALLOWED_CATEGORIES:
            return "OTHER"
        return v_upper

    @field_validator("priority")
    @classmethod
    def validate_priority(cls, v: str) -> str:
        v_upper = v.upper()
        if v_upper not in ALLOWED_PRIORITIES:
            return "MEDIUM"
        return v_upper


class GrievanceStatusUpdate(BaseModel):
    status: str
    actionTakenReport: Optional[str] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        v_upper = v.upper()
        legacy_map = {
            "NEW": "SUBMITTED",
            "IN_PROGRESS": "UNDER_INVESTIGATION"
        }
        v_mapped = legacy_map.get(v_upper, v_upper)
        if v_mapped not in ALLOWED_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(ALLOWED_STATUSES)}")
        return v_mapped


class GrievanceResponse(BaseModel):
    ticketId: str
    studentName: Optional[str] = None
    rollNo: Optional[str] = None
    isConfidential: bool = False
    complaint: Optional[str] = None
    summary: str
    category: str
    assignedCommittee: str
    grievanceType: str
    priority: str
    location: Optional[str] = None
    description: str
    startTime: Optional[str] = None
    endTime: Optional[str] = None
    recurrence: str
    affectedScope: str
    reliefSought: str
    priorReported: bool
    status: str
    actionTakenReport: Optional[str] = None
    slaHours: int = 48
    aiProcessed: bool
    createdAt: str
    updatedAt: str


class EmergingIncident(BaseModel):
    incidentId: str
    title: str
    category: str
    location: str
    reportCount: int
    severity: str
    status: str
    relatedTicketIds: List[str]
    aiRecommendation: str
    detectedAt: str


class CampusPulseNode(BaseModel):
    id: str
    name: str
    shortName: str
    activeTickets: int
    criticalCount: int
    highCount: int
    status: str
    categoryCounts: Dict[str, int]
    recentTicketIds: List[str]


class SettingsUpdateRequest(BaseModel):
    geminiApiKey: Optional[str] = None
    geminiModel: Optional[str] = None
