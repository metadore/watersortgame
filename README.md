# 💧 Aqua Sort — Water Puzzle Game

A production-quality, full-stack Water Sort Puzzle game with AI solving, voice control, analytics dashboard, dynamic difficulty, and an educational simulation page.

---

## 🗂 Project Structure

```
WaterSortGame/
├── backend/
│   ├── app.py                  # Flask REST API
│   ├── game_engine.py          # Core game logic (Tube, GameEngine classes)
│   ├── ai_solver.py            # BFS + A* optimal solver
│   ├── difficulty_manager.py   # Dynamic difficulty + procedural level gen
│   ├── analytics.py            # In-session analytics tracker
│   └── models.py               # SQLite persistence (save/load)
├── frontend/
│   ├── index.html              # Main game UI
│   ├── styles.css              # Dark futuristic theme
│   ├── app.js                  # Game controller + API calls
│   ├── animations.js           # Pour effects, confetti, ripple
│   ├── voice_control.js        # Web Speech API integration
│   └── visualizer.js           # Chart.js helpers
├── templates/
│   └── learn.html              # Educational simulation page
├── database/
│   └── game.db                 # Auto-created SQLite database
└── README.md
├── aquasort_docs.html
```

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- pip

### 1. Install dependencies

```bash
cd WaterSortGame/backend
pip install flask flask-cors
```

### 2. Start the backend

```bash
cd WaterSortGame/backend
python app.py
```

Backend runs at: **http://localhost:5000**

### 3. Open the game

Open your browser to **http://localhost:5000**

That's it — the Flask server serves both the API and the frontend!

---

## 🎮 Features

### Core Game
- 10 handcrafted levels (Easy → Grand Master)
- Procedural level generation for levels 11+
- Multicolor gradient liquid layers
- Smooth pour animations with particle effects
- Full undo stack
- Win detection

### 🤖 AI Solver
- BFS (optimal, small puzzles) + A* (large puzzles)
- "Show Solution" step-by-step panel
- Auto-play mode (executes solution automatically)

### 📊 Analytics Dashboard
- Session tracking (time, moves, undos, fails)
- Chart.js line + bar charts
- Tube click heatmap
- SQLite persistence

### ⚡ Dynamic Difficulty
- Adjusts based on solve time vs expected time
- Affects tube count, color count, empty tubes, scramble depth

### 🎙 Voice Control
- "Pour red into tube 2"
- "Undo move"
- "Restart level"
- "Hint" / "Solve"
- (Chrome/Edge only)

### 🎯 Challenge Mode
- Move limit per level
- Countdown timer
- Bonus score for fast completion

### 💾 Save / Load
- Auto-save after every move
- Manual save / load buttons
- SQLite backend storage

### 🌙 Dark / Light Mode
- Toggle with moon/sun button
- Preference persisted in localStorage

### 📚 Educational Page (/learn)
- Interactive simulation of the full request lifecycle
- Animated diagrams
- Code snippets with syntax highlighting
- Clickable step-by-step demo

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/start-level?level=N` | Initialize a level |
| POST | `/api/move` | Make a pour move |
| POST | `/api/undo` | Undo last move |
| POST | `/api/restart` | Restart current level |
| GET | `/api/ai-solve` | Get optimal solution |
| GET | `/api/analytics` | Get all analytics data |
| POST | `/api/voice-command` | Process voice command |
| POST | `/api/save` | Save game to DB |
| GET | `/api/load?session_id=X` | Load saved game |
| GET | `/api/colors` | Get color definitions |

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Z` | Undo |
| `R` | Restart |
| `Esc` | Deselect / Close overlays |

---

## 🏗 Architecture

The project follows strict separation of concerns:

- **game_engine.py** — Pure game logic, no Flask imports
- **ai_solver.py** — Search algorithms, no game imports
- **difficulty_manager.py** — Adaptive difficulty, pure Python
- **analytics.py** — Stats recording, no DB dependencies
- **models.py** — SQLite only, no game logic
- **app.py** — Thin API layer, orchestrates all modules

---

## 🎨 Design System

Color palette:
- Background: `#050810` (deep space)
- Accent: `#00d4ff` (cyan glow)
- Accent 2: `#7b2fff` (purple)
- Win: `#00ff88` (neon green)
- Font: Orbitron (headings) + Exo 2 (body)

---
## DO CHECK OUT THE CONCEPTS,LIBRARIES USED IN THE PROJECT
https://1drv.ms/u/c/e8f20ce819501d80/IQABmvnYOwc9R62zzqC-LRIYAdDLUb2T7tdRoqjNeh_6DKU?e=gw7H2k

## 📝 License

MIT — Built as a portfolio project.
