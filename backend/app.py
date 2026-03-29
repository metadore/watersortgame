"""
app.py
Flask REST API for the Water Sort Puzzle Game.
Provides all game, analytics, AI solver, and voice command endpoints.
"""

import os
import sys
import uuid
import time
import json
import re
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Ensure backend directory is on path
sys.path.insert(0, os.path.dirname(__file__))

from game_engine import GameEngine, GRADIENT_COLORS
from ai_solver import AISolver
from difficulty_manager import DifficultyManager
from analytics import Analytics
import models

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Serve frontend folder as static files, templates for learn page
app = Flask(__name__,
            static_folder=FRONTEND_DIR,
            static_url_path="",
            template_folder=TEMPLATES_DIR)
CORS(app)

# Print paths on startup for debugging
print(f"  BASE_DIR     : {BASE_DIR}")
print(f"  FRONTEND_DIR : {FRONTEND_DIR}  (exists={os.path.isdir(FRONTEND_DIR)})")
print(f"  TEMPLATES_DIR: {TEMPLATES_DIR} (exists={os.path.isdir(TEMPLATES_DIR)})")

# Global (in-memory) state per session
sessions: dict = {}        # session_id → {"engine": GameEngine, "level": int, "start_time": float}
difficulty_manager = DifficultyManager()
analytics = Analytics()
solver = AISolver()

models.init_db()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_session(session_id: str) -> dict:
    return sessions.get(session_id, {})


def build_state_response(session_id: str) -> dict:
    s = get_session(session_id)
    if not s:
        return {"error": "Session not found"}
    engine: GameEngine = s["engine"]
    colors_meta = {c["id"]: c for c in GRADIENT_COLORS}
    tubes_out = []
    for i, tube in enumerate(engine.tubes):
        tubes_out.append({
            "index": i,
            "capacity": tube.capacity,
            "layers": tube.layers,
            "top_color": tube.top_color(),
            "is_empty": tube.is_empty(),
            "is_full": tube.is_full(),
            "is_complete": tube.is_complete(),
            "free_space": tube.free_space(),
            "heat": engine.click_heatmap.get(i, 0),
        })
    return {
        "session_id": session_id,
        "level": s["level"],
        "tubes": tubes_out,
        "move_count": engine.move_count,
        "is_won": engine.is_won(),
        "colors_meta": colors_meta,
        "valid_moves": engine.get_valid_moves(),
        "difficulty_score": difficulty_manager.difficulty_score,
    }


# ---------------------------------------------------------------------------
# Static file serving
# ---------------------------------------------------------------------------

@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/learn")
def serve_learn():
    return send_from_directory(TEMPLATES_DIR, "learn.html")


# Catch-all: serve any file from frontend/ (styles.css, app.js, etc.)
@app.route("/<path:filename>")
def serve_static(filename):
    # Don't intercept API routes
    if filename.startswith("api/"):
        return jsonify({"error": "Not found"}), 404
    return send_from_directory(FRONTEND_DIR, filename)


# ---------------------------------------------------------------------------
# API: Session / Level management
# ---------------------------------------------------------------------------

@app.route("/api/start-level", methods=["GET"])
def start_level():
    level = int(request.args.get("level", 1))
    session_id = request.args.get("session_id") or str(uuid.uuid4())

    config = difficulty_manager.get_level_config(level)
    engine = GameEngine()
    engine.load_level(config)

    sessions[session_id] = {
        "engine": engine,
        "level": level,
        "start_time": time.time(),
        "config": config,
    }
    analytics.start_session(session_id, level)

    return jsonify({
        **build_state_response(session_id),
        "message": f"Level {level} started!",
        "level_name": config.get("name", f"Level {level}"),
        "colors": GRADIENT_COLORS,
    })


