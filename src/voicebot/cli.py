import asyncio
from typing import Annotated

import typer

from voicebot.config import AUTHORIZED_DESTINATION, get_settings
from voicebot.logging import configure_logging
from voicebot.telephony import TwilioGateway

app = typer.Typer(no_args_is_help=True, help="Run safety-bounded patient voice calls.")


@app.command()
def call(
    live: Annotated[
        bool,
        typer.Option("--live", help="Acknowledge that this makes a real, billable call."),
    ] = False,
) -> None:
    """Call the single authorized destination."""
    if not live:
        raise typer.BadParameter("Real calls require the explicit --live flag", param_hint="--live")
    settings = get_settings()
    configure_logging(settings.log_level)
    try:
        created = asyncio.run(TwilioGateway(settings).create_authorized_call())
    except ValueError as exc:
        raise typer.BadParameter(str(exc)) from exc
    typer.echo(f"Started {created.sid} to {AUTHORIZED_DESTINATION} ({created.status})")


if __name__ == "__main__":
    app()
