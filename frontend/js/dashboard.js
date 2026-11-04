/**
 * CampusVoice - Command Center Dashboard Logic
 * Features:
 * - Spatial Campus Pulse SVG Blueprint Map with dynamic radar beacons
 * - Emerging Incidents & AI Cluster Detection
 * - Real-Time Telemetry Feed & Redressal Queue
 * - Full Institutional Case Dossier & Action Taken Report (ATR)
 * - AI Settings / Gemini API Key Configuration
 */

let tickets = [];
let emergingIncidents = [];
let campusPulseNodes = [];
let activeMapFilter = "";

// Schematic Building Coordinates on 600x480 SVG Canvas
const FACILITY_LAYOUT = {
  "Block A": { x: 45, y: 40, w: 145, h: 95, icon: "🏢" },
  "Block B": { x: 227, y: 40, w: 145, h: 95, icon: "🏢" },
  "Block C": { x: 410, y: 40, w: 145, h: 95, icon: "🏢" },
  "Lab Complex": { x: 45, y: 175, w: 145, h: 95, icon: "🔬" },
  "Main Library": { x: 227, y: 175, w: 145, h: 95, icon: "📚" },
  "Auditorium": { x: 410, y: 175, w: 145, h: 95, icon: "🎭" },
  "Hostel": { x: 45, y: 310, w: 145, h: 95, icon: "🛏️" },
  "Cafeteria": { x: 227, y: 310, w: 145, h: 95, icon: "☕" },
  "Sports Complex": { x: 410, y: 310, w: 145, h: 95, icon: "⚽" }
};

// DOM Elements
const searchInput = document.querySelector("#search");
const categoryFilter = document.querySelector("#filter-category");
const priorityFilter = document.querySelector("#filter-priority");
const statusFilter = document.querySelector("#filter-status");
const locationFilter = document.querySelector("#filter-location");
const statsEl = document.querySelector("#stats");
const emptyEl = document.querySelector("#empty");
const tableBody = document.querySelector("#table-body");
const errorBox = document.querySelector("#error");
const refreshBtn = document.querySelector("#refresh");

const campusNodesLayer = document.querySelector("#campus-nodes-layer");
const emergingListEl = document.querySelector("#emerging-incidents-list");
const clusterCountBadge = document.querySelector("#incident-cluster-count");
const telemetryFeedEl = document.querySelector("#telemetry-feed");
const activeFilterIndicator = document.querySelector("#active-filter-indicator");
const clearMapFilterBtn = document.querySelector("#clear-map-filter");

// Modals
const dossierModal = document.querySelector("#dossier-modal");
const modalClose = document.querySelector("#modal-close");
const modalTicketId = document.querySelector("#modal-ticket-id");
const modalSummary = document.querySelector("#modal-summary");
const modalContent = document.querySelector("#modal-content");

const settingsModal = document.querySelector("#settings-modal");
const openSettingsBtn = document.querySelector("#open-settings-btn");
const settingsClose = document.querySelector("#settings-close");
const saveSettingsBtn = document.querySelector("#save-settings-btn");
const testAiBtn = document.querySelector("#test-ai-btn");
const geminiApiKeyInput = document.querySelector("#gemini-api-key-input");
const settingsEngineName = document.querySelector("#settings-engine-name");
const settingsActiveBadge = document.querySelector("#settings-active-badge");
const settingsNotice = document.querySelector("#settings-notice");
const aiEngineStatusLabel = document.querySelector("#ai-engine-status-label");

function showError(msg) {
  if (errorBox) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
    setTimeout(() => errorBox.classList.add("hidden"), 6000);
  }
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderOptions(map, selected) {
  if (Array.isArray(map)) {
    return [`<option value="">All Filter Options</option>`]
      .concat(map.map((val) => `<option value="${val}" ${val === selected ? "selected" : ""}>${val}</option>`))
      .join("");
  }
  return [`<option value="">All Categories</option>`]
    .concat(
      Object.entries(map).map(
        ([value, label]) => `<option value="${value}" ${value === selected ? "selected" : ""}>${label}</option>`
      )
    )
    .join("");
}

