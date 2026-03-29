/**
 * app.js — Main game controller
 * Handles state, API calls, tube rendering, UI updates.
 */

"use strict";

// ─── CONFIG ──────────────────────────────────────────────────────────────────
const API_BASE = "http://localhost:5000/api";

// ─── STATE ───────────────────────────────────────────────────────────────────
const State = {
  sessionId: null,
  currentLevel: 1,
  tubes: [],
  selectedTube: null,
  moveCount: 0,
  isWon: false,
  solutionSteps: [],
  solutionIndex: 0,
  autoPlayInterval: null,
  timerInterval: null,
  startTime: null,
  elapsed: 0,

  // Challenge mode
  challengeMode: false,
  maxMoves: 30,
  challengeSeconds: 120,
  challengeInterval: null,
  score: 0,
  challengeTimeLeft: 120,

  // Analytics
  movesChart: null,
  timeChart: null,

  colorsMap: {},
};

// ─── API HELPERS ─────────────────────────────────────────────────────────────
async function apiFetch(endpoint, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, opts);
    return await res.json();
  } catch (e) {
    console.error("API error:", e);
    showNotification("Backend offline — check Flask server", "error");
    return null;
  }
}

// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", async () => {
  // Restore or create session
  State.sessionId = localStorage.getItem("aqua_session") || null;
  State.currentLevel = parseInt(localStorage.getItem("aqua_level") || "1", 10);

  await loadLevel(State.currentLevel);
  setupEventListeners();
  startTimer();
  initTheme();
});

// ─── LEVEL MANAGEMENT ────────────────────────────────────────────────────────
async function loadLevel(level) {
  clearTimers();
  const params = new URLSearchParams({ level });
  if (State.sessionId) params.append("session_id", State.sessionId);

  const data = await apiFetch(`/start-level?${params}`);
  if (!data) return;

  State.sessionId = data.session_id;
  State.currentLevel = level;
  State.tubes = data.tubes;
  State.moveCount = 0;
  State.selectedTube = null;
  State.isWon = false;
  State.solutionSteps = [];
  State.solutionIndex = 0;
  State.colorsMap = data.colors || {};
  State.score = 0;

  localStorage.setItem("aqua_session", State.sessionId);
  localStorage.setItem("aqua_level", level);

  renderTubes(data.tubes);
  updateHUD(data);
  startTimer();

  if (State.challengeMode) initChallenge();

  showNotification(`Level ${level}: ${data.level_name || ""}`, "success");
}

// ─── RENDERING ───────────────────────────────────────────────────────────────
function renderTubes(tubes) {
  const container = document.getElementById("tubeContainer");
  container.innerHTML = "";

  // Tube height scales with tube capacity
  const capacity = tubes.length > 0 ? tubes[0].capacity : 4;
  const layerH = Math.min(40, Math.floor(200 / capacity));
  const tubeH = layerH * capacity;

  tubes.forEach((tube, idx) => {
    const wrap = document.createElement("div");
    wrap.className = "tube-wrap" + (tube.is_complete ? " complete" : "");
    wrap.dataset.index = idx;
    wrap.setAttribute("aria-label", `Tube ${idx + 1}`);

    const label = document.createElement("div");
    label.className = "tube-label";
    label.textContent = `T${idx + 1}`;

    const tubeEl = document.createElement("div");
    tubeEl.className = "tube";
    tubeEl.style.height = `${tubeH}px`;

    // Heat overlay
    const heat = tube.heat || 0;
    const maxHeat = Math.max(...State.tubes.map(t => t.heat || 0), 1);
    const heatRatio = heat / maxHeat;
    if (heatRatio > 0.1) {
      tubeEl.style.boxShadow = `inset 0 0 ${heatRatio * 20}px rgba(255,80,0,${heatRatio * 0.4})`;
    }

    // Liquid layers (bottom → top, reversed in DOM because column-reverse)
    tube.layers.forEach((color) => {
      const layer = document.createElement("div");
      layer.className = `liquid-layer layer-${color}`;
      layer.style.height = `${layerH}px`;
      layer.style.flexShrink = "0";
      tubeEl.appendChild(layer);
    });

    wrap.appendChild(tubeEl);
    wrap.appendChild(label);

    wrap.addEventListener("click", () => onTubeClick(idx));
    container.appendChild(wrap);
  });
}

