# napkin notes

Running notes from the campaign. Not documentation — this is the debugging story in order.
Polished version: `README.md`, `docs/findings.md`, `docs/assessment-ledger.md`.

---

## build order

- PR1 foundation → Twilio gateway, `--live` gate, one hard-coded destination, no `--to` flag ever
- PR2 realtime patient → bridge, PCMU straight through, no transcode
- PR3 analysis → recording → diarized transcript → structured eval
- PR4 polish → 12 scenarios, aggregate report, architecture doc

---

## call 1 — protocol failure

- call answered → hung up in **0 seconds**. duration=0, price=0, recording 835 bytes / 0.1s
- transcript = one line, the *other* agent saying "Thank you"
- assumed our audio path was broken → wrong
- Twilio alert **31921** on the call SID: *"your server closed the WebSocket"*
- `<Connect><Stream>` is terminal → closing the stream ends the call
- root cause: bridge required `start` as first frame. Twilio actually sends
  `{"event":"connected"}` **first**, then `start`. We 1008'd their handshake.
- fix = consume exactly one `connected`, then require `start`. auth untouched.
- 3 rejection tests kept passing → proved auth wasn't weakened
- our tests had been sending `start` first → the suite encoded the bug
- bonus find while writing tests: `logger.info("x", event=...)` → structlog reserves `event`.
  Any Twilio `mark`/`dtmf` frame would have crashed the bridge mid-call. 3 sites renamed.

## call 3 — voice works, caller doesn't

- audio flows both ways. pipeline end to end. 
- but: DOB drifted **1988 → 1980**, switched to **Spanish**, said **"I can help with that"**
- telephony untouched — zero evidence it was involved
- prompt said "Facts you may state" = permission, not immutability. no language pin. role named
  once and never defended against an assistant-trained base model
- fixes: immutable-facts block, `Scenario.language` (default English), explicit "never the
  receptionist", "let the other party finish"
- VAD `silence_duration_ms` 550 → 1200 (was answering into their pauses)

## call 4 — first real conversation

- full scheduling flow, booking confirmed, clean close, 2:33
- caller held DOB, language, role. "I can help with that" now comes from **their** side
- and the actual finding lands: **"your date of birth is July 4, 2000 for demo purposes"**
  — we never gave a DOB
- caller corrects → they ignore it → book anyway

## call 5 — unusual-edge

- their IVR offers Spanish; our caller stays English and *asks* for English → language pin works
- no privacy leak (the headline risk for this scenario) → scored a PASS for them
- "can't find your profile" → **not reportable**. our YAML invented that patient. their sandbox
  owes us nothing. this rule saved us repeatedly later
- transfer announced → dead line. first sighting.

## calls 5–7 — opening collisions

- 0.60s → 0.40s → **0.85s + five more overlaps to 22s**
- measured from stereo channels, not diarizer labels
- onset was always `notice_end + 1.2s + latency` = 7.80 / 7.85 / 8.35 / 8.25s
- → server VAD treats the **recording notice** as a caller turn and auto-generates our opening
- collision is luck: depends on when *their* greeting starts (5.75–8.25s)
- rejected raising `silence_duration_ms`: fixed offset into a race we don't control + taxes every
  good mid-call turn
- first gate attempt = timer after `speech_stopped`. wrong: call-007's notice→greeting gap was
  **2.55s**, longer than the 2.0s hold → would have fired into the greeting again
- final gate: session opens `create_response: false` → on first `speech_stopped` send a bare
  `session.update` enabling it → their greeting gets answered by normal VAD at its own turn end.
  timer survives only as a backstop (silent answer / office waiting for us)
- mid-call VAD byte-identical after release. that behaviour was good; don't touch it.
- call-008 = live confirmation. onset **17.50s**, behind their whole three-part opening, zero
  overlap

## call 9 — mid-word truncation

- transcript: "getting the **mail**", "and then **I'll stay**" → looked like prompt drift
- it wasn't. measured every caller response: `6.40 6.75 3.30 6.65 6.65 6.20 5.45 6.40 6.70 1.95 6.70`
  → **nothing ever above 6.75s** = a ceiling
