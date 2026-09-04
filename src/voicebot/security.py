from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from twilio.request_validator import RequestValidator

from voicebot.config import Settings, get_settings


async def verified_twilio_settings(
    request: Request, settings: Annotated[Settings, Depends(get_settings)]
) -> Settings:
    """Validate Twilio HTTP callback signatures unless tests explicitly disable it."""
    if not settings.validate_twilio_signatures:
        return settings
    if settings.twilio_auth_token is None or settings.public_base_url is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    signature = request.headers.get("X-Twilio-Signature", "")
    form = await request.form()
    parameters = {key: value for key, value in form.items() if isinstance(value, str)}
    public_url = f"{str(settings.public_base_url).rstrip('/')}{request.url.path}"
    if request.url.query:
        public_url = f"{public_url}?{request.url.query}"
    validator = RequestValidator(settings.twilio_auth_token.get_secret_value())
    if not validator.validate(public_url, parameters, signature):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Twilio signature"
        )
    return settings
