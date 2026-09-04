# High-confidence Voice Agent Issues

Generated from validated evaluations. Confidence threshold: 0.80.

## 1. The agent did not present available weekday-morning appointment options nor confirm any specific appointment date/time, so the scheduling objective was not achieved.

- Call: `call-003`
- Scenario: `appointment-scheduling`
- Category: `workflow_failure`
- Confidence: `0.96`
- Evidence: Patient requested appointment and asked for available times: 'I'd like to schedule my annual physical for a weekday morning next week.' [5.7s]; 'Could you let me know what times you have available?' [9.6s]. No times or booking confirmation appear later in the transcript.
- Recommendation: Offer concrete available appointment slots that match the patient's preference (weekday mornings next week), get the patient's selection, and confirm the full appointment details (date, start time, provider/location).

## 2. The agent failed to execute the scheduling workflow: no appointment was proposed, checked for availability, or booked.

- Call: `call-001`
- Scenario: `appointment-scheduling`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Only line in transcript: "[0.0s] A: Thank you." — there is no evidence of any scheduling steps or booking confirmation.
- Recommendation: Proceed with the full scheduling flow: ask for/confirm patient availability, check office availability, propose specific weekday-morning appointment times next week, and confirm an exact date and time before ending the call.

## 3. The agent falsely confirmed the patient's DOB as 'July 4, 2000' despite the patient having given a different DOB.

- Call: `call-003`
- Scenario: `appointment-scheduling`
- Category: `false_confirmation`
- Confidence: `0.95`
- Evidence: Agent: 'And your date of birth is July 4, 2000 for demo purposes.' [54.1s]-[56.6s] while the patient had stated 'February 14th, 1988.' [31.7s].
- Recommendation: Apologize for the error, correct the DOB in the system, and explicitly confirm the corrected DOB out loud with the patient.

## 4. Agent failed to complete the primary task of moving the existing appointment to a Thursday or Friday after 3pm and transferred the caller without resolving or securing the original appointment.

- Call: `call-007`
- Scenario: `rescheduling`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: After the caller requested checking Thursday/Friday after 3 p.m., the agent never provided available slots or completed a reschedule and instead offered to transfer: "Would you like to reschedule the September 8th appointment or do you want to check with the clinic about your October appointment?... Would you like me to transfer you to the clinic team... ?" Then: "Transferring you now."
- Recommendation: Follow the rescheduling workflow: verify identity and current appointment, check requested-day availability, propose options, confirm a new slot, and only then cancel the original appointment. If unable to find the appointment, place the appointment 'on hold' or escalate to a scheduler while keeping the caller on the line, rather than transferring without resolution.

## 5. Neither intent (rescheduling the specified Thursday 10:00 AM appointment nor providing the medical-records fax number) was completed before the call ended.

- Call: `call-009`
- Scenario: `multi-intent`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Caller repeatedly: "I need to reschedule my Thursday ten am appointment... and get the medical records." (22.0s, 43.0s). Agent promised: "I can provide the clinic's fax number after we finish with your appointment." (160.6s–165.3s). At the end the caller is still asking: "I'm still here to reschedule my Thursday 10 a m appointment to Monday afternoon, and get the medical record" (263.2s), indicating neither task was completed.
- Recommendation: Agent should complete the reschedule or confirm transfer to live staff and immediately provide the fax number. If unable to complete on the call, schedule a callback or transfer with an explicit confirmation of both actions and a reference number.

## 6. Agent failed to deliver the requested medical-records fax number before transferring the call, despite multiple promises to provide it.

- Call: `call-011`
- Scenario: `multi-intent`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Agent repeatedly promises to get the fax number: 'I'll also get the fax number for medical records for you as well.' [150.5s][176.6s][203.3s]. Caller explicitly asks: 'please go ahead and give me that fax number for medical records before the transfer.' [218.1s]. Agent immediately transfers without giving the fax number: 'Transferring you now.' [221.9s].
- Recommendation: Provide the requested fax number before transferring, or explicitly confirm that the receiving clinic agent will provide it and obtain the number from the clinic prior to completing the transfer.

## 7. Agent did not complete the requested cancellation and provided no alternative resolution or escalation.

- Call: `call-014`
- Scenario: `cancellation`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: "I'm just calling to cancel a specific appointment." (19.4). Agent: "Since I can't access your records without a profile, I won't be able to cancel your appointment right now." (50.2–55.6).
- Recommendation: Agent should offer alternative verification (e.g., confirm DOB and appointment details) or escalate to staff who can cancel. If profile creation is required, offer to take the cancellation request and submit it on behalf of the patient or provide a callback from someone who can cancel.

## 8. Agent did not provide the regular office hours the caller requested.

- Call: `call-016`
- Scenario: `office-hours`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Caller: "I'm just calling to find out your regular office hours." (17.3s–20.2s). Agent: "I don't have the office hours handy" (24.0s–25.9s) and then directed the caller to a QR code or in‑person staff (42.8s).
- Recommendation: Agent should provide the regular office hours directly when asked, or immediately transfer the caller to a staff member who can, rather than declining to provide the information.

## 9. Agent did not correct the specialty to dermatology nor attempt to schedule the requested dermatology visit.

- Call: `call-017`
- Scenario: `interruption`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: "Actually, I need a dermatology appointment, not orthopedics." ... "I don't have access to dermatology scheduling or transfers. You'll need to reach out to a dermatology clinic directly for an appointment."
- Recommendation: When a caller corrects the specialty, update the workflow to either (a) offer to schedule with the correct specialty or (b) transfer/connect to an appropriate clinic. If transfers are not supported, present a concrete alternative (list of partner dermatology clinics, online scheduling links, or an option to take contact details and have someone follow up).

## 10. The refill request was not advanced or submitted; no clear next step or timeline was provided to the patient.

- Call: `call-018`
- Scenario: `medication-refill`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Patient: "I need a refill for lisinopril, 10 milligrams once daily." Agent: "I don't see any medications on your chart that I can refill right now. If you'd like to speak with someone about this, I can connect you to our patient support team. Would you like to do that?" (lines 54.0s–73.1s).
- Recommendation: Ask clarifying questions needed to process a refill (confirm medication, dosage, pharmacy, how many pills remain), state whether the agent can submit the refill or must transfer to prescription support, and if transferring, explain who will handle it and the expected timeline (e.g., "I will submit this to your prescriber and you can expect a response within X hours/days") or immediately transfer with a warm handoff.

## 11. Agent insisted on creating a demo patient profile and did not gather or use the caller's identifying information (DOB, appointment date) before claiming the available appointments and rejecting the caller's stated appointment. This prevented proper verification and resolution.

- Call: `call-019`
- Scenario: `rescheduling`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Caller: "I'm actually calling about rescheduling my existing appointment." (17.2s). Agent: "I can help... but I'll need to create a demo patient profile for you first. Can I get your first and last name?" (24.0-28.4s). Caller gave name and later DOB, but the system still only showed September appointments and did not use caller-supplied info to find October 13 (80.9-94.4s, 136.5-161.9s).
- Recommendation: When a caller states they already have an appointment, ask for and use identifying details (DOB, appointment date/time, confirmation number) before creating new/demo records. Re-run searches across months and escalate appropriately if records differ.

## 12. Agent created a demo patient profile with an incorrect date of birth and failed to use the patient's provided DOB when creating the profile.

