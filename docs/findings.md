# PGai Voice Agent — Final Findings

Target: the Pretty Good AI test line reached at the single authorized destination.
Method: 22 outbound calls from a scripted OpenAI Realtime "patient" across 12 scenarios, each
recorded dual-channel, diarized, and evaluated. Every claim below is tied to a call id and
timestamp. Evidence text lives in [`docs/evidence/`](evidence); the full campaign narrative,
including our own harness defects, is in [`docs/assessment-ledger.md`](assessment-ledger.md).

## Attribution rules used

1. A finding is reported only if it survives removing everything our caller did wrong.
2. Speaker letters from diarization are never trusted; every quote was re-derived from the
   per-channel audio.
3. **We never claim PGai's backend "should" contain a record just because our scenario YAML
   invents one.** Our YAML is our fiction, not their database. Every "could not find my
   appointment/profile" observation is therefore unfalsifiable and excluded.
4. Findings from calls where our caller was truncated, collided with the greeting, drifted, or
   stalled are excluded or demoted.

---

## 1. Confirmed / reproduced findings

### F1 — Fabricates patient demographic data, then retains it over the patient's correction
**Severity: high. Reproduced in 11 independent calls across 7 scenarios.**

On creating a patient profile, the agent asserts a date of birth that the caller never supplied —
always the same value, `July 4, 2000`. When the caller corrects it, the agent either ignores the
correction or explicitly keeps the fabricated value.

| Call | Scenario | Fabrication | Caller correction | Outcome |
|---|---|---|---|---|
| call-004 | appointment-scheduling | 54.0s | 63.2s | ignored; booked at 117.5s |
| call-006 | medication-refill | 52.6s | 60.7s | ignored |
| call-007 | rescheduling | 65.7s | 78.1s | **explicitly retained** |
| call-009 | multi-intent | 70.9s | 80.6s | ignored |
| call-011 | multi-intent | 68.4s | — | not contested |
| call-012 | context-correction | 46.3s | 56.4s | ignored |
| call-013 | ambiguous-date | 67.1s | — | not contested |
| call-015 | weekend-scheduling | 47.8s | 59.7s | ignored |
| call-018 | medication-refill | 40.9s | 51.4s | ignored |
| call-019 | rescheduling | 57.5s | 66.6s | ignored |
| call-020 | weekend-scheduling | 74.1s | 97.7s | acknowledged (only instance) |

Strongest quote — call-007 at 83.1–86.4s, after the caller supplied June 9 1975:

> "I have your date of birth as July 4th, 2000. I'll make a note that you stated June 9th, 1975."

That is not a failure to reconcile; it is a decision to keep invented demographic data and demote
the patient-supplied value to a note. In a healthcare context a wrong DOB on a chart is an identity
and safety defect, not a cosmetic one.

