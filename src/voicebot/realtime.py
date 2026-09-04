import json
from collections.abc import Mapping
from typing import Any, Protocol, cast

from websockets.asyncio.client import connect

from voicebot.config import Settings
from voicebot.prompts import build_patient_prompt
from voicebot.scenarios import Scenario


class RealtimeSocket(Protocol):
    async def send(self, message: str) -> None: ...
    async def recv(self) -> str | bytes: ...
    async def close(self) -> None: ...


def _turn_detection(*, create_response: bool) -> dict[str, Any]:
    return {
        "type": "server_vad",
        "threshold": 0.55,
        "prefix_padding_ms": 300,
        "silence_duration_ms": 1200,
        "create_response": create_response,
        "interrupt_response": False,
    }


class RealtimeSession:
    def __init__(self, socket: RealtimeSocket) -> None:
        self._socket = socket

    async def configure(self, scenario: Scenario, voice: str) -> None:
        """Open with automatic responses OFF so the remote side owns the first turn."""
        await self._send(
            {
                "type": "session.update",
                "session": {
                    "type": "realtime",
                    "instructions": build_patient_prompt(scenario),
                    "output_modalities": ["audio"],
                    "audio": {
                        "input": {
                            "format": {"type": "audio/pcmu"},
                            "turn_detection": _turn_detection(create_response=False),
                        },
                        "output": {
                            "format": {"type": "audio/pcmu"},
                            "voice": voice,
                        },
                    },
                    "max_output_tokens": 180,
                },
            }
        )

    async def enable_automatic_responses(self) -> None:
        """Hand turn-taking back to unchanged server VAD once the remote side has spoken."""
        await self._send(
            {
                "type": "session.update",
                "session": {
                    "type": "realtime",
                    "audio": {"input": {"turn_detection": _turn_detection(create_response=True)}},
                },
            }
        )

    async def create_response(self) -> None:
        await self._send({"type": "response.create"})

    async def send_audio(self, base64_pcmu: str) -> None:
        await self._send({"type": "input_audio_buffer.append", "audio": base64_pcmu})

    async def receive(self) -> dict[str, Any]:
        raw = await self._socket.recv()
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        parsed: object = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Realtime event must be a JSON object")
        return cast(dict[str, Any], parsed)

    async def cancel_response(self) -> None:
        await self._send({"type": "response.cancel"})

    async def close(self) -> None:
        await self._socket.close()

    async def _send(self, event: Mapping[str, object]) -> None:
        await self._socket.send(json.dumps(event, separators=(",", ":")))


class OpenAIRealtimeClient:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def open(self, scenario: Scenario) -> RealtimeSession:
        self._settings.require_realtime()
        assert self._settings.openai_api_key is not None
        uri = f"wss://api.openai.com/v1/realtime?model={self._settings.openai_realtime_model}"
        socket = await connect(
            uri,
            additional_headers={
                "Authorization": f"Bearer {self._settings.openai_api_key.get_secret_value()}"
            },
            open_timeout=10,
            close_timeout=5,
            max_size=2**20,
        )
        session = RealtimeSession(cast(RealtimeSocket, socket))
        try:
            await session.configure(scenario, self._settings.openai_voice)
        except BaseException:
            await session.close()
            raise
        return session
