import asyncio
import json
from collections import deque
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from starlette.websockets import WebSocketDisconnect

from voicebot.bridge import _openai_to_twilio, _twilio_to_openai
from voicebot.config import Settings, get_settings
from voicebot.logging import configure_logging
from voicebot.prompts import build_patient_prompt
from voicebot.realtime import RealtimeSession
from voicebot.scenarios import Scenario, ScenarioRepository
from voicebot.sessions import SessionStore
from voicebot.turns import TurnManager
from voicebot.web import app


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


class FakeRealtimeClient:
    def __init__(self, session: RealtimeSession) -> None:
        self.session = session
        self.opened = False

    async def open(self, scenario: Scenario) -> RealtimeSession:
        self.opened = True
        return self.session


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
    assert len(scenarios) == 12
    prompt = build_patient_prompt(scenarios[0])
    assert scenarios[0].persona in prompt
    assert scenarios[0].objective in prompt
    assert "one or two short spoken sentences" in prompt
    assert "Never invent" in prompt


def test_every_scenario_prompt_pins_facts_identity_language_and_role() -> None:
    """Call 3 drifted: DOB 1988 became 1980, speech switched to Spanish, patient offered help."""
    for scenario in SCENARIOS.list():
        prompt = build_patient_prompt(scenario)
        for fact in scenario.facts:
            assert fact in prompt
        assert "Immutable facts" in prompt
        assert "Repeat any fact identically" in prompt
        assert "never accept a corrected version of your own" in prompt
        assert f"Speak only {scenario.language} for the whole call" in prompt
        assert "never the receptionist" in prompt
        assert '"I can help with' in prompt
        assert "Let the other party finish speaking" in prompt
        assert "improvise wording" in prompt


def test_prompt_language_follows_the_scenario_not_a_hard_coded_default() -> None:
    english = SCENARIOS.load("appointment-scheduling")
    assert english.language == "English"
    assert "Speak only English for the whole call" in build_patient_prompt(english)
    spanish = english.model_copy(update={"language": "Spanish"})
    spanish_prompt = build_patient_prompt(spanish)
    assert "Speak only Spanish for the whole call" in spanish_prompt
    assert "Speak only English" not in spanish_prompt


def test_immutable_dob_fact_is_rendered_verbatim() -> None:
    prompt = build_patient_prompt(SCENARIOS.load("appointment-scheduling"))
    assert "Date of birth is February 14, 1988." in prompt
    assert "1980" not in prompt


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
    assert audio["input"]["turn_detection"]["interrupt_response"] is False
    turn_detection = audio["input"]["turn_detection"]
    assert turn_detection["silence_duration_ms"] >= 1000, "patient must let the office finish"
    assert turn_detection["create_response"] is False, (
        "session must open closed so the remote side owns the first turn"
    )
    assert update["session"]["instructions"] == build_patient_prompt(
        SCENARIOS.load("appointment-scheduling")
    )


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
            {"type": "error", "error": {"code": "response_cancel_not_active"}},
        ]
    )
    realtime = RealtimeSession(socket)
    websocket = FakeWebSocket()
    task = asyncio.create_task(
        _openai_to_twilio(
            websocket, realtime, "CA123", "MZ123", TurnManager(), _hold_settings(0.05)
        )
    )
    for _ in range(4):
        await asyncio.sleep(0)
    assert not task.done()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert websocket.sent == [
        {"event": "media", "streamSid": "MZ123", "media": {"payload": "patient-audio"}},
        {"event": "clear", "streamSid": "MZ123"},
    ]
    assert {"type": "response.cancel"} in socket.sent