@app.route("/api/move", methods=["POST"])
def make_move():
    data = request.get_json()
    session_id = data.get("session_id")
    src = data.get("from_tube")   # 0-indexed
    dst = data.get("to_tube")

    s = get_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    engine: GameEngine = s["engine"]
    success, reason, layers_moved = engine.pour(src, dst)

    if success:
        analytics.record_move(session_id, src, dst)
        if engine.is_won():
            time_taken = time.time() - s["start_time"]
            analytics.record_win(session_id)
            difficulty_manager.adjust(s["level"], time_taken)
            # Persist analytics
            rec = analytics.get_session(session_id) or {}
            models.record_analytics(rec)

        # Auto-save
        models.save_game(session_id, s["level"], engine.to_dict())
    else:
        analytics.record_failed_attempt(session_id)

    return jsonify({
        **build_state_response(session_id),
        "success": success,
        "reason": reason,
        "layers_moved": layers_moved,
    })


@app.route("/api/undo", methods=["POST"])
def undo_move():
    data = request.get_json()
    session_id = data.get("session_id")
    s = get_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    engine: GameEngine = s["engine"]
    undone = engine.undo()
    if undone:
        analytics.record_undo(session_id)
    models.save_game(session_id, s["level"], engine.to_dict())

    return jsonify({
        **build_state_response(session_id),
        "undone": undone,
    })


@app.route("/api/next-level", methods=["POST"])
def next_level():
    data = request.get_json()
    session_id = data.get("session_id")
    s = get_session(session_id)
    current_level = s["level"] if s else 1
    return start_level.__wrapped__(current_level + 1, session_id) if hasattr(start_level, '__wrapped__') \
        else jsonify({"redirect": f"/api/start-level?level={current_level + 1}&session_id={session_id}"})


@app.route("/api/restart", methods=["POST"])
def restart_level():
    data = request.get_json()
    session_id = data.get("session_id")
    s = get_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404
    level = s["level"]
    config = difficulty_manager.get_level_config(level)
    engine = GameEngine()
    engine.load_level(config)
    sessions[session_id]["engine"] = engine
    sessions[session_id]["start_time"] = time.time()
    analytics.start_session(session_id, level)
    return jsonify({**build_state_response(session_id), "restarted": True})


# ---------------------------------------------------------------------------
# API: AI Solver
# ---------------------------------------------------------------------------

@app.route("/api/ai-solve", methods=["GET"])
def ai_solve():
    session_id = request.args.get("session_id")
    s = get_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404

    engine: GameEngine = s["engine"]
    tubes_data = engine.snapshot()
    solution = solver.solve(tubes_data)

    if solution is None:
        return jsonify({"solvable": False, "message": "No solution found", "steps": []})

    steps = solver.format_solution(solution)
    return jsonify({
        "solvable": True,
        "steps": steps,
        "total_steps": len(steps),
        "message": f"Solution found in {len(steps)} moves",
    })


# ---------------------------------------------------------------------------
# API: Analytics
# ---------------------------------------------------------------------------

@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    records = models.get_analytics_records()
    in_mem = analytics.summary()
    return jsonify({
        "database_records": records,
        "session_summary": in_mem,
    })


# ---------------------------------------------------------------------------
# API: Voice command parser
# ---------------------------------------------------------------------------

TUBE_WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
    "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
    "6": 6, "7": 7, "8": 8, "9": 9, "10": 10,
}

COLOR_IDS = {c["id"] for c in GRADIENT_COLORS}


def parse_voice_command(text: str) -> dict:
    """
    Parse natural-language voice commands into game actions.
    Supports: "pour red into tube 2", "undo", "restart", "hint", "solve"
    """
    t = text.lower().strip()

    # Undo
    if re.search(r"\bundo\b", t):
        return {"action": "undo"}

    # Restart
    if re.search(r"\brestart\b|\breset\b|\bnew game\b", t):
        return {"action": "restart"}

    # Hint / solve
    if re.search(r"\bhint\b|\bsolve\b|\bhelp\b", t):
        return {"action": "solve"}

    # Pour color into tube N
    match = re.search(r"pour\s+(\w+)\s+(?:into|to)\s+tube\s+(\w+)", t)
    if match:
        color = match.group(1)
        tube_word = match.group(2)
        tube_num = TUBE_WORDS.get(tube_word)
        if color in COLOR_IDS and tube_num:
            return {"action": "pour_color", "color": color, "to_tube": tube_num - 1}

    # Pour tube N into tube M
    match = re.search(r"pour\s+tube\s+(\w+)\s+(?:into|to)\s+tube\s+(\w+)", t)
    if match:
        src = TUBE_WORDS.get(match.group(1))
        dst = TUBE_WORDS.get(match.group(2))
        if src and dst:
            return {"action": "pour", "from_tube": src - 1, "to_tube": dst - 1}

    return {"action": "unknown", "raw": text}


