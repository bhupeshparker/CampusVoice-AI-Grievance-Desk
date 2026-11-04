/**
 * CampusVoice - Voice Engine (Web Speech API Recognition & Synthesis + Waveform Simulation)
 * Features:
 * - SpeechRecognition continuous / interim capture
 * - Web Speech Synthesis for conversational voice responses
 * - Real-time animated waveform bar driver
 * - Grace periods and silence detection
 */

class VoiceEngine {
  constructor() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.hasRecognition = Boolean(SpeechRecognition);
    this.recognition = null;
    this.isListening = false;
    this.shouldListen = false;
    this.isGracePeriod = false;
    this.speechSynthesis = window.speechSynthesis;

    this.finalTranscript = "";
    this.interimTranscript = "";
    this.startTime = 0;
    this.minListenDuration = 2500;
    this.extensionDuration = 2500;
    this.graceTimer = null;
    this.countdownInterval = null;
    this.silenceTimer = null;
    this.waveformInterval = null;

    this.onTranscriptCb = null;
    this.onStateChangeCb = null;
    this.onErrorCb = null;
    this.onFinalCompleteCb = null;

    if (this.hasRecognition) {
      this.initRecognition();
    }
  }

  initRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    this.recognition.continuous = true;
    this.recognition.interimResults = true;
    this.recognition.lang = "en-US";
    this.recognition.maxAlternatives = 1;

    this.recognition.onstart = () => {
      this.isListening = true;
      this.startWaveformAnimation();
      if (this.onStateChangeCb) {
        this.onStateChangeCb(true, this.isGracePeriod ? "wrapping" : "listening");
      }
    };

    this.recognition.onresult = (event) => {
      let currentSessionFinal = "";
      let currentSessionInterim = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const item = event.results[i];
        const text = item[0].transcript;
        if (item.isFinal) {
          currentSessionFinal += text + " ";
        } else {
          currentSessionInterim += text;
        }
      }

      if (currentSessionFinal) {
        this.finalTranscript = (this.finalTranscript + " " + currentSessionFinal).replace(/\s+/g, " ").trim();
      }
      this.interimTranscript = currentSessionInterim.trim();

      const fullText = (this.finalTranscript + (this.interimTranscript ? " " + this.interimTranscript : "")).trim();
      if (this.onTranscriptCb && fullText) {
        this.onTranscriptCb(fullText);
      }

      // Auto-wrap silence detection: after 2.5s of silence after hearing something
      if (fullText.length >= 6 && this.shouldListen) {
        if (this.silenceTimer) clearTimeout(this.silenceTimer);
        this.silenceTimer = setTimeout(() => {
          if (this.shouldListen && !this.isGracePeriod) {
            this.requestStop();
          }
        }, 2200);
      }
    };

    this.recognition.onerror = (event) => {
      console.warn("Speech recognition notice:", event.error);
      if (event.error === "not-allowed" || event.error === "service-not-allowed") {
        this.shouldListen = false;
        this.isGracePeriod = false;
        this.isListening = false;
        this.clearTimers();
        this.stopWaveformAnimation();
        if (this.onStateChangeCb) this.onStateChangeCb(false, "idle");
        if (this.onErrorCb) {
          this.onErrorCb("Microphone access was denied. Please allow microphone permissions in your browser or type your grievance.");
        }
        return;
      }

      if (event.error === "no-speech") {
        // Keep listening active
        return;
      }

      if (event.error !== "aborted" && this.onErrorCb) {
        this.onErrorCb(`Audio notice: ${event.error}`);
      }
    };

    this.recognition.onend = () => {
      if (this.shouldListen || this.isGracePeriod) {
        try {
          this.recognition.start();
          return;
        } catch (_) {
          // Will restart if needed
        }
      }

      this.isListening = false;
      this.stopWaveformAnimation();
      this.clearTimers();
      if (this.onStateChangeCb) {
        this.onStateChangeCb(false, "idle");
      }
    };
  }

  startWaveformAnimation() {
    this.stopWaveformAnimation();
    const bars = document.querySelectorAll("#waveform .bar");
    if (!bars || bars.length === 0) return;

    this.waveformInterval = setInterval(() => {
      bars.forEach((bar) => {
        const h = Math.floor(Math.random() * 24) + 6;
        bar.style.height = `${h}px`;
      });
    }, 120);
  }

  stopWaveformAnimation() {
    if (this.waveformInterval) {
      clearInterval(this.waveformInterval);
      this.waveformInterval = null;
    }
    const bars = document.querySelectorAll("#waveform .bar");
    if (bars) {
      bars.forEach((bar) => {
        bar.style.height = "4px";
      });
    }
  }

  clearTimers() {
    if (this.graceTimer) {
      clearTimeout(this.graceTimer);
      this.graceTimer = null;
    }
    if (this.countdownInterval) {
      clearInterval(this.countdownInterval);
      this.countdownInterval = null;
    }
    if (this.silenceTimer) {
      clearTimeout(this.silenceTimer);
      this.silenceTimer = null;
    }
  }

  startListening({ initialText = "", onTranscript, onStateChange, onFinalComplete, onError }) {
    if (!this.hasRecognition) {
      if (onError) onError("Speech recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge, or type your complaint.");
      return;
    }

    // Stop speaking if speech synthesis was running
    if (this.speechSynthesis) {
      this.speechSynthesis.cancel();
    }

    this.clearTimers();
    this.finalTranscript = initialText ? initialText.trim() : "";
    this.interimTranscript = "";
    this.onTranscriptCb = onTranscript;
    this.onStateChangeCb = onStateChange;
    this.onFinalCompleteCb = onFinalComplete;
    this.onErrorCb = onError;
    this.shouldListen = true;
    this.isGracePeriod = false;
    this.startTime = Date.now();

    try {
      this.recognition.start();
    } catch (e) {
      try {
        this.recognition.stop();
        setTimeout(() => {
          if (this.shouldListen) {
            try { this.recognition.start(); } catch (_) {}
          }
        }, 120);
      } catch (_) {}
    }

    if (this.onStateChangeCb) {
      this.onStateChangeCb(true, "listening");
    }
  }

  requestStop() {
    if (!this.isListening && !this.shouldListen) return;
    if (this.isGracePeriod) return;

    this.shouldListen = false;
    this.isGracePeriod = true;

    const elapsed = Date.now() - this.startTime;
    const remainingMin = Math.max(0, this.minListenDuration - elapsed);
    const totalGraceMs = remainingMin + this.extensionDuration;

    let secondsLeft = Math.ceil(totalGraceMs / 1000);
    if (this.onStateChangeCb) {
      this.onStateChangeCb(true, `extending-${secondsLeft}`);
    }

    this.countdownInterval = setInterval(() => {
      secondsLeft -= 1;
      if (secondsLeft > 0 && this.onStateChangeCb) {
        this.onStateChangeCb(true, `extending-${secondsLeft}`);
      }
    }, 1000);

    this.graceTimer = setTimeout(() => {
      this.stopListeningImmediately();
    }, totalGraceMs);
  }

  stopListeningImmediately() {
    this.clearTimers();
    this.shouldListen = false;
    this.isGracePeriod = false;
    this.isListening = false;
    this.stopWaveformAnimation();

    if (this.recognition) {
      try {
        this.recognition.stop();
      } catch (e) {
        console.warn("Recognition stop error:", e);
      }
    }

    if (this.interimTranscript) {
      this.finalTranscript = (this.finalTranscript + " " + this.interimTranscript).replace(/\s+/g, " ").trim();
      this.interimTranscript = "";
      if (this.onTranscriptCb && this.finalTranscript) {
        this.onTranscriptCb(this.finalTranscript);
      }
    }

    const completedText = this.finalTranscript.trim();

    if (this.onStateChangeCb) {
      this.onStateChangeCb(false, "idle");
    }

    if (this.onFinalCompleteCb && completedText) {
      const cb = this.onFinalCompleteCb;
      this.onFinalCompleteCb = null;
      cb(completedText);
    }
  }

  speak(text) {
    return new Promise((resolve) => {
      if (!this.speechSynthesis) {
        resolve();
        return;
      }
      this.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 1.02;
      utterance.pitch = 1.0;
      utterance.lang = "en-US";
      utterance.onend = () => resolve();
      utterance.onerror = () => resolve();
      this.speechSynthesis.speak(utterance);
    });
  }

  cancelSpeech() {
    if (this.speechSynthesis) {
      this.speechSynthesis.cancel();
    }
  }
}

window.voiceEngine = new VoiceEngine();
