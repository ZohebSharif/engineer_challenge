from dataclasses import dataclass


@dataclass(slots=True)
class TurnManager:
    """Tracks whether generated audio may still be queued at Twilio."""

    response_active: bool = False

    def output_started(self) -> None:
        self.response_active = True

    def output_finished(self) -> None:
        self.response_active = False

    def should_interrupt(self) -> bool:
        return self.response_active