function updateTubeState(tubes) {
  State.tubes = tubes;
  // Partial re-render — update layers without full rebuild for animation
  const wraps = document.querySelectorAll(".tube-wrap");
  const capacity = tubes.length > 0 ? tubes[0].capacity : 4;
  const layerH = Math.min(40, Math.floor(200 / capacity));

  wraps.forEach((wrap, idx) => {
    const tube = tubes[idx];
    if (!tube) return;
    const tubeEl = wrap.querySelector(".tube");
    tubeEl.innerHTML = "";
    wrap.classList.toggle("complete", tube.is_complete);

    // Heat
    const heat = tube.heat || 0;
    const maxHeat = Math.max(...tubes.map(t => t.heat || 0), 1);
    const heatRatio = heat / maxHeat;
    tubeEl.style.boxShadow = heatRatio > 0.1
      ? `inset 0 0 ${heatRatio * 20}px rgba(255,80,0,${heatRatio * 0.4})`
      : "";

    tube.layers.forEach((color) => {
      const layer = document.createElement("div");
      layer.className = `liquid-layer layer-${color}`;
      layer.style.height = `${layerH}px`;
      layer.style.flexShrink = "0";
      tubeEl.appendChild(layer);
    });
  });
}

// ─── TUBE INTERACTION ────────────────────────────────────────────────────────
async function onTubeClick(idx) {
  if (State.isWon) return;

  clearSolutionHighlights();

  if (State.selectedTube === null) {
    // Select source
    if (!State.tubes[idx] || State.tubes[idx].is_empty) {
      showNotification("Select a tube with liquid first", "error");
      return;
    }
    State.selectedTube = idx;
    setTubeSelected(idx, true);
    showNotification(`Selected Tube ${idx + 1} — now click target`, "");
    return;
  }

  if (State.selectedTube === idx) {
    // Deselect
    setTubeSelected(idx, false);
    State.selectedTube = null;
    showNotification("", "");
    return;
  }

  // Attempt pour
  const src = State.selectedTube;
  const dst = idx;
  setTubeSelected(src, false);
  State.selectedTube = null;

  await executePour(src, dst);
}

async function executePour(src, dst) {
  const data = await apiFetch("/move", "POST", {
    session_id: State.sessionId,
    from_tube: src,
    to_tube: dst,
  });
  if (!data) return;

  if (data.success) {
    Animations.pourEffect(src, dst);
    State.moveCount = data.move_count;
    updateTubeState(data.tubes);
    updateHUD(data);

    if (State.challengeMode) {
      if (State.moveCount >= State.maxMoves && !data.is_won) {
        endChallengeMode(false);
        return;
      }
    }

    if (data.is_won) {
      handleWin(data);
    }
  } else {
    Animations.shakeEffect(dst);
    showNotification(data.reason || "Invalid move", "error");
  }
}

function setTubeSelected(idx, selected) {
  const wraps = document.querySelectorAll(".tube-wrap");
  if (wraps[idx]) wraps[idx].classList.toggle("selected", selected);
}

function clearSolutionHighlights() {
  document.querySelectorAll(".tube-wrap").forEach(w => w.classList.remove("highlight"));
}

// ─── WIN ──────────────────────────────────────────────────────────────────────
function handleWin(data) {
  State.isWon = true;
  clearTimers();

  const timeStr = formatTime(State.elapsed);
  document.getElementById("winStats").textContent =
    `Solved in ${data.move_count} moves · Time: ${timeStr}`;

  Animations.winCelebration();

  setTimeout(() => {
    document.getElementById("winOverlay").classList.remove("hidden");
  }, 800);
}

// ─── HUD ──────────────────────────────────────────────────────────────────────
function updateHUD(data) {
  document.getElementById("levelBadge").textContent = `LVL ${State.currentLevel}`;
  document.getElementById("moveBadge").textContent = `${data.move_count} Moves`;
  document.getElementById("levelNum").textContent = State.currentLevel;
  document.getElementById("levelTitle").textContent =
    data.level_name || `Level ${State.currentLevel}`;

  if (State.challengeMode) {
    const remaining = State.maxMoves - (data.move_count || 0);
    document.getElementById("maxMoves").textContent = `${remaining} left`;
    document.getElementById("scoreDisplay").textContent = State.score;
  } else {
    document.getElementById("maxMoves").textContent = "—";
    document.getElementById("challengeTimer").textContent = "—";
  }
}

