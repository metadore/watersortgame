/**
 * voice_control.js — Web Speech API integration
 * Listens for commands and forwards them to the backend parser.
 */

"use strict";

const VoiceControl = (() => {
  let recognition = null;
  let listening = false;

  function isSupported() {
    return "SpeechRecognition" in window || "webkitSpeechRecognition" in window;
  }

  function init() {
    const btn = document.getElementById("voiceBtn");
    const statusEl = document.getElementById("voiceStatus");
    const textEl = document.getElementById("voiceText");

    if (!isSupported()) {
      btn.textContent = "🚫 Speech Not Supported";
      btn.disabled = true;
      statusEl.textContent = "Use Chrome/Edge for voice control";
      return;
    }

    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    recognition = new SR();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-US";

    recognition.onstart = () => {
      listening = true;
      btn.textContent = "🎙 Listening...";
      btn.classList.add("listening");
      statusEl.textContent = "Speak now...";
      textEl.textContent = "";
    };

    recognition.onend = () => {
      listening = false;
      btn.textContent = "🎙 Start Listening";
      btn.classList.remove("listening");
      statusEl.textContent = 'Say: "Pour red into tube 2"';
    };

    recognition.onerror = (e) => {
      statusEl.textContent = `Error: ${e.error}`;
      listening = false;
      btn.classList.remove("listening");
      btn.textContent = "🎙 Start Listening";
    };

    recognition.onresult = async (e) => {
      const transcript = e.results[0][0].transcript;
      textEl.textContent = `"${transcript}"`;
      await handleVoiceCommand(transcript, statusEl);
    };

    btn.addEventListener("click", () => {
      if (listening) {
        recognition.stop();
      } else {
        try {
          recognition.start();
        } catch (err) {
          statusEl.textContent = "Mic error — check permissions";
        }
      }
    });
  }

  async function handleVoiceCommand(text, statusEl) {
    // Send to backend parser
    const sessionId = typeof State !== "undefined" ? State.sessionId : null;
    if (!sessionId) {
      statusEl.textContent = "No active session";
      return;
    }

    try {
      const res = await fetch("http://localhost:5000/api/voice-command", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, text }),
      });
      const data = await res.json();

      statusEl.textContent = `Action: ${data.voice_action || "unknown"}`;

      // Sync game state
      if (data.tubes && typeof updateTubeState === "function") {
        updateTubeState(data.tubes);
      }
      if (data.tubes && typeof State !== "undefined") {
        State.tubes = data.tubes;
      }

      if (data.is_won && typeof handleWin === "function") {
        handleWin(data);
      }

      if (data.steps && data.steps.length > 0) {
        if (typeof State !== "undefined") State.solutionSteps = data.steps;
        if (typeof renderSolutionPanel === "function") renderSolutionPanel(data.steps);
        document.getElementById("solutionOverlay")?.classList.remove("hidden");
      }

      if (typeof showNotification === "function") {
        const msg = getVoiceFeedback(data.voice_action, data);
        showNotification(msg, data.success === false ? "error" : "success");
      }

    } catch (err) {
      statusEl.textContent = "Backend error";
      console.error("Voice command error:", err);
    }
  }

  function getVoiceFeedback(action, data) {
    switch (action) {
      case "undo":    return "↩ Undone";
      case "restart": return "↺ Restarted";
      case "solve":   return `🤖 Solution: ${data.steps?.length || 0} steps`;
      case "pour":
      case "pour_color":
        return data.success ? "✓ Poured!" : `✗ ${data.reason}`;
      default:        return `Heard: "${data.parsed?.raw || action}"`;
    }
  }

  // Expose init for app.js
  document.addEventListener("DOMContentLoaded", init);

  return { isSupported, handleVoiceCommand };
})();