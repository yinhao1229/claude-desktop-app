from __future__ import annotations

import datetime as dt
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional


ISO_FORMAT = "%Y-%m-%dT%H:%M:%S"


def now_ts() -> str:
    return dt.datetime.now().strftime(ISO_FORMAT)


@dataclass
class Message:
    role: str
    content: str
    ts: str = field(default_factory=now_ts)


@dataclass
class Session:
    id: str
    title: str
    created_at: str
    updated_at: str
    messages: List[Message] = field(default_factory=list)
    system_prompt: str = ""
    temperature: float = 1.0
    max_tokens: Optional[int] = None

    def add_message(self, message: Message) -> None:
        self.messages.append(message)
        self.updated_at = now_ts()


class AppState:
    def __init__(self) -> None:
        self.sessions: Dict[str, Session] = {}
        self.active_session_id: Optional[str] = None
        self.is_generating: bool = False

    @property
    def active_session(self) -> Optional[Session]:
        if self.active_session_id:
            return self.sessions.get(self.active_session_id)
        return None

    def create_session(self, title: str = "新对话") -> Session:
        session_id = str(uuid.uuid4())
        ts = now_ts()
        session = Session(
            id=session_id,
            title=title,
            created_at=ts,
            updated_at=ts,
            messages=[],
        )
        self.sessions[session_id] = session
        self.active_session_id = session_id
        return session

    def delete_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            del self.sessions[session_id]
            if self.active_session_id == session_id:
                self.active_session_id = next(iter(self.sessions), None)

    def rename_session(self, session_id: str, title: str) -> None:
        session = self.sessions.get(session_id)
        if session:
            session.title = title
            session.updated_at = now_ts()

    def set_active_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            self.active_session_id = session_id

    def add_message(self, role: str, content: str) -> Message:
        session = self.active_session
        if not session:
            raise RuntimeError("没有激活的会话")
        message = Message(role=role, content=content)
        session.add_message(message)
        return message

    def to_dict(self) -> Dict[str, Dict]:
        return {
            "sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at,
                    "messages": [m.__dict__ for m in s.messages],
                    "system_prompt": s.system_prompt,
                    "temperature": s.temperature,
                    "max_tokens": s.max_tokens,
                }
                for s in self.sessions.values()
            ],
            "active_session_id": self.active_session_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AppState":
        state = cls()
        for session_data in data.get("sessions", []):
            messages = [Message(**m) for m in session_data.get("messages", [])]
            session = Session(
                id=session_data["id"],
                title=session_data.get("title", "新对话"),
                created_at=session_data.get("created_at", now_ts()),
                updated_at=session_data.get("updated_at", now_ts()),
                messages=messages,
                system_prompt=session_data.get("system_prompt", ""),
                temperature=float(session_data.get("temperature", 1.0)),
                max_tokens=session_data.get("max_tokens"),
            )
            state.sessions[session.id] = session
        state.active_session_id = data.get("active_session_id") or next(iter(state.sessions), None)
        return state
