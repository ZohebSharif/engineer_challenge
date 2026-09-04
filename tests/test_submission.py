from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from click.utils import strip_ansi
from pydantic import SecretStr
from typer.testing import CliRunner

from voicebot.artifacts import CallMetadata
from voicebot.cli import app
from voicebot.config import Settings
from voicebot.evaluation import Evaluation, EvaluationIssue, IssueCategory
from voicebot.reporting import generate_report
from voicebot.scenarios import ScenarioRepository
from voicebot.telephony import TwilioGateway

EXPECTED_SCENARIOS = {
    "appointment-scheduling",
    "rescheduling",
    "cancellation",
    "medication-refill",
    "office-hours",
    "insurance",
    "weekend-scheduling",
    "ambiguous-date",
    "context-correction",
    "multi-intent",
    "interruption",
    "unusual-edge",
}


def test_complete_scenario_suite_is_valid() -> None:
    scenarios = ScenarioRepository().list()
    assert {scenario.id for scenario in scenarios} == EXPECTED_SCENARIOS
    assert len(scenarios) == 12
    assert all(scenario.evaluation_checks for scenario in scenarios)


def test_cli_help_exposes_clear_workflows_and_no_destination() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("call", "suite", "evaluate", "report"):
        assert command in result.output
    assert "--to" not in result.output


def test_suite_refuses_to_run_without_live_flag() -> None:
    result = CliRunner().invoke(app, ["suite"])
    assert result.exit_code == 2
    output = strip_ansi(result.output)
    assert "Real calls require" in output
    assert "--live" in output


def test_report_includes_only_high_confidence_issues(tmp_path: Path) -> None:
    calls = tmp_path / "calls"
    call = calls / "call-001"
    call.mkdir(parents=True)
    now = datetime.now(UTC)
    metadata = CallMetadata(
        call_id="call-001",
        call_sid="CA123",
        scenario_id="ambiguous-date",
        started_at=now,
        updated_at=now,
    )
    (call / "metadata.json").write_text(metadata.model_dump_json(), encoding="utf-8")
    evaluation = Evaluation(
        summary="Two findings",
        scenario_checks=[],
        issues=[
            EvaluationIssue(
                category=IssueCategory.FALSE_CONFIRMATION,
                confidence=0.91,
                description="Booked an ambiguous date.",
                evidence="Next Friday is confirmed.",
                recommendation="State and confirm the calendar date.",
            ),
            EvaluationIssue(
                category=IssueCategory.CONVERSATION_QUALITY,
                confidence=0.6,
                description="Minor pacing concern.",
                evidence="A short pause.",
                recommendation="Pause less.",
            ),
        ],
    )
    (call / "evaluation.json").write_text(evaluation.model_dump_json(), encoding="utf-8")
    output = tmp_path / "reports/BUGS.md"
    count = generate_report(calls, output, minimum_confidence=0.8)
    report = output.read_text(encoding="utf-8")
    assert count == 1
    assert "Booked an ambiguous date" in report
    assert "Minor pacing concern" not in report
    assert "ambiguous-date" in report


def test_report_skips_malformed_metadata(tmp_path: Path) -> None:
    call = tmp_path / "calls/call-001"
    call.mkdir(parents=True)
    (call / "metadata.json").write_text('{"scenario_id": 42}', encoding="utf-8")
    (call / "evaluation.json").write_text(
        Evaluation(summary="ignored", scenario_checks=[], issues=[]).model_dump_json(),
        encoding="utf-8",
    )
    output = tmp_path / "BUGS.md"
    assert generate_report(tmp_path / "calls", output) == 0
    assert "No issues met" in output.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_call_completion_poll_reaches_terminal_state() -> None:
    calls = Mock()
    context = calls.return_value
    context.fetch.side_effect = [
        SimpleNamespace(sid="CA123", status="in-progress"),
        SimpleNamespace(sid="CA123", status="completed"),
    ]
    settings = Settings(
        public_base_url="https://voice.example",
        twilio_account_sid="ACtest",
        twilio_auth_token=SecretStr("token"),
        twilio_from_number="+15555550100",
        media_stream_token=SecretStr("stream"),
        call_timeout_seconds=30,
        suite_poll_seconds=0.1,
    )
    status = await TwilioGateway(settings, calls).wait_until_complete("CA123")
    assert status == "completed"
    assert context.fetch.call_count == 2
