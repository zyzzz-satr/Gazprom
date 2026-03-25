import os
from typing import Dict

class StateManager:
    _SESSIONS: Dict[str, Dict] = {}

    @staticmethod
    def get_mode() -> str:
        return os.environ.get("APP_MODE", "OFFLINE").upper()

    @staticmethod
    def set_mode(mode: str) -> None:
        mode = mode.upper()
        os.environ["APP_MODE"] = mode

    @classmethod
    def ensure_session(cls, session_id: str) -> None:
        if session_id not in cls._SESSIONS:
            cls._SESSIONS[session_id] = {"history": [], "mode": cls.get_mode()}

    @classmethod
    def get_session(cls, session_id: str) -> Dict:
        return cls._SESSIONS.get(session_id, {"history": [], "mode": cls.get_mode()})

    @classmethod
    def update_session(cls, session_id: str, updates: Dict) -> None:
        sess = cls._SESSIONS.get(session_id, {"history": [], "mode": cls.get_mode()})
        sess.update(updates)
        cls._SESSIONS[session_id] = sess
