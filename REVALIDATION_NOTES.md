# NJC v328: paid re-validation of 2026-11-24 (evening)

Source: `efficient_corporate_travel_agent/pilot/ladder/runs/revalidation_2026-11-24/analysis.json`, key
`njc-v328-flight-policy@v2`. The run folders are under `njc-v328-flight-policy@v2/val_full/<scenario>/r1/`, and
`messages.json` in each holds the model's reasoning. The run had 27 runs, 3 valid and 24 failures. Line numbers
refer to `src/plugin/data/policy.txt`.

## The approver amendment (template SYNC_NOTES 4')

18 of the 24 failures had the approver `NONE` as their only wrong field. All of them are BOOKs whose sign-off was
already on file: basin-loon, cairn-thistle, cobalt-heron, dawn-trillium, delta-moss, eastern-larch, esker-finch,
fern-gable, fjord-clover, glacier-vetch, granite-wren, heath-sculpin, jade-tamarack, kelp-lantern,
rapids-aster, slate-yarrow, talus-cedar and wheat-bittern. Under rule 4', every BOOK now accepts `NONE` beside
the roles on file: `rules.on_file`, applied to `AUTHORIZER`, `NEXT_OF_KIN_SIGN_OFF` and `WEEKEND_SIGN_OFF` on
every BOOK. All 24 BOOK scenarios have their sign-offs on file: a written or blanket travel authority, plus the
physician's opinion for granite-wren and the supervisor's confirmation for kelp-lantern and dawn-trillium.

The other accept sets do not change:

- The holds (alder-fiddle, boreal-quill, iron-plover, lichen-arch) still accept only the awaited roles, and
  `NOT_NAMED` on the three holds over unclear words. None of them accepts `NONE`.
- The refusals (arctic-lupine, harbour-sumac, nettle-bramble, yew-coulee) already accepted `NONE` and the
  authorizer.

`MAX_PASS_ALWAYS_LOWEST` goes from 0 to 15. That is the 15 bookings whose right answer is the cheapest seat
listed. `MAX_PASS_ALWAYS_FLAG` stays at 3.

## Every failure not explained by the approver rule alone, classified

