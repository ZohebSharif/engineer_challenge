import asyncio
from pathlib import Path
from typing import Annotated

import typer

from voicebot.artifacts import ArtifactManager
from voicebot.config import AUTHORIZED_DESTINATION, Settings, get_settings
from voicebot.logging import configure_logging
from voicebot.reporting import generate_report
from voicebot.scenarios import ScenarioRepository
from voicebot.services import build_analysis_pipeline
from voicebot.telephony import CreatedCall, TwilioGateway

app = typer.Typer(no_args_is_help=True, help="Run and evaluate safety-bounded patient calls.")


def _settings() -> Settings:
    settings = get_settings()
    configure_logging(settings.log_level)
    return settings


def _require_live(settings: Settings, live: bool) -> None:
    if not live:
        raise typer.BadParameter("Real calls require the explicit --live flag", param_hint="--live")
    try:
        settings.require_live_twilio()
        settings.require_realtime()
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc


async def _place_call(settings: Settings, scenario_id: str) -> CreatedCall:
    gateway = TwilioGateway(settings)
    created = await gateway.create_authorized_call(scenario_id)
    await ArtifactManager(settings.calls_directory).ensure(created.sid, scenario_id)
    return created


@app.command()
def call(
    scenario: Annotated[
        str,
        typer.Option("--scenario", help="Validated scenario id from the bundled suite."),
    ] = "appointment-scheduling",
    live: Annotated[
        bool,
        typer.Option("--live", help="Acknowledge one real, billable authorized call."),
    ] = False,
) -> None:
    """Place one call to the hard-coded authorized destination."""
    settings = _settings()
    _require_live(settings, live)
    try:
        ScenarioRepository().load(scenario)
        created = asyncio.run(_place_call(settings, scenario))
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="--scenario") from exc
    typer.echo(f"Started {created.sid} to {AUTHORIZED_DESTINATION} ({created.status})")


@app.command()
def suite(
    live: Annotated[
        bool,
        typer.Option("--live", help="Acknowledge 12 sequential real, billable calls."),
    ] = False,
) -> None:
    """Run every bundled scenario sequentially; calls never overlap."""
    settings = _settings()
    _require_live(settings, live)
    scenarios = ScenarioRepository().list()

    async def run_all() -> None:
        gateway = TwilioGateway(settings)
        artifacts = ArtifactManager(settings.calls_directory)
        for index, scenario in enumerate(scenarios, 1):
            typer.echo(f"[{index}/{len(scenarios)}] Calling {scenario.id}")
            created = await gateway.create_authorized_call(scenario.id)
            await artifacts.ensure(created.sid, scenario.id)
            terminal_status = await gateway.wait_until_complete(created.sid)
            typer.echo(f"[{index}/{len(scenarios)}] {created.sid}: {terminal_status}")

    asyncio.run(run_all())


@app.command()
def evaluate(
    call_id: Annotated[str, typer.Argument(help="Artifact id such as call-001.")],
) -> None:
    """Re-transcribe and evaluate an existing saved recording."""
    settings = _settings()
    try:
        asyncio.run(build_analysis_pipeline(settings).reanalyze(call_id))
    except ValueError as exc:
        raise typer.BadParameter(str(exc), param_hint="call_id") from exc
    typer.echo(f"Updated transcript and evaluation for {call_id}")


@app.command()
def report(
    output: Annotated[
        Path,
        typer.Option("--output", help="Markdown report destination."),
    ] = Path("reports/BUGS.md"),
) -> None:
    """Regenerate the high-confidence aggregate bug report."""
    settings = _settings()
    count = generate_report(settings.calls_directory, output, settings.report_confidence_threshold)
    typer.echo(f"Wrote {count} high-confidence issues to {output}")


if __name__ == "__main__":
    app()
