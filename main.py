from pathlib import Path

from core.storage import load_state
from ui.main_window import run_app


if __name__ == "__main__":
    storage_path = Path("data/sessions.json")
    state = load_state(str(storage_path))
    run_app(state, storage_path)
