# napkin notes

Running notes from the live-call campaign, in order. Not polished documentation — this is the
debugging story as it happened. Polished versions: [`README.md`](README.md),
[`docs/findings.md`](docs/findings.md), [`docs/assessment-ledger.md`](docs/assessment-ledger.md).

---

## Call 1 — Protocol failure

- Protocol failure
- → found incorrect Twilio handshake assumption
- → minimal protocol fix
- → preserved authentication
- → regression tests

## Call 2 — VOID

- VOID — misclick

## Call 3 — Behavioral drift

- Voice pipeline works
- → new problem: behavioral drift
- → correctly leave telephony alone
- → inspect prompt + Realtime config
- → identify weak invariants + aggressive VAD
- → minimal prompt/config changes
- → regression tests

## Call 4 — Behavioral fixes validated

- → behavioral fixes validated
- → DOB/language/role stayed consistent
- → turn-taking improved
- → full scheduling flow completed
- → PGAI used conflicting demo DOB, never reconciled correction
- → caller now reliable → move to diverse scenarios

## Call 5 — Unusual edge — **QUALITY CALL #1**

- → identity/privacy stress test
- → caller held facts + refused duplicate profile
- → PGAI couldn't locate claimed existing profile
- → correctly escalated to staff
- → transfer appears to terminate at test line
- → opening overlap/clipping = nit, don't tune yet
- → no strong privacy leak observed

## Call 6 — Medication refill

- → rough opening / caller talks over greeting
- → rest of conversation stabilizes
- → facts + role stay consistent
- → PGAI again fabricates July 4, 2000 DOB
- → DOB correction ignored
- → refill correctly routed for review, not falsely approved
- → repeated DOB/state bug now stronger
- → watch opening overlap before counting as final quality call

## Call 7 — Rescheduling — VOID

- → VOID for final set: very rough opening
- → repeated opening collision now actionable
- → conversation stabilizes afterward
- → caller holds DOB + appointment facts
- → PGAI again fabricates July 4, 2000 DOB
- → explicitly refuses correction; only "makes a note"
- → reschedule blocked by sandbox/state mismatch
- → transfer dead-ends again

> Framing that unblocked the fix: *you're effectively telling the agent: find the code that decides
> when the patient's first Realtime response is allowed to happen, and gate that specific path.*

## Call 8 — Insurance — **QUALITY CALL #2**

- → clean opening
- → caller stayed on-task / no contamination
- → PGAI did NOT overpromise coverage
- → gave insurer verification path
- → billing contact gated behind profile = weak/unverified UX issue

## Call 9 — Multi-intent — VOID

- → VOID for final-quality set
- → opening okay, but caller degrades later
- → malformed wording / intent phrasing
- → transfer/disconnect handling gets messy
- → useful PGAI evidence still exists
- → output token ceiling truncating speech
- → diarizer then hallucinated completion ("mail")
- → audit existing quality set before spending on reruns

## Call 10 — Insurance rerun — **QUALITY CALL #3**

- → clean opening + stable caller
- → token-limit fix validated
- → PGAI handled exact-plan question correctly
- → no false coverage guarantee
- → clear verification options
- → no meaningful bug

## Call 11 — Multi-intent rerun

- → clean/stable caller
- → both intents stated immediately + retained
- → token truncation fixed
- → PGAI remembered both intents
- → repeatedly promised fax number
- → transferred without ever providing it
- → DOB fabrication reproduced again
- → strong submission candidate

## Call 12 — Context correction — **QUALITY CALL #4**

- → clean opening + stable caller
- → BP follow-up correction persisted ✅
- → PGAI remembered Dr. Ahmed initially
- → drifted Ahmed → "Almond" twice
- → recovered to Ahmed at final handoff
- → fabricated July 4, 2000 DOB again

## Call 13 — Ambiguous date — **QUALITY CALL #5**

- → clean/stable caller
- → PGAI guessed "next Friday" = Sep 11
- → caller corrected to Sep 18
- → correction persisted through booking
- → provider name drift: Judy Houser → "Doothy Hauser"
- → fabricated July 4, 2000 DOB again

## Call 14 — Cancellation

- → clean opening
- → caller clearly identifies exact appointment
- → PGAI refuses cancellation without profile
- → no alternate verification / no escalation
- → tries to end call unresolved
- → caller cut off mid-request at end
- → useful evidence, but not ideal final-quality call

## Call 15 — Weekend scheduling

- → PGAI correctly says no weekend availability
- → does NOT invent/book weekend slot
- → evaluator overcalls weekend constraint failure
- → fabricated July 4, 2000 DOB again
- → useful evidence, rerun optional

## Call 16 — Office hours — **QUALITY CALL #6**

- → clean/stable caller
- → simple factual info request
- → PGAI could not provide regular office hours
- → redirected to QR code / in-person staff
- → kept pushing demo-profile creation
- → evaluator overcalls emergency-hours issue

## Call 17 — Interruption — **QUALITY CALL #7**

- → recovered recording successfully
- → clean/stable caller
- → specialty correction landed
- → PGAI understood dermatology ≠ orthopedics
- → no transfer / no concrete dermatology handoff
- → evaluator overcalls "lost correction"

## Call 18 — Medication refill rerun

- → clean opening
- → caller stable until transfer question
- → PGAI misnames Ayesha → Aisha
- → fabricated July 4, 2000 DOB again
- → refill not advanced; only offers support transfer
- → caller stops responding / call stalls
- → useful evidence only

## Call 19 — Rescheduling rerun — **QUALITY CALL #8**

- → clean/stable caller
- → DOB + appointment facts held consistently
- → PGAI fabricates July 4, 2000 DOB again
- → correction not reconciled
- → PGAI contradicts itself on Oct 13 appointment
- → no unsafe reschedule of wrong appointment
- → escalates instead

## Call 20 — Weekend rerun — VOID

- → caller identity clean: Priya Shah
- → PGAI mishears Shah → Shaw; caller corrects
- → fabricated July 4, 2000 DOB again
- → CALL RESTARTS / greeting repeats mid-call
- → afterward DOB correction acknowledged
- → weekend-only constraint respected
- → no invented weekend availability
- → VOID because of mid call restart

## Call 21 — Unusual edge rerun — VOID

- → clean opening
- → caller delays appointment intent too long
- → PGAI prematurely closes after profile refusal
- → caller states booking goal only after goodbye
- → no duplicate-patient disclosure
- → VOID final-quality / contaminated

## Call 22 — Multi-intent rerun

- → clean opening, zero overlap, caller stable throughout
- → both intents stated in the first turn
- → PGAI refuses to search for the existing record five times
- → promises the fax number twice, always conditioned on profile creation
- → transfers with both requests unresolved
- → fax promise/abandon pattern now 3× in this scenario