- Call: `call-020`
- Scenario: `weekend-scheduling`
- Category: `state_management_error`
- Confidence: `0.95`
- Evidence: Agent: 'Your patient profile has been created and your date of birth is set as July 4th, 2000 for demo purposes.' [74.1s]. User then corrected: 'My date of birth is August 22, 1991.' [99.8s–102.8s].
- Recommendation: Do not finalize or rely on auto-filled demo data for an established patient. When a record is not found, confirm key identifiers (DOB, full name, MRN, phone or email) with the patient before creating or saving a demo profile. Update or delete any incorrect demo record and re-check the actual patient record.

## 13. Agent prematurely closed the call and signaled completion despite the caller still having an active request.

- Call: `call-021`
- Scenario: `unusual-edge`
- Category: `state_management_error`
- Confidence: `0.95`
- Evidence: Agent closed with 'Have a great day.' (29.0s) and did not respond to the caller's subsequent statement of intent: 'I'm actually calling to book an appointment.' (32.3s).
- Recommendation: Avoid closing language until the caller's needs are resolved. Use explicit closing checks like 'Is there anything else I can help with today?' and confirm resolution before ending the call.

## 14. Agent did not schedule the requested appointment or follow the appointment-booking workflow after the caller identified themself and stated they had a profile.

- Call: `call-021`
- Scenario: `unusual-edge`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Agent: 'If you ever need to create a profile, you can scan the QR code... Have a great day.' (29.0s) Caller: 'I'm actually calling to book an appointment.' (32.3s). No scheduling steps or appointment questions appear in the transcript.
- Recommendation: Do not end the interaction after obtaining only a name. Follow the appointment workflow: ask the reason for visit, verify identity, check availability, offer dates/times, and confirm the appointment details.

## 15. Neither requested action was completed: the appointment was not rescheduled and the medical-records fax number was not provided.

- Call: `call-022`
- Scenario: `multi-intent`
- Category: `workflow_failure`
- Confidence: `0.95`
- Evidence: Patient: 'I'm calling to reschedule my Thursday ten a m appointment and get the fax number for medical records.' (20.4s). Agent repeatedly asks for name/create demo profile and never confirms a new appointment or gives a fax number (33.9s–101.6s). The call is transferred before either request is resolved (117.0s).
- Recommendation: Agent should confirm the caller's existing appointment, propose/confirm alternate times (e.g., the caller's preferred Monday afternoon), and provide the fax number during the call or transfer to a staff member who can complete both tasks before ending the call.

## 16. The agent recorded an incorrect date of birth for the patient and did not update or reconcile the record after the patient provided DOB information.

- Call: `call-003`
- Scenario: `appointment-scheduling`
- Category: `state_management_error`
- Confidence: `0.94`
- Evidence: Patient: 'February 14th, 1988.' [31.7s]; Agent: 'And your date of birth is July 4, 2000 for demo purposes.' [54.1s]-[56.6s]; Patient later: 'Actually, my date of birth is February 14th, 1980.' [60.2s].
- Recommendation: Ask the patient to confirm their correct DOB (explicitly reconcile the conflicting values), correct the record, and verbally confirm the updated DOB back to the patient before proceeding.

## 17. Agent appears to have created or used the wrong patient profile (demo profile) and therefore could not find the caller's actual October 13 appointment.

- Call: `call-007`
- Scenario: `rescheduling`
- Category: `state_management_error`
- Confidence: `0.94`
- Evidence: "Your patient profile is set up... for demo purposes." Later the agent reports only a September 8 appointment in records and repeatedly states there is no October 13 appointment: "There isn't an appointment listed for October 13th at 2 p.m."
- Recommendation: Verify patient identity with multiple match points (full name, DOB, phone number) before searching or creating profiles; avoid creating demo/test profiles during live calls. If multiple profiles are present, search across them and confirm with the patient before making changes.

## 18. The agent created a demo patient profile instead of looking up the existing patient record as the patient requested, risking duplicate records and unnecessary steps.

- Call: `call-003`
- Scenario: `appointment-scheduling`
- Category: `workflow_failure`
- Confidence: `0.93`
- Evidence: Patient: 'I'm an established patient. You can look me up by my date of birth, February 14th, 1988.' [28.0s]-[31.7s]; Agent: 'Your patient profile is set up.' [51.7s].
- Recommendation: When a caller states they are an established patient, attempt a lookup first. If lookup fails, ask clarifying identifiers (full name, DOB, phone number) before creating a new/demo profile and explain why a new profile is necessary.

## 19. Agent created a new 'demo' patient profile for an established patient, then relied on that profile which did not contain the caller's Thursday appointment, causing inability to locate the correct appointment.

- Call: `call-009`
- Scenario: `multi-intent`
- Category: `state_management_error`
- Confidence: `0.93`
- Evidence: Caller: "I'm already a patient." (18.8s) and "I'm already an established patient." (38.8s). Agent: repeatedly requests to create a demo profile and then: "Your patient profile is set up and your date of birth is July 4, 2000 for demo purposes." (62.8s–74.5s). Agent later: "The only upcoming appointment I see on file is for Tuesday... There are no Thursday appointments on file." (91.7s–98.5s, 190.1s–193.2s).
- Recommendation: Do not create duplicate/demo profiles for callers who state they are established patients. Instead, authenticate with identifying details (DOB, phone, last 4 of SSN) and search the master schedule across locations/providers before concluding no appointment exists.

## 20. Agent created a demo patient profile instead of locating or using the caller's existing chart, then proceeded with refill handling in a way that suggests the patient record was not reconciled.

- Call: `call-006`
- Scenario: `medication-refill`
- Category: `workflow_failure`
- Confidence: `0.92`
- Evidence: "Before I can help with your refill, would you like to create a demo patient profile?" ... "Let me finish setting up your demo patient profile... Your patient profile is set up and your date of birth is July 4, 2000."
- Recommendation: Search for and open the established patient's real chart before processing refill requests. If a new/demo profile is used, explicitly confirm with the caller whether this is the correct patient record and transfer any actions to the correct chart.

## 21. Agent confirmed an incorrect date of birth for the patient (false confirmation).

- Call: `call-007`
- Scenario: `rescheduling`
- Category: `false_confirmation`
- Confidence: `0.92`
- Evidence: "Your patient profile is set up and your date of birth is July 4th, 2000 for demo purposes." Patient: "No, that's not correct. My date of birth is June 9th, 1975." Agent: "I have your date of birth as July 4th, 2000. I'll make a note that you stated June 9th, 1975."
- Recommendation: Immediately correct the patient record when the caller provides the correct DOB (update system entry rather than just 'note' it) and read back the corrected DOB to confirm it was saved.

## 22. Agent failed to elicit or confirm key details about the Thursday appointment (exact date, provider, clinic location) despite the caller repeatedly insisting the appointment exists on Thursday at 10 AM, and repeatedly offered to reschedule the Tuesday appointment instead.

- Call: `call-009`
- Scenario: `multi-intent`
- Category: `clarification_failure`
- Confidence: `0.92`
- Evidence: Caller: "my appointment is actually on Thursday at 10 a.m. I need to reschedule that one..." (107.2s–108.0s). Agent: "The only upcoming appointment I see on file is for Tuesday, September 8th at 10 a.m.... Would you like to reschedule this appointment? If you have another appointment, please let me know any other details..." (116.4s–127.1s). Caller again: "The appointment I need to reschedule is on Thursday at 10 a.m. Let's reschedule that." (133.6s–138.6s). Agent never asks for the Thursday appointment's date/provider/location details to reconcile the mismatch.
- Recommendation: Ask for concrete identifying appointment details (exact Thursday date, provider name, clinic location, confirmation number) and search all schedules/locations. If still not found, escalate to live scheduling staff or offer a callback after a manual records search.

