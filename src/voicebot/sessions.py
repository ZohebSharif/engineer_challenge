import asyncio
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(slots=True)
class CallSession:
    call_sid: str
    stream_sid: str | None = None
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    media_messages: int = 0


class SessionStore:
    """Concurrency-safe in-memory state for active calls, keyed by CallSid."""

    def __init__(self) -> None:
        self._sessions: dict[str, CallSession] = {}
        self._lock = asyncio.Lock()

    async def create(self, call_sid: str, stream_sid: str | None = None) -> CallSession:
        async with self._lock:
            session = CallSession(call_sid=call_sid, stream_sid=stream_sid)
            self._sessions[call_sid] = session
            return session

    async def get(self, call_sid: str) -> CallSession | None:
        async with self._lock:
            return self._sessions.get(call_sid)

    async def remove(self, call_sid: str) -> CallSession | None:
        async with self._lock:
            return self._sessions.pop(call_sid, None)

    async def count(self) -> int:
        async with self._lock:
            return len(self._sessions)