// Populate Filter Dropdowns
if (categoryFilter) categoryFilter.innerHTML = renderOptions(CV.categories, "");
if (priorityFilter) {
  priorityFilter.innerHTML = `
    <option value="">All Priorities</option>
    <option value="CRITICAL">Critical</option>
    <option value="HIGH">High</option>
    <option value="MEDIUM">Medium</option>
    <option value="LOW">Low</option>
  `;
}
if (statusFilter) {
  statusFilter.innerHTML = `
    <option value="">All Statuses</option>
    <option value="SUBMITTED">Submitted</option>
    <option value="UNDER_INVESTIGATION">Under Investigation</option>
    <option value="ACTION_TAKEN">Action Taken</option>
    <option value="RESOLVED">Resolved</option>
  `;
}
if (locationFilter) {
  locationFilter.innerHTML = `
    <option value="">All Campus Locations</option>
    ${Object.keys(FACILITY_LAYOUT).map((loc) => `<option value="${loc}">${loc}</option>`).join("")}
  `;
}

// Main Render Function
function render() {
  const query = searchInput.value.trim().toLowerCase();
  const category = categoryFilter ? categoryFilter.value : "";
  const priority = priorityFilter ? priorityFilter.value : "";
  const status = statusFilter ? statusFilter.value : "";
  const location = (activeMapFilter || (locationFilter ? locationFilter.value : "")).toLowerCase();

  const visible = tickets.filter((t) => {
    const haystack = `${t.ticketId} ${t.summary} ${t.studentName || ""} ${t.rollNo || ""} ${t.assignedCommittee || ""} ${t.location || ""} ${t.description} ${t.complaint || ""} ${t.reliefSought || ""}`.toLowerCase();
    if (query && !haystack.includes(query)) return false;
    if (category && t.category !== category) return false;
    if (priority && t.priority !== priority) return false;
    if (status && t.status !== status) return false;
    if (location && !(t.location || "").toLowerCase().includes(location)) return false;
    return true;
  });

  // Calculate KPI Counts
  const total = tickets.length;
  const activeCount = tickets.filter((t) => t.status === "SUBMITTED" || t.status === "UNDER_INVESTIGATION" || t.status === "NEW" || t.status === "IN_PROGRESS").length;
  const criticalCount = tickets.filter((t) => t.priority === "CRITICAL" || t.priority === "HIGH").length;
  const resolvedCount = tickets.filter((t) => t.status === "RESOLVED" || t.status === "ACTION_TAKEN").length;
  const emergingCount = emergingIncidents.length;
  const slaPct = total > 0 ? Math.round((resolvedCount / total) * 100) : 100;

  statsEl.innerHTML = `
    <article class="admin-kpi-card">
      <div class="kpi-label">Total Grievances Lodged</div>
      <div class="kpi-value">${total}</div>
      <div class="kpi-trend trend-neutral">Statutory Registrations</div>
    </article>
    <article class="admin-kpi-card card-accent-active">
      <div class="kpi-label">Active Campus Disruptions</div>
      <div class="kpi-value val-cyan">${activeCount}</div>
      <div class="kpi-trend trend-active">Under Active Redressal</div>
    </article>
    <article class="admin-kpi-card card-accent-alert">
      <div class="kpi-label">Emerging Incidents Detected</div>
      <div class="kpi-value val-alert">${emergingCount}</div>
      <div class="kpi-trend trend-alert">${emergingCount > 0 ? "⚡ AI Correlation Alerts" : "Normal Campus Baseline"}</div>
    </article>
    <article class="admin-kpi-card">
      <div class="kpi-label">Critical / High Severity</div>
      <div class="kpi-value val-orange">${criticalCount}</div>
      <div class="kpi-trend trend-neutral">High Urgency SLA</div>
    </article>
    <article class="admin-kpi-card">
      <div class="kpi-label">48h SLA Resolution Rate</div>
      <div class="kpi-value val-green">${slaPct}%</div>
      <div class="kpi-trend trend-green">Regulatory Compliance</div>
    </article>
  `;

  // Render Table
  emptyEl.classList.toggle("hidden", visible.length > 0);

  tableBody.innerHTML = visible.map((t) => `
    <tr id="row-${t.ticketId}" class="table-row-modern ${t.ticketId === activeFocusTicket ? 'row-focused' : ''}">
      <td>
        <span class="docket-tag">${t.ticketId}</span>
        <div class="meta-date">${CV.when(t.createdAt)}</div>
      </td>
      <td>
        <strong>${t.isConfidential ? "🔒 Confidential" : escapeHtml(t.studentName || "Demo Student")}</strong>
        <div class="meta-roll">${t.isConfidential ? "Protected Whistleblower" : escapeHtml(t.rollNo || "2023-CS-104")}</div>
      </td>
      <td>
        <div class="row-summary">${escapeHtml(t.summary)}</div>
        <div class="row-meta-sub">
          <span class="loc-badge">📍 ${escapeHtml(t.location || "General Campus")}</span>
          ${t.startTime ? `<span class="time-badge">⏱️ Inception: ${CV.when(t.startTime)}</span>` : ""}
        </div>
        ${t.complaint ? `<div class="row-quote">🎙️ “${escapeHtml(t.complaint)}”</div>` : ""}
      </td>
      <td>
        <span class="committee-cell">${escapeHtml(t.assignedCommittee || CV.committees[t.category] || "Central Redressal Cell")}</span>
        <div class="meta-sla">Target SLA: ${t.slaHours || 48}h</div>
      </td>
      <td>
        <span class="pill ${t.priority}">${t.priority}</span>
      </td>
      <td>
        <div class="relief-text" title="${escapeHtml(t.reliefSought || "")}">${escapeHtml(t.reliefSought || "Immediate Rectification")}</div>
        <div class="meta-recurrence">${escapeHtml(t.recurrence || "First-Time")}</div>
      </td>
      <td>
        <select class="status-select-modern ${t.status}" data-ticket="${t.ticketId}">
          <option value="SUBMITTED" ${t.status === "SUBMITTED" ? "selected" : ""}>Submitted</option>
          <option value="UNDER_INVESTIGATION" ${t.status === "UNDER_INVESTIGATION" ? "selected" : ""}>Under Investigation</option>
          <option value="ACTION_TAKEN" ${t.status === "ACTION_TAKEN" ? "selected" : ""}>Action Taken</option>
          <option value="RESOLVED" ${t.status === "RESOLVED" ? "selected" : ""}>Resolved with ATR</option>
        </select>
        ${t.actionTakenReport ? `<div class="atr-pill" title="${escapeHtml(t.actionTakenReport)}">📄 ATR Recorded</div>` : ""}
      </td>
      <td>
        <button class="dossier-view-btn" data-dossier="${t.ticketId}">Dossier</button>
      </td>
    </tr>
  `).join("");

  // Update active filter badge
  if (activeMapFilter) {
    activeFilterIndicator.innerHTML = `Filtering by Facility: <b>${escapeHtml(activeMapFilter)}</b>`;
    clearMapFilterBtn.classList.remove("hidden");
  } else {
    activeFilterIndicator.innerHTML = `Viewing: <b>All Locations (${visible.length} dockets)</b>`;
    clearMapFilterBtn.classList.add("hidden");
  }
}