## 23. The agent failed to resolve conflicting DOB information provided by the patient (patient first gave 1988, later said 1980) and did not ask which was correct.

- Call: `call-003`
- Scenario: `appointment-scheduling`
- Category: `clarification_failure`
- Confidence: `0.91`
- Evidence: Patient first: 'February 14th, 1988.' [31.7s]. Later patient: 'Actually, my date of birth is February 14th, 1980.' [60.2s]. The agent did not ask for clarification and instead asserted an unrelated DOB [54.1s]-[56.6s].
- Recommendation: When a patient supplies inconsistent identity information, explicitly point out the inconsistency and ask them which value is correct before proceeding with record changes or scheduling.

## 24. The agent did not confirm the patient's stated preference (weekday mornings next week) or clarify which specific day/time would work.

- Call: `call-001`
- Scenario: `appointment-scheduling`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: Transcript contains only: "[0.0s] A: Thank you." — no questions or clarifications about preferred days/times are present.
- Recommendation: Ask the patient to confirm their preference ('Do weekday mornings next week still work for you? Which days are best?'), then offer concrete time slots.

## 25. The interaction was prematurely closed with a single brief utterance, providing a poor user experience and leaving the request unfulfilled.

- Call: `call-001`
- Scenario: `appointment-scheduling`
- Category: `conversation_quality`
- Confidence: `0.90`
- Evidence: Agent's sole utterance: "[0.0s] A: Thank you." — no follow-up, options, or confirmation were offered.
- Recommendation: Avoid closing the call until the appointment is confirmed; use closing language only after confirming the appointment date/time and next steps.

## 26. The agent did not verify or record known patient facts (e.g., date of birth) that are typically required for appointment booking and identity confirmation.

- Call: `call-001`
- Scenario: `appointment-scheduling`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Transcript contains only: "[0.0s] A: Thank you." — there is no verification of DOB (Feb 14, 1988) or other patient details.
- Recommendation: Confirm the patient's identity and relevant details (e.g., DOB) before scheduling, and record them in the appointment record.

## 27. The agent stated a specific DOB in the newly created profile that contradicts the patient's later correction, creating a false/misleading record.

- Call: `call-004`
- Scenario: `appointment-scheduling`
- Category: `false_confirmation`
- Confidence: `0.90`
- Evidence: Agent: "Your patient profile is set up and your date of birth is July 4, 2000 for demo purposes." [54.0s-57.3s]
Patient correction: "actually, my date of birth is February 14, 1988." [63.2s-66.5s]
- Recommendation: Avoid declaring patient demographic details as finalized until verified. If an initial value is used 'for demo purposes,' make that transient and confirm/correct it before using the profile to schedule care.

## 28. The agent created a patient profile with an incorrect date of birth and did not update or reconcile the record after the patient corrected it.

- Call: `call-004`
- Scenario: `appointment-scheduling`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Agent: "Your patient profile is set up and your date of birth is July 4, 2000 for demo purposes." [54.0s-57.3s]
Patient: "Actually, my date of birth is February 14, 1988." [63.2s-66.5s]
No subsequent acknowledgement or confirmation that the DOB was corrected appears before booking or at confirmation [117.5s-120.2s].
- Recommendation: When creating or accessing a patient profile, confirm key identifiers (full name and DOB). If the patient provides a correction, explicitly update the record and confirm the updated DOB aloud before proceeding to book the appointment.

## 29. Agent declined the caller's request to confirm the postal code on file and did not attempt alternate searches or clarifying questions to reconcile the mismatch.

- Call: `call-005`
- Scenario: `unusual-edge`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: Caller: "Can you confirm the postal code 93101 on file?" (C:64.0). Agent: "I do not have access to any patient profile for you yet, so I cannot confirm any postal code on file." (B:72.0).
- Recommendation: Agent should attempt searches using the DOB and postal code provided (Jan 5, 1990; 93101), ask clarifying questions (middle name, phone number), or escalate to a staff member who can access the full record. Do not refuse to re-check when the caller supplies additional identifiers.

## 30. Transfer to clinic support appears to fail or disconnect immediately; the agent did not confirm the transfer completed or provide a callback option, leaving the appointment request unresolved.

- Call: `call-005`
- Scenario: `unusual-edge`
- Category: `conversation_quality`
- Confidence: `0.90`
- Evidence: Agent: "I'll connect you to our clinic support team. Please stay on the line. Transferring you now." (B:99.0–103.0). Immediately after: Caller: "You've reached the Pretty Good AI test line. Goodbye." (C:106.4–108.7) and then "Goodbye." (C:112.3).
- Recommendation: Before transferring, confirm the destination and inform the caller. Verify the transfer completed (e.g., hold music followed by live voice) or collect a callback number and offer to call back if the transfer fails. Confirm the appointment or next steps before ending the call.

## 31. Agent pushed creating a new 'demo patient profile' instead of thoroughly searching for or verifying an existing chart, creating a high risk of duplicate records and failing to schedule the appointment.

- Call: `call-005`
- Scenario: `unusual-edge`
- Category: `workflow_failure`
- Confidence: `0.90`
- Evidence: "Would you like me to create a demo patient profile now so we can schedule your appointment?" (B:34.7); "If you would like to schedule an appointment, I need to create a demo patient profile first." (B:52.6). The caller explicitly said their profile should already exist (C:42.3).
- Recommendation: Agent should search using multiple identifiers (full name, DOB, postal code) and escalate to trained staff to resolve potential duplicates before creating any new profile. Only create new records after confirming no matching chart exists.

## 32. Agent accepted an automatically set/incorrect date of birth and did not correct or reconcile the demographic error after the caller stated it was wrong.

- Call: `call-006`
- Scenario: `medication-refill`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: "Your patient profile is set up and your date of birth is July 4, 2000.""Actually, that's not my birth date."
- Recommendation: When a caller indicates demographic information is wrong, stop and correct the record (confirm correct DOB) before proceeding with medication or clinical actions to avoid mismatches and privacy/errors.

## 33. Agent incorrectly asserted that there is no appointment on October 13 at 2:00 PM despite the caller's repeated, consistent statement of that appointment.

- Call: `call-007`
- Scenario: `rescheduling`
- Category: `factual_error`
- Confidence: `0.90`
- Evidence: Caller: "My original appointment is Tuesday, October 13th at 2 p.m." Agent: "There isn't an appointment listed for October 13th at 2 p.m." (repeated multiple times).
- Recommendation: If the system does not show an appointment the patient insists exists, escalate or perform a broader search (other clinic locations, provider schedules, canceled/alternate records) before telling the patient the appointment does not exist. Offer to place a hold or create a temporary reservation while investigating to avoid losing the original booking.

## 34. Agent refused to provide any billing/contact details without a patient profile, blocking the caller from an in-office verification route and forcing the caller to call their insurer even though other publicly-available office contact options may exist.

- Call: `call-008`
- Scenario: `insurance`
- Category: `workflow_failure`
- Confidence: `0.90`
- Evidence: "If you want to reach our billing office, you'll need to create a patient profile first so I can provide you with direct contact details or connect you." (99.6s-101.6s); "I'm not able to give out the billing office number without a patient profile." (126.2s-130.0s)
- Recommendation: Unless policy prohibits it, provide a public billing phone number, general office billing email, or a website link that lists contact info without requiring a patient profile. At minimum offer to transfer the caller to a general billing line or provide a number/website for them to call independently.

## 35. Agent promised to provide the fax number later in the call but did not provide it and did not confirm next steps before the call was disconnected/poorly transferred.

