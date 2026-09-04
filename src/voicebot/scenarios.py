from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class Scenario(BaseModel):
    """Validated controls for one simulated patient conversation."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(pattern=r"^[a-z0-9][a-z0-9-]*$")
    title: str
    language: str = "English"
    persona: str
    facts: list[str] = Field(min_length=1)
    speaking_style: list[str] = Field(min_length=1)
    objective: str
    fallbacks: list[str] = Field(min_length=1)
    behavioral_constraints: list[str] = Field(min_length=1)
    stop_conditions: list[str] = Field(min_length=1)
    evaluation_checks: list[str] = Field(default_factory=list)


class ScenarioRepository:
    def __init__(self, root: Path | None = None) -> None:
        self._root = root or Path(__file__).parent / "scenario_data"

    def load(self, scenario_id: str) -> Scenario:
        if not scenario_id or any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in scenario_id
        ):
            raise ValueError(f"Invalid scenario id: {scenario_id!r}")
        path = self._root / f"{scenario_id}.yaml"
        if not path.is_file():
            raise ValueError(f"Unknown scenario: {scenario_id}")
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        return Scenario.model_validate(raw)

    def list(self) -> list[Scenario]:
        return [
            Scenario.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
            for path in sorted(self._root.glob("*.yaml"))
        ]
