from pathlib import Path
from typing import Any, cast

import httpx
from pydantic import BaseModel, ConfigDict

from voicebot.config import Settings


class TranscriptSegment(BaseModel):
    model_config = ConfigDict(extra="ignore")

    speaker: str = "unknown"
    text: str
    start: float | None = None
    end: float | None = None


class Transcript(BaseModel):
    model_config = ConfigDict(extra="ignore")

    text: str
    segments: list[TranscriptSegment] = []

    def as_text(self) -> str:
        if not self.segments:
            return self.text
        lines: list[str] = []
        for segment in self.segments:
            timestamp = f"[{segment.start:0.1f}s] " if segment.start is not None else ""
            lines.append(f"{timestamp}{segment.speaker}: {segment.text.strip()}")
        return "\n".join(lines)


class RecordingTranscriber:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client

    async def transcribe(self, recording: Path) -> Transcript:
        self._settings.require_realtime()
        assert self._settings.openai_api_key is not None
        owned = self._client is None
        client = self._client or httpx.AsyncClient(timeout=180)
        authorization = f"Bearer {self._settings.openai_api_key.get_secret_value()}"
        try:
            with recording.open("rb") as audio:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": authorization},
                    data={
                        "model": self._settings.openai_transcription_model,
                        "response_format": "diarized_json",
                        "chunking_strategy": "auto",
                    },
                    files={"file": (recording.name, audio, "audio/mpeg")},
                )
            response.raise_for_status()
            payload = cast(dict[str, Any], response.json())
            return Transcript.model_validate(payload)
        finally:
            if owned:
                await client.aclose()
