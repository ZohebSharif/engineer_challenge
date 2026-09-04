# Engineer Challenge

A safety-bounded FastAPI service that calls one authorized destination and bridges Twilio
bidirectional Media Streams to the OpenAI Realtime API.

## Realtime development

```bash
cp .env.example .env
uv sync
uv run uvicorn voicebot.main:app --reload
uv run voicebot --scenario appointment-scheduling --live
```

`voicebot` has no destination option. Without `--live` it exits before constructing a Twilio client. Tests and CI contain no live-call path.

Bundled scenarios are validated from `src/voicebot/scenario_data`. Twilio and OpenAI both use
PCMU, so base64 audio payloads cross the bridge without lossy transcoding. Server VAD drives turns;
new caller speech cancels the current model response and clears Twilio's buffered patient audio.
