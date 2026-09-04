import asyncio
from dataclasses import dataclass
from typing import Protocol, cast
from urllib.parse import urlencode

from twilio.rest import Client

from voicebot.config import AUTHORIZED_DESTINATION, Settings


@dataclass(frozen=True, slots=True)
class CreatedCall:
    sid: str
    status: str


class CallResult(Protocol):
    sid: str
    status: str


class CallContext(Protocol):
    def fetch(self) -> CallResult: ...


class CallsResource(Protocol):
    def __call__(self, sid: str) -> CallContext: ...
    def create(
        self,
        *,
        to: str,
        from_: str,
        url: str,
        method: str,
        status_callback: str,
        status_callback_event: list[str],
        record: bool,
        recording_channels: str,
        recording_status_callback: str,
        recording_status_callback_method: str,
    ) -> CallResult: ...


class TwilioGateway:
    """The sole boundary allowed to create billable phone calls."""

    def __init__(self, settings: Settings, calls: CallsResource | None = None) -> None:
        self._settings = settings
        self._calls = calls

    def _calls_resource(self) -> CallsResource:
        if self._calls is not None:
            return self._calls
        self._settings.require_live_twilio()
        assert self._settings.twilio_account_sid is not None
        assert self._settings.twilio_auth_token is not None
        return cast(
            CallsResource,
            Client(
                self._settings.twilio_account_sid,
                self._settings.twilio_auth_token.get_secret_value(),
            ).calls,
        )

    async def create_authorized_call(
        self, scenario_id: str = "appointment-scheduling"
    ) -> CreatedCall:
        """Call only the compile-time authorized destination."""
        self._settings.require_live_twilio()
        assert self._settings.public_base_url is not None
        assert self._settings.twilio_from_number is not None
        base = str(self._settings.public_base_url).rstrip("/")
        call = await asyncio.to_thread(
            self._calls_resource().create,
            to=AUTHORIZED_DESTINATION,
            from_=self._settings.twilio_from_number,
            url=f"{base}/twilio/voice?{urlencode({'scenario': scenario_id})}",
            method="POST",
            status_callback=f"{base}/twilio/status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            record=True,
            recording_channels="dual",
            recording_status_callback=f"{base}/twilio/recording",
            recording_status_callback_method="POST",
        )
        return CreatedCall(sid=str(call.sid), status=str(call.status))

    async def wait_until_complete(self, call_sid: str) -> str:
        """Poll one call to a terminal state so suites never overlap calls."""
        terminal = {"completed", "busy", "failed", "no-answer", "canceled"}
        async with asyncio.timeout(self._settings.call_timeout_seconds):
            while True:
                call = await asyncio.to_thread(self._calls_resource()(call_sid).fetch)
                status = str(call.status)
                if status in terminal:
                    return status
                await asyncio.sleep(self._settings.suite_poll_seconds)
