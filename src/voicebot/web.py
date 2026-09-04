from typing import Annotated, cast

import structlog
from fastapi import Depends, FastAPI, Form, Query, Response, WebSocket
from twilio.twiml.voice_response import Connect, Stream, VoiceResponse

from voicebot.bridge import run_media_bridge
from voicebot.config import Settings, get_settings
from voicebot.logging import configure_logging
from voicebot.scenarios import ScenarioRepository
from voicebot.sessions import SessionStore

settings = get_settings()
configure_logging(settings.log_level)
logger = structlog.get_logger()
app = FastAPI(title="Voicebot", version="0.2.0")
app.state.sessions = SessionStore()
app.state.realtime_client = None
app.state.scenarios = ScenarioRepository()


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/twilio/voice")
async def voice_webhook(
    config: Annotated[Settings, Depends(get_settings)],
    scenario: Annotated[str, Query()] = "appointment-scheduling",
) -> Response:
    if config.public_base_url is None or config.media_stream_token is None:
        return Response("Live stream configuration is incomplete", status_code=503)
    try:
        selected = app.state.scenarios.load(scenario)
    except ValueError as exc:
        return Response(str(exc), status_code=400)
    base = (
        str(config.public_base_url)
        .rstrip("/")
        .replace("https://", "wss://")
        .replace("http://", "ws://")
    )
    response = VoiceResponse()
    connect = Connect()
    stream = cast(
        Stream,
        connect.stream(url=f"{base}/twilio/media"),
    )
    stream.parameter(name="scenario", value=selected.id)
    stream.parameter(name="token", value=config.media_stream_token.get_secret_value())
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
    await run_media_bridge(
        websocket,
        config,
        app.state.sessions,
        realtime_client=app.state.realtime_client,
        scenarios=app.state.scenarios,
    )