def test_media_endpoint_validates_start_token_and_cleans_up_session() -> None:
    realtime_socket = FakeSocket()
    client = FakeRealtimeClient(RealtimeSession(realtime_socket))

    def settings() -> Settings:
        return Settings(
            media_stream_token=SecretStr("stream-secret"),
            call_timeout_seconds=30,
        )

    previous_client = app.state.realtime_client
    app.state.realtime_client = client
    app.dependency_overrides[get_settings] = settings
    try:
        with TestClient(app).websocket_connect("/twilio/media") as websocket:
            websocket.send_json({"event": "connected", "protocol": "Call", "version": "1.0.0"})
            websocket.send_json(
                {
                    "event": "start",
                    "start": {
                        "callSid": "CA123",
                        "streamSid": "MZ123",
                        "customParameters": {
                            "scenario": "appointment-scheduling",
                            "token": "stream-secret",
                        },
                    },
                }
            )
            websocket.send_json(
                {
                    "event": "media",
                    "sequenceNumber": "2",
                    "media": {"payload": "base64pcmu"},
                }
            )
            websocket.send_json({"event": "stop"})
    finally:
        app.dependency_overrides.clear()
        app.state.realtime_client = previous_client

    assert client.opened
    assert {"type": "input_audio_buffer.append", "audio": "base64pcmu"} in realtime_socket.sent
    assert realtime_socket.closed
    assert asyncio.run(app.state.sessions.count()) == 0


def test_media_endpoint_rejects_invalid_start_token() -> None:
    def settings() -> Settings:
        return Settings(media_stream_token=SecretStr("stream-secret"), call_timeout_seconds=30)

    app.dependency_overrides[get_settings] = settings
    try:
        with (
            pytest.raises(WebSocketDisconnect) as disconnect,
            TestClient(app).websocket_connect("/twilio/media") as websocket,
        ):
            websocket.send_json({"event": "connected", "protocol": "Call", "version": "1.0.0"})
            websocket.send_json(
                {
                    "event": "start",
                    "start": {
                        "callSid": "CA123",
                        "streamSid": "MZ123",
                        "customParameters": {
                            "scenario": "appointment-scheduling",
                            "token": "wrong",
                        },
                    },
                }
            )
            websocket.receive_json()
    finally:
        app.dependency_overrides.clear()
    assert disconnect.value.code == 1008


def _token_settings() -> Settings:
    return Settings(media_stream_token=SecretStr("stream-secret"), call_timeout_seconds=30)


def test_media_endpoint_survives_twilio_connected_then_start_then_media() -> None:
    """Twilio's real frame order must reach OpenAI; a 1008 or a log crash hangs up the call."""
    realtime_socket = FakeSocket()
    client = FakeRealtimeClient(RealtimeSession(realtime_socket))
    previous_client = app.state.realtime_client
    app.state.realtime_client = client
    app.dependency_overrides[get_settings] = _token_settings
    try:
        with TestClient(app).websocket_connect("/twilio/media") as websocket:
            websocket.send_json({"event": "connected", "protocol": "Call", "version": "1.0.0"})
            websocket.send_json(
                {
                    "event": "start",
                    "start": {
                        "callSid": "CA7c21e393",
                        "streamSid": "MZ7c21e393",
                        "customParameters": {
                            "scenario": "appointment-scheduling",
                            "token": "stream-secret",
                        },
                    },
                }
            )
            websocket.send_json({"event": "mark", "mark": {"name": "outbound"}})
            websocket.send_json(
                {"event": "media", "sequenceNumber": "3", "media": {"payload": "cGNtdQ=="}}
            )
            websocket.send_json({"event": "stop"})
    finally:
        app.dependency_overrides.clear()
        app.state.realtime_client = previous_client
    assert client.opened
    assert {"type": "input_audio_buffer.append", "audio": "cGNtdQ=="} in realtime_socket.sent


def test_media_endpoint_rejects_media_before_start() -> None:
    app.dependency_overrides[get_settings] = _token_settings
    try:
        with (
            pytest.raises(WebSocketDisconnect) as disconnect,
            TestClient(app).websocket_connect("/twilio/media") as websocket,
        ):
            websocket.send_json({"event": "connected", "protocol": "Call", "version": "1.0.0"})
            websocket.send_json(
                {"event": "media", "sequenceNumber": "1", "media": {"payload": "cGNtdQ=="}}
            )
            websocket.receive_json()
    finally:
        app.dependency_overrides.clear()
    assert disconnect.value.code == 1008


