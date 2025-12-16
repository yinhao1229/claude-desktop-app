from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .state import AppState


class Storage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> AppState:
        if not self.path.exists():
            return AppState()
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return AppState.from_dict(data)

    def save(self, state: AppState) -> None:
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)


def load_state(path: Optional[str] = None) -> AppState:
    storage = Storage(Path(path) if path else Path("data/sessions.json"))
    return storage.load()


def save_state(state: AppState, path: Optional[str] = None) -> None:
    storage = Storage(Path(path) if path else Path("data/sessions.json"))
    storage.save(state)
