# 🏛️ CampusVoice – Speak. Detect. Resolve.
### Next-Gen AI Campus Incident Intelligence & Grievance Redressal Platform

> **Hackathon Edition**: Built as a premium, production-grade AI incident platform. Transforms messy student voice complaints into verified institutional dossiers, detects emerging campus infrastructure crises in real time, and equips university administrators with a spatial command center.

---

## ⚡ The Winning 3-Minute Demo Story

Follow these exact steps during your presentation or evaluation to showcase the complete end-to-end intelligence pipeline:

### 1. Natural Voice Incident Capture & AI Clarification
1. Open the **Student Portal** at [`http://127.0.0.1:8000`](http://127.0.0.1:8000).
2. Tap the glowing **3D Animated AI Orb** or the **Start Speaking** button (or click the quick scenario chip: *"⚡ Electricity Outage (Block A)"*).
3. Say:
   > *"Electricity has been unavailable in Block A since morning."*
4. **Watch AI Follow-up in Action**:
   - The AI Orb transitions into a speaking state with cyan glowing ripple rings.
   - CampusVoice AI immediately asks a clarifying follow-up question:
     > *"Is the entire block affected or just one classroom?"*
5. Speak your reply:
   > *"The entire block."*
6. CampusVoice AI responds:
   > *"Understood. I will register this as an electricity disruption affecting Block A."*

### 2. Glassmorphic Structured Dossier & Instant Dispatch
1. A structured incident preview card slides smoothly into view:
   - **Title**: `Electricity Disruption in Block A`
   - **Category**: `ELECTRICITY`
   - **Jurisdiction**: `Electrical Engineering & Power Utility Services`
   - **Severity**: `HIGH`
   - **Location**: `Block A`
   - **Scope**: `Block-wide`
   - **Target SLA**: `24 Hours`
2. Click **🚀 Confirm & Register Incident Dossier**.
3. The platform displays the confirmation badge with Docket ID **`CV-1042`** and CampusVoice AI speaks the voice confirmation out loud.

### 3. Spatial Radar Map & Emerging Incident Detection
1. Click **Inspect on Authority Dashboard →** or open [`http://127.0.0.1:8000/dashboard.html`](http://127.0.0.1:8000/dashboard.html).
2. **Observe the Linear/Vercel-inspired Midnight Navy Command Center**:
   - **Spatial Blueprint Map (Campus Pulse)**:
     - Look at the `Block A` facility node.
     - With 3 active correlated reports (`CV-1031`, `CV-1040`, and your newly filed `CV-1042`), `Block A` has lit up into **CRITICAL** status with **pulsing animated radar wave rings**!
   - **Emerging Incidents & AI Mitigation Panel**:
     - A high-priority banner flashes:
       > **EMERGING INCIDENT DETECTED: Block A**
       > *Electricity Disruption (3 correlated reports within 2 hours)*
       > *AI Recommended Mitigation: Potential main switchgear or transformer fault. Deploy electrical maintenance crew to Block A distribution box immediately.*
   - **One-Click Actions**:
     - Click **⚡ Dispatch Response Crew** to issue dispatch telemetry.
     - Click **🔍 Filter Affected Dockets** or tap the `Block A` box on the map to filter the docket table.
   - **Case Dossier & ATR**:
     - Click **Dossier** on any ticket to view statutory committee particulars, student voice transcript, and file an official **Action Taken Report (ATR)**.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technologies & Design Patterns |
|---|---|
| **Frontend** | Pure HTML5, Modern CSS (Design Tokens, 3D CSS keyframe animations, SVG blueprint, glassmorphism), Vanilla ES6+ JavaScript. **Zero heavy frontend dependencies**. |
| **Voice & Speech Engine** | Web Speech API (`SpeechRecognition` continuous interim transcript + `SpeechSynthesis` conversational voice output + simulated audio waveform visualizer). |
| **Backend** | Python 3.10+, **FastAPI**, Starlette, Uvicorn asynchronous ASGI server. |
| **AI Incident Intelligence** | Google **Gemini 2.5 Flash** (via REST API) + **Deterministic Institutional Rule-based Neural Classifier** with multi-word phrase weighting, word boundary regex, and location normalizers for **100% offline fallback**. |
| **Storage & Persistence** | **SQLite** (`campusvoice.db`) with pre-seeded realistic campus grievances, SLA tracking, Action Taken Reports (ATR), and whistleblower anonymity protection. |

---

## 🚀 Quickstart & Portability

### Option A: 1-Click Launch (Recommended)
- **Windows**: Double-click `start_platform.bat` (or run `.\start_platform.ps1` in PowerShell).
- **Mac / Linux**: Run `chmod +x start_platform.sh && ./start_platform.sh`.

### Option B: Manual Setup
```bash
# 1. Activate virtual environment
python -m venv .venv
source .venv/bin/activate     # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r backend/requirements.txt

# 3. Start server
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```

---

## 🔑 AI API Key Configuration

The platform is designed to be **100% dependable**:
1. **Cloud Inference with Gemini**:
   - Provide a Gemini API key in `backend/.env`:
     ```env
     GEMINI_API_KEY=AIzaSy...
     ```
   - Or open the **Admin Command Center** (`/dashboard.html`), click **⚙️ AI Settings**, paste your Gemini key, and click **Save AI Configuration**.
2. **Offline Mode**:
   - If no key is provided, the platform automatically engages its built-in Institutional Rule-based Neural Engine with zero downtime, zero cost, and zero external network calls.

---

## 📦 Transferring to Another Machine / ID

The project includes an automatic packaging utility:
```bash
python package_project.py
```
This produces `CampusVoice-AI-Platform.zip` (~0.06 MB) containing all code, database seeds, and launchers with zero junk. Simply send this zip to any folder or machine, unzip, and double click `start_platform.bat`!

---

## ⚖️ Compliance & Statutory Standards
CampusVoice aligns with statutory Higher Education Guidelines:
- Departmental redressal committees (Electrical, Public Health, Estates, Proctorial Board).
- SLA timeline tracking (24h emergency, 48h routine).
- Protected whistleblower confidential disclosures.
- Action Taken Report (ATR) audit trails.