def test_media_endpoint_rejects_repeated_connected_frames() -> None:
    app.dependency_overrides[get_settings] = _token_settings
    try:
        with (
            pytest.raises(WebSocketDisconnect) as disconnect,
            TestClient(app).websocket_connect("/twilio/media") as websocket,
        ):
            websocket.send_json({"event": "connected", "protocol": "Call", "version": "1.0.0"})
            websocket.send_json({"event": "connected", "protocol": "Call", "version": "1.0.0"})
            websocket.receive_json()
    finally:
        app.dependency_overrides.clear()
    assert disconnect.value.code == 1008


def test_media_endpoint_rejects_untokened_start_after_connected() -> None:
    app.dependency_overrides[get_settings] = _token_settings
    try:
        with (
            pytest.raises(WebSocketDisconnect) as disconnect,
            TestClient(app).websocket_connect("/twilio/media") as websocket,
        ):
            websocket.send_json({"event": "connected", "protocol": "Call", "version": "1.0.0"})
            websocket.send_json(
                {
                    "event": "start",
                    "start": {
                        "callSid": "CA123",
                        "streamSid": "MZ123",
                        "customParameters": {"scenario": "appointment-scheduling"},
                    },
                }
            )
            websocket.receive_json()
    finally:
        app.dependency_overrides.clear()
    assert disconnect.value.code == 1008


@pytest.mark.asyncio
async def test_twilio_control_frames_do_not_kill_the_bridge() -> None:
    """Twilio `mark`/`dtmf` frames are logged, not fatal; a raised error ends the call."""
    websocket = FakeWebSocket(
        [
            {"event": "mark", "mark": {"name": "outbound"}},
            {"event": "dtmf", "dtmf": {"digit": "1"}},
            {"event": "media", "sequenceNumber": "4", "media": {"payload": "cGNtdQ=="}},
            {"event": "stop"},
        ]
    )
    socket = FakeSocket()
    sessions = SessionStore()
    await sessions.create("CA123", "MZ123")
    settings = Settings(media_stream_token=SecretStr("stream-secret"), call_timeout_seconds=30)
    await _twilio_to_openai(
        websocket,  # type: ignore[arg-type]
        RealtimeSession(socket),  # type: ignore[arg-type]
        "CA123",
        settings,
        sessions,
    )
    assert {"type": "input_audio_buffer.append", "audio": "cGNtdQ=="} in socket.sent


@pytest.mark.asyncio
async def test_unhandled_openai_events_do_not_kill_the_bridge() -> None:
    """Realtime lifecycle events log at debug level without aborting the stream."""
    configure_logging("DEBUG")
    try:
        socket = FakeSocket(
            [
                {"type": "session.created"},
                {"type": "response.output_audio.delta", "delta": "cGNtdQ=="},
                {"type": "response.done"},
            ]
        )
        websocket = FakeWebSocket()
        task = asyncio.create_task(
            _openai_to_twilio(
                websocket,  # type: ignore[arg-type]
                RealtimeSession(socket),  # type: ignore[arg-type]
                "CA123",
                "MZ123",
                TurnManager(),
                _hold_settings(0.05),
            )
        )
        for _ in range(4):
            await asyncio.sleep(0)
        assert not task.done()
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
    finally:
        configure_logging("INFO")
    assert websocket.sent == [
        {"event": "media", "streamSid": "MZ123", "media": {"payload": "cGNtdQ=="}}
    ]


def _hold_settings(hold: float) -> Settings:
    return Settings(call_timeout_seconds=30, opening_hold_seconds=hold)


