<div align="center">

<img src="https://readme-typing-svg.demolab.com?font=Orbitron&size=40&duration=3000&pause=1000&color=00D4FF&center=true&vCenter=true&width=600&lines=💧+AQUA+SORT;Water+Sort+Puzzle+Game;Sort.+Pour.+Conquer." alt="Aqua Sort" />

<br/>

[![Live Demo](https://img.shields.io/badge/🎮%20PLAY%20LIVE-00D4FF?style=for-the-badge&logoColor=white)](https://aqua-sort-water-puzzle.vercel.app)
[![GitHub](https://img.shields.io/badge/GitHub-metadore%2Fwatersortgame-181717?style=for-the-badge&logo=github)](https://github.com/metadore/watersortgame)
[![Backend](https://img.shields.io/badge/Backend-Render-46E3B7?style=for-the-badge&logo=render)](https://watersortgame-backend.onrender.com)
[![Frontend](https://img.shields.io/badge/Frontend-Vercel-000000?style=for-the-badge&logo=vercel)](https://aqua-sort-water-puzzle.vercel.app)

<br/>

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.2-000000?style=flat-square&logo=flask&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Chart.js](https://img.shields.io/badge/Chart.js-Analytics-FF6384?style=flat-square&logo=chartdotjs&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

<br/>

> **A production-quality, full-stack Water Sort Puzzle game featuring gradient liquid physics, AI solving with BFS/A\*, voice control, real-time analytics, adaptive difficulty, and an interactive educational simulation page.**

<br/>

---

</div>

## 📌 Table of Contents

- [🎮 Live Demo](#-live-demo)
- [✨ Features](#-features)
- [🏗️ Architecture](#️-architecture)
- [📁 Project Structure](#-project-structure)
- [⚡ Quick Start](#-quick-start)
- [🔌 API Reference](#-api-reference)
- [🤖 AI Solver](#-ai-solver)
- [📊 Analytics](#-analytics)
- [🎙️ Voice Control](#️-voice-control)
- [⌨️ Keyboard Shortcuts](#️-keyboard-shortcuts)
- [🚀 Deployment](#-deployment)
- [🎨 Design System](#-design-system)
- [📝 License](#-license)

---

## 🎮 Live Demo

<div align="center">

### 👉 [Play Now — aqua-sort-water-puzzle.vercel.app](https://aqua-sort-water-puzzle.vercel.app)

| 🎮 Game | 📚 Learn How It Works |
|:---:|:---:|
| [Play the Game](https://aqua-sort-water-puzzle.vercel.app) | [Interactive Tutorial](https://aqua-sort-water-puzzle.vercel.app/learn) |

> ⚠️ **Note:** Backend is on Render's free tier. First load after inactivity may take ~30 seconds to wake up. Subsequent loads are instant.

</div>

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🎮 Core Gameplay
- **10 handcrafted levels** — Easy → Grand Master
- **Infinite procedural levels** beyond level 10
- **Multicolor gradient liquid layers** via CSS linear-gradients
- **Smooth pour animations** with arc particles & ripple effects
- **Full undo stack** — go back any number of moves
- **Win detection** with confetti celebration

</td>
<td width="50%">

### 🤖 AI Solver
- **BFS algorithm** — guaranteed optimal solution for small puzzles
- **A\* algorithm** — heuristic-guided for complex puzzles
- **Step-by-step solution panel** with highlighted moves
- **Auto-play mode** — watch the AI solve it automatically
- Automatically switches algorithm based on puzzle complexity

</td>
</tr>
<tr>
<td width="50%">

### 📊 Analytics Dashboard
- **Session tracking** — time, moves, undos, failed attempts
- **Chart.js visualizations** — line charts & bar charts
- **Tube click heatmap** — see where you struggle most
- **SQLite persistence** — data survives page reloads
- Win rate, average moves, average time statistics

</td>
<td width="50%">

### ⚡ Dynamic Difficulty
- **Adaptive scoring** based on solve time vs expected time
- Continuously adjusts `difficulty_score` (0.0 → 1.0)
- Affects tube count, color count, empty tubes, scramble depth
- Gets harder when you're fast, easier when you struggle

</td>
</tr>
<tr>
<td width="50%">

### 🎙️ Voice Control
- Powered by **Web Speech API** (Chrome/Edge)
- `"Pour red into tube 2"` — color-based pour
- `"Undo move"` — undo last action
- `"Restart level"` — restart current level
- `"Hint"` / `"Solve"` — trigger AI solver

</td>
<td width="50%">

### 🎯 Challenge Mode
- **Move limit** per level — think before you pour
- **Countdown timer** — beat the clock
- **Bonus scoring** — faster = more points
- Formula: `time_left × 10 + unused_moves × 50`

</td>
</tr>
<tr>
<td width="50%">

### 💾 Save / Load System
- **Auto-save** after every single move
- **Manual save** button for checkpoints
- **Resume anytime** — loads exact game state
- SQLite database on backend

</td>
<td width="50%">

### 📚 Educational Page `/learn`
- **Interactive simulation** of the full request lifecycle
- **9-step animated walkthrough** — click to tube → DOM update
- **Syntax-highlighted code snippets**
- **Live "Simulate Pour"** button with real-time log output

</td>
</tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                       FRONTEND  (Vercel)                         │
│                                                                   │
│   index.html ──► app.js ──► animations.js                        │
│   styles.css      │         voice_control.js                     │
│                   │         visualizer.js                        │
└───────────────────│─────────────────────────────────────────────┘
                    │  REST API  (JSON over HTTP)
                    ▼
┌─────────────────────────────────────────────────────────────────┐
│                       BACKEND  (Render)                          │
│                                                                   │
│   app.py (Flask API)                                             │
│     ├── game_engine.py      ← pure game logic, Tube class        │
│     ├── ai_solver.py        ← BFS + A* algorithms                │
│     ├── difficulty_manager.py ← adaptive difficulty + gen        │
│     ├── analytics.py        ← session stats recorder             │
│     └── models.py           ← SQLite persistence layer           │
│                                    │                             │
│                               game.db (SQLite)                   │
└─────────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

| Module | Responsibility | External Dependencies |
|--------|---------------|----------------------|
| `game_engine.py` | Tube class, GameEngine, undo stack, heatmap | None |
| `ai_solver.py` | BFS + A* search, state hashing | None |
| `difficulty_manager.py` | Adaptive difficulty, procedural generation | game_engine |
| `analytics.py` | In-session stats, win recording | None |
| `models.py` | SQLite save/load/analytics only | None |
| `app.py` | Flask routes, voice parsing, orchestration | All above |

---

## 📁 Project Structure

```
WaterSortGame/
│
├── backend/
│   ├── app.py                  # Flask REST API — 10 endpoints
│   ├── game_engine.py          # Tube + GameEngine classes, undo stack
│   ├── ai_solver.py            # BFS (optimal) + A* (complex) solver
│   ├── difficulty_manager.py   # Dynamic difficulty + procedural levels
│   ├── analytics.py            # Per-session analytics tracker
│   ├── models.py               # SQLite save/load/analytics persistence
│   ├── requirements.txt        # Python dependencies
│   ├── Procfile                # Render start command
│   └── runtime.txt             # Python version pin (3.11)
│
├── frontend/
│   ├── index.html              # Main game UI — 5 overlays, sidebar
│   ├── styles.css              # Dark futuristic bioluminescent theme
│   ├── app.js                  # Game controller, API calls, state mgmt
│   ├── animations.js           # Pour particles, ripple, confetti, shake
│   ├── voice_control.js        # Web Speech API integration
│   └── visualizer.js           # Chart.js radar, doughnut, heatmap helpers
│
├── templates/
│   └── learn.html              # Interactive educational simulation page
│
├── static/
│   ├── sounds/                 # Sound effect files (.mp3)
│   └── assets/                 # Images and assets
│
├── database/
│   └── game.db                 # Auto-created SQLite database
│
└── README.md
```

---

## ⚡ Quick Start

### Prerequisites

- Python 3.8+
- pip
- Modern browser (Chrome/Edge recommended for voice control)

### 1. Clone the repository

```bash
git clone https://github.com/metadore/watersortgame.git
cd watersortgame
```

### 2. Install dependencies

```bash
cd backend
pip install flask flask-cors
```

### 3. Start the backend

```bash
python app.py
```

You should see:
```
🎮 Water Sort Puzzle Game — Backend starting on http://localhost:5000
* Running on http://0.0.0.0:5000
```

### 4. Open the game

Open your browser and go to:
```
http://localhost:5000
```

> ✅ The Flask server serves both the API **and** the frontend — no separate server needed!

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/start-level?level=N` | Initialize a level, returns full game state |
| `POST` | `/api/move` | Execute a pour move `{from_tube, to_tube}` |
| `POST` | `/api/undo` | Undo the last move |
| `POST` | `/api/restart` | Restart current level from beginning |
| `GET` | `/api/ai-solve` | Get optimal BFS/A* solution steps |
| `GET` | `/api/analytics` | Get all analytics data + DB records |
| `POST` | `/api/voice-command` | Parse and execute voice command `{text}` |
| `POST` | `/api/save` | Save game state to SQLite |
| `GET` | `/api/load?session_id=X` | Load saved game state |
| `GET` | `/api/colors` | Get all color definitions with CSS gradients |

### Example — Make a Move

```json
POST /api/move
{
  "session_id": "abc-123",
  "from_tube": 0,
  "to_tube": 2
}
```
```json
{
  "success": true,
  "reason": "OK",
  "layers_moved": 2,
  "move_count": 7,
  "is_won": false,
  "tubes": [...]
}
```

### Example — Voice Command

```json
POST /api/voice-command
{
  "session_id": "abc-123",
  "text": "pour red into tube 2"
}
```
```json
{
  "voice_action": "pour_color",
  "success": true,
  "from_tube": 0,
  "tubes": [...]
}
```

---

## 🤖 AI Solver

The solver automatically picks the best algorithm based on puzzle complexity:

```
Complexity = num_tubes × tube_capacity

complexity ≤ 24  →  BFS   (breadth-first, guaranteed optimal path)
complexity  > 24  →  A*    (heuristic-guided, handles large state spaces)
```

### BFS — Optimal Solver

```python
def _bfs(self, start):
    queue = deque([start])
    visited = {start.key()}
    while queue:
        state = queue.popleft()
        for src, dst in state.legal_moves():
            next_state = state.apply_move(src, dst)
            if next_state.is_won():
                return next_state.path   # shortest solution
            visited.add(next_state.key())
            queue.append(next_state)
```

### A\* Heuristic

```python
def heuristic(self) -> int:
    # Number of tubes not yet complete (full + uniform color)
    return sum(1 for t in self.tubes
               if t["layers"] and
               (len(t["layers"]) != t["capacity"] or
                len(set(t["layers"])) != 1))
```

---

## 📊 Analytics

Every interaction is tracked and persisted to SQLite:

| Metric | Description |
|--------|-------------|
| `time_taken` | Seconds from level start to win |
| `moves` | Total pour moves made |
| `undo_count` | Number of undos used |
| `failed_attempts` | Invalid move attempts |
| `heatmap` | Click count per tube index |
| `won` | Whether the level was completed |

Visualized in the dashboard with Chart.js line + bar charts and an interactive color-coded heatmap.

---

## 🎙️ Voice Control

Supported commands (Chrome/Edge only):

| Say This | Action |
|----------|--------|
| `"Pour red into tube 2"` | Pours red-topped tube into tube 2 |
| `"Pour tube 1 into tube 3"` | Direct tube-to-tube pour |
| `"Undo move"` | Undoes the last action |
| `"Restart level"` | Restarts the current level |
| `"Hint"` or `"Solve"` | Triggers the AI solver |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Z` | Undo last move |
| `R` | Restart level |
| `Esc` | Deselect tube / Close all overlays |

---

## 🚀 Deployment

| Layer | Platform | URL |
|-------|----------|-----|
| 🎮 Frontend | Vercel | [aqua-sort-water-puzzle.vercel.app](https://aqua-sort-water-puzzle.vercel.app) |
| 🔌 Backend | Render | [watersortgame-backend.onrender.com](https://watersortgame-backend.onrender.com) |
| 💾 Database | SQLite on Render | Persistent within service lifetime |
| 📦 Source | GitHub | [metadore/watersortgame](https://github.com/metadore/watersortgame) |

### Deploy Your Own Copy

**1. Backend on Render:**
```
Root Directory:  backend
Build Command:   pip install -r requirements.txt
Start Command:   gunicorn app:app
Instance Type:   Free
```

**2. Frontend on Vercel:**
```
Root Directory:    frontend
Framework Preset:  Other
```

**3. Update API URL in `frontend/app.js`:**
```javascript
const API_BASE = "https://YOUR-RENDER-URL.onrender.com/api";
```

---

## 🎨 Design System

### Color Palette

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#050810` | Deep space base |
| Surface | `#0a0f1e` | Cards, panels |
| Accent Cyan | `#00d4ff` | Primary highlights, glow effects |
| Accent Purple | `#7b2fff` | Secondary highlights |
| Win Green | `#00ff88` | Success states, challenge mode |
| Error Red | `#ff4466` | Invalid moves, errors |

### Liquid Gradient Colors

| Color | From | To |
|-------|------|----|
| 🔴 Red | `#ff4e50` | `#fc466b` |
| 🔵 Blue | `#2980b9` | `#6dd5fa` |
| 🟢 Green | `#11998e` | `#38ef7d` |
| 🟡 Yellow | `#f7971e` | `#ffd200` |
| 🟣 Purple | `#834d9b` | `#d04ed6` |
| 🟠 Orange | `#f46b45` | `#eea849` |

### Typography
- **Display:** `Orbitron` — headers, badges, level numbers
- **Body:** `Exo 2` — paragraphs, UI text, labels

---

## 📝 License

```
MIT License

Copyright (c) 2025 metadore

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software.
```

---

<div align="center">

**Built with 💧 by [metadore](https://github.com/metadore)**

<br/>

[![Play Now](https://img.shields.io/badge/🎮%20Play%20Aqua%20Sort%20Now-00D4FF?style=for-the-badge)](https://aqua-sort-water-puzzle.vercel.app)
[![Star on GitHub](https://img.shields.io/github/stars/metadore/watersortgame?style=for-the-badge&logo=github&color=yellow)](https://github.com/metadore/watersortgame)

<br/>

*If you enjoyed this project, please ⭐ star it on GitHub — it helps a lot!*

<br/>

`Python` · `Flask` · `JavaScript` · `SQLite` · `BFS` · `A*` · `Chart.js` · `Web Speech API` · `Vercel` · `Render`

</div>