- Call: `call-009`
- Scenario: `multi-intent`
- Category: `conversation_quality`
- Confidence: `0.90`
- Evidence: Agent: "For medical records, I can provide the clinic's fax number after we finish with your appointment." (160.6s–165.3s). Caller: "And I still need the fax." (244.0s). End of transcript shows a transfer/misconnect and caller still asking: "and get the medical record" (263.2s).
- Recommendation: Provide critical single-piece information (clinic fax) immediately once the caller requests it if it does not depend on completing another step, or provide a clear transfer/hold/next-step confirmation before leaving the call.

## 36. Agent repeatedly insisted the only appointment on file was Tuesday (Sep 8) and did not reconcile the caller's repeated statement that the appointment was Thursday at 10 a.m., failing to locate or confirm the correct appointment to reschedule.

- Call: `call-011`
- Scenario: `multi-intent`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Agent: 'You have an appointment scheduled for Tuesday, September 8th at 10 a.m.' [93.5s-100.2s]. Caller: 'my appointment is actually on Thursday at 10 a.m., not Tuesday.' [105.5s][110.4s]. Agent: 'The only upcoming appointment I see on file is for Tuesday...' [114.7s][136.8s]. Caller persists: 'My appointment is on Thursday at 10 a.m. and I need to reschedule that.' [157.3s].
- Recommendation: Ask clarifying questions (confirm clinic/location, provider, DOB, or appointment confirmation number), search alternate scheduling records/systems, or escalate to clinic staff to locate the correct Thursday appointment before offering rescheduling options or transfers.

## 37. Agent used an incorrect clinician name ('Almond') after the patient clearly requested Dr. Ahmed, introducing inconsistent clinician identifiers that could confuse scheduling or downstream staff.

- Call: `call-012`
- Scenario: `context-correction`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Caller: "And also I need it to be with Dr. Ahmed, not Kelly Noble." (84.7-87.0)  Agent (correct at times): "To switch your appointment to Dr. Ahmed..." (91.2-93.0)  Later agent: "I still only see openings with Kelly Noble, M.D., not Dr. Almond," (154.6-158.4)  Agent again: "Would you like help from the clinic team to find a slot with Dr. Almond?" (160.0-167.6)
- Recommendation: Confirm and read back clinician names exactly as the patient states them; if unclear, spell the clinician name and verify system entries to avoid introducing a different name.

## 38. Agent initiated/treated the call as a demo/new-patient flow before confirming the caller was an established patient, which could lead to incorrect record handling.

- Call: `call-012`
- Scenario: `context-correction`
- Category: `workflow_failure`
- Confidence: `0.90`
- Evidence: Agent: "Would you like to create a demo patient profile?" (10.0)  Agent later: "Your patient profile is set up and your date of birth is July 4th, 2000 for demo purposes." (46.3)  Caller: "I'm actually an established patient and I'm calling to correct the reason for my upcoming appointment." (19.8-26.7)
- Recommendation: Ask or verify patient status (new vs. established) before initiating demo/new-patient flows; when a caller states they are established, switch immediately to record lookup/update workflow and confirm the existing appointment details.

## 39. Agent initially asserted an incorrect calendar date for the caller's phrase 'next Friday' instead of asking the caller to confirm which calendar date they meant, risking booking the wrong day if the caller had not corrected them.

- Call: `call-013`
- Scenario: `ambiguous-date`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: Caller: "I need to book an appointment for next Friday afternoon." (76.4s) Agent: "Next Friday, September 11th, would you like to book an afternoon slot on that day?" (123.4s) Caller then corrected the date to September 18th, 2026 (131.2s-132.9s).
- Recommendation: When a caller uses a relative date term (e.g., 'next Friday'), explicitly ask the caller to confirm the calendar date ("Do you mean Friday, September 18, 2026?") before offering slots or proposing a date to avoid potential mis-booking.

## 40. Agent failed to use available identifying information to verify identity and acted as if a new profile was the only option.

- Call: `call-014`
- Scenario: `cancellation`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: Caller gave name and specific appointment details: "I'm Robert Kim and I'm canceling my appointment with Dr. Singh on Monday, November 2nd at 1130 a.m." (35.8–39.5). Agent replied: "Since I can't access your records without a profile, I won't be able to cancel your appointment right now." (50.2–55.6). The agent did not ask for DOB (March 18, 1964) or other verification.
- Recommendation: Use standard alternate identity verification (DOB, phone, address, last four of SSN, etc.) instead of requiring account creation for simple actions like cancellations. If policy requires a profile, explain why and offer immediate alternatives (take request, transfer, or schedule staff callback).

## 41. Agent ended the interaction without addressing the customer's request or confirming next steps, leaving the caller mid-utterance.

- Call: `call-014`
- Scenario: `cancellation`
- Category: `conversation_quality`
- Confidence: `0.90`
- Evidence: Agent: "I won't be able to cancel your appointment right now. Have a great day." (50.2–55.6). Caller: "I need this exact appointment canceled. Can you get someone to" (58.5–60.8) — unresolved and cut off.
- Recommendation: Stay on the call until the caller's request is resolved or a clear escalation/next-step is documented and communicated (e.g., transfer, ticket created, callback scheduled).

## 42. Agent created a demo patient profile with an incorrect date of birth and did not acknowledge or update the record after the patient corrected it.

- Call: `call-015`
- Scenario: `weekend-scheduling`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Agent: 'Your patient profile has been created and your date of birth is listed as July 4th 2000 for demo purposes.' [47.8]. Patient: 'My date of birth is actually August 22, 1991.' [59.7-63.7]. There is no subsequent confirmation or update to the DOB in the transcript.
- Recommendation: Confirm the corrected DOB aloud, update the patient record immediately, and verbally confirm the update to the patient. If a demo profile was created in error, clarify and merge or recreate the correct established patient record.

## 43. Agent failed to ask follow‑up clarifying questions or address the caller's expressed interest in evening availability.

- Call: `call-016`
- Scenario: `office-hours`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: Caller expressed the request for hours and interest in hearing them (17.3s–20.2s), but agent gave no information about evening hours nor asked whether the caller meant weekday/evening/weekend hours.
- Recommendation: Ask a brief clarifying question (e.g., 'Do you mean weekday hours, weekend hours, or evening availability?') and then provide or look up the specific hours requested.

## 44. Agent acknowledged the caller's correction with 'I understand.' but took no corrective action—this is a confirmation without follow-through.

- Call: `call-017`
- Scenario: `interruption`
- Category: `false_confirmation`
- Confidence: `0.90`
- Evidence: "C: Actually, I need a dermatology appointment, not orthopedics." "B: I understand." ... no subsequent action to change specialty or schedule.
- Recommendation: Avoid simple acknowledgements without next steps. After confirming understanding, explicitly state the next action (e.g., 'I can transfer you to dermatology' or 'I will schedule a dermatology appointment; can I get your DOB and preferred times?').

## 45. System did not handle the interruption: the caller interrupted the initial name prompt to correct the specialty, but the system continued the orthopedics-oriented flow and did not preserve or act on the correction.

- Call: `call-017`
- Scenario: `interruption`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Agent: "I just need your first and last name to get started." Caller interrupts: "Actually, I need a dermatology appointment, not orthopedics." Agent continues with orthopedics-focused responses and does not switch flow.
- Recommendation: Implement interruption handling so that corrections to patient intent (e.g., specialty change) immediately interrupt and redirect the dialog flow. Persist the corrected intent in session state so subsequent prompts follow the updated specialty.

