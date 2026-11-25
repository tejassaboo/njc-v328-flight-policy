# NJC Travel Directive Flight Policy

**No affiliation with the National Joint Council.** The handbook is the NJC *Travel Directive*, version 328
(effective December 1, 2026), with NJC Decision 1575 (December 18, 2013), both public Government of Canada web
pages, bundled verbatim for research. Do not publish this plugin until it has passed validation (MASTER_PLAN
section 4). Crown copyright terms for redistribution have not been checked.

A `nanoagent.plugin/v0001` plugin. An agent handles one flight booking request under the real directive: it
reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and directive section. A deterministic Python
verifier, with no LLM, rebuilds the offers and the directive's answer itself and checks every field. Built from
the original-handbook template (`handbook_plugins/_template`), porting the NJC scenario design in
`pilot_work/tier_plan/build/njc` (`tests/build_scenarios.py` writes the scenario files from it).

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 18,988 words, 3,236 lines, sha256 `3859c4c8...a52b3da65`, equal to
`pilot_work/originals/njc-cabin-meal-allowance/frozen/SHA256SUMS`) is never paraphrased, and the task text
restates no rule. Under stock NanoAgent the agent does not see it: the plugin then runs as the `off` baseline.
The `harness.policy` switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds
it to the system prompt: `harness.policy: full` adds all of it, and the selection methods add parts of it. These
plugins are meant to run with `query: instructions+input`, so a selector sees the traveller's request.

**Size.** At 1.33 tokens a word (the long-handbook bench's calibration) the directive alone is about 25,300
tokens. Under `full` the first call carries about 29,600 input tokens (directive, task instructions about 190,
tool and submit schemas about 4,100 at 4 characters a token, the request), and later calls up to about 31,600 as
tool results accumulate. A run makes 3 calls (`get_trip`, `search_flights`, `submit`), or 4 for the two spouse
visits: about 90,000 input tokens per run (90,000 to 122,000; output tokens not counted). The hosted cap of
65,536 total tokens is crossed during the third call in every one of the 32 cases, so `full` cannot finish
hosted: run it locally with a raised cap.

## Task

- **Input:** `TaskInput`: `scenario` (one of 32 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on each route the decision needs (one search for most cases: the
  one-way fare out, and the trip record gives no return date since the return is booked separately; a trip home
  is one round-trip fare, and a spouse visit needs the visitor's round trip and the employee's own trip home), then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when
  refusing), `reason_code`, `approver` and `clause`, each from a closed list. The reason list is the template's
  shared list (codes for rules this directive lacks) plus `WEEKEND_TRAVEL_HOME`, `SPOUSE_ALTERNATIVE`,
  `NEXT_OF_KIN_TRAVEL` and `WEEKEND_TRIP_NOT_EARNED`, and decoy codes from other handbooks' rules. Fares are in cents of Canadian dollars (`currency: CAD`).
- **Success:** every field is one the answer key accepts. Score = fields right / 6.
- **Hidden facts** (`answer_key_inputs`, never shown by a tool): each trip's region (Canada, continental USA,
  Alaska, Hawaii, elsewhere), what the request asks for (business class if entitled, cheapest, no wish, a loyalty
  carrier) and the kind of booking. The agent works them out from the request, the airports and the directive.

