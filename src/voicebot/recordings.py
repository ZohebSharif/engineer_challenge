import asyncio
import contextlib
from pathlib import Path

import httpx

from voicebot.config import Settings


class RecordingDownloader:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client

    async def download(self, recording_sid: str, destination: Path) -> str:
        self._settings.require_live_twilio()
        assert self._settings.twilio_account_sid is not None
        assert self._settings.twilio_auth_token is not None
        url = (
            "https://api.twilio.com/2010-04-01/Accounts/"
            f"{self._settings.twilio_account_sid}/Recordings/{recording_sid}.mp3"
        )
        owned = self._client is None
        client = self._client or httpx.AsyncClient(timeout=60)
        try:
            for attempt in range(self._settings.recording_download_attempts):
                async with client.stream(
                    "GET",
                    url,
                    auth=(
                        self._settings.twilio_account_sid,
                        self._settings.twilio_auth_token.get_secret_value(),
                    ),
                ) as response:
                    if response.status_code == 200:
                        await _save_response(response, destination)
                        return url
                    if response.status_code not in {404, 409}:
                        response.raise_for_status()
                if attempt + 1 < self._settings.recording_download_attempts:
                    await asyncio.sleep(self._settings.recording_retry_seconds * 2**attempt)
            raise RuntimeError(f"Recording {recording_sid} was not ready after bounded retries")
        finally:
            if owned:
                await client.aclose()


async def _save_response(response: httpx.Response, destination: Path) -> None:
    temporary = destination.with_suffix(".mp3.tmp")
    file = await asyncio.to_thread(temporary.open, "wb")
    try:
        async for chunk in response.aiter_bytes(64 * 1024):
            await asyncio.to_thread(file.write, chunk)
        await asyncio.to_thread(file.close)
        await asyncio.to_thread(temporary.replace, destination)
    except BaseException:
        with contextlib.suppress(OSError):
            await asyncio.to_thread(file.close)
            await asyncio.to_thread(temporary.unlink)
        raise