// ─── TIMER ────────────────────────────────────────────────────────────────────
function startTimer() {
  State.startTime = Date.now();
  State.elapsed = 0;
  State.timerInterval = setInterval(() => {
    State.elapsed = Math.floor((Date.now() - State.startTime) / 1000);
    document.getElementById("timerBadge").textContent = formatTime(State.elapsed);
  }, 1000);
}

function clearTimers() {
  clearInterval(State.timerInterval);
  clearInterval(State.challengeInterval);
  clearInterval(State.autoPlayInterval);
}

function formatTime(seconds) {
  const m = String(Math.floor(seconds / 60)).padStart(2, "0");
  const s = String(seconds % 60).padStart(2, "0");
  return `${m}:${s}`;
}

// ─── CHALLENGE MODE ────────────────────────────────────────────────────────
function initChallenge() {
  const lvl = State.currentLevel;
  State.maxMoves = 15 + lvl * 3;
  State.challengeTimeLeft = 60 + lvl * 15;
  State.score = 0;

  document.getElementById("maxMoves").textContent = State.maxMoves;
  document.getElementById("challengeTimer").textContent = formatTime(State.challengeTimeLeft);

  clearInterval(State.challengeInterval);
  State.challengeInterval = setInterval(() => {
    State.challengeTimeLeft--;
    document.getElementById("challengeTimer").textContent = formatTime(State.challengeTimeLeft);
    if (State.challengeTimeLeft <= 0) {
      endChallengeMode(false);
    }
  }, 1000);
}

function endChallengeMode(won) {
  clearInterval(State.challengeInterval);
  if (won) {
    const bonus = State.challengeTimeLeft * 10 + (State.maxMoves - State.moveCount) * 50;
    State.score += bonus;
    document.getElementById("scoreDisplay").textContent = State.score;
    showNotification(`🏆 Challenge Complete! Bonus: +${bonus}`, "success");
  } else {
    showNotification("⏰ Challenge failed — try again!", "error");
    setTimeout(() => loadLevel(State.currentLevel), 2000);
  }
}

// ─── AI SOLVER ────────────────────────────────────────────────────────────────
async function requestSolution() {
  showNotification("🤖 Computing solution...", "");
  const data = await apiFetch(`/ai-solve?session_id=${State.sessionId}`);
  if (!data) return;

  if (!data.solvable) {
    showNotification("No solution found for current state", "error");
    return;
  }

  State.solutionSteps = data.steps;
  State.solutionIndex = 0;

  renderSolutionPanel(data.steps);
  document.getElementById("solutionOverlay").classList.remove("hidden");
}

function renderSolutionPanel(steps) {
  const container = document.getElementById("solutionSteps");
  container.innerHTML = "";
  document.getElementById("solutionMsg").textContent =
    `Found ${steps.length} step solution`;

  steps.forEach((step, i) => {
    const el = document.createElement("div");
    el.className = "solution-step";
    el.id = `step-${i}`;
    el.innerHTML = `
      <span class="step-num">${step.step}</span>
      <span>Tube ${step.from_tube}</span>
      <span class="step-arrow">→</span>
      <span>Tube ${step.to_tube}</span>
    `;
    container.appendChild(el);
  });

  highlightCurrentSolutionStep();
}

function highlightCurrentSolutionStep() {
  document.querySelectorAll(".solution-step").forEach((el, i) => {
    el.classList.remove("current", "done");
    if (i < State.solutionIndex) el.classList.add("done");
    if (i === State.solutionIndex) el.classList.add("current");
  });

  // Highlight tubes in game
  clearSolutionHighlights();
  const step = State.solutionSteps[State.solutionIndex];
  if (step) {
    const wraps = document.querySelectorAll(".tube-wrap");
    if (wraps[step.from_tube - 1]) wraps[step.from_tube - 1].classList.add("highlight");
    if (wraps[step.to_tube - 1]) wraps[step.to_tube - 1].classList.add("highlight");
  }
}