let activeFocusTicket = null;

// Render Campus Pulse SVG Nodes
function renderCampusPulseMap() {
  if (!campusNodesLayer) return;

  const nodeElements = Object.entries(FACILITY_LAYOUT).map(([locName, coord]) => {
    // Find node status from pulse data
    const pulseData = campusPulseNodes.find((n) => 
      (n.id && n.id.toLowerCase() === locName.toLowerCase()) || 
      (n.name && n.name.toLowerCase() === locName.toLowerCase()) ||
      (n.shortName && n.shortName.toLowerCase().includes(locName.toLowerCase()))
    ) || {
      id: locName,
      name: locName,
      activeTickets: 0,
      activeComplaints: 0,
      status: "NORMAL"
    };

    const count = pulseData.activeTickets !== undefined ? pulseData.activeTickets : (pulseData.activeComplaints || 0);
    const isCritical = pulseData.status === "CRITICAL" || count >= 3;
    const isElevated = pulseData.status === "ELEVATED" || count >= 1;

    let statusClass = "node-normal";
    let statusColor = "#10b981"; // green
    if (isCritical) {
      statusClass = "node-critical";
      statusColor = "#ef4444"; // red
    } else if (isElevated) {
      statusClass = "node-elevated";
      statusColor = "#f59e0b"; // amber
    }

    const isSelected = activeMapFilter.toLowerCase() === locName.toLowerCase();

    return `
      <g class="campus-node-group ${statusClass} ${isSelected ? 'node-selected' : ''}" data-facility="${locName}" transform="translate(${coord.x}, ${coord.y})" cursor="pointer">
        <!-- Node Box Card -->
        <rect class="node-box" width="${coord.w}" height="${coord.h}" rx="8" ry="8" />

        <!-- Facility Header -->
        <text x="14" y="24" class="node-icon">${coord.icon}</text>
        <text x="36" y="24" class="node-title">${locName}</text>

        <!-- Status & Count Subtext -->
        <text x="14" y="52" class="node-sub">${count === 0 ? 'Status: Normal' : `${count} Active ${count === 1 ? 'Report' : 'Reports'}`}</text>
        <text x="14" y="70" class="node-category">${pulseData.primaryCategory || (count > 0 ? 'Active Redressal' : 'Facility Nominal')}</text>

        <!-- Pulsing Hotspot Radar Indicator (Top Right of Card) -->
        <g class="hotspot-beacon" transform="translate(${coord.w - 20}, 20)">
          ${isCritical ? `
            <!-- Animated Expanding Radar Wave Rings -->
            <circle cx="0" cy="0" r="16" class="radar-wave wave-1" />
            <circle cx="0" cy="0" r="10" class="radar-wave wave-2" />
          ` : isElevated ? `
            <circle cx="0" cy="0" r="8" class="radar-wave wave-amber" />
          ` : ''}
          <circle cx="0" cy="0" r="5" fill="${statusColor}" class="hotspot-core" />
        </g>
      </g>
    `;
  });

  campusNodesLayer.innerHTML = nodeElements.join("");

  // Attach click listener for facility nodes
  campusNodesLayer.querySelectorAll(".campus-node-group").forEach((group) => {
    group.addEventListener("click", () => {
      const facility = group.dataset.facility;
      if (activeMapFilter.toLowerCase() === facility.toLowerCase()) {
        activeMapFilter = "";
      } else {
        activeMapFilter = facility;
      }
      renderCampusPulseMap();
      render();
    });
  });
}

