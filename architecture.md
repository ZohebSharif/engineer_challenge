# Architecture

## System flow

```text
voicebot CLI
  -> Twilio REST call (fixed destination, explicit --live)
  -> POST /twilio/voice -> TwiML <Connect><Stream>
  -> WSS /twilio/media
       Twilio PCMU -> OpenAI input_audio_buffer.append
       OpenAI PCMU -> Twilio media
       caller speech -> response.cancel + Twilio clear
  -> Twilio dual-channel recording
  -> POST /twilio/recording
  -> recording.mp3 -> diarized transcript -> structured evaluation
  -> voicebot report -> reports/BUGS.md
```

## Boundaries

### Configuration and safety

`config.Settings` is the single typed environment boundary. `telephony.TwilioGateway` is the only
component that creates billable calls; it does not accept a destination and always uses
`AUTHORIZED_DESTINATION`. CLI live paths validate all required settings before entering the
Twilio boundary. CI invokes only static checks and tests.

Twilio signs HTTP callbacks with the account auth token. `security.verified_twilio_settings`
validates those signatures against the configured public URL. The WebSocket cannot use the normal
HTTP signature dependency, so TwiML sends the per-installation secret as a custom `<Parameter>`;
the endpoint validates it from Twilio's start event before opening provider sessions.

### Realtime conversation

`bridge.run_media_bridge` owns one Twilio socket and one `RealtimeSession`. Both providers support
8 kHz G.711 mu-law/PCMU, so the bridge forwards base64 payloads directly. Avoiding decode,
resampling, and re-encoding reduces latency, CPU work, and quality loss.

Two concurrent pumps handle each direction. Completion or failure in either pump cancels the
other, closes OpenAI, and removes in-memory call state. A call timeout bounds abandoned sessions.
`TurnManager` tracks queued model speech. OpenAI server-VAD speech-start events cancel generation
and send Twilio `clear`, preventing stale patient audio after an interruption.

Scenario YAML is parsed into an extra-forbidden Pydantic model before a call. Prompt generation
uses every scenario control and adds global truthfulness and short-response constraints. The model
improvises from facts and objectives rather than reading a script.

### Durable analysis

`ArtifactManager` creates `call-NNN` directories and uses write-then-rename for JSON and text.
`AnalysisPipeline` is deliberately linear:

1. download the canonical Twilio MP3 with bounded retry;
2. persist recording status;
3. request diarized transcription and write TXT plus JSON;
4. request strict-schema evaluation and validate it with Pydantic.

Each stage catches and records its own failure. Later failure never removes an earlier artifact.
The evaluator receives scenario checks plus a fixed taxonomy covering factual, workflow,
confirmation, state, clarification, conversational, policy, and unexpected consequential issues.
Its prompt explicitly excludes punctuation and trivial style findings.

`reporting.generate_report` revalidates evaluation files, filters by confidence, sorts
deterministically, and atomically replaces the Markdown report.

## Tradeoffs

- **In-memory sessions:** simplest reliable model for one assessment instance. Horizontal workers
  would require shared session routing and are intentionally unsupported.
- **Local filesystem artifacts:** transparent and reviewer-friendly. Production durability would
  require object storage and a database-backed call index.
- **BackgroundTasks pipeline:** sufficient for a local long-running process, but process loss can
  interrupt analysis. A durable queue is the production alternative.
- **Model diarization:** practical speaker-aware output without a bespoke audio pipeline. Labels can
  be wrong; retaining the recording and timestamps makes results auditable.
- **Server VAD:** minimizes turn latency and API control traffic. Threshold and silence duration are
  explicit tuning points that must be judged by listening to live calls.
- **Sequential suite polling:** prevents overlapping billable calls and audio sessions at the cost
  of a longer suite runtime.

## Extension points

Provider I/O is isolated in `telephony.py`, `realtime.py`, `recordings.py`, `transcription.py`, and
`evaluation.py`. Scenario content is data. Tests replace external boundaries with fakes while
exercising the same orchestration and artifact code used by live calls.
