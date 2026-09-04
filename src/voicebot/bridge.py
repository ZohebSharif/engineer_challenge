import asyncio
import contextlib
import json
from typing import Any, Protocol, cast

import structlog
from fastapi import WebSocket, WebSocketDisconnect, status

from voicebot.config import Settings
from voicebot.realtime import OpenAIRealtimeClient, RealtimeSession
from voicebot.scenarios import ScenarioRepository
from voicebot.sessions import SessionStore
from voicebot.turns import TurnManager

logger = structlog.get_logger()


class RealtimeClient(Protocol):
    async def open(self, scenario: object) -> RealtimeSession: ...


async def run_media_bridge(
    websocket: WebSocket,
    settings: Settings,
    sessions: SessionStore,
    realtime_client: OpenAIRealtimeClient | None = None,
    scenarios: ScenarioRepository | None = None,
) -> None:
    """Bridge Twilio PCMU frames to OpenAI and return generated PCMU unchanged."""
    expected = (
        settings.media_stream_token.get_secret_value() if settings.media_stream_token else None
    )
    if expected is None or websocket.query_params.get("token") != expected:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    call_sid: str | None = None
    realtime: RealtimeSession | None = None
    try:
        raw = await asyncio.wait_for(
            websocket.receive_text(), timeout=settings.call_timeout_seconds
        )
        first = _parse_event(raw)
        if first.get("event") != "start":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        start = _mapping(first.get("start"))
        call_sid = str(start.get("callSid", ""))
        stream_sid = str(start.get("streamSid", ""))
        custom = _mapping(start.get("customParameters"))
        scenario_id = str(custom.get("scenario", settings.default_scenario))
        if not call_sid or not stream_sid:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        scenario = (scenarios or ScenarioRepository()).load(scenario_id)
        await sessions.create(call_sid, stream_sid)
        await logger.ainfo(
            "twilio_stream_started",
            call_sid=call_sid,
            stream_sid=stream_sid,
            scenario=scenario.id,
        )
        realtime = await (realtime_client or OpenAIRealtimeClient(settings)).open(scenario)
        turns = TurnManager()
        tasks = {
            asyncio.create_task(
                _twilio_to_openai(websocket, realtime, call_sid, settings, sessions)
            ),
            asyncio.create_task(
                _openai_to_twilio(websocket, realtime, call_sid, stream_sid, turns)
            ),
        }
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
        await asyncio.gather(*pending, return_exceptions=True)
        for task in done:
            task.result()
    except TimeoutError:
        await logger.awarning("twilio_stream_timeout", call_sid=call_sid)
        with contextlib.suppress(RuntimeError):
            await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
    except WebSocketDisconnect:
        await logger.ainfo("twilio_stream_disconnected", call_sid=call_sid)
    finally:
        if realtime is not None:
            await realtime.close()
        if call_sid:
            await sessions.remove(call_sid)
        await logger.ainfo("media_bridge_closed", call_sid=call_sid)


async def _twilio_to_openai(
    websocket: WebSocket,
    realtime: RealtimeSession,
    call_sid: str,
    settings: Settings,
    sessions: SessionStore,
) -> None:
    while True:
        raw = await asyncio.wait_for(
            websocket.receive_text(), timeout=settings.call_timeout_seconds
        )
        event = _parse_event(raw)
        event_type = str(event.get("event", "unknown"))
        if event_type == "media":
            media = _mapping(event.get("media"))
            payload = media.get("payload")
            if isinstance(payload, str):
                await realtime.send_audio(payload)
                session = await sessions.get(call_sid)
                if session:
                    session.media_messages += 1
            await logger.adebug(
                "twilio_media_received",
                call_sid=call_sid,
                sequence_number=event.get("sequenceNumber"),
            )
        elif event_type == "stop":
            await logger.ainfo("twilio_stream_stopped", call_sid=call_sid)
            return
        else:
            await logger.ainfo("twilio_control_event", event=event_type, call_sid=call_sid)


async def _openai_to_twilio(
    websocket: WebSocket,
    realtime: RealtimeSession,
    call_sid: str,
    stream_sid: str,
    turns: TurnManager,
) -> None:
    while True:
        event = await realtime.receive()
        event_type = str(event.get("type", "unknown"))
        if event_type == "response.output_audio.delta":
            delta = event.get("delta")
            if isinstance(delta, str):
                turns.output_started()
                await websocket.send_json(
                    {"event": "media", "streamSid": stream_sid, "media": {"payload": delta}}
                )
        elif event_type == "input_audio_buffer.speech_started" and turns.should_interrupt():
            await realtime.cancel_response()
            await websocket.send_json({"event": "clear", "streamSid": stream_sid})
            turns.output_finished()
            await logger.ainfo("patient_speech_interrupted", call_sid=call_sid)
        elif event_type in {"response.done", "response.output_audio.done"}:
            turns.output_finished()
        elif event_type == "error":
            await logger.aerror(
                "openai_realtime_error", call_sid=call_sid, error=event.get("error")
            )
            raise RuntimeError("OpenAI Realtime returned an error")
        else:
            await logger.adebug("openai_realtime_event", call_sid=call_sid, event=event_type)


def _parse_event(raw: str) -> dict[str, Any]:
    parsed: object = json.loads(raw)
    if not isinstance(parsed, dict):
        raise ValueError("Twilio event must be a JSON object")
    return cast(dict[str, Any], parsed)


def _mapping(value: object) -> dict[str, Any]:
    return cast(dict[str, Any], value) if isinstance(value, dict) else {}