// Render Emerging Incidents List
function renderEmergingIncidents() {
  if (!emergingListEl) return;

  clusterCountBadge.textContent = `${emergingIncidents.length} Detected`;
  clusterCountBadge.className = `cluster-badge ${emergingIncidents.length > 0 ? 'badge-alert' : ''}`;

  if (emergingIncidents.length === 0) {
    emergingListEl.innerHTML = `
      <div class="empty-incidents-box">
        <span class="icon-nominal">🛡️</span>
        <h4>All Campus Sectors Operating Within Baseline</h4>
        <p>No anomalous complaint spikes or multi-student clusters detected in the last 24 hours.</p>
      </div>
    `;
    return;
  }

  emergingListEl.innerHTML = emergingIncidents.map((inc) => {
    const reportCount = inc.reportCount !== undefined ? inc.reportCount : (inc.complaintCount || 3);
    const recommendation = inc.aiRecommendation || inc.recommendedAction || "Recommend immediate emergency response crew inspection.";
    const timeWin = inc.timeWindow || "Active Incident Window";

    return `
    <div class="incident-alert-card incident-${inc.severity.toLowerCase()}">
      <div class="incident-card-top">
        <span class="incident-pulsing-badge">
          <span class="pulse-dot"></span> EMERGING INCIDENT DETECTED
        </span>
        <span class="incident-time-badge">${timeWin}</span>
      </div>

      <h3 class="incident-headline">${escapeHtml(inc.title)}</h3>

      <div class="incident-metrics-row">
        <span>📍 Location: <b>${escapeHtml(inc.location)}</b></span>
        <span>👥 Correlated Reports: <b>${reportCount}</b></span>
        <span>⚡ Department: <b>${escapeHtml(inc.category)}</b></span>
      </div>

      <div class="incident-ai-recommendation">
        <div class="rec-title">🤖 AI Incident Intelligence & Mitigation:</div>
        <p class="rec-body">${escapeHtml(recommendation)}</p>
      </div>

      <div class="incident-actions-bar">
        <button class="btn-incident-action dispatch-crew" data-location="${escapeHtml(inc.location)}" data-category="${escapeHtml(inc.category)}">
          ⚡ Dispatch Response Crew
        </button>
        <button class="btn-incident-action filter-cluster" data-location="${escapeHtml(inc.location)}">
          🔍 Filter Affected Dockets
        </button>
      </div>
    </div>
  `;
  }).join("");

  // Attach action buttons
  emergingListEl.querySelectorAll(".filter-cluster").forEach((btn) => {
    btn.addEventListener("click", () => {
      activeMapFilter = btn.dataset.location;
      renderCampusPulseMap();
      render();
      document.querySelector(".queue-card").scrollIntoView({ behavior: "smooth" });
    });
  });

  emergingListEl.querySelectorAll(".dispatch-crew").forEach((btn) => {
    btn.addEventListener("click", () => {
      alert(`Automated dispatch order transmitted to ${btn.dataset.category} emergency response team for ${btn.dataset.location}. SLA priority escalated.`);
    });
  });
}

