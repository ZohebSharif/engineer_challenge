import asyncio
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CallMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")

    call_id: str
    call_sid: str
    scenario_id: str
    started_at: datetime
    updated_at: datetime
    recording_sid: str | None = None
    recording_status: str | None = None
    transcription_status: str | None = None
    evaluation_status: str | None = None
    errors: list[str] = Field(default_factory=list)


@dataclass(frozen=True, slots=True)
class CallArtifacts:
    root: Path

    @property
    def recording(self) -> Path:
        return self.root / "recording.mp3"

    @property
    def transcript_text(self) -> Path:
        return self.root / "transcript.txt"

    @property
    def transcript_json(self) -> Path:
        return self.root / "transcript.json"

    @property
    def metadata(self) -> Path:
        return self.root / "metadata.json"

    @property
    def evaluation(self) -> Path:
        return self.root / "evaluation.json"


class ArtifactManager:
    """Creates stable call-NNN directories and writes artifacts atomically."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._lock = asyncio.Lock()

    async def ensure(
        self, call_sid: str, scenario_id: str = "appointment-scheduling"
    ) -> tuple[CallArtifacts, CallMetadata]:
        async with self._lock:
            existing = self._find_unlocked(call_sid)
            if existing:
                return existing, self.read_metadata(existing)
            self.root.mkdir(parents=True, exist_ok=True)
            indexes = [
                int(path.name.removeprefix("call-"))
                for path in self.root.glob("call-[0-9][0-9][0-9]")
                if path.name.removeprefix("call-").isdigit()
            ]
            call_id = f"call-{max(indexes, default=0) + 1:03d}"
            artifacts = CallArtifacts(self.root / call_id)
            artifacts.root.mkdir(parents=False, exist_ok=False)
            now = datetime.now(UTC)
            metadata = CallMetadata(
                call_id=call_id,
                call_sid=call_sid,
                scenario_id=scenario_id,
                started_at=now,
                updated_at=now,
            )
            self.write_json(artifacts.metadata, metadata.model_dump(mode="json"))
            return artifacts, metadata

    def find(self, call_sid: str) -> CallArtifacts | None:
        return self._find_unlocked(call_sid)

    def _find_unlocked(self, call_sid: str) -> CallArtifacts | None:
        if not self.root.exists():
            return None
        for metadata_path in self.root.glob("call-*/metadata.json"):
            try:
                raw = json.loads(metadata_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if raw.get("call_sid") == call_sid:
                return CallArtifacts(metadata_path.parent)
        return None

    @staticmethod
    def read_metadata(artifacts: CallArtifacts) -> CallMetadata:
        return CallMetadata.model_validate_json(artifacts.metadata.read_text(encoding="utf-8"))

    @staticmethod
    def write_json(path: Path, value: Any) -> None:
        ArtifactManager._atomic_write(path, json.dumps(value, indent=2, sort_keys=True) + "\n")

    @staticmethod
    def write_text(path: Path, value: str) -> None:
        ArtifactManager._atomic_write(path, value.rstrip() + "\n")

    @staticmethod
    def _atomic_write(path: Path, value: str) -> None:
        temporary = path.with_suffix(f"{path.suffix}.tmp")
        temporary.write_text(value, encoding="utf-8")
        temporary.replace(path)
