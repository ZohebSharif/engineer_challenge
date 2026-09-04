from datetime import UTC, datetime
from pathlib import Path

import structlog

from voicebot.artifacts import ArtifactManager, CallMetadata
from voicebot.evaluation import ConversationEvaluator
from voicebot.recordings import RecordingDownloader
from voicebot.scenarios import ScenarioRepository
from voicebot.transcription import RecordingTranscriber, Transcript

logger = structlog.get_logger()


class AnalysisPipeline:
    """Persist-first recording pipeline; downstream failures never remove prior artifacts."""

    def __init__(
        self,
        artifacts: ArtifactManager,
        downloader: RecordingDownloader,
        transcriber: RecordingTranscriber,
        evaluator: ConversationEvaluator,
        scenarios: ScenarioRepository | None = None,
    ) -> None:
        self._artifacts = artifacts
        self._downloader = downloader
        self._transcriber = transcriber
        self._evaluator = evaluator
        self._scenarios = scenarios or ScenarioRepository()

    async def process(self, call_sid: str, recording_sid: str) -> None:
        files, metadata = await self._artifacts.ensure(call_sid)
        metadata.recording_sid = recording_sid
        metadata.recording_status = "downloading"
        self._save_metadata(files.metadata, metadata)
        try:
            await self._downloader.download(recording_sid, files.recording)
            metadata.recording_status = "saved"
            self._save_metadata(files.metadata, metadata)
        except Exception as exc:
            await self._fail(files.metadata, metadata, "recording", exc)
            return

        transcript: Transcript
        try:
            transcript = await self._transcriber.transcribe(files.recording)
            self._artifacts.write_text(files.transcript_text, transcript.as_text())
            self._artifacts.write_json(files.transcript_json, transcript.model_dump(mode="json"))
            metadata.transcription_status = "complete"
            self._save_metadata(files.metadata, metadata)
        except Exception as exc:
            await self._fail(files.metadata, metadata, "transcription", exc)
            return

        try:
            scenario = self._scenarios.load(metadata.scenario_id)
            evaluation = await self._evaluator.evaluate(transcript, scenario)
            self._artifacts.write_json(files.evaluation, evaluation.model_dump(mode="json"))
            metadata.evaluation_status = "complete"
            self._save_metadata(files.metadata, metadata)
        except Exception as exc:
            await self._fail(files.metadata, metadata, "evaluation", exc)

    async def _fail(
        self, metadata_path: Path, metadata: CallMetadata, stage: str, exc: Exception
    ) -> None:
        setattr(metadata, f"{stage}_status", "failed")
        metadata.errors.append(f"{stage}: {type(exc).__name__}: {exc}")
        self._save_metadata(metadata_path, metadata)
        await logger.aexception("call_analysis_failed", stage=stage, call_sid=metadata.call_sid)

    def _save_metadata(self, path: Path, metadata: CallMetadata) -> None:
        metadata.updated_at = datetime.now(UTC)
        self._artifacts.write_json(path, metadata.model_dump(mode="json"))
