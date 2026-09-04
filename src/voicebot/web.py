import asyncio
import json
from typing import Annotated, Any

import structlog
from fastapi import Depends, FastAPI, Form, Response, WebSocket, WebSocketDisconnect, status
from twilio.twiml.voice_response import Connect, VoiceResponse

from voicebot.config import Settings, get_settings
from voicebot.logging import configure_logging
from voicebot.sessions import SessionStore

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger()
app = FastAPI(title="Voicebot", version="0.1.0")
app.state.sessions = SessionStore()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/twilio/voice")
async def voice_webhook(config: Annotated[Settings, Depends(get_settings)]) -> Response:
    if config.public_base_url is None or config.media_stream_token is None:
        return Response("Live stream configuration is incomplete", status_code=503)
    base = (
        str(config.public_base_url)
        .rstrip("/")
        .replace("https://", "wss://")
        .replace("http://", "ws://")
    )
    response = VoiceResponse()
    connect = Connect()
    connect.stream(url=f"{base}/twilio/media?token={config.media_stream_token.get_secret_value()}")
    response.append(connect)
    return Response(content=str(response), media_type="application/xml")


@app.post("/twilio/status")
async def call_status(
    call_sid: Annotated[str, Form(alias="CallSid")],
    call_status: Annotated[str, Form(alias="CallStatus")],
) -> dict[str, bool]:
    await logger.ainfo("twilio_call_status", call_sid=call_sid, call_status=call_status)
    return {"accepted": True}


@app.websocket("/twilio/media")
async def media_stream(
    websocket: WebSocket, config: Annotated[Settings, Depends(get_settings)]
) -> None:
    expected = config.media_stream_token.get_secret_value() if config.media_stream_token else None
    if expected is None or websocket.query_params.get("token") != expected:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    call_sid: str | None = None
    try:
        while True:
            raw = await asyncio.wait_for(
                websocket.receive_text(), timeout=config.call_timeout_seconds
            )
            event: dict[str, Any] = json.loads(raw)
            event_type = str(event.get("event", "unknown"))
            if event_type == "start":
                start = event.get("start", {})
                call_sid = str(start.get("callSid", ""))
                stream_sid = str(start.get("streamSid", ""))
                if not call_sid:
                    await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                    return
                await app.state.sessions.create(call_sid, stream_sid)
                await logger.ainfo(
                    "twilio_stream_started", call_sid=call_sid, stream_sid=stream_sid
                )
            elif event_type == "media" and call_sid:
                session = await app.state.sessions.get(call_sid)
                if session:
                    session.media_messages += 1
                await logger.adebug(
                    "twilio_media_received",
                    call_sid=call_sid,
                    sequence_number=event.get("sequenceNumber"),
                )
            elif event_type == "stop":
                await logger.ainfo("twilio_stream_stopped", call_sid=call_sid)
                break
            else:
                await logger.ainfo("twilio_control_event", event=event_type, call_sid=call_sid)
    except TimeoutError:
        await logger.awarning("twilio_stream_timeout", call_sid=call_sid)
        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
    except WebSocketDisconnect:
        await logger.ainfo("twilio_stream_disconnected", call_sid=call_sid)
    finally:
        if call_sid:
            await app.state.sessions.remove(call_sid)
