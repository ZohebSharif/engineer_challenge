# Engineer Challenge

A safety-bounded AI patient caller for evaluating healthcare phone agents. FastAPI accepts Twilio
bidirectional Media Streams, forwards PCMU audio directly to OpenAI Realtime, records both call
channels, and turns completed calls into transcripts, structured evaluations, and an aggregate bug
report.

## Safety boundary

- The only destination is the source constant `+18054398008`.
- No CLI command accepts a destination number.
- `voicebot call` and `voicebot suite` refuse to dial without `--live`.
- Missing Twilio, OpenAI, tunnel, or stream-token settings fail before call creation.
- CI and tests inject fakes and never enter a live-call path.
- Twilio HTTP callbacks require a valid Twilio signature by default; the media WebSocket requires a
  secret token.
- There is no deployment or automatic calling workflow.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)
- A Twilio account and voice-capable Twilio number
- An OpenAI API key with Realtime, transcription, and Responses API access
- A public HTTPS tunnel for local live calls
- Docker is optional

## Setup

```bash
git clone https://github.com/ZohebSharif/engineer_challenge.git
cd engineer_challenge
cp .env.example .env
uv sync
```

Fill `.env`; never commit it. Generate `VOICEBOT_MEDIA_STREAM_TOKEN` as a long random secret.

### Twilio configuration

Set:

- `VOICEBOT_TWILIO_ACCOUNT_SID`
- `VOICEBOT_TWILIO_AUTH_TOKEN`
- `VOICEBOT_TWILIO_FROM_NUMBER` in E.164 format
- `VOICEBOT_PUBLIC_BASE_URL` to the public HTTPS origin, without a trailing slash

Each outbound call supplies its own TwiML URL, status callback, dual-channel recording settings,
and recording callback. No incoming-number webhook is required. Signature validation assumes the
public URL is the URL Twilio signs. Keep `VOICEBOT_VALIDATE_TWILIO_SIGNATURES=true` outside tests.

### OpenAI configuration

Set `VOICEBOT_OPENAI_API_KEY`. Defaults are:

```dotenv
VOICEBOT_OPENAI_REALTIME_MODEL=gpt-realtime
VOICEBOT_OPENAI_VOICE=marin
VOICEBOT_OPENAI_TRANSCRIPTION_MODEL=gpt-4o-transcribe-diarize
VOICEBOT_OPENAI_EVALUATION_MODEL=gpt-5-mini
```

Twilio and OpenAI both use PCMU, avoiding realtime transcoding. Server VAD creates turns. Caller
speech during generated audio cancels the response and clears Twilio's buffered audio.

### Local tunnel

Start the app:

```bash
uv run uvicorn voicebot.main:app --host 0.0.0.0 --port 8000
```

In another terminal, expose port 8000 with a trusted tunnel, for example:

```bash
cloudflared tunnel --url http://localhost:8000
# or: ngrok http 8000
```

Copy the resulting HTTPS origin into `VOICEBOT_PUBLIC_BASE_URL`, then restart the app. Twilio must
be able to reach `/twilio/voice`, `/twilio/status`, `/twilio/recording`, and the WSS endpoint
`/twilio/media`.

## Commands

```bash
# Inspect every command and safety flag
uv run voicebot --help

# One authorized call
uv run voicebot call --scenario appointment-scheduling --live

# All 12 scenarios, one completed call at a time
uv run voicebot suite --live

# Re-run transcription and evaluation for an existing recording
uv run voicebot evaluate call-001

# Regenerate the aggregate high-confidence report
uv run voicebot report
```

Scenario IDs come only from validated YAML files in `src/voicebot/scenario_data`. `suite` waits for
each Twilio call to reach a terminal state before starting the next.

## Artifacts

Calls receive stable sequential directories:

```text
calls/
  call-001/
    recording.mp3
    transcript.txt
    transcript.json
    metadata.json
    evaluation.json
reports/
  BUGS.md
```

The recording is stored before transcription or evaluation. Writes are atomic. A downstream
failure is recorded in `metadata.json` and does not delete successful earlier artifacts. The report
includes only issues at or above `VOICEBOT_REPORT_CONFIDENCE_THRESHOLD` (default `0.80`).

## Scenarios

The suite covers scheduling, rescheduling, cancellation, medication refill, office hours,
insurance, weekend availability, ambiguous dates, context correction, multiple intents,
interruption, and a duplicate-name privacy edge case. Scenarios control persona, known facts,
speaking style, objective, fallback behavior, constraints, stop conditions, and evaluation checks.

## Quality checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run pyright
uv run pytest
uv run pre-commit run --all-files
```

Tests exercise call-destination isolation, TwiML and stream behavior, direct PCMU forwarding,
barge-in cancellation, scenario validation, recording retrieval, partial-failure durability,
evaluation validation, report filtering, and CLI safety. They make no network calls.

## Docker

```bash
docker build -t engineer-challenge .
docker run --rm -p 8000:8000 --env-file .env \
  -v "$PWD/calls:/app/calls" engineer-challenge
```

## Limitations

- Active stream state is in memory; use one application process for local assessment calls.
- Artifacts are local files, not shared object storage.
- Speaker labels come from model diarization and may be imperfect; the dual-channel source improves
  separation but does not guarantee attribution.
- Recording and evaluation callbacks run as in-process background tasks. A production deployment
  should use a durable job queue.
- Voice quality depends on phone conditions, VAD tuning, model availability, and live-call review.
  Listen to real calls before changing prompts or VAD settings.
- A failed or unanswered suite call still reaches a terminal state and the suite proceeds; inspect
  metadata and Twilio logs for the cause.

See [architecture.md](architecture.md) for subsystem boundaries and tradeoffs.
