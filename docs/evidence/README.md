# Evidence index

Classification index for every call in the campaign. Text artifacts are mirrored here; the
authoritative per-call directory, **including the dual-channel `recording.mp3`**, is
`calls/call-NNN/` at the repository root. Each row pins the Twilio call SID, recording SID, and
recording MD5 so any recording can be re-fetched from Twilio and byte-verified against the
committed file.

| Call | Scenario | Class | Length | Call SID | Recording SID | Recording MD5 |
|---|---|---|---|---|---|---|
| call-001 | appointment-scheduling | VOID | 0.1s | `CA7c21e3937c2c17e9a53b1d4b4dd63b04` | `RE47a8bb2d170817245d6601ad1978f5da` | `48720dd91eeaac78c1eadd1967f31a17` |
| call-002 | appointment-scheduling | VOID | - | `CAd3ad0aa99ba582953e2beedbf999f72f` | `-` | `-` |
| call-003 | appointment-scheduling | VOID | 64.0s | `CA6772b532ad005f61bd46a54668368968` | `RE510341e9dc3a86e5992fd24e122e3be7` | `db43f0fcb9c6b16e18abad643f4e1554` |
| call-004 | appointment-scheduling | FINAL QUALITY | 153.2s | `CAe9a1271d5423aff3bca543cc8e0d0384` | `REf116923bca1a12e6c15ad5d2fc35853f` | `66808962ffadf93e3984a53f65ffa45e` |
| call-005 | unusual-edge | VALID EVIDENCE | 112.9s | `CA2f01743acf60bfa39463a563955ee904` | `REa17f15bb220dcaa7844b95ca2180f4b1` | `7b791a51b363ded13588a279a7344fb4` |
| call-006 | medication-refill | VALID EVIDENCE | 116.7s | `CA8157745d7e7c219e50ced0b7bf4a368d` | `REa267c550fcbe11d72f1fe128b5315f73` | `bd93eafb7cab80362c2c2fc58bbfe7ed` |
| call-007 | rescheduling | VOID | 221.9s | `CA977137d4640c47f53439b0eda3841029` | `REa298b9b60680b3d0e4eb0d40569d9930` | `1dabea21a7cdac7fa5f9808fe4c776b1` |
| call-008 | insurance | VALID EVIDENCE | 196.1s | `CA487ad55f374496b7e887560315ffcab7` | `REf2983204d903399a4c364fdf6f9073ef` | `87801ed0d668410c9c673a3e05c78036` |
| call-009 | multi-intent | VOID | 268.4s | `CAf15f306168497ba9b5b514336d9497ce` | `REd70b9368378858ebc724524a5a561f71` | `46633b877e78dca33c0a06e2d4aaad98` |
| call-010 | insurance | FINAL QUALITY | 119.1s | `CA0ac23e28081940a630aad3e58f7e0576` | `REcfc81aa0774606a7b17593eca4ad2a08` | `1cd73e4211c2bb36497cea781e3dd432` |
| call-011 | multi-intent | FINAL QUALITY | 233.4s | `CA20746e9d9a3258f44406a6e8233e0e6b` | `REe95dbb8e3f79c2ad511d357e839a1b6b` | `1127cd19677b9d9252d43cad5c1c55e3` |
| call-012 | context-correction | FINAL QUALITY | 210.7s | `CAee7c21b983e0fc12c304dcdd70d58b27` | `RE0202157aa7cf40634cea11cf3b25fe91` | `78d588bdbd6d8d333b37e66e21fd9ec7` |
| call-013 | ambiguous-date | FINAL QUALITY | 186.5s | `CA6ff184469bc179d458793e8b8fd01bbb` | `REb0ff66987453ecadf238c1f7d7823473` | `9056e4858bbdcc65de755411a3c7a622` |
| call-014 | cancellation | FINAL QUALITY | 61.9s | `CAd4cf144d633e003ad9e51f9f9bc9a306` | `REaef21ad51260ae892859d200360bec06` | `2fa60eb61aedd6a8d498cdc870e2cf04` |
| call-015 | weekend-scheduling | FINAL QUALITY | 147.5s | `CAae6081b28869fb6861f4c665f1e0f20c` | `RE761bb6702a67b7dee6624cb615dd4e2e` | `9c33f175186c335a143e06bd78c70263` |
| call-016 | office-hours | FINAL QUALITY | 68.2s | `CA47889a05cb6855f516705766a16c468f` | `RE9df33a9b13d31a42c8fdcc906e5625eb` | `baaac9c0c4ad2923e2e1f58a096e92ec` |
| call-017 | interruption | FINAL QUALITY | 68.6s | `CAc0e4baa6ccdd1e8ffcea3669500989dc` | `REa1bbe57b937303694742f8dc3a76e9a7` | `7d5f45482c584ca05c570d356ee6f17e` |
| call-018 | medication-refill | VOID | 89.2s | `CAb88d1f363dfff85d0e6ab4e283266155` | `REaad671c3fad849baccb3f21108376499` | `8668f21b0f8a76d940b308201f78ee4b` |
| call-019 | rescheduling | FINAL QUALITY | 223.0s | `CA3ea752055fac2af800586862fd25301f` | `RE794d2b9c89968edd0a958e450557e36c` | `c94c56719f8e8b2f470e1b5f7a5096dd` |
| call-020 | weekend-scheduling | FINAL QUALITY | 221.7s | `CAba4667e71289f9e8809630ad641f3f57` | `REb2bb4db2ecad6e7ab0dd0740bbe2817f` | `734cf9aa7f4d79141f63e2953a0d2a69` |
| call-021 | unusual-edge | VALID EVIDENCE | 34.7s | `CA964178fdd8869e578127de5ebe1588e3` | `RE54ad6aa59b74e9183745f31d516f0ffd` | `83160ecbcf6f0465e045860d9a4c5691` |
| call-022 | multi-intent | FINAL QUALITY | 127.7s | `CAbccd2fb58de0472a2490e35f901767c1` | `REf351c2080e80126401d6b0d6df8fd233` | `2b9189717a12059343a44dc2a1a0dc5a` |