| scenario | category | submitted vs key | class | evidence | fix |
|---|---|---|---|---|---|
| alder-fiddle | flag | BOOK G5W4-WDNK, LOWEST_FARE, NONE, CANADA_USA_TRANSPORTATION; key FLAG / APPROVAL_REQUIRED / DEFINITIONS or WRITTEN_AUTHORIZATION | model slip | The record says `authority_kind` BLANKET_TRAVEL_AUTHORITY and `authority_issued_to` GROUP. The model reasoned "The blanket travel authority covers this trip, so no approval needed" and never weighed line 57, "BTA does not apply to groups of employees". It made the same miss in the first validation. It wondered whether "the case buys one ticket" fits three travellers, but settled that the sentence is about outbound against return, and that doubt did not change its decision. | none |
| boreal-quill | flag | BOOK LYZ7-JDEK BUSINESS, LONG_FLIGHT_APPROVED, NONE; key FLAG / UNCLEAR_POLICY_TEXT | model slip | It quoted Appendix C itself ("Alaska follows the Yukon rates", line 1689, and the "Outside the Continental USA ONLY" list, line 1691), then said "Anyway, for flight class determination" and took Module 4 (line 851) without flagging. The key's two readings (lines 609 and 851 against 1689-1691) are both in the frozen text. The model saw the conflict and did not treat it as open. | none |
| iron-plover | flag | FLAG 3DAG-V258 BUSINESS, **APPROVAL_REQUIRED**, MANAGER_DELEGATED_AUTHORITY, EMPLOYER_AUTHORIZATION; key UNCLEAR_POLICY_TEXT (decision, offer, approver and clause right) | **grader defect** | This is the second run in a row with this answer. The record's `itinerary_note` reads "The director has not yet chosen between the nonstop and the routing with a hotel night in London". So the ticket also waits for the director's sign-off on the routing (line 119, the employer determines arrangements after consultation), and the task instruction says FLAG covers both "someone's sign-off" and "the directive's words leave the answer open". The model reasoned "This routing decision is pending the director's sign-off". The key's own explanation cites line 119's consultation. The template's hold rules (answer.py) allow APPROVAL_REQUIRED beside UNCLEAR_POLICY_TEXT on a hold over unclear words. | Routing-hold branch of `rules.flight` accepts [UNCLEAR_POLICY_TEXT, APPROVAL_REQUIRED]. `build_scenarios.REVALIDATION_REASONS`. The id stays; the answer is still FLAG. |
| lichen-arch | flag | BOOK LDX8-X7KV ECONOMY, LONG_FLIGHT_CONDITION_NOT_MET, NONE; key FLAG / UNCLEAR_POLICY_TEXT | model slip | It read the 390-minute terminal wait across midnight straight as an "overnight stop" ("An overnight stop breaks continuous air travel"). It even noted "6.5 hours is not exactly overnight" and "no hotel is booked", but never asked whether a terminal wait is a "layover equivalent to an overnight stop" (line 1019, undefined), and it did not consider Decision 1575's "comprehensive review" (line 3236). The record states both facts that make the phrase open: an overnight connection and no hotel. Same miss as the first validation. | none |
| maple-osprey | distractor | BOOK T4JA-KDP2 ECONOMY (right), **REFUNDABLE_FARE_NOT_ALLOWED**, NONE; key LOWEST_FARE | **grader defect** (plus the approver) | The request asks for "a changeable ticket since I might stay on for a few days of holiday". The model booked the cheapest non-refundable economy fare and gave its reason as "A more expensive refundable fare would only be needed for the traveller's personal plans". That is the scenario's own design note: change fees are paid only "for legitimate authorized official government purposes" (line 1003), and the lowest appropriate fare is sought (line 1017). REFUNDABLE_FARE_NOT_ALLOWED is a shared code, not a decoy, and it names why the requested fare was declined. Thornton's kestrel-loom fix accepts the same kind of code for a rejected alternative. | `rules.flight` adds REFUNDABLE_FARE_NOT_ALLOWED when `answer_key_inputs.changeable_asked` is true. That key is new and optional (`OPTIONAL_KEYS`, never shown to the agent), and the rule raises ValueError unless a dearer refundable economy offer exists. Scenario JSON: reason accept set and answer_key_inputs. The id stays; the answer is still BOOK O1. |
| yew-coulee | refusal | REFUSE (right), **SPOUSE_ALTERNATIVE**, NONE, INTERNATIONAL_WEEKEND_ALTERNATIVES (right); key COMPANION_NOT_COVERED or NO_COMPLIANT_OFFER | **grader defect** | The reasoning is right throughout: one trip is earned on every reading (9 weeks in, line 1065-1075), and the visitor's $1,900 return costs more than the employee's own $1,240, so the visit fails "no additional cost to the employer" (line 1097). The model looked at COMPANION_NOT_COVERED and rejected it because "The spouse is not really a companion on the employee's trip; it's a spouse alternative", which is a fair reading: she travels alone as a visitor. The shared list has no code for a visit refused on cost. SPOUSE_ALTERNATIVE names the provision whose condition fails, and it lets no wrong reasoning pass: a not-earned refusal (WEEKEND_TRIP_NOT_EARNED, the first validation's error) still fails. | The spouse-visit refusal in `rules.weekend` accepts SPOUSE_ALTERNATIVE beside the two codes. `build_scenarios.REVALIDATION_REASONS`. The id stays; the answer is still REFUSE. |

No failure is a scenario defect. None needed a change to facts or wording, so the world is unchanged and
`tools/world_diff.py` was not needed (`world.py` is untouched, and no search or trip record changed). In 24 runs
the conversation passed the hosted cap (65,536 tokens) before step 4. Every one of those runs still submitted
with `stop_reason` "answer", so none is classed budget/cap.

## Scenario files changed

- Approver only (`NONE` added): basin-loon, cairn-thistle, cobalt-heron, dawn-trillium, delta-moss,
  eastern-larch, esker-finch, fern-gable, fjord-clover, glacier-vetch, granite-wren, heath-sculpin,
  jade-tamarack, kelp-lantern, ochre-marten, pine-cormorant, quarry-tern, rapids-aster, slate-yarrow,
  talus-cedar, upland-sorrel, violet-muskeg and wheat-bittern.
- maple-osprey: approver plus reason, and `changeable_asked` in answer_key_inputs.
- iron-plover: reason (APPROVAL_REQUIRED).
- yew-coulee: reason (SPOUSE_ALTERNATIVE).

Unchanged: alder-fiddle, arctic-lupine, boreal-quill, harbour-sumac, lichen-arch and nettle-bramble.

## Re-validate

The fixed reason sets can be re-checked with iron-plover, maple-osprey and yew-coulee (3 runs). The approver
change needs no run. Re-graded against the new accept sets, 21 of the 24 submitted answers pass as they
stand: the 18 approver-only failures plus iron-plover, maple-osprey and yew-coulee. The 3 that still fail are
the model slips (alder-fiddle, boreal-quill, lichen-arch).
