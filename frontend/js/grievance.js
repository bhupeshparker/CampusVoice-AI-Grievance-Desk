/**
 * CampusVoice - Voice AI Concierge & Incident Registration Flow
 * Features:
 * - 3D AI Orb state manager (idle, listening, processing, speaking)
 * - Conversational follow-up question flow (Block A scope question, etc.)
 * - Live transcription captioning & Audio Waveform animation
 * - Structured Incident Preview Card & Institutional Dossier dispatch
 * - Voice speech synthesis confirmation
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements: Orb & AI Interaction
  const orb = document.querySelector("#ai-orb");
  const micButton = document.querySelector("#mic");
  const stopButton = document.querySelector("#stop-listening-btn");
  const aiStatusBadge = document.querySelector("#ai-status-badge");
  const aiStatusText = document.querySelector("#ai-status-text");
  const liveCaptionBox = document.querySelector("#live-caption-box");
  const liveCaptionText = document.querySelector("#live-caption-text");
  const complaintInput = document.querySelector("#complaint");
  const analyzeButton = document.querySelector("#analyze");
  const chatStreamSection = document.querySelector("#chat-stream-section");
  const chatMessages = document.querySelector("#chat-messages");
  const aiTypingIndicator = document.querySelector("#ai-typing-indicator");

  // Elements: Preview Card
  const previewSection = document.querySelector("#preview-card-section");
  const previewTitle = document.querySelector("#preview-title");
  const previewPriorityPill = document.querySelector("#preview-priority-pill");
  const previewCategoryPill = document.querySelector("#preview-category-pill");
  const previewLocation = document.querySelector("#preview-location");
  const previewCommittee = document.querySelector("#preview-committee");
  const previewScope = document.querySelector("#preview-scope");
  const previewType = document.querySelector("#preview-type");
  const previewRelief = document.querySelector("#preview-relief");
  const previewDescription = document.querySelector("#preview-description");
  const previewStudentName = document.querySelector("#preview-student-name");
  const previewRollNo = document.querySelector("#preview-roll-no");
  const previewConfidential = document.querySelector("#preview-confidential");
  const confirmSubmitBtn = document.querySelector("#confirm-submit-btn");
  const toggleDetailedBtn = document.querySelector("#toggle-detailed-form-btn");
  const resetConversationBtn = document.querySelector("#reset-conversation-btn");

  // Elements: Detailed Form (Collapsible)
  const reviewPanel = document.querySelector("#review");
  const hideDetailedBtn = document.querySelector("#hide-detailed-btn");
  const reviewComplaintInput = document.querySelector("#review-complaint-input");
  const submitButton = document.querySelector("#submit");
  const errorBox = document.querySelector("#error");

  const fields = {
    summary: document.querySelector("#summary"),
    category: document.querySelector("#category"),
    assignedCommittee: document.querySelector("#assigned-committee"),
    grievanceType: document.querySelector("#grievance-type"),
    priority: document.querySelector("#priority"),
    startTime: document.querySelector("#start-time"),
    endTime: document.querySelector("#end-time"),
    recurrence: document.querySelector("#recurrence"),
    priorReported: document.querySelector("#prior-reported"),
    affectedScope: document.querySelector("#affected-scope"),
    reliefSought: document.querySelector("#relief-sought"),
    location: document.querySelector("#location"),
    description: document.querySelector("#description")
  };

  // Elements: Success Screen
  const successPanel = document.querySelector("#success");
  const ticketIdEl = document.querySelector("#ticket-id");
  const ticketMetaEl = document.querySelector("#ticket-meta");
  const ticketCommitteeMetaEl = document.querySelector("#ticket-committee-meta");
  const ticketTimeMetaEl = document.querySelector("#ticket-time-meta");
  const ticketReliefMetaEl = document.querySelector("#ticket-relief-meta");
  const loggedQuoteEl = document.querySelector("#logged-quote");
  const dashboardLink = document.querySelector("#dashboard-link");
  const anotherButton = document.querySelector("#another");

  // State
  let conversationState = null;
  let currentAnalysis = null;
  let fullVerbatimTestimony = "";
  let isListening = false;
  let debounceSyncTimer = null;

  function setOrbState(state, message) {
    orb.classList.remove("state-idle", "state-listening", "state-processing", "state-speaking");
    orb.classList.add(`state-${state}`);

    if (message) {
      aiStatusText.textContent = message;
    }

    if (state === "listening") {
      micButton.classList.add("hidden");
      stopButton.classList.remove("hidden");
      liveCaptionBox.classList.remove("hidden");
    } else {
      micButton.classList.remove("hidden");
      stopButton.classList.add("hidden");
      if (state === "idle") {
        setTimeout(() => {
          if (!isListening) liveCaptionBox.classList.add("hidden");
        }, 3000);
      }
    }
  }

  function appendChatMessage(sender, text) {
    chatStreamSection.classList.remove("hidden");
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble chat-bubble-${sender}`;

    const author = document.createElement("div");
    author.className = "chat-bubble-author";
    author.textContent = sender === "user" ? "You (Student)" : "CampusVoice AI";

    const body = document.createElement("div");
    body.className = "chat-bubble-text";
    body.textContent = text;

    bubble.appendChild(author);
    bubble.appendChild(body);
    chatMessages.appendChild(bubble);

    // Smooth scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  // Populate Dropdown Menus for Detailed Form
  function renderOptions(map, selected) {
    if (Array.isArray(map)) {
      return map
        .map((val) => `<option value="${val}" ${val === selected ? "selected" : ""}>${val}</option>`)
        .join("");
    }
    return Object.entries(map)
      .map(([value, label]) => `<option value="${value}" ${value === selected ? "selected" : ""}>${label}</option>`)
      .join("");
  }

  if (fields.category) {
    fields.category.innerHTML = renderOptions(CV.categories, "ELECTRICITY");
    fields.priority.innerHTML = renderOptions(CV.priorities, "HIGH");
    fields.grievanceType.innerHTML = renderOptions(CV.grievanceTypes, "Service Outage");
    fields.recurrence.innerHTML = renderOptions(CV.recurrences, "First-Time Occurrence");
    fields.affectedScope.innerHTML = renderOptions(CV.scopes, "Department-wide");
    fields.assignedCommittee.value = CV.committees["ELECTRICITY"];

    fields.category.addEventListener("change", () => {
      fields.assignedCommittee.value = CV.committees[fields.category.value] || "Central Student Grievance Redressal Committee";
    });
  }

  // Populate popular location chips in detailed form
  const blockChipsContainer = document.querySelector("#block-chips");
  const popularBlocks = [
    "Block A",
    "Block B",
    "Block C",
    "Main Library",
    "Hostel",
    "Cafeteria",
    "Auditorium",
    "Lab Complex",
    "Sports Complex"
  ];

  if (blockChipsContainer) {
    blockChipsContainer.innerHTML = popularBlocks
      .map((blk) => `<button type="button" class="block-chip-btn" data-block="${blk}">${blk}</button>`)
      .join("");

    blockChipsContainer.addEventListener("click", (e) => {
      const btn = e.target.closest("button[data-block]");
      if (!btn) return;
      fields.location.value = btn.dataset.block;
      if (previewLocation) previewLocation.textContent = `📍 ${btn.dataset.block}`;
    });
  }

  // Send message turn to backend conversational endpoint
  async function sendTurn(userText) {
    if (!userText || !userText.trim()) return;
    const cleanText = userText.trim();

    appendChatMessage("user", cleanText);
    fullVerbatimTestimony = fullVerbatimTestimony ? `${fullVerbatimTestimony}. ${cleanText}` : cleanText;
    complaintInput.value = "";
    liveCaptionText.textContent = "";

    setOrbState("processing", "AI is analyzing campus incident...");
    aiTypingIndicator.classList.remove("hidden");

    try {
      const response = await CV.request("/api/conversation/chat", {
        method: "POST",
        body: JSON.stringify({
          message: cleanText,
          conversationState: conversationState
        })
      });

      aiTypingIndicator.classList.add("hidden");

      if (response.needsFollowUp) {
        // AI asks a clarifying follow-up question
        conversationState = response.partialState;
        appendChatMessage("ai", response.aiMessage);
        setOrbState("speaking", "CampusVoice speaking...");

        await window.voiceEngine.speak(response.aiMessage);

        setOrbState("listening", "Listening for your reply...");
        // Auto-listen for the student's answer
        startVoiceListening();
      } else {
        // Conversation complete! AI generated full incident dossier
        conversationState = null;
        currentAnalysis = response.analysis;
        appendChatMessage("ai", response.aiMessage);
        setOrbState("speaking", "CampusVoice speaking...");

        // Render structured preview card
        renderPreviewCard(response.analysis);

        await window.voiceEngine.speak(response.aiMessage);
        setOrbState("idle", "Incident structured. Review details below.");
      }
    } catch (err) {
      aiTypingIndicator.classList.add("hidden");
      setOrbState("idle", "Error processing statement.");
      showError(err.message || "Failed to process message with AI Concierge.");
    }
  }

  function renderPreviewCard(analysis) {
    if (!analysis) return;

    previewTitle.textContent = analysis.summary || "Campus Incident Dossier";
    previewCategoryPill.textContent = analysis.category || "GENERAL";
    previewPriorityPill.textContent = analysis.priority || "MEDIUM";
    previewPriorityPill.className = `pill ${analysis.priority || "MEDIUM"}`;
    previewLocation.textContent = `📍 ${analysis.location || "Block A"}`;
    previewCommittee.textContent = `🏛️ ${analysis.assignedCommittee || "Designated Redressal Committee"}`;
    previewScope.textContent = `👥 ${analysis.affectedScope || "Block-wide"}`;
    previewType.textContent = `⚡ ${analysis.grievanceType || "Facility Breakdown"}`;
    previewRelief.textContent = analysis.reliefSought || "Immediate inspection & rectification";
    previewDescription.textContent = analysis.description || fullVerbatimTestimony;

    // Prefill the collapsible detailed form as well
    if (fields.summary) {
      fields.summary.value = analysis.summary || "";
      fields.category.value = analysis.category || "ELECTRICITY";
      fields.assignedCommittee.value = analysis.assignedCommittee || CV.committees[analysis.category] || "";
      fields.grievanceType.value = analysis.grievanceType || "Service Outage";
      fields.priority.value = analysis.priority || "HIGH";
      fields.location.value = analysis.location || "Block A";
      fields.affectedScope.value = analysis.affectedScope || "Department-wide";
      fields.reliefSought.value = analysis.reliefSought || "";
      fields.description.value = analysis.description || fullVerbatimTestimony;
      if (reviewComplaintInput) reviewComplaintInput.value = fullVerbatimTestimony;
    }

    previewSection.classList.remove("hidden");
    previewSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function startVoiceListening() {
    isListening = true;
    window.voiceEngine.startListening({
      initialText: "",
      onTranscript: (text) => {
        liveCaptionText.textContent = text;
        liveCaptionBox.classList.remove("hidden");
      },
      onStateChange: (active, stateName) => {
        if (active) {
          if (stateName.startsWith("extending")) {
            setOrbState("listening", "Finalizing listening in 2s...");
          } else {
            setOrbState("listening", "Listening to your voice...");
          }
        } else {
          isListening = false;
        }
      },
      onFinalComplete: (finalSpeech) => {
        isListening = false;
        setOrbState("processing", "Speech captured. Processing...");
        sendTurn(finalSpeech);
      },
      onError: (errMsg) => {
        isListening = false;
        setOrbState("idle", "Voice capture paused.");
        showError(errMsg);
      }
    });
  }

  function stopVoiceListening() {
    isListening = false;
    window.voiceEngine.stopListeningImmediately();
    setOrbState("idle", "Microphone stopped.");
  }

  // Click Orb or Mic Button to toggle voice recording
  orb.addEventListener("click", () => {
    if (isListening) {
      stopVoiceListening();
    } else {
      startVoiceListening();
    }
  });

  micButton.addEventListener("click", () => {
    startVoiceListening();
  });

  stopButton.addEventListener("click", () => {
    stopVoiceListening();
  });

  // Typed input handler
  analyzeButton.addEventListener("click", () => {
    const text = complaintInput.value.trim();
    if (text) sendTurn(text);
  });

  complaintInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const text = complaintInput.value.trim();
      if (text) sendTurn(text);
    }
  });

  // Demo scenario chips
  document.querySelectorAll(".scenario-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      const hint = chip.dataset.hint;
      complaintInput.value = hint;
      sendTurn(hint);
    });
  });

  // Toggle Granular Institutional Form
  toggleDetailedBtn.addEventListener("click", () => {
    const isHidden = reviewPanel.classList.contains("hidden");
    reviewPanel.classList.toggle("hidden", !isHidden);
    toggleDetailedBtn.textContent = isHidden ? "▲ Collapse Detailed Form" : "⚙️ Edit Granular Institutional Form";
    if (isHidden) {
      reviewPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    }
  });

  if (hideDetailedBtn) {
    hideDetailedBtn.addEventListener("click", () => {
      reviewPanel.classList.add("hidden");
      toggleDetailedBtn.textContent = "⚙️ Edit Granular Institutional Form";
    });
  }

  // Reset Conversation
  resetConversationBtn.addEventListener("click", () => {
    conversationState = null;
    currentAnalysis = null;
    fullVerbatimTestimony = "";
    chatMessages.innerHTML = "";
    chatStreamSection.classList.add("hidden");
    previewSection.classList.add("hidden");
    reviewPanel.classList.add("hidden");
    complaintInput.value = "";
    liveCaptionText.textContent = "";
    setOrbState("idle", "Ready — Tap Orb or Speak Button to Start");
  });

  // Confirm and Register Incident Dossier
  async function submitGrievance() {
    confirmSubmitBtn.disabled = true;
    confirmSubmitBtn.textContent = "Registering Incident...";

    const payload = {
      summary: (fields.summary && fields.summary.value) || (currentAnalysis && currentAnalysis.summary) || "Campus Incident Dossier",
      category: (fields.category && fields.category.value) || (currentAnalysis && currentAnalysis.category) || "ELECTRICITY",
      assignedCommittee: (fields.assignedCommittee && fields.assignedCommittee.value) || (currentAnalysis && currentAnalysis.assignedCommittee) || "Electrical Engineering & Power Utility Services",
      grievanceType: (fields.grievanceType && fields.grievanceType.value) || (currentAnalysis && currentAnalysis.grievanceType) || "Service Outage",
      priority: (fields.priority && fields.priority.value) || (currentAnalysis && currentAnalysis.priority) || "HIGH",
      location: (fields.location && fields.location.value) || (currentAnalysis && currentAnalysis.location) || "Block A",
      description: (fields.description && fields.description.value) || (currentAnalysis && currentAnalysis.description) || fullVerbatimTestimony,
      complaint: fullVerbatimTestimony || (fields.description && fields.description.value),
      startTime: (fields.startTime && fields.startTime.value) || new Date().toISOString(),
      endTime: fields.endTime ? fields.endTime.value : null,
      recurrence: (fields.recurrence && fields.recurrence.value) || "First-Time Occurrence",
      affectedScope: (fields.affectedScope && fields.affectedScope.value) || (currentAnalysis && currentAnalysis.affectedScope) || "Block-wide",
      reliefSought: (fields.reliefSought && fields.reliefSought.value) || (currentAnalysis && currentAnalysis.reliefSought) || "Immediate restoration of electricity and maintenance inspection",
      priorReported: fields.priorReported ? fields.priorReported.checked : false,
      studentName: previewStudentName.value.trim() || "Demo Student",
      rollNo: previewRollNo.value.trim() || "2023-CS-104",
      isConfidential: previewConfidential.checked,
      aiProcessed: true
    };

    try {
      const created = await CV.request("/api/grievances", {
        method: "POST",
        body: JSON.stringify(payload)
      });

      // Hide interaction panels
      document.querySelector(".concierge-orb-section").classList.add("hidden");
      chatStreamSection.classList.add("hidden");
      previewSection.classList.add("hidden");
      reviewPanel.classList.add("hidden");

      // Show success screen
      ticketIdEl.textContent = created.ticketId;
      ticketMetaEl.textContent = created.location || "Campus Facility";
      ticketCommitteeMetaEl.textContent = created.assignedCommittee || "Designated Redressal Committee";
      ticketTimeMetaEl.textContent = `Target SLA: ${created.slaHours || 24} Hours`;
      ticketReliefMetaEl.textContent = created.reliefSought || "Resolution Initiated";
      loggedQuoteEl.textContent = `“${created.summary}”`;
      dashboardLink.href = `/dashboard.html?ticket=${encodeURIComponent(created.ticketId)}`;

      successPanel.classList.remove("hidden");
      successPanel.scrollIntoView({ behavior: "smooth", block: "start" });

      // Spoken voice confirmation with ticket ID!
      const confirmationSpeech = `Your complaint ${created.ticketId} has been registered and dispatched to the ${created.assignedCommittee || "committee"}.`;
      window.voiceEngine.speak(confirmationSpeech);

    } catch (err) {
      confirmSubmitBtn.disabled = false;
      confirmSubmitBtn.textContent = "Confirm & Register Incident Dossier";
      showError(err.message || "Failed to register formal grievance dossier.");
    }
  }

  confirmSubmitBtn.addEventListener("click", submitGrievance);
  if (submitButton) submitButton.addEventListener("click", submitGrievance);

  // Lodge another grievance
  if (anotherButton) {
    anotherButton.addEventListener("click", () => {
      window.location.reload();
    });
  }

  function showError(msg) {
    if (errorBox) {
      errorBox.textContent = msg;
      errorBox.classList.remove("hidden");
      setTimeout(() => {
        errorBox.classList.add("hidden");
      }, 6000);
    }
  }
});
