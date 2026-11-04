/**
 * CampusVoice - Institutional Grievance Redressal Framework
 * Common Definitions, Committee Jurisdictions & Standards
 */

const CV = {
  categories: {
    HOSTEL: "Hostel & Residence Oversight",
    INFRASTRUCTURE: "Physical Works & Estates",
    ELECTRICITY: "Electrical Engineering & Power Utility",
    WATER_SUPPLY: "Public Health & Campus Plumbing",
    CLEANLINESS: "Sanitation & Waste Management",
    MESS_CANTEEN: "Food Quality & Mess Supervisory",
    NETWORK_IT: "Campus IT & Network Computing",
    LABORATORY: "Laboratory Standards & Equipment",
    LIBRARY: "Central Library Advisory Council",
    ACADEMICS: "Dean of Academic Affairs & Faculty",
    EXAMINATION: "Controller of Examinations (COE)",
    SECURITY: "Campus Safety & Proctorial Board",
    SPORTS: "Physical Education & Sports Directorate",
    HEALTH_CARE: "Campus Medical Board & Clinic",
    TRANSPORT: "Transport & Bus Operations Fleet",
    OTHER: "Central Student Grievance Redressal Committee"
  },

  committees: {
    HOSTEL: "Hostel Administration & Residence Oversight Committee",
    INFRASTRUCTURE: "Campus Works, Estates & Physical Infrastructure Cell",
    ELECTRICITY: "Electrical Engineering & Power Utility Services",
    WATER_SUPPLY: "Public Health & Campus Sanitation Division",
    CLEANLINESS: "Sanitation, Waste Management & Environment Committee",
    MESS_CANTEEN: "Food Quality & Mess Supervisory Committee",
    NETWORK_IT: "Campus IT, Network & Computing Resource Center",
    LABORATORY: "Laboratory Standards, Equipment & Safety Committee",
    LIBRARY: "Central Library Advisory & Digital Resources Council",
    ACADEMICS: "Dean of Academic Affairs & Faculty Grievance Board",
    EXAMINATION: "Office of the Controller of Examinations (COE)",
    SECURITY: "Campus Security, Safety & Proctorial Board",
    SPORTS: "Physical Education & Sports Directorate",
    HEALTH_CARE: "Campus Medical Board & Health Center",
    TRANSPORT: "Commute, Transport Operations & Bus Fleet Desk",
    OTHER: "Central Student Grievance Redressal Committee (CGRC)"
  },

  priorities: {
    LOW: "Low (Routine / Maintenance)",
    MEDIUM: "Medium (Operational Disturbance)",
    HIGH: "High (Severe Disruption)",
    CRITICAL: "Critical (Emergency / Safety Hazard)"
  },

  statuses: {
    SUBMITTED: "Submitted (Pending Committee)",
    UNDER_INVESTIGATION: "Under Investigation",
    ACTION_TAKEN: "Action Initiated",
    RESOLVED: "Resolved with ATR"
  },

  grievanceTypes: [
    "Facility Breakdown",
    "Living Conditions Failure",
    "Academic Evaluation Dispute",
    "Safety & Security Hazard",
    "Sanitation & Hygiene Violation",
    "Administrative Delay",
    "Code of Conduct / Harassment",
    "Service Outage"
  ],

  recurrences: [
    "First-Time Occurrence",
    "Repeated / Unresolved Negligence",
    "Chronic / Systemic Defect"
  ],

  scopes: [
    "Individual Student",
    "Group / Class of Students",
    "Floor / Wing of Hostel",
    "Department-wide",
    "Campus-wide"
  ],

  locations: [
    "Hostel Block A",
    "Hostel Block B",
    "Hostel Block C",
    "Hostel Block D",
    "Boys Hostel 1",
    "Boys Hostel 2",
    "Girls Hostel Wing A",
    "Girls Hostel Wing B",
    "Academic Block 1 (ECE & CSE)",
    "Academic Block 2 (Mech & Civil)",
    "Academic Block 3 (Biotech)",
    "Science & Research Block",
    "Computer Lab 1",
    "Computer Lab 2",
    "Robotics & IoT Lab",
    "Mechanical Workshop",
    "Physics & Chemistry Lab",
    "Central Library 1st Floor",
    "Central Library 2nd Floor",
    "Digital Library Hall",
    "Main Cafeteria Courtyard",
    "Hostel Mess Hall A",
    "Hostel Mess Hall B",
    "Indoor Sports Complex & Gym",
    "Campus Health Center / Dispensary",
    "Main Auditorium",
    "Student Activity Center (SAC)",
    "Campus Main Gate & Bus Bay",
    "Admin Block / Registrar Office",
    "Student Parking Lot 1"
  ],

  label(map, key) {
    return map[key] || key || "Unknown";
  },

  when(isoString) {
    if (!isoString) return "-";
    try {
      const d = new Date(isoString);
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return isoString;
    }
  },

  async request(url, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };
    const response = await fetch(url, { ...options, headers });
    if (!response.ok) {
      let errMessage = `Request failed (${response.status})`;
      try {
        const errData = await response.json();
        errMessage = errData.detail || errData.message || errMessage;
      } catch {
        // fallback
      }
      throw new Error(errMessage);
    }
    return response.json();
  }
};