## 46. The agent did not collect essential refill details (pharmacy, how many tablets remain) needed to process the refill.

- Call: `call-018`
- Scenario: `medication-refill`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: After the patient provides medication and dose ("I need a refill for lisinopril, 10 milligrams once daily."), the agent replies that they don't see medications on chart and offers to connect to support without asking for pharmacy or pill count (lines 54.0s–73.1s).
- Recommendation: Ask for the patient's pharmacy name and phone number and how many pills remain, and verify prescription details before attempting to submit a refill.

## 47. A demo patient profile was created during the call (including a demo date of birth) without clearly confirming or tying it to the caller's actual records; caller's name was also handled inconsistently.

- Call: `call-018`
- Scenario: `medication-refill`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Agent: "Would you like to create a demo patient profile? I just need your first and last name to get started." Later: "Your patient profile has been created and your date of birth is set as July 4, 2000 for demo purposes." The agent also says "Thanks, Aisha." while the caller identified as "Ayesha Patel." (lines 7.1s–47.1s and 23.8s–24.2s).
- Recommendation: Do not create demo profiles during real patient calls. If creating or editing a record, explicitly confirm that the caller wants this, verify full name and DOB, and confirm which existing patient record (if any) will be used to process clinical requests.

## 48. Agent failed to clarify or collect sufficient information to locate the caller's claimed October 13 appointment (did not request confirmation number, alternate identifiers, or check future months thoroughly) and moved to transfer without resolving the mismatch.

- Call: `call-019`
- Scenario: `rescheduling`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: Caller repeatedly asserts the October 13, 2 p.m. appointment (102.0-108.2s, 154.8-161.9s). Agent never asks for a confirmation number or alternative identifiers, offers only to reschedule Sept appointments or transfer the caller (117.7-169.6s, 201.6-206.3s).
- Recommendation: Request the appointment confirmation number, clinic/location, provider name, or other identifiers; check appointment schedules beyond visible month or different systems; only transfer after documenting what was searched and why escalation is needed.

## 49. Agent falsely confirmed the caller's DOB (July 4, 2000) even though the caller later provided a different DOB (June 9, 1975).

- Call: `call-019`
- Scenario: `rescheduling`
- Category: `false_confirmation`
- Confidence: `0.90`
- Evidence: Agent: "Your patient profile ... date of birth is July 4, 2000" (57.5-60.8s). Caller corrects: "my date of birth is June 9, 1975." (66.6-69.2s).
- Recommendation: Acknowledge the correction, apologize for the mistake, update the record immediately, and re-check appointments after correcting the DOB.

## 50. Agent created or confirmed a patient profile with an incorrect date of birth and did not reconcile it with the patient's correction, indicating improper state handling of identity data.

- Call: `call-019`
- Scenario: `rescheduling`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Agent: "Your patient profile is set up and your date of birth is July 4, 2000, for demo purposes." (57.5-60.8s). Caller: "Actually, my date of birth is June 9, 1975." (66.6-69.2s).
- Recommendation: Do not finalize or rely on automatically-created/demo profiles without confirming critical identifiers. Promptly update the record when the caller corrects DOB and re-run appointment lookups using corrected DOB.

## 51. Agent's appointment data is inconsistent or contradicts the caller's account; agent repeatedly states no October 13 appointment exists and at one point makes a contradictory statement about an October 13 listing, indicating inconsistent state reporting.

- Call: `call-019`
- Scenario: `rescheduling`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Agent: "There isn't an appointment listed for October 13th." (117.7s). Later agent: "There is one listed for October 13th. Would you like to reschedule either the September 8th or the September 18th appointment..." (141.7s). Agent again: "I don't see an appointment for October 13th at 2 p.m." (161.9s).
- Recommendation: Ensure system queries are consistent and explain any discrepancies to the caller (e.g., different systems, view filters). If records disagree with caller, escalate to clinic/records staff and flag the account before making changes.

## 52. Agent could not add the patient to a weekend waitlist or check other clinics and did not offer a clear, supported alternative other than transferring to live support.

- Call: `call-020`
- Scenario: `weekend-scheduling`
- Category: `workflow_failure`
- Confidence: `0.90`
- Evidence: User asked: 'Is there a weekend waitlist I can join, or another clinic with weekend availability?' [178.2s]. Agent: 'I can't add you to a weekend wait list or check other clinics directly.' [185.0s] and offered transfer to live support at [189.3s].
- Recommendation: When automated tools lack functionality, agent should offer concrete alternatives: collect contact info to notify if a weekend opening appears or to escalate a formal request, offer to place the patient on a cancellation list if available, provide estimated timeframes for next weekend availability, or query other clinics via escalation so the patient leaves with a clear next step rather than only a transfer option.

## 53. Agent collected only the caller's name and did not verify required identity fields (date of birth or postal code) to ensure the correct chart was accessed.

- Call: `call-021`
- Scenario: `unusual-edge`
- Category: `clarification_failure`
- Confidence: `0.90`
- Evidence: Agent: 'I just need your first and last name to get started.' Caller: 'My name is Taylor Morgan.' There is no question or confirmation of DOB (Jan 5, 1990) or postal code (93101) in the transcript.
- Recommendation: Verify at least two identifiers (e.g., date of birth and postal code) before accessing or scheduling against a patient chart to avoid mixing records. For this patient ask: 'Can I please confirm your date of birth and zip/postal code?'

## 54. Agent refused to validate the caller as an established patient or search alternative identifiers and insisted on creating a new 'demo patient profile', risking duplicate records and blocking service.

- Call: `call-022`
- Scenario: `multi-intent`
- Category: `state_management_error`
- Confidence: `0.90`
- Evidence: Caller: 'I'm already an established patient. Could you check your system for my existing record?' (42.1s, 63.3s). Agent: 'I don't see an existing profile for you in the system yet... I'll need to create a demo patient profile.' (49.5s–56.2s) and later: 'Right now, I can only assist if we create a demo patient profile in this system.' (68.8s).
- Recommendation: If an established record isn't found, the agent should attempt other verification methods (DOB, phone, MRN) or escalate/transfer to staff who can access the production system, rather than forcing a duplicate demo profile.

## 55. Agent first said there were no medications on the chart that could be refilled, then later confirmed they had sent a refill request — a workflow contradiction that could confuse the patient about what action was actually taken and on which record.

- Call: `call-006`
- Scenario: `medication-refill`
- Category: `false_confirmation`
- Confidence: `0.88`
- Evidence: "I don't see any medications on your chart that I can refill right now." ... "I've sent your refill request for lisinopril ten milligram once daily to our clinic support team."
- Recommendation: If the agent cannot refill from the chart, they must clearly explain what alternative action they are taking (e.g., sending a message to clinician) and on which record. Resolve chart discrepancies first, or explicitly document that a message was sent and to whom/how it will be processed.

## 56. Agent made and relied on a system-generated claim about the patient's appointments (only a Tuesday appointment exists) without adequately reconciling the patient's repeated assertions to the contrary, creating a false confirmation that the Thursday appointment did not exist.

- Call: `call-009`
- Scenario: `multi-intent`
- Category: `false_confirmation`
- Confidence: `0.88`
- Evidence: Agent repeatedly: "I only see an appointment for Tuesday... There are no Thursday appointments on file." (116.4s–123.4s, 179.7s–185.8s). Caller insists otherwise: "I need to reschedule my Thursday 10 a.m. appointment... Please check again." (171.7s–175.8s).
- Recommendation: When system results conflict with patient assertions, explicitly acknowledge the mismatch, perform expanded searches (other locations/providers/time windows), and, if necessary, escalate to a human scheduler rather than insisting system view is definitive.

