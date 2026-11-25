# Validation notes: njc-v328-flight-policy (paid wave 1 validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w1v3_2026-11-25/njc-v328-flight-policy@w1v3/`,
arm `full`, DeepSeek V4 Flash (Nebius fp8 pinned), temperature 0, max_steps 6, max_tokens 8192, one run per scenario,
at plugin head e6cc20f (after the approver rule 4' and the declined-request sentence). Line numbers are lines of
`src/plugin/data/policy.txt`.

## Results

27/32 valid (84.4%), **easy 6/6**. By category: boundary 7/8, distractor 3/3, easy 6/6, flag 0/4, hidden 3/3,
multi 5/5, refusal 3/3. No run errored; all 32 submitted. Re-scoring the stored submissions at this commit gives the
same **27/32**: no key changed.

The declined-request sentence did its job here: all seven declined-business bookings that lost `LOWEST_FARE` in
e6cc20f (basin-loon, cairn-thistle, fern-gable, fjord-clover, ochre-marten, quarry-tern, wheat-bittern) either passed
or failed on the offer, never on `LOWEST_FARE`. pine-cormorant passed.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| alder-fiddle | flag | BOOK economy G5W4-WDNK, LOWEST_FARE, clause CANADA_USA_TRANSPORTATION; key FLAG, APPROVAL_REQUIRED for EMPLOYER / MANAGER_DELEGATED_AUTHORITY | model slip | The record says `authority_kind: BLANKET_TRAVEL_AUTHORITY`, `authority_issued_to: GROUP`. The model: "The three travellers are covered by the group blanket travel authority. So the request is authorized." It never checked line 57, "BTA does not apply to groups of employees". Same slip as 2026-11-24. |
| boreal-quill | flag | BOOK business LYZ7-JDEK, INTERNATIONAL_LONG_FLIGHT; key FLAG, UNCLEAR_POLICY_TEXT | model slip | "Alaska is not part of the continental USA ... So Module 4 applies." That is the first reading, and the 585-minute arithmetic is right. It never opened Appendix C, which files Alaska with the Yukon rates under Modules 1-3 (line 1689) and leaves it off the "Outside the Continental USA ONLY" list (line 1691). Same slip as 2026-11-24. |
| fjord-clover | boundary_twin | BOOK business MLCB-3JQA, INTERNATIONAL_LONG_FLIGHT; key economy Z5PP-M97A, LONG_FLIGHT_CONDITION_NOT_MET / UPGRADE_NOT_ELIGIBLE | model slip (arithmetic) | Its reading of line 1019 is the key's: a 60-minute connection is not an overnight stop, so continuous air travel runs from first departure to arrival, layover included. It then subtracted local clock times across five time zones: "from departure 20:00 to arrival 10:00 = 14 hours". The offer lists `depart_utc 2026-12-15 01:00`, `arrive_utc 10:00` and `elapsed_minutes: 540`: exactly nine hours, which does not "exceed" nine hours. The twin delta-moss (61-minute layover, 541 minutes) keys business; the pair differs by one minute, by design. In boreal-quill the same run family converted to UTC correctly ("13:00 UTC ... 22:45 UTC"). |
| iron-plover | flag | BOOK business nonstop 3DAG-V258, INTERNATIONAL_LONG_FLIGHT; key FLAG, APPROVAL_REQUIRED / UNCLEAR_POLICY_TEXT | model slip | It read the record's note and named the hold: "The director has not yet chosen between the nonstop and the routing with a hotel night in London. This suggests the decision between itineraries is pending ... Should we flag for approval because the director hasn't chosen?" Then it took the traveller's preference as settling it. The routing is the director's to choose (line 119), and Decision 1575 (lines 3214, 3236) says the choice is reviewed case by case. |
| lichen-arch | flag | BOOK economy LDX8-X7KV, LONG_FLIGHT_CONDITION_NOT_MET; key FLAG, UNCLEAR_POLICY_TEXT | model slip (borderline: a weak flag) | "The itinerary note says connects in Frankfurt overnight. So yes, it's an overnight stop." It never weighed the rest of the same note ("no hotel is booked and the traveller waits in the terminal") or the offer's `stopover_nights: [false]`, which open the second reading of "layover equivalent to an overnight stop" (line 1019). Same answer as 2026-11-24. Economy is arguably the stronger reading of a 390-minute wait across midnight; if a re-run books economy again, consider converting the case to a BOOK under a new id. |

## Cross-plugin consistency (wave 2 follow-ups)

- **Long-flight codes:** every NJC business-on-a-long-flight key already accepts both `INTERNATIONAL_LONG_FLIGHT`
  and `LONG_FLIGHT_APPROVED` (delta-moss, violet-muskeg and the premium branch). Nothing to do.
- **Route codes:** no NJC scenario books a connection that declines a nonstop, and no key uses a route code
  (granite-wren's connection declines nothing). Nothing to do.

## Fixes

None. No rule, scenario, request or README row changed apart from this file and the README pointer to it. Nothing
was loosened for a slip.

## Q2

Unchanged: the always-cheapest agent passes **8/32 (25%)** (cobalt-heron, dawn-trillium, eastern-larch,
granite-wren, kelp-lantern, maple-osprey, pine-cormorant, upland-sorrel; `MAX_PASS_ALWAYS_LOWEST = 8`).

## Re-run

None required (no record or request changed). Optional variance check: lichen-arch (weak flag).

## Checks

`uv run pytest -q` (265 passed), `uv run ruff check .`, `uv lock --check`, `check_shared.py`,
`tools/stock_verify.py` (32 scenarios, 0 failures), stock `nanoagent plugin inspect .` (exit 0).