- `max_output_tokens: 180` — audio tokens count against it → speech cut at ~6.5s
- re-transcribed our channel alone, 20s past the cut: audio stops after "and getting the",
  silence for 20s. so **neither "mail" nor "medical records" was ever spoken**
- → the **diarizer invented "mail"** from a truncated syllable. two stacked defects.
- worse: truncation ate the **second intent** from turn 1 of a multi-intent call → our own
  scenario premise was never satisfied → call void
- also: kept talking 7s after their transfer/goodbye → no terminal-state rule → prompt rule added
- fix: 180 → 800

## retro-audit — was the ceiling eating earlier calls?

- re-measured 004/005/006/008 on preserved audio
- tried a tail-energy metric first. it did **not** separate the calibration set → threw it out
  rather than tune it. energy only shortlists; **continuation decides**
- 004 longest 4.30s, 005 5.30s → never near the ceiling
- 006 hit 6.00/6.40/6.45s three times but every ending decays with complete text → close, not cut
- 008 **was** cut: "Could we focus on the **insur|**" at 24.15s → demoted from submission-quality
- lesson: the ceiling was live for the entire campaign; length, not luck, decided who escaped

## call 17 — lost recording callback

- artifacts never appeared. calls 16 and 18 (same minute) were fine
- asked Twilio directly: recording `REa1bbe57…` **exists**, completed, 69s, no error, no 11200 alert
- our handler logs on entry → no log line → request never reached us
- three calls overlapped (17:30:55 / :58 / 17:31:04) and call-018 threw alert 15003 on
  `/twilio/status` in that same window → callback path was failing under concurrent load
- **serial vs concurrent lesson**: `suite` polls each call to a terminal state precisely so calls
  never overlap. these were launched as concurrent one-off `call` invocations.
- recovery: fed the known SIDs to the existing `AnalysisPipeline.process` → full artifacts, no
  rerun, no new billable call

## the finding that kept reproducing

- `July 4, 2000` on **11 calls / 7 scenarios**, always at profile creation, never supplied by us
- call-007 is the money quote: *"I have your date of birth as July 4th, 2000. I'll make a note
  that you stated June 9th, 1975."*
- not a memory failure — a **decision** to keep invented data over the patient
- only clean counter-example is call-020, right after their own mid-call restart

## other things they actually did

- **promise then abandon**: fax number promised 4× in call-011, requested explicitly before the
  transfer, transferred anyway without it. same shape as call-008's billing number
- **public info gated**: billing number, fax number, *office hours* ("I don't have the office
  hours handy") — none of it PHI
- **premature close**: call-014 "I won't be able to cancel your appointment right now. Have a
  great day" → hangup mid-caller-sentence. call-021 ended at 29s before ever asking why we called
- **name drift**: Dr. Ahmed → "Dr. Almond"; one provider called both "Doogie Howser" and
  "Judy Hauser" *in the same call*
- **mid-call restart**: call-020, their recording notice + greeting replay at 82.8s, mid-conversation

## overclaims we refused to ship

- "no medications on chart" + "sent your refill request" ≠ contradiction. both can be true
- "should have searched existing records first" → assumes a record exists. our YAML is fiction
- call-019 "self-contradiction" → **diarizer dropped a negation**. audio says "there *isn't* one
  listed for October 13th". listened, rejected
- transfer dead-end: 6 observations and still unreported — can't distinguish a broken transfer
  from an unstaffed sandbox endpoint
- demo-profile push: 9 observations, loudest thing in the campaign, **deliberately not reported**

## quality vs void

- FINAL QUALITY 11 · VALID EVIDENCE 4 · VOID 6 · 1 in flight at audit
- void reasons are all *ours*: protocol failure, caller drift, opening collision, token
  truncation, caller stall
- two scenarios have no final-quality call: **unusual-edge** and **medication-refill**

## rules that earned their place

1. don't tune on vibes — measure the audio, then change one thing
2. never trust diarizer speaker letters or its words near a cut
3. our scenario fiction is not their database
4. a caller-side defect can never become a PGai finding
5. few high-confidence findings > many weak ones
