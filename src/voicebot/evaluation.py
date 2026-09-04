import json
from enum import StrEnum
from typing import Any, cast

import httpx
from pydantic import BaseModel, ConfigDict, Field

from voicebot.config import Settings
from voicebot.scenarios import Scenario
from voicebot.transcription import Transcript


class IssueCategory(StrEnum):
    FACTUAL_ERROR = "factual_error"
    WORKFLOW_FAILURE = "workflow_failure"
    FALSE_CONFIRMATION = "false_confirmation"
    STATE_MANAGEMENT = "state_management_error"
    CLARIFICATION_FAILURE = "clarification_failure"
    CONVERSATION_QUALITY = "conversation_quality"
    SCOPE_POLICY = "scope_policy_problem"
    OTHER = "other_meaningful_issue"


class EvaluationIssue(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: IssueCategory
    confidence: float = Field(ge=0, le=1)
    description: str
    evidence: str
    recommendation: str


class ScenarioCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    check: str
    passed: bool
    evidence: str


class Evaluation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str
    scenario_checks: list[ScenarioCheck]
    issues: list[EvaluationIssue]


class ConversationEvaluator:
    def __init__(self, settings: Settings, client: httpx.AsyncClient | None = None) -> None:
        self._settings = settings
        self._client = client

    async def evaluate(self, transcript: Transcript, scenario: Scenario) -> Evaluation:
        self._settings.require_realtime()
        assert self._settings.openai_api_key is not None
        prompt = f"""Evaluate this phone-agent conversation against the scenario.

Scenario objective: {scenario.objective}
Known patient facts: {json.dumps(scenario.facts)}
Required checks: {json.dumps(scenario.evaluation_checks)}
Transcript:\n{transcript.as_text()}

Identify factual errors, workflow failures, false confirmations, state-management errors,
clarification failures, poor conversation behavior, scope/policy problems, and other meaningful
issues. Report only consequential defects supported by quoted evidence. Never report punctuation,
minor wording preferences, or trivial stylistic nitpicks. An empty issue list is valid.
"""
        schema = Evaluation.model_json_schema()
        owned = self._client is None
        client = self._client or httpx.AsyncClient(timeout=120)
        try:
            response = await client.post(
                "https://api.openai.com/v1/responses",
                headers={
                    "Authorization": f"Bearer {self._settings.openai_api_key.get_secret_value()}"
                },
                json={
                    "model": self._settings.openai_evaluation_model,
                    "input": prompt,
                    "text": {
                        "format": {
                            "type": "json_schema",
                            "name": "call_evaluation",
                            "strict": True,
                            "schema": schema,
                        }
                    },
                },
            )
            response.raise_for_status()
            payload = cast(dict[str, Any], response.json())
            text = _response_text(payload)
            return Evaluation.model_validate_json(text)
        finally:
            if owned:
                await client.aclose()


def _response_text(payload: dict[str, Any]) -> str:
    outputs = payload.get("output")
    if not isinstance(outputs, list):
        raise ValueError("OpenAI evaluation response contained no output")
    for output_value in cast(list[object], outputs):
        if not isinstance(output_value, dict):
            continue
        output = cast(dict[str, object], output_value)
        contents = output.get("content")
        if not isinstance(contents, list):
            continue
        for content_value in cast(list[object], contents):
            if not isinstance(content_value, dict):
                continue
            content = cast(dict[str, object], content_value)
            text = content.get("text")
            if content.get("type") == "output_text" and isinstance(text, str):
                return text
    raise ValueError("OpenAI evaluation response contained no output text")