@app.route("/api/voice-command", methods=["POST"])
def voice_command():
    data = request.get_json()
    session_id = data.get("session_id")
    text = data.get("text", "")

    parsed = parse_voice_command(text)
    action = parsed.get("action")

    s = get_session(session_id)
    if not s:
        return jsonify({"error": "Session not found", "parsed": parsed}), 404

    engine: GameEngine = s["engine"]

    if action == "undo":
        engine.undo()
        return jsonify({**build_state_response(session_id), "voice_action": "undo"})

    elif action == "restart":
        level = s["level"]
        config = difficulty_manager.get_level_config(level)
        engine.load_level(config)
        sessions[session_id]["start_time"] = time.time()
        return jsonify({**build_state_response(session_id), "voice_action": "restart"})

    elif action == "solve":
        solution = solver.solve(engine.snapshot())
        steps = solver.format_solution(solution) if solution else []
        return jsonify({**build_state_response(session_id), "voice_action": "solve", "steps": steps})

    elif action == "pour":
        src = parsed["from_tube"]
        dst = parsed["to_tube"]
        success, reason, moved = engine.pour(src, dst)
        return jsonify({**build_state_response(session_id), "voice_action": "pour",
                        "success": success, "reason": reason})

    elif action == "pour_color":
        # Find first tube with that color on top
        color = parsed["color"]
        dst = parsed["to_tube"]
        src = None
        for i, tube in enumerate(engine.tubes):
            if tube.top_color() == color:
                src = i
                break
        if src is not None:
            success, reason, moved = engine.pour(src, dst)
            return jsonify({**build_state_response(session_id), "voice_action": "pour_color",
                            "success": success, "reason": reason, "from_tube": src})
        return jsonify({**build_state_response(session_id), "voice_action": "pour_color",
                        "success": False, "reason": f"No tube with {color} on top"})

    return jsonify({**build_state_response(session_id), "voice_action": "unknown", "parsed": parsed})


# ---------------------------------------------------------------------------
# API: Save / Load
# ---------------------------------------------------------------------------

@app.route("/api/save", methods=["POST"])
def save():
    data = request.get_json()
    session_id = data.get("session_id")
    s = get_session(session_id)
    if not s:
        return jsonify({"error": "Session not found"}), 404
    models.save_game(session_id, s["level"], s["engine"].to_dict())
    return jsonify({"saved": True, "session_id": session_id})


@app.route("/api/load", methods=["GET"])
def load():
    session_id = request.args.get("session_id")
    saved = models.load_game(session_id)
    if not saved:
        return jsonify({"found": False}), 404

    engine = GameEngine.from_dict(saved["state"])
    level = saved["level"]
    config = difficulty_manager.get_level_config(level)
    sessions[session_id] = {
        "engine": engine, "level": level,
        "start_time": time.time(), "config": config,
    }
    return jsonify({**build_state_response(session_id), "found": True, "loaded": True})


# ---------------------------------------------------------------------------
# API: Colors metadata
# ---------------------------------------------------------------------------

@app.route("/api/colors", methods=["GET"])
def get_colors():
    return jsonify({"colors": GRADIENT_COLORS})


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🎮 Water Sort Puzzle Game — Backend starting on http://localhost:5000")
    print("   Open http://localhost:5000 in your browser")
    app.run(debug=True, host="0.0.0.0", port=5000)