// Render Live Telemetry Feed
function renderTelemetryFeed() {
  if (!telemetryFeedEl) return;

  const recent = tickets.slice(0, 6);
  telemetryFeedEl.innerHTML = recent.map((t) => `
    <div class="telemetry-item">
      <div class="telemetry-item-time">${CV.when(t.createdAt)}</div>
      <div class="telemetry-item-msg">
        <span class="telemetry-id">${t.ticketId}</span>
        <span class="telemetry-text">${escapeHtml(t.summary)}</span>
      </div>
      <div class="telemetry-sub">📍 ${escapeHtml(t.location || "General Campus")} • <span class="pill-mini ${t.priority}">${t.priority}</span></div>
    </div>
  `).join("");
}

// Load Data from Backend
async function load() {
  try {
    const [fetchedTickets, fetchedIncidents, fetchedPulse, fetchedSettings] = await Promise.all([
      CV.request("/api/grievances"),
      CV.request("/api/incidents/emerging"),
      CV.request("/api/campus/pulse"),
      CV.request("/api/settings").catch(() => ({ hasGeminiKey: false, activeEngine: "Neural Fallback" }))
    ]);

    tickets = fetchedTickets;
    emergingIncidents = fetchedIncidents;
    campusPulseNodes = fetchedPulse;

    if (fetchedSettings && fetchedSettings.hasGeminiKey) {
      aiEngineStatusLabel.textContent = "AI DETECTOR: GEMINI ONLINE";
    } else {
      aiEngineStatusLabel.textContent = "AI DETECTOR: OFFLINE NEURAL";
    }

    // Check focus query param
    const focus = new URLSearchParams(window.location.search).get("ticket");
    if (focus) {
      activeFocusTicket = focus;
    }

    renderCampusPulseMap();
    renderEmergingIncidents();
    renderTelemetryFeed();
    render();

    if (focus) {
      setTimeout(() => {
        const row = document.querySelector(`#row-${CSS.escape(focus)}`);
        if (row) {
          row.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 250);
    }
  } catch (err) {
    showError(err.message || "Failed to load real-time telemetry from authority server.");
  }
}

// Inline Status Update Handler
tableBody.addEventListener("change", async (event) => {
  const select = event.target.closest("select[data-ticket]");
  if (!select) return;
  const ticketId = select.dataset.ticket;
  const previous = tickets.find((t) => t.ticketId === ticketId)?.status;
  const newStatus = select.value;
  select.disabled = true;

  let atrText = null;
  if (newStatus === "RESOLVED" || newStatus === "ACTION_TAKEN") {
    atrText = prompt(
      `Enter Statutory Action Taken Report (ATR) summary for Docket ${ticketId}:`,
      "On-site inspection completed. Emergency maintenance work executed and verified."
    );
    if (!atrText) {
      select.value = previous;
      select.disabled = false;
      return;
    }
  }

  try {
    const updated = await CV.request(`/api/grievances/${ticketId}/status`, {
      method: "PATCH",
      body: JSON.stringify({
        status: newStatus,
        actionTakenReport: atrText
      })
    });
    tickets = tickets.map((t) => (t.ticketId === ticketId ? updated : t));
    await load();
  } catch (error) {
    select.value = previous;
    showError(error.message || "Status was not updated.");
  } finally {
    select.disabled = false;
  }
});

// View Full Dossier Modal Handler
tableBody.addEventListener("click", (e) => {
  const btn = e.target.closest("button[data-dossier]");
  if (!btn) return;
  const ticketId = btn.dataset.dossier;
  const t = tickets.find((item) => item.ticketId === ticketId);
  if (!t || !dossierModal) return;

  modalTicketId.textContent = t.ticketId;
  modalSummary.textContent = t.summary;

  modalContent.innerHTML = `
    <div class="dossier-grid">
      <div class="dossier-card">
        <h3>🏛️ Jurisdiction & Statutory Committee</h3>
        <p><strong>Department:</strong> ${CV.label(CV.categories, t.category)}</p>
        <p><strong>Designated Committee:</strong> ${escapeHtml(t.assignedCommittee || CV.committees[t.category] || "Central Cell")}</p>
        <p><strong>Statutory SLA:</strong> ${t.slaHours || 48} Hours Target</p>
      </div>

      <div class="dossier-card">
        <h3>📍 Location & Temporal Timeline</h3>
        <p><strong>Campus Location:</strong> ${escapeHtml(t.location || "General Campus")}</p>
        <p><strong>Incident Inception:</strong> ${CV.when(t.startTime)}</p>
        <p><strong>Registration Timestamp:</strong> ${CV.when(t.createdAt)}</p>
        <p><strong>Recurrence Record:</strong> ${escapeHtml(t.recurrence || "First-Time Occurrence")}</p>
      </div>

      <div class="dossier-card">
        <h3>👥 Impact & Relief Sought</h3>
        <p><strong>Affected Community:</strong> ${escapeHtml(t.affectedScope || "Individual Student")}</p>
        <p><strong>Nature of Grievance:</strong> ${escapeHtml(t.grievanceType || "Facility Breakdown")}</p>
        <p><strong>Severity Priority:</strong> <span class="pill ${t.priority}">${t.priority}</span></p>
        <p><strong>Specific Relief Requested:</strong> ${escapeHtml(t.reliefSought || "Immediate Rectification")}</p>
      </div>

      <div class="dossier-card">
        <h3>🧑‍🎓 Complainant Particulars</h3>
        <p><strong>Student Name:</strong> ${t.isConfidential ? "🔒 PROTECTED (Confidential Disclosure)" : escapeHtml(t.studentName || "Demo Student")}</p>
        <p><strong>Roll / Reg. No:</strong> ${t.isConfidential ? "REDACTED" : escapeHtml(t.rollNo || "2023-CS-104")}</p>
        <p><strong>Prior Local Notice:</strong> ${t.priorReported ? "Yes (Informed caretaker/warden)" : "No"}</p>
        <p><strong>AI Verified:</strong> ${t.aiProcessed ? "Yes (Speech Intent Engine)" : "Manual"}</p>
      </div>

      <div class="dossier-card wide">
        <h3>🎙️ Verbatim Student Voice Testimony</h3>
        <div class="dossier-quote">${escapeHtml(t.complaint || t.description || "No verbatim transcript recorded.")}</div>
      </div>

      <div class="dossier-card wide">
        <h3>📋 Comprehensive Factual Particulars</h3>
        <p>${escapeHtml(t.description)}</p>
      </div>

      <div class="dossier-card wide ${t.actionTakenReport ? 'atr-card' : 'atr-pending'}">
        <h3>📄 Action Taken Report (ATR)</h3>
        ${t.actionTakenReport ? `
          <div class="atr-text">“${escapeHtml(t.actionTakenReport)}”</div>
          <div class="atr-meta">Formally entered into University Redressal Record.</div>
        ` : `
          <p>No Action Taken Report has been filed yet. Change status to 'Action Taken' or 'Resolved' to record official ATR.</p>
        `}
      </div>
    </div>
  `;

  dossierModal.showModal();
});

modalClose.addEventListener("click", () => {
  dossierModal.close();
});

dossierModal.addEventListener("click", (e) => {
  if (e.target === dossierModal) dossierModal.close();
});

// AI Settings Modal Handlers
if (openSettingsBtn && settingsModal) {
  openSettingsBtn.addEventListener("click", async () => {
    try {
      const cfg = await CV.request("/api/settings");
      if (cfg.hasGeminiKey) {
        settingsEngineName.textContent = "Google Gemini 2.5 Flash (Active Cloud Inference)";
        settingsActiveBadge.textContent = "Cloud Active";
        settingsActiveBadge.className = "badge-active";
      } else {
        settingsEngineName.textContent = "Institutional Neural Rule Engine (Offline Active)";
        settingsActiveBadge.textContent = "Offline Active";
        settingsActiveBadge.className = "badge-offline";
      }
    } catch (_) {}
    settingsModal.showModal();
  });

  settingsClose.addEventListener("click", () => settingsModal.close());
  settingsModal.addEventListener("click", (e) => {
    if (e.target === settingsModal) settingsModal.close();
  });

  saveSettingsBtn.addEventListener("click", async () => {
    const key = geminiApiKeyInput.value.trim();
    saveSettingsBtn.disabled = true;
    saveSettingsBtn.textContent = "Saving...";

    try {
      const res = await CV.request("/api/settings", {
        method: "POST",
        body: JSON.stringify({ geminiApiKey: key })
      });
      settingsNotice.textContent = res.message || "Settings updated successfully!";
      settingsNotice.className = "settings-notice success";
      settingsNotice.classList.remove("hidden");
      await load();
      setTimeout(() => {
        settingsModal.close();
        settingsNotice.classList.add("hidden");
      }, 1500);
    } catch (err) {
      settingsNotice.textContent = err.message || "Failed to save settings.";
      settingsNotice.className = "settings-notice error";
      settingsNotice.classList.remove("hidden");
    } finally {
      saveSettingsBtn.disabled = false;
      saveSettingsBtn.textContent = "Save AI Configuration";
    }
  });

  testAiBtn.addEventListener("click", async () => {
    testAiBtn.disabled = true;
    testAiBtn.textContent = "Testing...";
    try {
      const testRes = await CV.request("/api/conversation/chat", {
        method: "POST",
        body: JSON.stringify({
          message: "Electricity is unavailable in Block A since morning."
        })
      });
      settingsNotice.textContent = `Test Success! Engine response: "${testRes.aiMessage}"`;
      settingsNotice.className = "settings-notice success";
      settingsNotice.classList.remove("hidden");
    } catch (err) {
      settingsNotice.textContent = `Test failed: ${err.message}`;
      settingsNotice.className = "settings-notice error";
      settingsNotice.classList.remove("hidden");
    } finally {
      testAiBtn.disabled = false;
      testAiBtn.textContent = "Test AI Response";
    }
  });
}

// Clear Map Filter Button
clearMapFilterBtn.addEventListener("click", () => {
  activeMapFilter = "";
  renderCampusPulseMap();
  render();
});

// Event Listeners for Filters & Search
searchInput.addEventListener("input", render);
categoryFilter.addEventListener("change", render);
priorityFilter.addEventListener("change", render);
statusFilter.addEventListener("change", render);
locationFilter.addEventListener("change", (e) => {
  activeMapFilter = e.target.value;
  renderCampusPulseMap();
  render();
});

refreshBtn.addEventListener("click", load);

// Auto-refresh telemetry every 20 seconds
setInterval(load, 20000);

// Initial Load
document.addEventListener("DOMContentLoaded", load);