## 57. Agent gave blanket availability statements without offering specific next-available options, and provided inconsistent date ranges for availability when the caller asked for Monday afternoon or the next available afternoon opening.

- Call: `call-011`
- Scenario: `multi-intent`
- Category: `clarification_failure`
- Confidence: `0.88`
- Evidence: Caller: 'Let's go ahead and move it to Monday afternoon...' [161.9s]. Agent: 'There are no Monday afternoon openings between September 7th and October 8th.' [170.0s]. Caller: 'could you tell me what the next available afternoon opening is?' [187.3s-189.7s]. Agent: 'There are no afternoon openings available between September 5th and October 6th.' [195.9s].
- Recommendation: Provide specific next-available dates/times or offer to check the clinic schedule in real time. Avoid inconsistent date ranges; if none are available, provide the earliest concrete options or immediately offer transfer/escalation.

## 58. Agent initially indicated willingness to help but then stated they could not perform the cancellation, which is misleading.

- Call: `call-014`
- Scenario: `cancellation`
- Category: `false_confirmation`
- Confidence: `0.88`
- Evidence: Agent: "I can help with that." (23.7). Later: "Since I can't access your records without a profile, I won't be able to cancel your appointment right now." (50.2–55.6).
- Recommendation: Avoid promising actions before confirming capability. If there are constraints, state them up front and offer immediate next steps or alternatives.

## 59. Agent gave inconsistent information about the patient's record/appointments (initially said there was no profile, then created a demo profile, and later referenced an existing Friday appointment), which could mislead the patient about actual scheduling status.

- Call: `call-015`
- Scenario: `weekend-scheduling`
- Category: `state_management_error`
- Confidence: `0.88`
- Evidence: Agent: 'I don't see a patient profile for you yet.' [25.4] and later 'Your patient profile has been created...' [47.8]. Shortly after, Agent: 'You already have a follow-up appointment scheduled for Friday, September 18th at 2 p.m.' [88.0-93.2].
- Recommendation: Verify whether the appointment referenced is an existing real appointment or an example/demo. If an existing appointment exists, state how it was found and confirm with the patient. If not, avoid presenting demo data as real scheduling information.

## 60. Agent repeatedly offered to create a demo patient profile instead of addressing the caller's primary question.

- Call: `call-016`
- Scenario: `office-hours`
- Category: `workflow_failure`
- Confidence: `0.88`
- Evidence: Agent: "Would you like to create a demo patient profile? I'll just need your first and last name to get started." (10.1s–12.8s). Later: "I don't have the office hours handy, but I can help you with other questions or help you create a demo patient profile if you'd like." (24.0s–25.9s).
- Recommendation: Prioritize answering the caller's question. Only offer ancillary actions (like creating a demo profile) after the primary information request has been addressed or if the caller indicates interest.

## 61. Agent's closing remarks ('No problem... Have a great day.') implied the caller's needs were addressed when they had not been, creating a false impression of completion.

- Call: `call-021`
- Scenario: `unusual-edge`
- Category: `false_confirmation`
- Confidence: `0.88`
- Evidence: After the caller said they already have a profile, the agent responded 'No problem...' and then closed the call. The caller then says they were calling to book an appointment, indicating the need was not addressed.
- Recommendation: Avoid phrasing that implies task completion until the caller's request is explicitly handled. Use clarifying confirmation (e.g., 'I understand you already have a profile — are you calling to schedule an appointment now?') before closing.

## 62. Call was terminated/poorly transferred to an incorrect/automated test line, preventing resolution.

- Call: `call-009`
- Scenario: `multi-intent`
- Category: `other_meaningful_issue`
- Confidence: `0.87`
- Evidence: "Trace ringing out. Thank you." (250.8s) then an automated/test line: "you've reached the pretty good AI test line." (253.6s–254.3s). Caller: "I think we got disconnected." (261.5s).
- Recommendation: Review transfer procedures and systems to ensure live-support transfers go to appropriate endpoints and that callers can be reconnected promptly. Offer an immediate callback or queue position if a transfer fails.

## 63. Agent did not explicitly explain that submitting a refill request is not the same as clinically approving or authorizing a new prescription, nor did they outline possible outcomes or expected timeframe in detail.

- Call: `call-006`
- Scenario: `medication-refill`
- Category: `clarification_failure`
- Confidence: `0.86`
- Evidence: "I've sent your refill request... They will review it and get back to you as soon as they can." (no explicit statement that review may result in approval, denial, or need for clinician input)
- Recommendation: Explicitly tell the caller that a refill request will be reviewed by clinical staff, that submission does not guarantee approval, outline possible outcomes (approved, denied, or requires clinician follow-up), and give an expected timeframe or how the patient will be notified.

## 64. Agent failed to pursue or offer reasonable alternatives to a weekend appointment when weekends were unavailable (no escalation, no referral, no after-hours/telehealth offer, and no waitlist beyond a flat 'none').

- Call: `call-015`
- Scenario: `weekend-scheduling`
- Category: `clarification_failure`
- Confidence: `0.86`
- Evidence: Patient: 'I can do Saturdays or Sundays only.' [83.6]. Patient: 'Do you have a waitlist or maybe an affiliated weekend clinic I could try?' [106.2]. Agent: 'We don't have a weekend waitlist or an affiliated clinic for weekend appointments. All visits are scheduled Monday through Friday.' [112.1-117.0]. The agent did not propose other options (e.g., telehealth, evening hours, referral to weekend provider, escalation) or offer to check multiple locations/providers.
- Recommendation: When a patient's availability cannot be met, proactively offer and document best-supported alternatives: check for telemedicine, evening hours, cross-site availability, referrals to weekend clinics, or place the patient on a waiting list/notification list if openings appear. If none exist, offer to escalate to a scheduler or supervisor who can check broader options and follow up.

## 65. Agent transferred the call without confirming that the caller's requests were resolved or explaining what would happen next, leaving the caller without a clear outcome.

- Call: `call-022`
- Scenario: `multi-intent`
- Category: `conversation_quality`
- Confidence: `0.86`
- Evidence: Caller: 'Could you help find my record or transfer me?' (112.3s). Agent: 'Transferring you now.' (117.0s). After transfer the exchange ends with no confirmation of reschedule or fax number being provided (117.0s–126.8s).
- Recommendation: Before transferring, the agent should summarize what has/has not been done, explain what the receiving party will handle, and, if possible, provide interim assistance (e.g., the fax number) so the caller is not left without any resolution if the transfer fails.

## 66. Agent's handling increases the chance of creating duplicate patient records, which violates the requirement to avoid using or creating duplicate patient information.

- Call: `call-005`
- Scenario: `unusual-edge`
- Category: `scope_policy_problem`
- Confidence: `0.85`
- Evidence: Agent repeatedly offered to create a 'demo patient profile' rather than resolving the existing profile: "Would you like me to create a demo patient profile now so we can schedule your appointment?" (B:34.7); "I need to create a demo patient profile first." (B:52.6).
- Recommendation: Implement and follow a policy that requires verification of multiple unique identifiers and escalation to staff before creating any new patient records. Train agents to avoid 'demo' profile creation when an existing chart is suspected.

## 67. Agent did not clarify why the system record differed from the caller's stated appointment (no explanation or troubleshooting steps were offered).