## Exclusion reasons

- **call-001 — VOID**: harness: bridge closed the media socket (Twilio 31921); 0.1s recording
- **call-002 — VOID**: harness: no artifacts (aborted before media)
- **call-003 — VOID**: caller drift: DOB 1988->1980, unrequested Spanish, receptionist role; 0.9s opening overlap
- **call-005 — VALID EVIDENCE**: 0.55s opening collision with the greeting (pre-gate)
- **call-006 — VALID EVIDENCE**: 0.35s opening collision; three utterances at the 6.0-6.45s token ceiling
- **call-007 — VOID**: 2.6s of opening collisions across six overlaps, no self-correction until ~22s
- **call-008 — VALID EVIDENCE**: caller utterance truncated mid-word at 24.15s ('...the insur|') by the token ceiling
- **call-009 — VOID**: token truncation removed the second intent from the caller's first turn; also spoke into a closed line
- **call-018 — VOID**: caller stalled from 55.7s and never answered; call died at 89.2s
- **call-021 — VALID EVIDENCE**: PGai ended the call at 29.0s (finding F3); our caller then spoke into the closed line

## Final-quality selection

- **call-004** (appointment-scheduling): clean audio, longest utterance 4.3s, no overlap; caveat: caller volunteered DOB unprompted at 63.2s
- **call-010** (insurance): post-fix: zero overlap, longest 3.75s, complete artifacts
- **call-011** (multi-intent): post-fix: zero overlap, longest 7.85s verified complete
- **call-012** (context-correction): post-fix: zero overlap, longest 5.5s
- **call-013** (ambiguous-date): post-fix: zero overlap, longest 4.1s
- **call-014** (cancellation): post-fix: zero overlap; call ended by PGai mid-caller-sentence (finding F3), caller behaviour correct
- **call-015** (weekend-scheduling): post-fix: zero overlap, longest 5.1s
- **call-016** (office-hours): post-fix: zero overlap, longest 6.1s verified complete
- **call-017** (interruption): post-fix; recording callback was lost and recovered from Twilio by SID; caveat: caller never actually barged in
- **call-019** (rescheduling): post-fix: zero overlap, longest 5.95s
- **call-020** (weekend-scheduling): post-fix: zero overlap; PGai restarted its own session mid-call (finding F5)
- **call-022** (multi-intent): post-fix: zero overlap, onset 17.45s, longest 7.65s verified complete; both intents stated in the opening turn, so the scenario premise was satisfied
