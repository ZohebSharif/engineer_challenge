from functools import lru_cache
from pathlib import Path

from pydantic import Field, HttpUrl, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

AUTHORIZED_DESTINATION = "+18054398008"


class Settings(BaseSettings):
    """Runtime configuration loaded from VOICEBOT_* variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_prefix="VOICEBOT_", extra="ignore", case_sensitive=False
    )

    public_base_url: HttpUrl | None = None
    twilio_account_sid: str | None = None
    twilio_auth_token: SecretStr | None = None
    twilio_from_number: str | None = None
    validate_twilio_signatures: bool = True
    media_stream_token: SecretStr | None = None
    openai_api_key: SecretStr | None = None
    openai_realtime_model: str = "gpt-realtime"
    openai_voice: str = "marin"
    default_scenario: str = "appointment-scheduling"
    openai_transcription_model: str = "gpt-4o-transcribe-diarize"
    openai_evaluation_model: str = "gpt-5-mini"
    calls_directory: Path = Path("calls")
    recording_download_attempts: int = Field(default=4, ge=1, le=8)
    recording_retry_seconds: float = Field(default=2.0, ge=0.1, le=30)
    call_timeout_seconds: int = Field(default=300, ge=30, le=1800)
    suite_poll_seconds: float = Field(default=2.0, ge=0.1, le=30)
    report_confidence_threshold: float = Field(default=0.8, ge=0, le=1)
    log_level: str = "INFO"

    def require_live_twilio(self) -> None:
        missing = [
            name
            for name, value in (
                ("VOICEBOT_PUBLIC_BASE_URL", self.public_base_url),
                ("VOICEBOT_TWILIO_ACCOUNT_SID", self.twilio_account_sid),
                ("VOICEBOT_TWILIO_AUTH_TOKEN", self.twilio_auth_token),
                ("VOICEBOT_TWILIO_FROM_NUMBER", self.twilio_from_number),
                ("VOICEBOT_MEDIA_STREAM_TOKEN", self.media_stream_token),
            )
            if value is None
        ]
        if missing:
            raise ValueError(f"Live calling requires: {', '.join(missing)}")

    def require_realtime(self) -> None:
        if self.openai_api_key is None:
            raise ValueError("Realtime calling requires: VOICEBOT_OPENAI_API_KEY")


@lru_cache
def get_settings() -> Settings:
    return Settings()