Notably the single counter-example, call-020 at 107.0s ("Thanks for sharing your date of birth,
August 22, 1991"), occurred immediately after the agent's own mid-call restart (F5) — so the
correct behavior appears to depend on a fresh session rather than on reconciliation logic.

Uncontaminated: every fabrication precedes any DOB from our caller, and all occur >40s into the
call, far from any opening-collision window.

### F2 — Gates public, non-sensitive information behind profile creation, then abandons it
**Severity: medium-high. Reproduced in 4 calls across 3 scenarios.**

- call-008, insurance, 126.2s: *"I'm not able to give out the billing office number without a
  patient profile."* (also 99.6s, 121.8s) A billing office number is public contact information,
  not PHI. The caller was left with no verification route except phoning their insurer.
- call-009, multi-intent: the medical-records fax number was acknowledged and deferred twice
  (160.6s, 202.2s: *"I can provide the clinic's fax number after we finish with your
  appointment"*), sequenced behind a task that could not complete, then dropped when the call
  transferred at 250.8s. **Promised, never delivered.**
- call-011, multi-intent: same pattern, four promises (28.9s, 150.5s, 177.5s, 207.7s) and an
  explicit request at 218.1s (*"please go ahead and give me that fax number before the
  transfer"*), then transfer at 221.9s with the number never given.
- call-016, office-hours, 24.0s: *"I don't have the office hours handy."* Office hours are the most
  basic public fact a clinic line should know; the caller was redirected to a QR code at the booth.

Why this is falsifiable while "can't find my record" is not: whether a fax number, billing number,
or opening hours is public information does not depend on the contents of their sandbox database.

**Explicitly not claimed:** that PGai forgot the second intent. In call-009 and call-011 it tracked
the fax request faithfully across many turns. The defect is non-fulfilment, not memory.

### F3 — Ends the call while the caller's request is unresolved
**Severity: high. Reproduced in 2 calls across 2 scenarios.**

- call-014, cancellation, 50.2–55.6s: *"Since I can't access your records without a profile, I
  won't be able to cancel your appointment right now. Have a great day."* — then hangs up. The
  caller had stated a specific appointment to cancel (Dr. Singh, Monday November 2, 11:30 AM) and
  was mid-sentence asking for a human when the line dropped at 61.9s.
- call-021, unusual-edge, 23.6–29.0s: caller declines a profile and gives their name; the agent
  replies *"If you ever need to create a profile, you can scan the QR code at the booth later.
  Have a great day"* and ends at 34.7s — **before ever asking why the patient called.**

Both endings were verified from the agent's own channel audio. Declining a profile should not
terminate a healthcare call; the correct behavior is escalation to a human.

### F4 — Provider and clinician name instability
**Severity: medium. Reproduced in 3 calls.**

Verified from the agent's channel audio, not the diarizer:

- call-012, 158.2s: the caller's requested clinician "Dr. Ahmed" is rendered **"Dr. Almond"**
  (after being correct at 92.6s).
- call-019, 89.2s: the provider is **"Doogie Howser"**, then "Judy Hauser" at 114.7s — two
  different names for one provider inside one call.
- call-013, 160.6s: booking is confirmed with "Doothy Hauser" after being offered as
  "Judy Houser" at 107.0s.

Impact: a confirmation that names the wrong clinician is a false confirmation, and the patient has
no way to know which name is on the record.

---

## 2. Strong single-call findings

### F5 — Mid-call session restart (call-020)
At 82.8s the agent's own channel replays the recording notice and a fresh greeting:
*"Thanks for calling Pivot Point Orthopedics, part of Pretty Good AI. How may I help you today?"*
— mid-conversation, after a profile had already been created. Verified from the agent channel.
The agent then re-asked for the reason for the visit, though it did retain the Sept 18 appointment
later. Single observation, so not promoted, but a session restart mid-call is a serious class of
defect and worth their attention.

### F6 — Repeated identical utterance / stalled loop (call-018)
The agent emits a byte-identical turn twice (64.7s and 83.9s) before the call dies at 89.2s.
**Caveat: our caller stalled first** (silent from 55.7s onward), so the loop may be a reasonable
response to dead air. Reported only as an observation for this reason.

---

## 3. Weak / unverified candidates (not reported as bugs)

- **Transfer dead-end** (calls 5, 7, 9, 11, 19, 20): "Transferring you now" is followed
  immediately by "You've reached the Pretty Good AI test line. Goodbye" and the call ends. Six
  observations, yet still unreportable: the destination is plausibly an unstaffed sandbox endpoint,
  and we cannot distinguish that from a broken transfer without knowing their intended routing.
- **Demo-profile push despite an established-patient claim** (calls 4, 5, 6, 9, 11, 13, 15, 19,
  20): highly consistent, but rests on the premise that a record exists — see attribution rule 3.
  Excluded on principle despite nine observations.
- **Facility/specialty mismatch:** "Pivot Point Orthopedics" booking an annual physical (call-004)
  looked wrong until call-006's greeting confirmed Pivot Point is their fixture identity.
  Downgraded to sandbox naming.
- **Cross-call state sharing:** the same "Tuesday, September 8th, 10 a.m., Kelly Noble" record and
  the Sept 18 appointment our own call-013 created reappear for different callers
  (calls 7, 9, 11, 15, 19, 20). Expected for a shared demo environment, not a defect.
- **Out-of-scope handling** (call-017): the agent correctly refused dermatology scheduling and said
  so plainly. Scored a pass.

## 4. Evaluator overclaims we rejected

Our LLM evaluator produced these; we did not report them.

| Evaluator claim | Call | Why rejected |
|---|---|---|
| "No medications on chart" then "sent your refill request" is a contradiction (0.88) | call-006 | Not contradictory — being unable to refill from an empty chart and forwarding a request to staff coexist. |
| Failed to state explicitly that a refill request is not an approval (0.86) | call-006 | Style preference. The agent did say clinic support would review it, which correctly separates submission from approval. |
| Should have searched existing records before creating a profile (0.9) | calls 4, 5 | Assumes a searchable record exists. Attribution rule 3. |
| Refused to re-check postal code (0.9) | call-005 | Same unprovable premise. |
| Should have supplied the insurer's phone number (0.85) | call-008 | The office is not obliged to know a third party's contact details. |
| Self-contradiction: "only see September… there is one listed for October 13th" (implied) | call-019 | **Diarizer dropped a negation.** The audio says "there *isn't* one listed for October 13th." Rejected after listening. |
| Invented scenario checks not present in the scenario YAML | several | Evaluator-authored criteria are leads, not scored results. |

## 5. Harness / caller defects — must NOT be attributed to PGai

Documented so a reviewer can separate our bugs from theirs. Full detail in the ledger.

| Our defect | Symptom | Calls affected | Fix |
|---|---|---|---|
| Twilio `connected` frame rejected | We closed the media socket; Twilio alert 31921; 0-second call | call-001 | Consume `connected`, then require `start` |
| Reserved structlog `event=` kwarg | Any Twilio `mark`/`dtmf` frame would crash the bridge | latent | Renamed to `twilio_event`/`openai_event` |
| Weak prompt constraints | DOB drift 1988→1980, unrequested Spanish, patient adopting the receptionist role | call-003 | Immutable-facts, language pin, role lock |
| Auto-response on the IVR notice | Our caller talked over the agent's greeting | calls 3, 5, 6, 7 | Event-driven opening-turn gate |
| `max_output_tokens: 180` | Caller speech truncated mid-word at ~6.5s | calls 3, 6?, 8, 9 | Raised to 800 |
| No terminal-state rule | Caller restated requests into a closed line | calls 9, 21 | Prompt rule: stop after goodbye/transfer |
| Concurrent calls | A recording callback was lost | call-017 | Recovered from Twilio by SID; run calls serially |

Two of these directly caused us to almost misreport PGai: the diarizer invented the word "mail"
from a truncated syllable in call-009, and dropped a negation in call-019 that would have read as a
self-contradiction.

---

## Summary for the reviewer

The single most important result is **F1**: across 7 scenarios and 11 calls, the agent invents a
patient date of birth and, when corrected, keeps its own value. F2 (public information withheld,
then promised and abandoned) and F3 (ending calls with the request unresolved) are the next two,
both reproduced across scenarios. F4 shows clinician names are not stable even within a single
call.

We deliberately did not report the loudest, most frequent observation in the whole campaign — the
demo-profile push — because it depends on a record existing in their sandbox that we cannot verify.
