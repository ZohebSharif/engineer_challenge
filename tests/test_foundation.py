from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from click.utils import strip_ansi
from fastapi.testclient import TestClient
from pydantic import SecretStr
from twilio.request_validator import RequestValidator
from typer.testing import CliRunner

from voicebot.artifacts import ArtifactManager
from voicebot.cli import app as cli_app
from voicebot.config import AUTHORIZED_DESTINATION, Settings, get_settings
from voicebot.telephony import TwilioGateway
from voicebot.web import app


def live_settings() -> Settings:
    return Settings(
        public_base_url="https://voice.example",
        twilio_account_sid="ACtest",
        twilio_auth_token=SecretStr("token"),
        twilio_from_number="+15555550100",
        media_stream_token=SecretStr("stream-secret"),
        validate_twilio_signatures=False,
    )


def test_healthcheck() -> None:
    assert TestClient(app).get("/healthz").json() == {"status": "ok"}


def test_cli_requires_live_and_has_no_destination_option() -> None:
    result = CliRunner().invoke(cli_app, ["call"])
    assert result.exit_code == 2
    output = strip_ansi(result.output)
    assert "Real calls require" in output
    assert "--live" in output
    help_result = CliRunner().invoke(cli_app, ["call", "--help"])
    assert "--to" not in help_result.output


@pytest.mark.asyncio
async def test_gateway_uses_only_authorized_destination() -> None:
    calls = Mock()
    calls.create.return_value = SimpleNamespace(sid="CA123", status="queued")
    created = await TwilioGateway(live_settings(), calls).create_authorized_call()
    assert created.sid == "CA123"
    assert calls.create.call_args.kwargs["to"] == AUTHORIZED_DESTINATION
    assert calls.create.call_args.kwargs["record"] is True
    assert calls.create.call_args.kwargs["recording_channels"] == "dual"
    assert calls.create.call_args.kwargs["recording_status_callback"].endswith("/twilio/recording")


def test_voice_webhook_connects_bidirectional_stream() -> None:
    app.dependency_overrides[get_settings] = live_settings
    try:
        response = TestClient(app).post("/twilio/voice")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert (
        '<Connect><Stream url="wss://voice.example/twilio/media">'
        '<Parameter name="scenario" value="appointment-scheduling" />'
        '<Parameter name="token" value="stream-secret" />' in response.text
    )


def test_unsigned_twilio_webhook_is_rejected() -> None:
    def validating_settings() -> Settings:
        return live_settings().model_copy(update={"validate_twilio_signatures": True})

    app.dependency_overrides[get_settings] = validating_settings
    try:
        response = TestClient(app).post("/twilio/voice")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 403


def test_valid_twilio_signature_is_accepted() -> None:
    parameters = {"CallSid": "CA123", "CallStatus": "completed"}
    signature = RequestValidator("token").compute_signature(
        "https://voice.example/twilio/status", parameters
    )

    def validating_settings() -> Settings:
        return live_settings().model_copy(update={"validate_twilio_signatures": True})

    app.dependency_overrides[get_settings] = validating_settings
    try:
        response = TestClient(app).post(
            "/twilio/status",
            data=parameters,
            headers={"X-Twilio-Signature": signature},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200


def test_failed_recording_callback_persists_diagnostic(tmp_path: Path) -> None:
    def settings() -> Settings:
        return live_settings().model_copy(update={"calls_directory": tmp_path / "calls"})

    app.dependency_overrides[get_settings] = settings
    try:
        response = TestClient(app).post(
            "/twilio/recording",
            data={"CallSid": "CA123", "RecordingSid": "RE123", "RecordingStatus": "failed"},
        )
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    artifacts = ArtifactManager(tmp_path / "calls").find("CA123")
    assert artifacts is not None
    metadata = ArtifactManager.read_metadata(artifacts)
    assert metadata.recording_status == "failed"
    assert metadata.recording_sid == "RE123"
    assert "terminal status failed" in metadata.errors[0]
