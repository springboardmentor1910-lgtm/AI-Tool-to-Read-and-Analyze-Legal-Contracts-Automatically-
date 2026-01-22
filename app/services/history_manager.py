import json
import os
from datetime import datetime
from typing import List, Dict, Any

HISTORY_FILE = "history.json"

def get_history() -> List[Dict[str, Any]]:
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history: List[Dict[str, Any]]):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def add_action(action_type: str, details: Dict[str, Any]):
    history = get_history()
    new_action = {
        "id": len(history) + 1,
        "timestamp": datetime.now().isoformat(),
        "type": action_type,
        "details": details
    }
    history.insert(0, new_action)  # Most recent first
    # Keep only last 50 actions
    save_history(history[:50])
    return new_action
