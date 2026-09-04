from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr
from typer.testing import CliRunner

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
    )


def test_healthcheck() -> None:
    assert TestClient(app).get("/healthz").json() == {"status": "ok"}


def test_cli_requires_live_and_has_no_destination_option() -> None:
    result = CliRunner().invoke(cli_app, [])
    assert result.exit_code == 2
    assert "explicit --live flag" in result.output
    help_result = CliRunner().invoke(cli_app, ["--help"])
    assert "--to" not in help_result.output


@pytest.mark.asyncio
async def test_gateway_uses_only_authorized_destination() -> None:
    calls = Mock()
    calls.create.return_value = SimpleNamespace(sid="CA123", status="queued")
    created = await TwilioGateway(live_settings(), calls).create_authorized_call()
    assert created.sid == "CA123"
    assert calls.create.call_args.kwargs["to"] == AUTHORIZED_DESTINATION


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
