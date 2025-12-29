"""Simple JSON-backed settings helper for the project."""
import json
import os
from typing import Dict, Any

_SETTINGS_PATH = os.path.join(os.path.dirname(__file__), 'settings.json')

DEFAULTS: Dict[str, Any] = {
    'show_splash': True,
    'reports_dir': 'reports',
}


def load_settings() -> Dict[str, Any]:
    try:
        if os.path.exists(_SETTINGS_PATH):
            with open(_SETTINGS_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    out = DEFAULTS.copy()
                    out.update(data)
                    return out
    except Exception:
        pass
    return DEFAULTS.copy()


def save_settings(s: Dict[str, Any]) -> None:
    try:
        with open(_SETTINGS_PATH, 'w', encoding='utf-8') as f:
            json.dump(s, f, indent=2)
    except Exception:
        # best-effort; do not fail the app for settings save errors
        pass
