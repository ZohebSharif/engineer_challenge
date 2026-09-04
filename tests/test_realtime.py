import asyncio
import json
from collections import deque
from pathlib import Path
from typing import Any

import pytest

from voicebot.bridge import _openai_to_twilio, _twilio_to_openai
from voicebot.config import Settings
from voicebot.prompts import build_patient_prompt
from voicebot.realtime import RealtimeSession
from voicebot.scenarios import ScenarioRepository
from voicebot.sessions import SessionStore
from voicebot.turns import TurnManager


class FakeSocket:
    def __init__(self, incoming: list[dict[str, Any]] | None = None) -> None:
        self.sent: list[dict[str, Any]] = []
        self.incoming = deque(json.dumps(item) for item in (incoming or []))
        self.closed = False

    async def send(self, message: str) -> None:
        self.sent.append(json.loads(message))

    async def recv(self) -> str:
        if self.incoming:
            return self.incoming.popleft()
        await asyncio.Future()
        raise AssertionError("unreachable")

    async def close(self) -> None:
        self.closed = True


class FakeWebSocket:
    def __init__(self, incoming: list[dict[str, Any]] | None = None) -> None:
        self.incoming = deque(json.dumps(item) for item in (incoming or []))
        self.sent: list[dict[str, Any]] = []

    async def receive_text(self) -> str:
        return self.incoming.popleft()

    async def send_json(self, event: dict[str, Any]) -> None:
        self.sent.append(event)


SCENARIOS = ScenarioRepository(Path(__file__).parents[1] / "src/voicebot/scenario_data")


def test_scenarios_are_valid_and_prompt_constrains_behavior() -> None:
    scenarios = SCENARIOS.list()
    assert len(scenarios) == 3
    prompt = build_patient_prompt(scenarios[0])
    assert scenarios[0].persona in prompt
    assert scenarios[0].objective in prompt
    assert "one or two short spoken sentences" in prompt
    assert "Never invent" in prompt


@pytest.mark.asyncio
async def test_realtime_session_configures_direct_pcmu_audio() -> None:
    socket = FakeSocket()
    session = RealtimeSession(socket)
    await session.configure(SCENARIOS.load("appointment-scheduling"), "marin")
    update = socket.sent[0]
    assert update["type"] == "session.update"
    audio = update["session"]["audio"]
    assert audio["input"]["format"] == {"type": "audio/pcmu"}
    assert audio["output"]["format"] == {"type": "audio/pcmu"}
    assert audio["input"]["turn_detection"]["interrupt_response"] is True


@pytest.mark.asyncio
async def test_twilio_audio_is_forwarded_unchanged() -> None:
    websocket = FakeWebSocket(
        [
            {"event": "media", "sequenceNumber": "2", "media": {"payload": "base64pcmu"}},
            {"event": "stop"},
        ]
    )
    socket = FakeSocket()
    realtime = RealtimeSession(socket)
    sessions = SessionStore()
    await sessions.create("CA123", "MZ123")
    await _twilio_to_openai(
        websocket, realtime, "CA123", Settings(call_timeout_seconds=30), sessions
    )
    assert socket.sent == [{"type": "input_audio_buffer.append", "audio": "base64pcmu"}]
    session = await sessions.get("CA123")
    assert session is not None and session.media_messages == 1


@pytest.mark.asyncio
async def test_output_audio_and_barge_in_clear_twilio_buffer() -> None:
    socket = FakeSocket(
        [
            {"type": "response.output_audio.delta", "delta": "patient-audio"},
            {"type": "input_audio_buffer.speech_started"},
        ]
    )
    realtime = RealtimeSession(socket)
    websocket = FakeWebSocket()
    task = asyncio.create_task(
        _openai_to_twilio(websocket, realtime, "CA123", "MZ123", TurnManager())
    )
    await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert websocket.sent == [
        {"event": "media", "streamSid": "MZ123", "media": {"payload": "patient-audio"}},
        {"event": "clear", "streamSid": "MZ123"},
    ]
    assert {"type": "response.cancel"} in socket.sent