- Call: `call-007`
- Scenario: `rescheduling`
- Category: `clarification_failure`
- Confidence: `0.85`
- Evidence: Caller asks multiple times to 'double check the schedule' for October 13th; agent repeatedly responds that only a September 8 appointment is in records and offers transfer, but does not explain search scope or next diagnostic steps: "I only see an appointment for Tuesday, September 8th... There isn't an appointment listed for October 13th at 2 p.m. Would you like me to connect you to the clinic team so they can look into your October appointment?"
- Recommendation: Explain what was searched (locations, providers, cancelled appointments) and run additional checks (alternate records, date ranges) while informing the caller of steps being taken. This reduces confusion and demonstrates due diligence before transferring.

## 68. Agent advised the caller to call their insurance provider but did not offer guidance or the insurer's contact information or where to find it, adding friction for the caller to verify network status independently.

- Call: `call-008`
- Scenario: `insurance`
- Category: `workflow_failure`
- Confidence: `0.85`
- Evidence: "you can also call your insurance provider and ask if Pivot Point Orthopedics is in network for your Blue Shield PPO Silver 70 plan." (66.8s-67.9s); caller: "How do I call or contact your billing office to verify this?" (86.2s) — agent did not provide insurer contact or other guidance.
- Recommendation: Provide clear instructions for finding insurer contact details (e.g., insurer's member services phone number on the back of the card, insurer website) or offer to look up the insurer contact while on the call. If allowed, offer to provide a direct line for the practice's billing team or a website page with billing/contact info.

## 69. Agent created a 'demo patient profile' and assigned a date of birth without establishing why it was necessary or confirming the DOB with the caller, despite the caller stating they are an established patient.

- Call: `call-011`
- Scenario: `multi-intent`
- Category: `other_meaningful_issue`
- Confidence: `0.85`
- Evidence: Caller: 'I'm actually already a patient.' [18.1s]. Agent repeatedly asks to create a demo profile: 'Before we continue, would you like to create a demo patient profile?' [32.2s]; 'To assist you, I'll need to create a demo patient profile for this system.' [49.5s]. Agent asserts: 'Your patient profile is set up and your date of birth is July 4, 2000 for demo purposes.' [68.4s-74.3s], although the caller did not provide a DOB earlier.
- Recommendation: Respect the patient's stated established status. If a demo profile is required, explain why, obtain explicit consent, and confirm any personal data (like DOB) with the patient rather than assigning values arbitrarily.

## 70. Agent never explicitly confirmed that the appointment reason on the patient's existing scheduled appointment was updated in the system; the agent only stated they had notified the clinic team to find a slot with Dr. Ahmed and noted the required reason to that team, leaving ambiguity about whether the existing appointment's reason was changed.

- Call: `call-012`
- Scenario: `context-correction`
- Category: `clarification_failure`
- Confidence: `0.85`
- Evidence: After patient agrees to update reason: "Would you like me to update the reason for this appointment to a follow-up for blood pressure management?" Patient: "Yes, please." (76.6-84.7)  No explicit 'updated' confirmation appears; final statement: "I've let the clinic team know you need a follow-up appointment with Dr. Ahmed for blood pressure management. They'll reach out as soon as they find an opening that works for you." (185.7-194.5)
- Recommendation: When a caller requests a reason change, explicitly confirm the system update (e.g., 'I've updated the appointment reason in your record to "Follow-up: blood pressure management" for the existing appointment') or state clearly when only a notification to clinic staff was made and what follow-up the patient should expect.

## 71. Agent confirmed the booked appointment as being with a provider name that was not among the providers listed earlier and was not chosen by the caller, which risks assigning the wrong clinician without caller consent.

- Call: `call-013`
- Scenario: `ambiguous-date`
- Category: `false_confirmation`
- Confidence: `0.85`
- Evidence: Agent earlier offered: "Would you like to see Judy Houser, Carl Mintz, P.T., or Kelly Noble, M.D., or do you have a preference?" (107.0s-111.7s). Caller: "I don't have a preference." (116.7s). At confirmation the agent said: "Your follow-up appointment is set for Friday, September 18th at 2 p.m. with Doothy Hauser at Pivot Point Orthopedics." (158.2s) — 'Doothy Hauser' differs from the previously listed names and the caller did not confirm a provider.
- Recommendation: If a provider must be assigned when the caller has no preference, explicitly tell the caller which provider you are assigning and confirm acceptance ("I'll assign you to Judy Houser—does that work?") before finalizing the appointment.

## 72. Agent enforced account/profile creation as a precondition for canceling an appointment; this creates an unnecessary barrier for a routine request.

- Call: `call-014`
- Scenario: `cancellation`
- Category: `scope_policy_problem`
- Confidence: `0.85`
- Evidence: Agent repeatedly pushed profile creation: "To access your records, you'll need a Devo patient profile." (25.2–29.1). "Since I can't access your records without a profile... I won't be able to cancel your appointment right now." (50.2–55.6).
- Recommendation: Revise policy or agent training so routine actions (like cancellations) can be performed after appropriate phone verification, or ensure agents can escalate to staff who can perform such actions without forcing profile creation.

## 73. Agent did not provide any emergency/after‑hours instructions or explicitly separate normal hours from emergency coverage.

- Call: `call-016`
- Scenario: `office-hours`
- Category: `other_meaningful_issue`
- Confidence: `0.85`
- Evidence: No mention of emergency contact or after‑hours instructions in the entire interaction; agent only referred the caller to a QR code or in‑person staff (24.0s–42.8s).
- Recommendation: When giving hours (or when unable to provide them immediately), explicitly state normal office hours and then provide emergency/after‑hours instructions (e.g., contact number for urgent issues, hospital directions, or on‑call service) so callers know what to do outside normal hours.

## 74. Agent states it cannot transfer or schedule dermatology and simply instructs the caller to contact dermatology directly, without providing referrals or any actionable assistance.

- Call: `call-017`
- Scenario: `interruption`
- Category: `scope_policy_problem`
- Confidence: `0.85`
- Evidence: "I don't have access to dermatology scheduling or transfers." "You'll need to reach out to a dermatology clinic directly for an appointment."
- Recommendation: If the system cannot perform transfers, it should at minimum provide helpful alternatives: a list of recommended dermatology clinics (with phone numbers or links), offer to take the caller's details for a callback, or provide next steps for scheduling. This improves customer experience and meets the caller's request more helpfully.

## 75. Agent mis-stated the caller's name and repeated/abandoned sentences, producing a confusing interaction.

- Call: `call-018`
- Scenario: `medication-refill`
- Category: `conversation_quality`
- Confidence: `0.85`
- Evidence: Caller: "My name is Ayesha Patel." Agent: "Thanks, Aisha." (lines 20.2s–24.2s). Agent repeats and trails off: "If you'd like to speak with someone about this," (lines 68.7s–87.2s).
- Recommendation: Confirm the caller's name by repeating it back for verification. Avoid repeating partial sentences and ensure complete, clear prompts or actions (e.g., confirm transfer before proceeding).

## 76. Agent did not resolve the caller's issue and gave repeated, unhelpful responses (denying the caller's appointment without adequate verification), resulting in an unresolved transfer and poor caller experience.

- Call: `call-019`
- Scenario: `rescheduling`
- Category: `conversation_quality`
- Confidence: `0.85`
- Evidence: Caller insists: "my appointment is Tuesday, October 13th at 2 p.m. That's the one I need to reschedule." (128.3-130.9s). Agent repeatedly replies it does not exist and offers a transfer (136.5-169.6s), then transfers without resolving the discrepancy (201.6-218.8s).
- Recommendation: Improve agent troubleshooting and empathy: acknowledge caller's certainty, explain what was checked, and outline next steps (e.g., hold while searching extended schedules or escalate to a records specialist) before transferring.

## 77. Agent's schedule-search statement is ambiguous/truncated and does not clearly communicate the date range searched for weekend openings.

- Call: `call-020`
- Scenario: `weekend-scheduling`
- Category: `clarification_failure`
- Confidence: `0.85`
- Evidence: Agent: 'There are no weekend openings between September.' [165.8s] followed moments later by 'There are no weekend openings.' [171.5s]. The phrasing is unclear about the search window (e.g., 'between September'—between what dates?).
- Recommendation: State clearly which date range and locations were searched (e.g., 'I searched weekends from Sept 1 through Nov 30 and found no openings at this clinic'). If the search is limited, offer to expand the search or specify next available weekend dates.

## 78. Agent repeatedly assured the caller they could help, but never performed the promised actions.

- Call: `call-022`
- Scenario: `multi-intent`
- Category: `false_confirmation`
- Confidence: `0.85`
- Evidence: Agent: 'I can help with both.' (27.3s); 'Once that's set up, I can help with rescheduling and provide the fax number.' (73.1s). Despite these assurances, no scheduling or fax number was provided before transfer (117.0s).
- Recommendation: Avoid promising help unless the agent has a clear path to fulfill the request during the call; if assistance requires steps the caller will not accept (e.g., creating a demo profile), the agent should state limitations clearly and offer immediate alternative actions (direct transfer, supervisor, or provide the fax number if accessible without profile creation).

## 79. The agent repeatedly attempted to create a (demo) patient profile even after the caller stated they were an established patient; the agent did not offer or document searching existing records or verifying identity prior to creating a demo record.

- Call: `call-004`
- Scenario: `appointment-scheduling`
- Category: `workflow_failure`
- Confidence: `0.80`
- Evidence: Caller: "Actually, I'm an established patient already. My name is Maya Chen." [27.9s-30.9s]
Agent: "I don't see a patient profile for you yet. Would you like to create a demo patient profile now so I can look up appointment options for you? I just need your first and last name." [36.1s-43.6s]
- Recommendation: If the caller says they are an established patient, attempt to locate the existing record (ask for DOB, phone, or patient ID) before creating a new/demo profile; if no match is found, clearly explain why a new/demo profile is necessary and confirm all demographics before booking.

## 80. Agent stated they "cannot check your insurance directly in our system" without a profile and did not attempt to clarify whether a general network check by plan name (without member ID) could be performed, nor did they ask for available plan/member details that might allow a limited check.

- Call: `call-008`
- Scenario: `insurance`
- Category: `clarification_failure`
- Confidence: `0.80`
- Evidence: "Since you do not have a patient profile yet, I cannot check your insurance directly in our system." (50.9s-56.0s); "Usually, we verify if a specific insurance plan is in network by checking your details in our system after you create a patient profile." (150.5s-158.6s)
- Recommendation: Ask whether the caller can provide relevant plan details (e.g., member ID, group number, full plan name) or whether the caller wants a general check of whether the practice accepts the plan type. If policy prevents checking without a profile, explicitly explain why (e.g., need member ID to confirm benefits) so the caller understands the limitation.

## 81. Agent persisted with an incorrect appointment record instead of escalating sooner; the call devolved into transfer without fulfilling the caller's main requests.

- Call: `call-011`
- Scenario: `multi-intent`
- Category: `conversation_quality`
- Confidence: `0.80`
- Evidence: Agent repeatedly returns to the Tuesday appointment record despite the caller's repeated corrections about a Thursday appointment [93.5s-140.8s], then offers transfer as fallback [176.6s][203.3s][210.8s], and transfers before delivering the fax number [221.9s].
- Recommendation: When records and the patient's report disagree, clarify and escalate promptly. Prioritize completing simple fulfillments (like giving a fax number) before transferring and ensure the transfer target will handle unresolved scheduling conflicts.

## 82. Agent asserted a specific date of birth for the patient without the patient having provided it, potentially creating incorrect personal data in the record.

- Call: `call-011`
- Scenario: `multi-intent`
- Category: `false_confirmation`
- Confidence: `0.80`
- Evidence: Agent: 'Your patient profile is set up and your date of birth is July 4, 2000 for demo purposes.' [68.4s-74.3s]. There is no prior patient-provided DOB in the transcript.
- Recommendation: Do not state or confirm personal data unless the patient has provided it or it has been verified in existing records. Ask the patient to confirm DOB instead of assigning one.

## 83. Caller stated they were an existing patient, but the agent proceeded to create a demo patient profile without addressing why the existing record wasn't found or offering to verify/merge records. This can create duplicate records and impede continuity of care.

- Call: `call-013`
- Scenario: `ambiguous-date`
- Category: `state_management_error`
- Confidence: `0.80`
- Evidence: Caller: "I'm an existing patient. My name is Noah Williams." (16.7s-18.6s) Agent: "I don't see a patient profile for you yet. Would you like to create a demo patient profile now?" and later: "Your patient profile has been created..." (24.2s-28.8s; 67.1s).
- Recommendation: When a caller says they are an existing patient but no profile is found, ask identifying details (e.g., date of birth, phone number, or patient ID) to attempt to locate or reconcile the existing record before creating a new/demo profile.

## 84. Agent's handling lacked empathy and actionable support: after the patient reiterated inability to do weekdays the agent offered only 'call us if your schedule changes' and did not outline next steps or offer follow-up assistance.

- Call: `call-015`
- Scenario: `weekend-scheduling`
- Category: `conversation_quality`
- Confidence: `0.80`
- Evidence: Patient: 'I really can't do weekdays.' [104.0-106.2]. Patient: 'I can't do weekdays at all... So if there's no weekend option, I'll have to figure something else out.' [127.1-132.9]. Agent: 'If your schedule changes or you need help in the future, feel free to call us.' [136.4-141.1].
- Recommendation: Acknowledge the constraint explicitly ('I understand this is difficult') and offer to take a concrete next step (e.g., add the patient to a contact list for cancellations, escalate to check other sites/providers, offer a return call once research is done). Ensure the patient leaves with a clear next step or documented refusal of further assistance.

## 85. The agent offered to create a 'demo patient profile' during what appears to be a real clinical refill request, which is inappropriate and may confuse the patient's expectations about whether a real clinical action will occur.

- Call: `call-018`
- Scenario: `medication-refill`
- Category: `scope_policy_problem`
- Confidence: `0.80`
- Evidence: Agent asks twice about creating a demo profile: "Would you like to create a demo patient profile?" and later: "I just need your last name to complete it." Then: "Your patient profile has been created and your date of birth is set as July 4, 2000 for demo purposes." (lines 7.1s–32.8s and 40.9s–47.1s).
- Recommendation: Separate demo/test workflows from production triage. Do not use demo profiles when handling actual patient refill requests; instead, access the patient's real chart or instruct the patient on proper channels if this call is a demo.

## 86. Agent incorrectly confirmed the patient's last name ('Shaw') instead of the user's stated 'Shah', producing a false confirmation that could lead to mis-identification.

- Call: `call-020`
- Scenario: `weekend-scheduling`
- Category: `false_confirmation`
- Confidence: `0.80`
- Evidence: Agent: 'Can I confirm your first name is Priya and your last name is Shaw?' [54.9s]. User corrected: 'My first name is Priya and my last name is Shah.' [61.1s].
- Recommendation: Read back and ask the patient to spell uncommon or easily-misheard names, and explicitly confirm any corrections before creating or modifying records.
