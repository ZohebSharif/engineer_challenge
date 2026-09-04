from dataclasses import dataclass
from pathlib import Path

import structlog

from voicebot.artifacts import CallMetadata
from voicebot.evaluation import Evaluation, EvaluationIssue

logger = structlog.get_logger()


@dataclass(frozen=True, slots=True)
class ReportedIssue:
    call_id: str
    scenario_id: str
    issue: EvaluationIssue


def collect_issues(calls_directory: Path, minimum_confidence: float) -> list[ReportedIssue]:
    issues: list[ReportedIssue] = []
    for evaluation_path in sorted(calls_directory.glob("call-*/evaluation.json")):
        try:
            evaluation = Evaluation.model_validate_json(evaluation_path.read_text(encoding="utf-8"))
            metadata = CallMetadata.model_validate_json(
                evaluation_path.with_name("metadata.json").read_text(encoding="utf-8")
            )
            scenario_id = metadata.scenario_id
        except (OSError, ValueError) as exc:
            logger.warning(
                "evaluation_artifact_unreadable",
                path=str(evaluation_path),
                error=str(exc),
            )
            continue
        issues.extend(
            ReportedIssue(evaluation_path.parent.name, scenario_id, issue)
            for issue in evaluation.issues
            if issue.confidence >= minimum_confidence
        )
    return sorted(
        issues,
        key=lambda item: (-item.issue.confidence, item.call_id, item.issue.category.value),
    )


def render_bug_report(issues: list[ReportedIssue], minimum_confidence: float) -> str:
    lines = [
        "# High-confidence Voice Agent Issues",
        "",
        f"Generated from validated evaluations. Confidence threshold: {minimum_confidence:.2f}.",
        "",
    ]
    if not issues:
        lines.append("No issues met the confidence threshold.")
        return "\n".join(lines) + "\n"
    for index, reported in enumerate(issues, 1):
        issue = reported.issue
        lines.extend(
            [
                f"## {index}. {issue.description}",
                "",
                f"- Call: `{reported.call_id}`",
                f"- Scenario: `{reported.scenario_id}`",
                f"- Category: `{issue.category.value}`",
                f"- Confidence: `{issue.confidence:.2f}`",
                f"- Evidence: {issue.evidence}",
                f"- Recommendation: {issue.recommendation}",
                "",
            ]
        )
    return "\n".join(lines)


def generate_report(calls_directory: Path, output: Path, minimum_confidence: float = 0.8) -> int:
    issues = collect_issues(calls_directory, minimum_confidence)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".md.tmp")
    temporary.write_text(render_bug_report(issues, minimum_confidence), encoding="utf-8")
    temporary.replace(output)
    return len(issues)