| Scenario | Category | Expected decision (offer, cabin) | Reason | Approver | Clause (frozen lines) |
|---|---|---|---|---|---|
| `cobalt-heron` | easy | BOOK (O1; ECONOMY) | LOWEST_FARE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | CANADA_USA_MODULE or CANADA_USA_TRANSPORTATION (607-609, 769) |
| `eastern-larch` | easy | BOOK (O1; ECONOMY) | LOWEST_FARE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | CANADA_USA_TRANSPORTATION or DEFINITIONS (57, 607-609, 769) |
| `glacier-vetch` | easy | BOOK (O3; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1019) |
| `heath-sculpin` | easy | BOOK (O3; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1019) |
| `ochre-marten` | easy | BOOK (O1; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (83, 849-851, 1017, 1019) |
| `upland-sorrel` | easy | BOOK (O1; ECONOMY) | LOWEST_FARE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1017, 1019) |
| `cairn-thistle` | boundary_twin | BOOK (O1; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1017, 1019) |
| `delta-moss` | boundary_twin | BOOK (O3; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1019) |
| `fjord-clover` | boundary_twin | BOOK (O1; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1019, 1017, 979-989) |
| `harbour-sumac` | boundary_twin | REFUSE (none; NONE) | NO_COMPLIANT_OFFER or WEEKEND_TRIP_NOT_EARNED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_WEEKEND_HOME (849-851, 1057-1079) |
| `jade-tamarack` | boundary_twin | BOOK (O2; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1019) |
| `kelp-lantern` | boundary_twin | BOOK (O1; ECONOMY) | LOWEST_FARE or WEEKEND_TRAVEL_HOME | EMPLOYER or IMMEDIATE_SUPERVISOR or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_WEEKEND_HOME (849-851, 1057-1079) |
| `quarry-tern` | boundary_twin | BOOK (O1; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION or NJC_DECISION (849-851, 1017, 1019, 3214, 3236) |
| `violet-muskeg` | boundary_twin | BOOK (O2; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1019) |
| `dawn-trillium` | multi_rule | BOOK (S1; ECONOMY) | LOWEST_FARE or SPOUSE_ALTERNATIVE | EMPLOYER or IMMEDIATE_SUPERVISOR or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_WEEKEND_ALTERNATIVES (849-851, 1057-1079, 1095-1097) |
| `esker-finch` | multi_rule | BOOK (O3; PREMIUM_ECONOMY) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED or PREMIUM_ECONOMY_ALLOWED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (83, 849-851, 1019) |
| `pine-cormorant` | multi_rule | BOOK (O1; ECONOMY) | LOWEST_FARE or LOYALTY_PROGRAM_PREFERENCE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION or LOYALTY_PROGRAMS (127, 849-851, 1017) |
| `slate-yarrow` | multi_rule | BOOK (O2; ECONOMY) | LOWEST_FARE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | CANADA_USA_TRANSPORTATION or EMPLOYER_AUTHORIZATION (119, 607-609, 769) |
| `wheat-bittern` | multi_rule | BOOK (O1; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | CANADA_USA_MODULE or CANADA_USA_TRANSPORTATION (607-609, 769, 849-851, 1019) |
| `granite-wren` | hidden_clause | BOOK (O1; ECONOMY) | LOWEST_FARE or NEXT_OF_KIN_TRAVEL | ATTENDING_PHYSICIAN or EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | NEXT_OF_KIN (45, 849-851, 1149) |
| `rapids-aster` | hidden_clause | BOOK (O2; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | APPENDIX_C or INTERNATIONAL_MODULE or INTERNATIONAL_TRANSPORTATION (849-851, 1019, 1687-1691) |
| `talus-cedar` | hidden_clause | BOOK (O3; BUSINESS) | INTERNATIONAL_LONG_FLIGHT or LONG_FLIGHT_APPROVED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_MODULE or INTERNATIONAL_TRANSPORTATION (849-851, 1019) |
| `basin-loon` | distractor | BOOK (O1; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1017, 1019, 1101-1105) |
| `fern-gable` | distractor | BOOK (O1; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 979-989, 1017, 1019) |
| `maple-osprey` | distractor | BOOK (O1; ECONOMY) | LOWEST_FARE or REFUNDABLE_FARE_NOT_ALLOWED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_TRANSPORTATION (849-851, 1017, 1019, 1003) |
| `arctic-lupine` | refusal | REFUSE (none; NONE) | OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | APPLICATION or DEFINITIONS or EMPLOYER_AUTHORIZATION or WRITTEN_AUTHORIZATION (45, 89, 121) |
| `nettle-bramble` | refusal | REFUSE (none; NONE) | PERSONAL_TRAVEL_NOT_COVERED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_WEEKEND_ALTERNATIVES (849-851, 1083-1093) |
| `yew-coulee` | refusal | REFUSE (none; NONE) | COMPANION_NOT_COVERED or NO_COMPLIANT_OFFER or SPOUSE_ALTERNATIVE | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NONE | INTERNATIONAL_WEEKEND_ALTERNATIVES (849-851, 1057-1079, 1095-1097) |
| `alder-fiddle` | flag | FLAG_FOR_APPROVAL (O1; ECONOMY) | APPROVAL_REQUIRED | EMPLOYER or MANAGER_DELEGATED_AUTHORITY | DEFINITIONS or WRITTEN_AUTHORIZATION (57, 121, 145-153) |
| `boreal-quill` | flag | FLAG_FOR_APPROVAL (O1, O2; BUSINESS or ECONOMY) | UNCLEAR_POLICY_TEXT | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NOT_NAMED | APPENDIX_C or CANADA_USA_MODULE or INTERNATIONAL_MODULE or INTERNATIONAL_TRANSPORTATION (145-153, 607-609, 849-851, 1019, 1687-1691) |
| `iron-plover` | flag | FLAG_FOR_APPROVAL (O2, O3; BUSINESS or ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NOT_NAMED | EMPLOYER_AUTHORIZATION or INTERNATIONAL_TRANSPORTATION or NJC_DECISION (119, 145-153, 1017, 1019, 3214, 3236) |
| `lichen-arch` | flag | FLAG_FOR_APPROVAL (O1, O2; BUSINESS or ECONOMY) | UNCLEAR_POLICY_TEXT | EMPLOYER or MANAGER_DELEGATED_AUTHORITY or NOT_NAMED | INTERNATIONAL_TRANSPORTATION or NJC_DECISION (145-153, 849-851, 1019, 3214, 3236) |

Mix (EDGE_CASES.md 5.2, 32 row): 6 easy, 8 boundary twins, 5 multi-rule, 3 hidden clause, 3 distractor, 3
refusal, 4 flags (12.5%; the 15% cap is 4). Decisions: 24 BOOK (7 business, 1 premium economy, 16
economy), 4 REFUSE, 4 FLAG_FOR_APPROVAL. Unclear words are each one flag with clear
twins on both sides: "continental USA" for Alaska (`boreal-quill`; twins `wheat-bittern`, `rapids-aster`),
"layover equivalent to an overnight stop" (`lichen-arch`; twins `quarry-tern`, `violet-muskeg`) and Decision
1575's "comprehensive review of the circumstances of each case" when no routing is chosen (`iron-plover`; twins
`heath-sculpin`, `quarry-tern`). `alder-fiddle` is an approval-required hold (a blanket authority issued to a
group), never the same as "no compliant offer". The approver is the role whose sign-off the decision relies on,
on file or awaited. A booking relies on the travel authorization on file (lines 119, 145-153), so
`MANAGER_DELEGATED_AUTHORITY` and `EMPLOYER` are accepted (plus `ATTENDING_PHYSICIAN` for next-of-kin travel,
line 1149, and `IMMEDIATE_SUPERVISOR` where a weekend trip rests on the work schedule, line 1061); since that
sign-off is routine and already given, `NONE` is accepted too (template SYNC_NOTES 4', after the paid
re-validation of 2026-11-24). A refusal relies on no sign-off, so `NONE` is accepted beside those two. A hold
waits for a sign-off and never accepts `NONE`: it is the manager with delegated authority (lines 145-153) or the
employer, and on a hold over unclear words also `NOT_NAMED` (nobody is named to settle what the words mean).
A booking that declines what the traveller asked for gives the reason the request is declined (the task says so), and accepts `LOWEST_FARE` only where the lowest-fare rule is that reason.
The always-cheapest agent (approver `NONE`, reason `LOWEST_FARE`) passes 8 cases, the always-flag agent 3. The cabin is graded as
the chosen offer's own cabin. Re-validation findings: `tests/REVALIDATION_NOTES.md`;
paid validation of 2026-11-25: `tests/VALIDATION_NOTES.md`.

Duration (`rules.over`): continuous air travel from the first scheduled departure, connections included, cut
by an overnight stop (a ticketed stopover with a hotel night); strictly over 540 minutes ("exceeds nine
hours", line 1019); Module 4 only. A terminal wait of 240 minutes or more across local midnight with no hotel
is unsettled and returns `None` when the two readings disagree. Background offers are off for the whole
plugin (`background_offers: 0`): a filler connection could put a routing on the other side of 540 minutes.

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, route, dates, purpose, authorization, assignment, visitor, timings, notes | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date (one way, or round trip with `return_date`): the pinned scenario offers; no background offers in this plugin | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-njc-v328-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this directive's scenario ids, approvers, sections, reason
  codes and trip record.
- `src/plugin/`: `world.py`, `scenarios.py`, `guide.py`, `answer.py`, `tools.py` (shared), `rules.py` (this
  directive's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of the shared modules and `rules.py`, plus `booking.py` and `tools.py`.
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this directive's settings;
  `tests/test_njc_checks.py` the NJC checklist (dates, Module 4 only, one flag each for Alaska and the night
  wait, world constraints, request lint).
- `tests/build_scenarios.py`: ports the NJC design into the scenario files (an authoring aid, not a test).

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 ../_template/check_shared.py .
# from a NanoAgent checkout (read-only use):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/njc-v328-flight-policy.tar.gz
# from this folder, with that checkout's Python:
/path/to/nanoagent/nanoagent/.venv/bin/python ../_template/tools/stock_verify.py
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`, on or after
December 1, 2026).