@pytest.mark.asyncio
async def test_opening_turn_is_released_by_the_remote_side_not_a_timer() -> None:
    """Reproduces calls 5-7: IVR notice, long gap, then greeting.

    The notice ending must hand turn-taking back to server VAD WITHOUT us speaking, so the
    greeting is answered by normal VAD at its own turn end. A timer-based release would fire
    during the 2.55s notice->greeting gap measured in call-007 and collide again.
    """
    socket = FakeSocket(
        [
            {"type": "input_audio_buffer.speech_started"},  # recording notice
            {"type": "input_audio_buffer.speech_stopped"},
        ]
    )
    task = asyncio.create_task(
        _openai_to_twilio(
            FakeWebSocket(),  # type: ignore[arg-type]
            RealtimeSession(socket),  # type: ignore[arg-type]
            "CA123",
            "MZ123",
            TurnManager(),
            _hold_settings(0.1),
        )
    )
    await asyncio.sleep(0.05)
    assert socket.sent == [
        {
            "type": "session.update",
            "session": {
                "type": "realtime",
                "audio": {
                    "input": {
                        "turn_detection": {
                            "type": "server_vad",
                            "threshold": 0.55,
                            "prefix_padding_ms": 300,
                            "silence_duration_ms": 1200,
                            "create_response": True,
                            "interrupt_response": False,
                        }
                    }
                },
            },
        }
    ], "release must be a bare session.update, never a response.create"
    assert {"type": "response.create"} not in socket.sent
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_opening_speaks_when_the_remote_waits_after_the_notice() -> None:
    """call-004 pattern: notice ends, then the office waits for the caller.

    Event-driven release alone would leave us mute (enabling create_response cannot answer an
    already-ended turn), so the hold must fire and speak. call-004 measured 12.4s of far-end
    silence after the notice; without this we regress that call from 7.8s to dead air.
    """
    socket = FakeSocket(
        [
            {"type": "input_audio_buffer.speech_started"},
            {"type": "input_audio_buffer.speech_stopped"},
        ]
    )
    task = asyncio.create_task(
        _openai_to_twilio(
            FakeWebSocket(),  # type: ignore[arg-type]
            RealtimeSession(socket),  # type: ignore[arg-type]
            "CA123",
            "MZ123",
            TurnManager(),
            _hold_settings(0.1),
        )
    )
    await asyncio.sleep(0.05)
    assert {"type": "response.create"} not in socket.sent, "spoke inside the hold window"
    await asyncio.sleep(0.2)
    assert {"type": "response.create"} in socket.sent, "never spoke; remote was waiting for us"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


def test_default_opening_hold_exceeds_the_largest_observed_greeting_gap() -> None:
    """Measured notice->greeting gaps: 1.65s (calls 5-6), 2.55s (call-007)."""
    assert Settings().opening_hold_seconds > 2.55


@pytest.mark.asyncio
async def test_opening_backstop_never_fires_while_the_remote_is_still_speaking() -> None:
    """speech_started with no speech_stopped must not time out into talking over them."""
    socket = FakeSocket([{"type": "input_audio_buffer.speech_started"}])
    task = asyncio.create_task(
        _openai_to_twilio(
            FakeWebSocket(),  # type: ignore[arg-type]
            RealtimeSession(socket),  # type: ignore[arg-type]
            "CA123",
            "MZ123",
            TurnManager(),
            _hold_settings(0.05),
        )
    )
    await asyncio.sleep(0.5)
    assert socket.sent == [], "spoke over an in-progress remote turn"
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_opening_turn_releases_when_the_remote_never_speaks() -> None:
    """A silent answer emits no speech_stopped; the absolute cap must still release us."""
    socket = FakeSocket()
    task = asyncio.create_task(
        _openai_to_twilio(
            FakeWebSocket(),  # type: ignore[arg-type]
            RealtimeSession(socket),  # type: ignore[arg-type]
            "CA123",
            "MZ123",
            TurnManager(),
            _hold_settings(0.05),
        )
    )
    await asyncio.sleep(0.4)
    assert {"type": "response.create"} in socket.sent
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task


@pytest.mark.asyncio
async def test_opening_gate_does_not_weaken_barge_in_after_release() -> None:
    """Post-opening interruption behaviour must be byte-identical to before the gate."""
    socket = FakeSocket(
        [
            {"type": "input_audio_buffer.speech_stopped"},
            {"type": "response.output_audio.delta", "delta": "patient-audio"},
            {"type": "input_audio_buffer.speech_started"},
        ]
    )
    websocket = FakeWebSocket()
    task = asyncio.create_task(
        _openai_to_twilio(
            websocket,  # type: ignore[arg-type]
            RealtimeSession(socket),  # type: ignore[arg-type]
            "CA123",
            "MZ123",
            TurnManager(),
            _hold_settings(0.05),
        )
    )
    await asyncio.sleep(0.3)
    assert {"type": "response.cancel"} in socket.sent
    assert {"event": "clear", "streamSid": "MZ123"} in websocket.sent
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
