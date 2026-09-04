import asyncio
import json
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr

from voicebot.analysis import AnalysisPipeline
from voicebot.artifacts import ArtifactManager
from voicebot.config import Settings
from voicebot.evaluation import Evaluation, EvaluationIssue, IssueCategory, ScenarioCheck
from voicebot.recordings import RecordingDownloader
from voicebot.scenarios import ScenarioRepository
from voicebot.transcription import Transcript, TranscriptSegment


class FakeDownloader:
    async def download(self, recording_sid: str, destination: Path) -> str:
        assert recording_sid == "RE123"
        await asyncio.to_thread(destination.write_bytes, b"ID3 phone recording")
        return "https://api.twilio.test/RE123.mp3"


class FakeTranscriber:
    async def transcribe(self, recording: Path) -> Transcript:
        content = await asyncio.to_thread(recording.read_bytes)
        assert content.startswith(b"ID3")
        return Transcript(
            text="Patient asks for an appointment. Agent confirms.",
            segments=[
                TranscriptSegment(speaker="speaker_0", text="I need an appointment.", start=0),
                TranscriptSegment(speaker="speaker_1", text="Tuesday at nine.", start=1.2),
            ],
        )


class FakeEvaluator:
    async def evaluate(self, transcript: Transcript, scenario: object) -> Evaluation:
        assert "appointment" in transcript.text.lower()
        return Evaluation(
            summary="A confirmation was incomplete.",
            scenario_checks=[
                ScenarioCheck(check="Confirm exact date and time", passed=False, evidence="Tuesday")
            ],
            issues=[
                EvaluationIssue(
                    category=IssueCategory.CLARIFICATION_FAILURE,
                    confidence=0.93,
                    description="Date lacks a calendar date.",
                    evidence="Tuesday at nine.",
                    recommendation="Confirm the full date and time.",
                )
            ],
        )


class FailingEvaluator:
    async def evaluate(self, transcript: Transcript, scenario: object) -> Evaluation:
        raise RuntimeError("evaluation unavailable")


@pytest.mark.asyncio
async def test_pipeline_creates_complete_durable_artifact_set(tmp_path: Path) -> None:
    manager = ArtifactManager(tmp_path / "calls")
    await manager.ensure("CA123", "appointment-scheduling")
    pipeline = AnalysisPipeline(
        manager,
        FakeDownloader(),  # type: ignore[arg-type]
        FakeTranscriber(),  # type: ignore[arg-type]
        FakeEvaluator(),  # type: ignore[arg-type]
        ScenarioRepository(),
    )
    await pipeline.process("CA123", "RE123")
    files = manager.find("CA123")
    assert files is not None
    assert {path.name for path in files.root.iterdir()} == {
        "recording.mp3",
        "transcript.txt",
        "transcript.json",
        "metadata.json",
        "evaluation.json",
    }
    transcript = json.loads(files.transcript_json.read_text())
    assert transcript["segments"][0]["speaker"] == "speaker_0"
    assert transcript["segments"][1]["start"] == 1.2
    evaluation = Evaluation.model_validate_json(files.evaluation.read_text())
    assert evaluation.issues[0].confidence == 0.93


@pytest.mark.asyncio
async def test_evaluation_failure_preserves_recording_and_transcript(tmp_path: Path) -> None:
    manager = ArtifactManager(tmp_path / "calls")
    await manager.ensure("CA456", "appointment-scheduling")
    pipeline = AnalysisPipeline(
        manager,
        FakeDownloader(),  # type: ignore[arg-type]
        FakeTranscriber(),  # type: ignore[arg-type]
        FailingEvaluator(),  # type: ignore[arg-type]
    )
    await pipeline.process("CA456", "RE123")
    files = manager.find("CA456")
    assert files is not None
    assert files.recording.exists()
    assert files.transcript_json.exists()
    assert not files.evaluation.exists()
    metadata = manager.read_metadata(files)
    assert metadata.recording_status == "saved"
    assert metadata.transcription_status == "complete"
    assert metadata.evaluation_status == "failed"
    assert "evaluation unavailable" in metadata.errors[0]


@pytest.mark.asyncio
async def test_artifact_ids_are_stable_and_sequential(tmp_path: Path) -> None:
    manager = ArtifactManager(tmp_path / "calls")
    first, _ = await manager.ensure("CA1")
    same, _ = await manager.ensure("CA1")
    second, _ = await manager.ensure("CA2")
    assert first.root.name == "call-001"
    assert same.root == first.root
    assert second.root.name == "call-002"


@pytest.mark.asyncio
async def test_recording_download_uses_canonical_url_and_bounded_retry(
    tmp_path: Path,
) -> None:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(404)
        return httpx.Response(200, content=b"ID3 canonical recording")

    settings = Settings(
        public_base_url="https://voice.example",
        twilio_account_sid="ACtest",
        twilio_auth_token=SecretStr("token"),
        twilio_from_number="+15555550100",
        media_stream_token=SecretStr("stream"),
        recording_download_attempts=2,
        recording_retry_seconds=0.1,
    )
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        destination = tmp_path / "recording.mp3"
        url = await RecordingDownloader(settings, client).download("RE123", destination)
    assert len(requests) == 2
    assert url.endswith("/Accounts/ACtest/Recordings/RE123.mp3")
    assert destination.read_bytes() == b"ID3 canonical recording"