async function autoPlaySolution() {
  clearInterval(State.autoPlayInterval);
  document.getElementById("closeSolution").click();

  State.autoPlayInterval = setInterval(async () => {
    if (State.solutionIndex >= State.solutionSteps.length || State.isWon) {
      clearInterval(State.autoPlayInterval);
      return;
    }
    const step = State.solutionSteps[State.solutionIndex];
    await executePour(step.from_tube - 1, step.to_tube - 1);
    State.solutionIndex++;
    highlightCurrentSolutionStep();
  }, 900);
}

// ─── ANALYTICS ────────────────────────────────────────────────────────────────
async function openAnalytics() {
  const data = await apiFetch("/analytics");
  if (!data) return;

  const summary = data.session_summary || {};
  document.getElementById("aSessions").textContent = summary.total_sessions || 0;
  document.getElementById("aWins").textContent = summary.total_wins || 0;
  document.getElementById("aAvgMoves").textContent = Math.round(summary.avg_moves || 0);
  document.getElementById("aAvgTime").textContent = formatTime(Math.round(summary.avg_time || 0));

  renderAnalyticsCharts(data.database_records || []);
  renderHeatmap();

  document.getElementById("analyticsOverlay").classList.remove("hidden");
}

function renderAnalyticsCharts(records) {
  // Destroy old charts
  if (State.movesChart) State.movesChart.destroy();
  if (State.timeChart) State.timeChart.destroy();

  const won = records.filter(r => r.won).slice(0, 10).reverse();
  const labels = won.map((r, i) => `S${i + 1}`);

  const chartDefaults = {
    backgroundColor: "rgba(0,212,255,.15)",
    borderColor: "#00d4ff",
    borderWidth: 2,
    tension: 0.4,
    fill: true,
  };

  State.movesChart = new Chart(document.getElementById("movesChart"), {
    type: "line",
    data: { labels, datasets: [{ label: "Moves", data: won.map(r => r.moves), ...chartDefaults }] },
    options: { responsive: true, plugins: { legend: { labels: { color: "#8ba4cc" } } },
      scales: { x: { ticks: { color: "#8ba4cc" }, grid: { color: "rgba(80,160,255,.08)" } },
                 y: { ticks: { color: "#8ba4cc" }, grid: { color: "rgba(80,160,255,.08)" } } } },
  });

  State.timeChart = new Chart(document.getElementById("timeChart"), {
    type: "bar",
    data: { labels, datasets: [{ label: "Time (s)", data: won.map(r => Math.round(r.time_taken || 0)),
      backgroundColor: "rgba(123,47,255,.25)", borderColor: "#7b2fff", borderWidth: 2 }] },
    options: { responsive: true, plugins: { legend: { labels: { color: "#8ba4cc" } } },
      scales: { x: { ticks: { color: "#8ba4cc" }, grid: { color: "rgba(80,160,255,.08)" } },
                 y: { ticks: { color: "#8ba4cc" }, grid: { color: "rgba(80,160,255,.08)" } } } },
  });
}

function renderHeatmap() {
  const container = document.getElementById("heatmapContainer");
  container.innerHTML = "";
  const heatData = State.tubes.map((t, i) => ({ i, heat: t.heat || 0 }));
  const maxH = Math.max(...heatData.map(d => d.heat), 1);

  heatData.forEach(d => {
    const cell = document.createElement("div");
    cell.className = "heat-cell";
    const ratio = d.heat / maxH;
    const r = Math.round(255 * ratio);
    const g = Math.round(80 * (1 - ratio));
    cell.style.background = `rgba(${r},${g},40,${0.3 + ratio * 0.7})`;
    cell.textContent = `T${d.i + 1}`;
    cell.title = `${d.heat} clicks`;
    container.appendChild(cell);
  });
}

// ─── NOTIFICATIONS ────────────────────────────────────────────────────────────
let notifTimeout;
function showNotification(msg, type = "") {
  const el = document.getElementById("notification");
  if (!msg) { el.classList.add("hidden"); return; }
  el.textContent = msg;
  el.className = `notification ${type}`;
  clearTimeout(notifTimeout);
  notifTimeout = setTimeout(() => el.classList.add("hidden"), 3000);
}

// ─── THEME ────────────────────────────────────────────────────────────────────
function initTheme() {
  const saved = localStorage.getItem("aqua_theme") || "dark";
  document.body.dataset.theme = saved;
  document.getElementById("darkToggle").textContent = saved === "dark" ? "🌙" : "☀️";
}

