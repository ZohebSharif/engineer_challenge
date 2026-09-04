# Engineer Challenge

A safety-bounded FastAPI service that places a call only to the authorized test destination and accepts Twilio bidirectional Media Streams.

## Foundation development

```bash
cp .env.example .env
uv sync
uv run uvicorn voicebot.main:app --reload
uv run voicebot call --live
```

`voicebot call` has no destination option. Without `--live` it exits before constructing a Twilio client. Tests and CI contain no live-call path.
