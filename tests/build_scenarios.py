"""Writes the NJC v328 scenario JSON files by porting the finished NJC design (authoring aid; the JSON files
under src/plugin/data/scenarios are the source of truth once written).

    python3 tests/build_scenarios.py [path/to/pilot_work/tier_plan/build/njc]

The design (scenarios.json, RULES.md) is ported as it stands. What the port adds or changes is listed in
PORT_NOTES and in each scenario's design_notes: template field names, upper-case cabins, fares in CAD cents,
digit-free section codes, the shared reason list, local departure times for the flights the design left
untimed, and two plausibility fixes. The expected answers are written here from the design's key (not from
rules.solve); tests/test_scenarios.py requires them to equal what the rules compute.
"""

import hashlib
import json
import re
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
DESIGN = Path(sys.argv[1]) if len(sys.argv) > 1 else PLUGIN.parents[1] / "pilot_work" / "tier_plan" / "build" / "njc"
POLICY = (PLUGIN / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = PLUGIN / "src/plugin/data/scenarios"

CATEGORY = {"hidden_or_synonym": "hidden_clause"}
OVERLAY = {"dearer_option_correct": "dearer_option"}
REGION = {"CA": "CANADA", "INTL": "INTERNATIONAL"}
REASON = {
    "BUSINESS_LONG_JOURNEY": "INTERNATIONAL_LONG_FLIGHT", "LOWER_CLASS_BUSINESS_NOT_SOLD": "PREMIUM_ECONOMY_ALLOWED",
    "ECONOMY_STANDARD": "LOWEST_FARE", "TRAVELLER_CHOSE_LOWER_CLASS": "LOWEST_FARE",
    "WEEKEND_TRAVEL_HOME": "WEEKEND_TRAVEL_HOME", "SPOUSE_ALTERNATIVE": "SPOUSE_ALTERNATIVE",
    "NEXT_OF_KIN_TRAVEL": "NEXT_OF_KIN_TRAVEL", "WEEKEND_TRIP_NOT_EARNED": "WEEKEND_TRIP_NOT_EARNED",
    "NOT_GOVERNMENT_TRAVEL": "PERSONAL_TRAVEL_NOT_COVERED", "PERSONAL_ARRANGEMENT": "PERSONAL_TRAVEL_NOT_COVERED",
    "ADDITIONAL_COST_TO_EMPLOYER": "COMPANION_NOT_COVERED",
    "GROUP_NOT_COVERED_BY_BLANKET_AUTHORITY": "APPROVAL_REQUIRED", "UNCLEAR_CLAUSE": "UNCLEAR_POLICY_TEXT",
}
CLAUSE = {
    "Definitions": "DEFINITIONS", "Application": "APPLICATION", "1.1.1": "EMPLOYER_AUTHORIZATION",
    "1.1.2": "WRITTEN_AUTHORIZATION", "1.2.1": "LOYALTY_PROGRAMS", "3.3": "CANADA_USA_MODULE",
    "3.3.11": "CANADA_USA_TRANSPORTATION", "3.4": "INTERNATIONAL_MODULE", "3.4.11": "INTERNATIONAL_TRANSPORTATION",
    "3.4.12": "INTERNATIONAL_WEEKEND_HOME", "3.4.13": "INTERNATIONAL_WEEKEND_ALTERNATIVES", "5.2.4": "NEXT_OF_KIN",
    "Appendix C": "APPENDIX_C", "Decision 1575": "NJC_DECISION",
}

# Accept-set additions the template's shared reason list calls for (TEMPLATE_GUIDE 3.3: every value a careful
# reader could defend; coordinator, Thornton audit: the general code beside a specific one where a sibling
# scenario already accepts it, as granite-wren does with LOWEST_FARE).
BEST_NOT_ENTITLED_M4 = ["UPGRADE_NOT_ELIGIBLE", "LONG_FLIGHT_CONDITION_NOT_MET"]
EXTRA_REASONS = {
    "basin-loon": BEST_NOT_ENTITLED_M4, "cairn-thistle": BEST_NOT_ENTITLED_M4, "fern-gable": BEST_NOT_ENTITLED_M4,
    "fjord-clover": BEST_NOT_ENTITLED_M4, "ochre-marten": BEST_NOT_ENTITLED_M4, "quarry-tern": BEST_NOT_ENTITLED_M4,
    "wheat-bittern": ["UPGRADE_NOT_ELIGIBLE"],
    "kelp-lantern": ["LOWEST_FARE"], "dawn-trillium": ["LOWEST_FARE"],
    "harbour-sumac": ["NO_COMPLIANT_OFFER"], "yew-coulee": ["NO_COMPLIANT_OFFER"],
}

# Plugin audit (commit bb9df6c): further defensible codes. Business (and premium economy on an entitled journey)
# also accept LONG_FLIGHT_APPROVED, premium economy INTERNATIONAL_LONG_FLIGHT (line 1019); Module 3 best-seat
# economy also LONG_FLIGHT_CONDITION_NOT_MET; holds over unclear words also NOT_NAMED; next-of-kin travel also
# ATTENDING_PHYSICIAN (line 1149); weekend trips home and spouse visits that book also IMMEDIATE_SUPERVISOR
# (line 1061); the family-holiday refusal also OUTSIDE_POLICY_SCOPE and EMPLOYER_AUTHORIZATION (lines 45, 119).
LONG_APPROVED = ["LONG_FLIGHT_APPROVED"]
AUDIT_REASONS = {
    "arctic-lupine": ["OUTSIDE_POLICY_SCOPE"], "delta-moss": LONG_APPROVED, "glacier-vetch": LONG_APPROVED,
    "heath-sculpin": LONG_APPROVED, "jade-tamarack": LONG_APPROVED, "rapids-aster": LONG_APPROVED,
    "talus-cedar": LONG_APPROVED, "violet-muskeg": LONG_APPROVED,
    "esker-finch": ["INTERNATIONAL_LONG_FLIGHT", "LONG_FLIGHT_APPROVED"], "wheat-bittern": ["LONG_FLIGHT_CONDITION_NOT_MET"],
}
AUDIT_APPROVERS = {
    "boreal-quill": ["NOT_NAMED"], "iron-plover": ["NOT_NAMED"], "lichen-arch": ["NOT_NAMED"],
    "dawn-trillium": ["IMMEDIATE_SUPERVISOR"], "kelp-lantern": ["IMMEDIATE_SUPERVISOR"],
    "granite-wren": ["ATTENDING_PHYSICIAN"],
}
AUDIT_CLAUSES = {"arctic-lupine": ["EMPLOYER_AUTHORIZATION"]}

# Approver wording (template SYNC_NOTES 4', after the paid re-validation of 2026-11-24, superseding the earlier
# rule that dropped NONE from bookings): a BOOK or REFUSE whose sign-off is already on file accepts that role and
# NONE; a hold accepts only the awaited role(s), never NONE. Every case that books has its sign-offs on file (the
# travel authorization, and the physician's opinion or the supervisor's confirmation where needed), so every BOOK
# accept set holds NONE (as the design had it).

# Paid re-validation of 2026-11-24 (tests/REVALIDATION_NOTES.md): grader defects, each a code a careful reader could
# defend. iron-plover's hold also waits for the director to choose the routing (line 119); maple-osprey declines
# the changeable fare wanted for personal plans (line 1003); yew-coulee's visit is refused under the spouse
# provision, and the shared list has no code for a visit refused on cost (line 1097).
REVALIDATION_REASONS = {
    "iron-plover": ["APPROVAL_REQUIRED"], "maple-osprey": ["REFUNDABLE_FARE_NOT_ALLOWED"],
    "yew-coulee": ["SPOUSE_ALTERNATIVE"],
}
REVALIDATION_NOTES = {
    "iron-plover": ("Re-validation 2026-11-24: reason accept set widened with APPROVAL_REQUIRED (the hold waits for "
                    "the director's choice of routing, line 119)."),
    "maple-osprey": ("Re-validation 2026-11-24: reason accept set widened with REFUNDABLE_FARE_NOT_ALLOWED (the "
                     "changeable fare is declined, line 1003); answer_key_inputs changeable_asked."),
    "yew-coulee": ("Re-validation 2026-11-24: reason accept set widened with SPOUSE_ALTERNATIVE (the provision whose "
                   "no-additional-cost condition fails, line 1097)."),
}
HIDDEN_FIXES = {"maple-osprey": {"changeable_asked": True}}

# Weekend-home timing (paid validation: kelp-lantern and yew-coulee were answered on weeks elapsed by the trip
# date, the key counts the whole travel-status period). The dates move so that every reading of "Minimum of:
# 7 weeks = 1 trip" (lines 1065-1075) gives the same count: weeks of the whole period, weeks elapsed by the trip,
# and weeks counted from the directive's effective date (line 37, 2026-12-01; no date may precede it). The
# kelp-lantern / harbour-sumac pair flies home on Friday 2027-01-22 (was 2027-01-15, "mid-January"), so a
# travel status from 2026-12-01 has 52 days elapsed; dawn-trillium moves with its twin yew-coulee, so each pair
# still differs in one fact.
SHIFTED_HOME = {"depart_date": "2027-01-22", "return_date": "2027-01-24"}
TRIP_FIXES = {
    "kelp-lantern": {"travel_status_start": "2026-12-01", **SHIFTED_HOME},
    "harbour-sumac": SHIFTED_HOME,
    "yew-coulee": {"travel_status_start": "2026-12-14"},
    "dawn-trillium": {"travel_status_start": "2026-12-14"},
}
SEARCH_FIXES = {
    "kelp-lantern": {"employee_home": {"date": "2027-01-22", "return_date": "2027-01-24"}},
    "harbour-sumac": {"employee_home": {"date": "2027-01-22", "return_date": "2027-01-24"}},
}
REQUEST_FIXES = {"kelp-lantern": ("in mid-January", "in late January"),
                 "harbour-sumac": ("in mid-January", "in late January")}
KELP_HARBOUR = ("travel status 64 days, 2026-12-01 to 2027-02-03 (52 elapsed by the trip home on 2027-01-22), or "
                "45 days, 2026-12-14 to 2027-01-28 (39 elapsed)")
TWIN_FACTS = {"kelp-lantern": KELP_HARBOUR, "harbour-sumac": KELP_HARBOUR}
TIMING_NOTES = {
    "kelp-lantern": ("Port: travel status from 2026-12-01 (was 2026-12-14) and the trip home on 2027-01-22 (was "
                     "2027-01-15): 64 days in all (9 whole weeks), 52 elapsed by the trip (7 whole weeks), so one "
                     "trip is earned on every reading of lines 1065-1075."),
    "harbour-sumac": ("Port: the trip home on 2027-01-22 (was 2027-01-15), with its twin kelp-lantern: 45 days in "
                      "all and 39 elapsed, so no trip is earned on any reading of lines 1065-1075."),
    "yew-coulee": ("Port: travel status from 2026-12-14 (was 2027-01-04): 91 days in all (13 whole weeks, two "
                   "trips) and 60 by the visit (8 whole weeks, one trip), so a trip is available on every reading "
                   "and the visit is refused on cost alone (line 1097)."),
    "dawn-trillium": ("Port: travel status from 2026-12-14 (was 2027-01-04), with its twin yew-coulee: a trip is "
                      "available on every reading of lines 1065-1075, and the visit costs less than the trip home."),
}


UNCLEAR = {
    "boreal-quill": ("continental USA", [
        ("Alaska is not contiguous with the other states, so a trip there is outside 'the continental USA' "
        "(lines 609, 851): Module 4, and the 585-minute journey exceeds nine hours (line 1019): business."),
        ("Appendix C, titled 'Modules 1, 2 and 3', says 'Alaska follows the Yukon rates' (line 1689) and leaves "
        "Alaska off the 'Outside the Continental USA ONLY' list (line 1691): Module 3, which has no business "
        "sentence (line 769): economy.")]),
    "lichen-arch": ("layover equivalent to an overnight stop", [
        ("The 390-minute wait in the Frankfurt terminal across local midnight is a 'layover equivalent to an "
        "overnight stop' (line 1019): blocks of 460 and 505 minutes, neither over nine hours: economy."),
        ("No overnight stop is made (no hotel night), so continuous air travel runs 1,355 minutes from the first "
        "departure to Nairobi: business. Decision 1575 (line 3236) asks for a review of each case.")]),
    "iron-plover": ("comprehensive review of the circumstances of each case", [
        ("The lowest available airfare (line 1017) is the routing with a hotel night in London, split by the "
        "overnight stop into blocks within nine hours: economy, as Decision 1575 upheld."),
        ("Decision 1575 says 3.4.11 'should be based on a comprehensive review of the circumstances of each case' "
        "and 'the total cost should not be the only consideration'; with 1.1.1 consultation, the traveller's "
        "preferred nonstop (760 minutes) gives business.")]),
}
FLAG_TWINS = {
    "boreal-quill": ["wheat-bittern", "rapids-aster"], "lichen-arch": ["quarry-tern", "violet-muskeg"],
    "iron-plover": ["heath-sculpin", "quarry-tern"], "alder-fiddle": ["eastern-larch", "arctic-lupine"],
}

# Local departure times for the flights the design left untimed (the design pins times only where they
# decide the answer). Per scenario: carrier -> times of its first, second ... flight out, and of the flight
# back for round trips. Connections land and leave between 06:00 and 23:00 local on one date (world W4).
TIMES = {
    "delta-moss": {"BA": ["20:00"], "VS": ["21:30"]}, "fjord-clover": {"BA": ["20:00"], "VS": ["21:30"]},
    "granite-wren": {"BA": ["20:00"], "VS": ["21:00"]},
    "boreal-quill": {"AC": ["08:00"]}, "wheat-bittern": {"AC": ["07:00"], "WS": ["09:30"]},
    "iron-plover": {"EK": ["21:50"]},
    # The supervisor allows absence from Friday afternoon: the weekend flights home leave after lunch.
    "harbour-sumac": {"BA": ["15:00"], "VS": ["16:30"]}, "kelp-lantern": {"BA": ["15:00"], "VS": ["16:30"]},
}
RETURN_TIMES = {"BA": ["18:30"], "VS": ["19:45"], "AF": ["18:00", "20:30"], "LH": ["17:10", "19:40"]}
DEFAULT_OUT = ["08:15", "11:05", "13:40", "16:20"]
PORT_NOTES = {
    "granite-wren": "Port: the design's KQ economy via London is not plausible in the template world (KQ's only "
                    "hub is NBO, so YOW-LHR touches no KQ hub); that offer is flown by VS (hub LHR) at the same "
                    "fare. BA stays cheapest; no Canadian carrier sells the route (W3 holds).",
    "iron-plover": "Port: the design's London stop was 1475 minutes but its clock times (06:40 day 1 to 09:15 "
                   "day 2) are 1595 minutes apart; the clock times are kept, so the stop is 1595 minutes.",
}


def norm(text):
    return " ".join(text.split())


def rule_quotes():
    text = (DESIGN / "RULES.md").read_text(encoding="utf-8")
    found = {}
    for match in re.finditer(r"^### (R\d\d) (.*?) \(lines (\d+)-(\d+)\)\n\n> (.*)$", text, re.MULTILINE):
        found[match.group(1)] = {"topic": match.group(2), "quote": match.group(5)}
    return found


def keep(entry, quotes):
    a, b = entry["lines"]
    text = norm(" ".join(POLICY[a - 1:b]))
    digest = hashlib.sha256(text.encode()).hexdigest()
    assert digest == entry["sha256_words"], entry
    rule = quotes[entry["rule"]]
    assert norm(rule["quote"]) in text, rule
    return {"lines": [a, b], "sha256": digest, "quote": rule["quote"], "why": f"{entry['rule']} {rule['topic']}"}


def decision_keep():
    """Decision 1575 (design range 3214-3236) narrowed to the two paragraphs the answers rest on: the background
    (an itinerary divided by an overnight stop gives economy) and the Committee's decision. Lines 3218-3228
    hold the parties' presentations only (and the words "one day", "two days", which the number lint shares
    with the template's fixed text)."""
    made = []
    for line, quote, why in (
            (3214, ("As air travel time in the second itinerary was divided and therefore less than nine continuous "
                   "hours the employee would travel in economy class."), ("Decision 1575 background: an overnight "
                   "stop divides continuous air travel")),
            (3236, ("The Committee noted that the application of section 3.4.11 of the Directive should be based on "
                   "a comprehensive review of the circumstances of each case. Likewise, the total cost should not "
                   "be the only consideration when making arrangements."), "Decision 1575: the Committee's decision")):
        text = norm(POLICY[line - 1])
        assert norm(quote) in text
        made.append({"lines": [line, line], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote,
                     "why": why})
    return made


def trip_record(facts, design):
    traveller, auth = facts["traveller"], facts["authorization"]
    assignment = facts.get("assignment", {})
    visitor = facts.get("visitor", {})
    notes = [facts[name] for name in ("supervisor_note",) if name in facts]
    if "escorted_person_seat" in facts:
        notes.append(f"The escorted person's seat is {facts['escorted_person_seat']}.")
    loyalty = ["KLM"] if any(offer.get("carrier_role") == "traveller_loyalty_program"
                             for group in design["offer_constraints"]["groups"] for offer in group["offers"]) else []
    known = {"booking_date", "traveller", "purpose", "authorization", "origin", "destination", "depart_date",
             "return_date", "companions", "assignment", "visitor", "supervisor_note", "physician_opinion_on_file",
             "ground_minutes_to_departure_terminal", "ground_minutes_from_arrival_terminal", "rest_period_on_arrival",
             "escorted_person_seat", "meeting_starts_local", "airport_to_venue_minutes", "itinerary_note"}
    assert set(facts) <= known, set(facts) - known
    assert set(auth) <= {"kind", "issued_to", "by", "covers", "individual_trip_authority_on_file"}, auth
    assert not auth.get("individual_trip_authority_on_file", False)
    return {
        "traveller_title": traveller["title"],
        "traveller_kind": {"employee": "EMPLOYEE", "next_of_kin": "FAMILY_MEMBER"}[traveller["kind"]],
        "workplace": "" if traveller["kind"] != "employee" else traveller["workplace"],
        "companions": [f"{c['title']} ({c['workplace']})" for c in facts.get("companions", [])],
        "origin": facts["origin"]["airport"],
        "origin_state_or_province": facts["origin"].get("state_or_province", ""),
        "destination": facts["destination"]["airport"],
        "destination_state_or_province": facts["destination"].get("state_or_province", ""),
        "depart_date": facts["depart_date"], "return_date": facts["return_date"], "booking_date": facts["booking_date"],
        "purpose": facts["purpose"],
        "authority_kind": {"written_trip_authority": "WRITTEN_TRIP_AUTHORITY", "none": "NONE",
                           "blanket_travel_authority": "BLANKET_TRAVEL_AUTHORITY"}[auth["kind"]],
        "authority_issued_to": auth["issued_to"].upper(),
        "authority_given_by": auth["by"] or "",
        "authority_covers": auth.get("covers", ""),
        "assignment_location": assignment.get("location", ""),
        "travel_status_start": assignment.get("travel_status_start", ""),
        "travel_status_end": assignment.get("travel_status_end", ""),
        "continuous_travel_status": assignment.get("continuous_travel_status", False),
        "weekend_trips_home_taken": assignment.get("weekend_trips_home_taken", 0),
        "must_stay_at_duty_location": assignment.get("required_to_remain_at_duty_location", False),
        "visitor_relationship": visitor.get("relationship", ""),
        "visitor_home": visitor.get("home", ""),
        "physician_opinion": facts.get("physician_opinion_on_file", ""),
        "ground_minutes_to_departure_terminal": facts.get("ground_minutes_to_departure_terminal", 0),
        "ground_minutes_from_arrival_terminal": facts.get("ground_minutes_from_arrival_terminal", 0),
        "rest_period_on_arrival": facts.get("rest_period_on_arrival", ""),
        "meeting_starts_local": facts.get("meeting_starts_local", "").replace("T", " "),
        "airport_to_venue_minutes": facts.get("airport_to_venue_minutes", 0),
        "loyalty_programs": loyalty,
        "itinerary_note": facts.get("itinerary_note", ""),
        "other_notes": notes,
    }


def routing(offer):
    return (tuple((s["from"], s["to"], s["block_minutes"], s.get("depart_local")) for s in offer["segments"]),
            tuple((c["minutes"], c["hotel_night"]) for c in offer["connections"]))


def search(sid, group):
    """One template search from one design offer group: a flight spec per carrier and routing (a second
    flight for a second non-refundable fare in the same cabin), the offers in CAD cents."""
    flights, offers, made_flights, carriers = {}, [], [], []
    for offer in group["offers"]:
        carrier = "VS" if sid == "granite-wren" and offer["carrier"] == "KQ" else offer["carrier"]
        if carrier not in carriers:
            carriers.append(carrier)
        mine = [f for f in made_flights if f["carrier"] == carrier and f["routing"] == routing(offer)]
        home = None
        for candidate in mine:
            if offer["refundable"] or offer["cabin"] not in candidate["cabins"]:
                home = candidate
                break
        if home is None:
            count = len([f for f in made_flights if f["carrier"] == carrier])
            segments = offer["segments"]
            pinned = segments[0].get("depart_local")
            if pinned:
                depart = pinned
            elif carrier in TIMES.get(sid, {}):
                depart = TIMES[sid][carrier][count]
            else:
                depart = DEFAULT_OUT[(carriers.index(carrier) + count) % len(DEFAULT_OUT)]
            spec = {"carrier": carrier, "depart": depart, "minutes": [s["block_minutes"] for s in segments]}
            if len(segments) > 1:
                spec["via"] = [s["to"] for s in segments[:-1]]
                layovers = [c["minutes"] for c in offer["connections"]]
                if sid == "iron-plover" and layovers == [1475]:
                    layovers = [1595]
                spec["layovers"] = layovers
                if any(c["hotel_night"] for c in offer["connections"]):
                    spec["stopovers"] = [c["hotel_night"] for c in offer["connections"]]
            if group.get("return_date"):
                back = RETURN_TIMES[carrier]
                spec["return"] = {"depart": back[count % len(back)], "minutes": [group["return_block_minutes"]]}
            home = {"name": f"{carrier.lower()}-{count + 1}", "carrier": carrier, "routing": routing(offer),
                    "cabins": set()}
            made_flights.append(home)
            flights[home["name"]] = spec
        if not offer["refundable"]:
            home["cabins"].add(offer["cabin"])
        made = {"slot": offer["tag"], "flight": home["name"], "cabin": offer["cabin"].upper(),
                "fare_cents": offer["fare_cad"] * 100}
        if offer["refundable"]:
            made["refundable"] = True
        offers.append(made)
    return {"name": group["group"], "origin": group["from"], "destination": group["to"], "date": group["date"],
            "return_date": group.get("return_date", ""), "background": 0, "flights": flights, "offers": offers}


def expected(sid, design):
    exp = design["expected"]
    decision = exp["decision"]
    slots = exp["offer_tags"] if decision == "BOOK" else exp["hold_tags"]
    tags = {o["tag"]: o for g in design["offer_constraints"]["groups"] for o in g["offers"]}
    cabins = sorted({tags[slot]["cabin"].upper() for slot in slots}) or ["NONE"]
    reasons = sorted({REASON[code] for code in exp["reason_accept"]} | set(EXTRA_REASONS.get(sid, []))
                     | set(AUDIT_REASONS.get(sid, [])) | set(REVALIDATION_REASONS.get(sid, [])))
    approvers = set(exp["approver_accept"]) | set(AUDIT_APPROVERS.get(sid, []))
    if decision == "BOOK":
        approvers.add("NONE")
    else:
        assert decision == "REFUSE" or "NONE" not in approvers, sid
    approvers = sorted(approvers)
    clauses = sorted({CLAUSE[name] for name in exp["clause_accept"]} | set(AUDIT_CLAUSES.get(sid, [])))
    phrase = UNCLEAR[sid][0] if sid in UNCLEAR else ""
    return {"decision": decision, "offer_slots": sorted(slots), "cabins": cabins, "reason_codes": reasons,
            "approvers": approvers, "clauses": clauses, "unclear_phrase": phrase}


def main():
    data = json.loads((DESIGN / "scenarios.json").read_text(encoding="utf-8"))
    quotes = rule_quotes()
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.json"):
        old.unlink()
    for design in data["scenarios"]:
        sid = design["id"]
        category = "flag" if design["expected"]["decision"] == "FLAG_FOR_APPROVAL" else CATEGORY.get(
            design["category"], design["category"])
        hidden = {name: REGION.get(value, value) if name.endswith("region") else
                  (value.upper() if isinstance(value, str) else value)
                  for name, value in design["answer_key_inputs"].items()}
        if sid in UNCLEAR:
            note = {"phrase": UNCLEAR[sid][0], "readings": UNCLEAR[sid][1]}
        elif category == "flag":
            note = "none: the words are clear; the trip lacks an approval (a group cannot rely on a blanket authority)"
        else:
            note = "none"
        notes = f"Design {design['design_name']}. {design.get('note') or ''}".strip()
        if category != CATEGORY.get(design["category"], design["category"]):
            notes += (" Port: category hidden_or_synonym -> flag (the template files every FLAG decision under "
                      "flag; the 32-mix is then 3 hidden and 4 flags, as EDGE_CASES 5.2 gives).")
        if sid in PORT_NOTES:
            notes += " " + PORT_NOTES[sid]
        if any(entry["lines"] == [3214, 3236] for entry in design["must_keep"]):
            notes += " Port: must_keep Decision 1575 narrowed from lines 3214-3236 to 3214 and 3236."
        if sid in EXTRA_REASONS:
            notes += f" Port: reason accept set widened with {EXTRA_REASONS[sid]} (shared reason list)."
        if sid in TIMING_NOTES:
            notes += " " + TIMING_NOTES[sid]
        if sid in REVALIDATION_NOTES:
            notes += " " + REVALIDATION_NOTES[sid]
        hidden.update(HIDDEN_FIXES.get(sid, {}))
        trip = trip_record(design["trip_facts"], design)
        for name, value in TRIP_FIXES.get(sid, {}).items():
            assert name in trip, name
            trip[name] = value
        searches = [search(sid, group) for group in design["offer_constraints"]["groups"]]
        for made in searches:
            for name, value in SEARCH_FIXES.get(sid, {}).get(made["name"], {}).items():
                made[name] = value
        if not any(made["return_date"] for made in searches):
            # One ticket per case (template convention, paid validation 2026-11-24 and the UC G-28 audit): a case
            # whose ticket is one way gives no return date, which would invite a round-trip search; the return of
            # the trip is booked separately and no rule here reads it.
            trip["return_date"] = ""
        request = design["request"]
        if sid in REQUEST_FIXES:
            old, new = REQUEST_FIXES[sid]
            assert old in request, sid
            request = request.replace(old, new)
        must_keep = []
        for entry in design["must_keep"]:
            if entry["lines"] == [3214, 3236]:
                must_keep += decision_keep()
            else:
                must_keep.append(keep(entry, quotes))
        scenario = {
            "id": sid, "category": category,
            "overlays": [OVERLAY.get(tag, tag) for tag in design["overlays"]],
            "twin_of": design["twin_of"] or "", "twin_fact": TWIN_FACTS.get(sid, design.get("twin_diff") or ""),
            "flag_twins": FLAG_TWINS.get(sid, []), "ambiguity_note": note,
            "request": request, "trip": trip,
            "world": {"searches": searches},
            "expected": expected(sid, design),
            "must_keep": must_keep,
            "distractors": [], "design_notes": notes, "answer_key_inputs": hidden,
        }
        (OUT / f"{sid}.json").write_text(json.dumps(scenario, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(data['scenarios'])} scenarios to {OUT}")


if __name__ == "__main__":
    main()