// ─── EVENT LISTENERS ─────────────────────────────────────────────────────────
function setupEventListeners() {
  // Level nav
  document.getElementById("prevLevel").addEventListener("click", () => {
    if (State.currentLevel > 1) loadLevel(State.currentLevel - 1);
  });
  document.getElementById("nextLevelNav").addEventListener("click", () => {
    loadLevel(State.currentLevel + 1);
  });

  // Undo
  document.getElementById("undoBtn").addEventListener("click", async () => {
    const data = await apiFetch("/undo", "POST", { session_id: State.sessionId });
    if (data) { updateTubeState(data.tubes); updateHUD(data); }
  });

  // Restart
  document.getElementById("restartBtn").addEventListener("click", async () => {
    const data = await apiFetch("/restart", "POST", { session_id: State.sessionId });
    if (data) { State.isWon = false; renderTubes(data.tubes); updateHUD(data); startTimer(); }
  });

  // AI Solve
  document.getElementById("solveBtn").addEventListener("click", requestSolution);
  document.getElementById("closeSolution").addEventListener("click", () => {
    document.getElementById("solutionOverlay").classList.add("hidden");
    clearSolutionHighlights();
  });
  document.getElementById("autoPlayBtn").addEventListener("click", autoPlaySolution);

  // Analytics
  document.getElementById("analyticsBtn").addEventListener("click", openAnalytics);
  document.getElementById("closeAnalytics").addEventListener("click", () => {
    document.getElementById("analyticsOverlay").classList.add("hidden");
  });

  // Win overlay
  document.getElementById("nextLevelBtn").addEventListener("click", () => {
    document.getElementById("winOverlay").classList.add("hidden");
    loadLevel(State.currentLevel + 1);
  });
  document.getElementById("replayBtn").addEventListener("click", () => {
    document.getElementById("winOverlay").classList.add("hidden");
    loadLevel(State.currentLevel);
  });

  // Dark mode
  document.getElementById("darkToggle").addEventListener("click", () => {
    const current = document.body.dataset.theme;
    const next = current === "dark" ? "light" : "dark";
    document.body.dataset.theme = next;
    localStorage.setItem("aqua_theme", next);
    document.getElementById("darkToggle").textContent = next === "dark" ? "🌙" : "☀️";
  });

  // Challenge mode
  document.getElementById("challengeToggle").addEventListener("click", () => {
    State.challengeMode = !State.challengeMode;
    document.getElementById("challengeToggle").textContent =
      State.challengeMode ? "Disable Challenge" : "Enable Challenge";
    if (State.challengeMode) {
      initChallenge();
      showNotification("⚡ Challenge Mode ON!", "success");
    } else {
      clearInterval(State.challengeInterval);
      document.getElementById("maxMoves").textContent = "—";
      document.getElementById("challengeTimer").textContent = "—";
    }
  });

  // Save / Load
  document.getElementById("saveBtn").addEventListener("click", async () => {
    await apiFetch("/save", "POST", { session_id: State.sessionId });
    showNotification("💾 Game saved!", "success");
  });
  document.getElementById("loadBtn").addEventListener("click", async () => {
    const data = await apiFetch(`/load?session_id=${State.sessionId}`);
    if (data && data.found) {
      State.tubes = data.tubes;
      State.currentLevel = data.level;
      renderTubes(data.tubes);
      updateHUD(data);
      showNotification("📂 Game loaded!", "success");
    } else {
      showNotification("No saved game found", "error");
    }
  });

  // Learn
  document.getElementById("learnBtn").addEventListener("click", () => {
    window.open("/learn", "_blank");
  });

  // Keyboard shortcuts
  document.addEventListener("keydown", (e) => {
    if (e.key === "z" || e.key === "Z") document.getElementById("undoBtn").click();
    if (e.key === "r" || e.key === "R") document.getElementById("restartBtn").click();
    if (e.key === "Escape") {
      document.querySelectorAll(".overlay").forEach(o => o.classList.add("hidden"));
      if (State.selectedTube !== null) {
        setTubeSelected(State.selectedTube, false);
        State.selectedTube = null;
      }
    }
  });
}