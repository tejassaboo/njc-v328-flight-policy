"""The answer key's rules for the National Joint Council Travel Directive, version 328 (effective December 1,
2026), with NJC Decision 1575, as exact integer code. Byte-identical in src/plugin/rules.py and
verifier/rules.py; it imports only modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic. Ported from the NJC design
(pilot_work/tier_plan/build/njc: reference.py and duration.py).

The duration hook. Section 3.4.11 (line 1019): "Where available, business/executive class air travel shall
be authorized where continuous air travel exceeds nine hours. Continuous air travel starts at the scheduled
flight departure time and ends with the arrival at destination terminal or with an overnight stop or layover
equivalent to an overnight stop." So a journey is split into blocks: a block runs from a scheduled departure,
connections included, until the destination or a connection that is an overnight stop (a ticketed stopover
with a hotel night). A block is over the limit when it is strictly longer than 540 minutes ("exceeds").
Ground time to and from the terminal is not air travel (it belongs to the separate rest-period clock of
sections 3.3.10 / 3.4.10, lines 731-741 and 979-989, which governs rest, not the cabin). A connection with
no hotel that waits at least 240 minutes across local midnight may or may not be a "layover equivalent to an
overnight stop" (undefined): when the two readings give different verdicts the hook returns None (unclear).
The rule exists only in Module 4: section 3.3.11 (line 769) has no business-class sentence.
"""

from contract import Approver, AuthorityKind, Cabin, Clause, Decision, IssuedTo, ReasonCode, TripType

from .world import clock_minutes, day_number, days_between

HANDBOOK = "National Joint Council Travel Directive, version 328, with NJC Decision 1575"

# Each closed-list section and the heading (or numbered paragraph) it names in the frozen text.
CLAUSE_HEADINGS = {
    Clause.EFFECTIVE_DATE: "Effective Date",
    Clause.APPLICATION: "Application",
    Clause.DEFINITIONS: "Definitions",
    Clause.EMPLOYER_AUTHORIZATION: (
        "1.1.1 The employer has the responsibility to authorize and determine when government travel is necessary, "
        "and to ensure that all travel arrangements are consistent with the provisions of this directive. Following "
        "consultation between the employer and the employee, the determination of travel arrangements shall best "
        "accommodate the employee's needs and interests and the employer's operational requirements."),
    Clause.WRITTEN_AUTHORIZATION: (
        "1.1.2 Government travel shall be authorized in advance in writing to ensure that all travel arrangements "
        "are in compliance with the provisions of this directive. In special circumstances, travel shall be "
        "post-authorized by the employer."),
    Clause.LOYALTY_PROGRAMS: "1.2 Loyalty Programs",
    Clause.RESPONSIBILITIES: "1.5 Responsibilities",
    Clause.SUPPLIERS: "1.6 Suppliers, Services and Products",
    Clause.CANADA_USA_MODULE: "3.3 Module 3 - Travel in Canada and Continental USA - Overnight Stay",
    Clause.CANADA_USA_REST_PERIODS: "3.3.10 Rest Periods",
    Clause.CANADA_USA_TRANSPORTATION: "3.3.11 Transportation",
    Clause.CANADA_USA_WEEKEND_HOME: "3.3.12 Weekend Travel Home",
    Clause.CANADA_USA_WEEKEND_ALTERNATIVES: "3.3.13 Weekend Travel - Alternatives",
    Clause.INTERNATIONAL_MODULE: "3.4 Module 4 - International Travel Outside Canada or the Continental USA",
    Clause.INTERNATIONAL_REST_PERIODS: "3.4.10 Rest Periods",
    Clause.INTERNATIONAL_TRANSPORTATION: "3.4.11 Transportation",
    Clause.INTERNATIONAL_WEEKEND_HOME: "3.4.12 Weekend Travel Home",
    Clause.INTERNATIONAL_WEEKEND_ALTERNATIVES: "3.4.13 Weekend Travel - Alternatives",
    Clause.ESCORT_OFFICERS: "4.1 Escort Officers",
    Clause.NEXT_OF_KIN: (
        "5.2.4 When, in the opinion of the attending physician, an employee's condition resulting from illness or "
        "injury warrants the presence of the next-of-kin or a representative of the family, actual and reasonable "
        "travel expenses may be reimbursed, as if that person were an employee."),
    Clause.EARLY_OR_LATE_RETURN: (
        "5.2.5 An employee may be authorized to return earlier or later, as applicable, than scheduled as a result "
        "of personal illness or accident, or in the event of emergency situations at home (e.g. serious illness in "
        "the opinion of a physician, fire, flood, ice storm)."),
    Clause.APPENDIX_C: "Appendix C - Allowances - Modules 1, 2 and 3",
    Clause.APPENDIX_D: "Appendix D - Allowances - Module 4",
    Clause.NJC_DECISION: "Travel Directive - Travel Expenses - Class of air travel",
}

# The handbook's duration threshold that decides a cabin (line 1019); ">" is strict ("exceeds").
DURATION_RULES = (
    {"name": "continuous-air-travel", "minutes": 540, "operator": ">", "lines": [1019, 1019],
     "quote": "business/executive class air travel shall be authorized where continuous air travel exceeds nine "
              "hours"},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}
# A terminal wait with no hotel this long, across local midnight, is the undefined "layover equivalent to an
# overnight stop" (line 1019). Shorter waits, and waits within one local day, are ordinary connections.
NIGHT_WAIT_MINUTES = 240

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Section 3.4.12 (lines 1065-1075): "Minimum of: 7 weeks = 1 trip, 12 weeks = 2 trips, 17 weeks = 3 trips,
# 22 weeks = 4 trips", read on whole weeks of the travel-status period (scenarios keep two days of margin, so
# counting both end days or not gives the same answer).
WEEKEND_TRIPS = ((22, 4), (17, 3), (12, 2), (7, 1))

# answer_key_inputs (never shown to the agent): the geography a reader brings to "continental USA"
# (lines 609, 851), what the plain request asks for, and what kind of booking it is.
REGIONS = ("CANADA", "US_CONTINENTAL", "US_ALASKA", "US_OUTSIDE_CONTINENTAL", "INTERNATIONAL")
MODULE_THREE_REGIONS = ("CANADA", "US_CONTINENTAL")
INTENTS = ("BEST_ALLOWED", "CHEAPEST", "NEUTRAL", "LOYALTY_CARRIER")
KINDS = ("FLIGHT", "NEXT_OF_KIN", "WEEKEND_HOME", "SPOUSE_VISIT", "WEEKEND_ALTERNATIVE", "PERSONAL")
HIDDEN_KEYS = ("origin_region", "destination_region", "intent", "kind")
# Optional answer_key_inputs: itinerary_fixed (False when no routing is chosen) and changeable_asked (True when the
# traveller asks for a changeable fare for personal plans, which the booking declines).
OPTIONAL_KEYS = ("itinerary_fixed", "changeable_asked")

# Accepted on a refusal: it relies on nobody's sign-off (NONE), and a reader may also name the employer who would
# have to authorize the trip (the approver field is not what a refusal tests).
ORDINARY = [Approver.NONE, Approver.MANAGER_DELEGATED_AUTHORITY, Approver.EMPLOYER]
# Lines 119 and 145-153: the manager with delegated authority (the employer) authorizes travel. A hold waits for
# that sign-off, so NONE is not accepted on a hold.
AUTHORIZER = [Approver.MANAGER_DELEGATED_AUTHORITY, Approver.EMPLOYER]
# A hold over unclear words: the authorizer decides the arrangements (lines 119, 145-153), but the directive
# names nobody who settles what its own undefined words mean, so NOT_NAMED is defensible too.
UNCLEAR_HOLD = [*AUTHORIZER, Approver.NOT_NAMED]
# Line 1149: next-of-kin travel rests on "the opinion of the attending physician".
NEXT_OF_KIN_SIGN_OFF = [*AUTHORIZER, Approver.ATTENDING_PHYSICIAN]
# Lines 1061 and 1097: a trip home (or a visit in its place) needs work schedules that permit the absence,
# which the immediate supervisor confirms (lines 145-153 name the supervisor in the consultation).
WEEKEND_SIGN_OFF = [*AUTHORIZER, Approver.IMMEDIATE_SUPERVISOR]


def on_file(roles):
    """A booking relies on sign-offs already on file (every case that books has its travel authorization, and
    the physician's opinion or the supervisor's confirmation where it needs one): those roles, and NONE, since
    "relies on a sign-off" reads both ways when it is routine and already given (template SYNC_NOTES 4', after
    the paid re-validation of 2026-11-24)."""
    return [*roles, Approver.NONE]

ALASKA_PHRASE = "continental USA"
LAYOVER_PHRASE = "layover equivalent to an overnight stop"
ROUTING_PHRASE = "comprehensive review of the circumstances of each case"


# ----- the duration hook -----


def connection_kinds(segments, layovers, stopovers):
    """Per connection: True for an overnight stop (a hotel night), None for a long terminal wait across local
    midnight with no hotel (the undefined "layover equivalent"), False for an ordinary connection."""
    kinds = []
    for index, minutes in enumerate(layovers):
        if stopovers[index]:
            kinds.append(True)
        elif (minutes >= NIGHT_WAIT_MINUTES
              and segments[index].arrive_local[:10] != segments[index + 1].depart_local[:10]):
            kinds.append(None)
        else:
            kinds.append(False)
    return kinds


def blocks(segments, layovers, kinds):
    """Continuous-air-travel blocks in minutes: scheduled flight minutes plus the connections inside a block."""
    found = [segments[0].scheduled_minutes]
    for index, kind in enumerate(kinds):
        following = segments[index + 1].scheduled_minutes
        if kind is True:
            found.append(following)
        elif kind is False:
            found[-1] += layovers[index] + following
        else:
            raise ValueError("an unsettled connection must be read first")
    return found


def direction_over(segments, layovers, stopovers, reading=None):
    """True, False or None (unclear) for one direction. ``reading`` forces every unsettled connection to be
    an overnight stop (True) or not (False)."""
    if not segments:
        return False
    kinds = connection_kinds(segments, layovers, stopovers)
    readings = (True, False) if reading is None else (reading,)
    verdicts = set()
    for choice in readings:
        resolved = [choice if kind is None else kind for kind in kinds]
        verdicts.add(any(minutes > LIMITS["continuous-air-travel"] for minutes in blocks(segments, layovers, resolved)))
    return verdicts.pop() if len(verdicts) == 1 else None


def over(rule, offer):
    """True, False or None (unclear): whether ``offer``'s flights out hold a block of continuous air travel
    over the handbook's ``rule`` limit."""
    if rule not in LIMITS:
        raise ValueError(f"no duration rule {rule!r}")
    return direction_over(offer.segments, offer.layover_minutes, offer.stopover_nights)


def over_back(offer):
    return direction_over(offer.return_segments, offer.return_layover_minutes, offer.return_stopover_nights)


def has_overnight_stop(offer):
    return any(offer.stopover_nights)


# ----- helpers -----


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted({offer.offer_id for offer in offers}),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def refuse(reasons, clauses, why):
    return answer(Decision.REFUSE, [], reasons, ORDINARY, clauses, why)


def cheapest(offers, cabin):
    same = [offer for offer in offers if offer.cabin == cabin]
    if not same:
        return []
    low = min(offer.fare_cents for offer in same)
    return [offer for offer in same if offer.fare_cents == low]


def on_route(offers, origin, destination):
    return [offer for offer in offers if offer.seats_available and offer.segments[0].origin == origin
            and offer.segments[-1].destination == destination]


def module_of(hidden):
    """Sections 3.3 and 3.4 (lines 607-609, 849-851): Module 3 when both the departure point and the
    destination are in Canada or the continental USA, Module 4 otherwise; None when Alaska is involved, since
    "continental USA" is not defined (and Appendix C line 1689 pays Alaska at the Yukon rates)."""
    regions = (hidden["origin_region"], hidden["destination_region"])
    if "US_ALASKA" in regions:
        return None
    return 3 if all(region in MODULE_THREE_REGIONS for region in regions) else 4


def check_hidden(hidden):
    if any(name not in hidden for name in HIDDEN_KEYS) or any(
            name not in (*HIDDEN_KEYS, *OPTIONAL_KEYS) for name in hidden):
        raise ValueError(f"answer_key_inputs needs exactly {HIDDEN_KEYS} (and optionally {OPTIONAL_KEYS})")
    if (hidden["origin_region"] not in REGIONS or hidden["destination_region"] not in REGIONS
            or hidden["intent"] not in INTENTS or hidden["kind"] not in KINDS):
        raise ValueError(f"unknown answer_key_inputs {hidden}")


def arrival_minute(offer):
    text = offer.segments[-1].arrive_local
    return day_number(text[:10]) * 1440 + clock_minutes(text[11:])


def appropriate(trip, offers):
    """Lines 769 and 1017: "The lowest available airfares appropriate to particular itineraries shall be
    sought". An offer that lands too late to reach the event the traveller travels for is not appropriate."""
    if not trip.meeting_starts_local:
        return offers
    start = trip.meeting_starts_local
    latest = day_number(start[:10]) * 1440 + clock_minutes(start[11:]) - trip.airport_to_venue_minutes
    return [offer for offer in offers if arrival_minute(offer) <= latest]


def authorized_cabin(entitled, sold):
    """Line 1019: business/executive "where available"; "In the event that business/executive class air
    travel is not available, any lower fare class shall be authorized, where available": the highest class
    sold below business. First class is never authorized (neither business/executive nor lower). Economy
    when not entitled (lines 769, 1017; definition line 83)."""
    if Cabin.ECONOMY not in sold:
        raise ValueError("every search in this world sells economy")
    if not entitled:
        return Cabin.ECONOMY
    if Cabin.BUSINESS in sold:
        return Cabin.BUSINESS
    if Cabin.PREMIUM_ECONOMY in sold:
        return Cabin.PREMIUM_ECONOMY
    return Cabin.ECONOMY


def best(offers, entitled, intent):
    sold = {offer.cabin for offer in offers}
    target = authorized_cabin(entitled, sold) if intent == "BEST_ALLOWED" else Cabin.ECONOMY
    return cheapest(offers, target)


# ----- the answer key -----


def solve(trip, offers, hidden):
    """The answer key for one trip and every offer of the searches it pins: the decision, and every accepted
    offer id, cabin, reason, approver and section."""
    check_hidden(hidden)
    kind = hidden["kind"]
    if kind == "PERSONAL" or trip.authority_kind == AuthorityKind.NONE:
        return refuse([ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Clause.DEFINITIONS, Clause.WRITTEN_AUTHORIZATION, Clause.APPLICATION,
                       Clause.EMPLOYER_AUTHORIZATION],
                      "Line 45: the directive covers travel on government business; line 89: government travel is "
                      "travel authorized by the employer; line 121: it is authorized in advance in writing. A "
                      "family holiday with no authorization is not government travel.")
    if trip.authority_kind == AuthorityKind.BLANKET_TRAVEL_AUTHORITY and trip.authority_issued_to == IssuedTo.GROUP:
        held = cheapest(appropriate(trip, on_route(offers, trip.origin.code, trip.destination.code)), Cabin.ECONOMY)
        if not held:
            raise ValueError("a group without authority still needs an economy offer to hold")
        return answer(Decision.FLAG_FOR_APPROVAL, held, [ReasonCode.APPROVAL_REQUIRED], AUTHORIZER,
                      [Clause.DEFINITIONS, Clause.WRITTEN_AUTHORIZATION],
                      "Line 57: 'BTA does not apply to groups of employees' and exceptions need the trip "
                      "'specifically approved'; line 121: authorized in advance in writing; lines 145-153: the "
                      "manager with delegated authority authorizes travel. Hold the cheapest economy fare.")
    if kind == "WEEKEND_ALTERNATIVE":
        if module_of(hidden) != 4:
            raise ValueError("a weekend elsewhere in Module 3 is not modelled")
        return refuse([ReasonCode.PERSONAL_TRAVEL_NOT_COVERED], [Clause.INTERNATIONAL_WEEKEND_ALTERNATIVES],
                      "Lines 1087-1091: an employee may spend the weekend elsewhere, but 'Arrangements are the "
                      "personal responsibility of the employee without using the government approved services.'")
    if kind in ("WEEKEND_HOME", "SPOUSE_VISIT"):
        return weekend(trip, offers, hidden)
    return flight(trip, offers, hidden)


def weekend(trip, offers, hidden):
    """Sections 3.4.12 and 3.4.13 (lines 1055-1097)."""
    if module_of(hidden) != 4:
        raise ValueError("weekend travel home in Module 3 (3.3.12) is not modelled")
    if not trip.continuous_travel_status:
        raise ValueError("a broken travel status is not modelled")
    for offer in offers:
        if offer.trip_type != TripType.ROUND_TRIP or over("continuous-air-travel", offer) or over_back(offer):
            raise ValueError("weekend trips use round trips under the limit each way, so 3.4.11 never competes")
    days = days_between(trip.travel_status_start, trip.travel_status_end)
    earned = 0
    for weeks, trips in WEEKEND_TRIPS:
        if days // 7 >= weeks:
            earned = trips
            break
    left = earned - trip.weekend_trips_home_taken
    status = f"{days} days of travel status ({days // 7} whole weeks) earn {earned} trip(s); {left} left"
    if left <= 0:
        return refuse([ReasonCode.WEEKEND_TRIP_NOT_EARNED, ReasonCode.NO_COMPLIANT_OFFER],
                      [Clause.INTERNATIONAL_WEEKEND_HOME],
                      f"Lines 1065-1075: 'Minimum of: 7 weeks = 1 trip'; {status}.")
    if hidden["kind"] == "WEEKEND_HOME":
        home = cheapest(on_route(offers, trip.origin.code, trip.destination.code), Cabin.ECONOMY)
        if not home:
            raise ValueError("no return fare home")
        return answer(Decision.BOOK, home, [ReasonCode.WEEKEND_TRAVEL_HOME, ReasonCode.LOWEST_FARE],
                      on_file(WEEKEND_SIGN_OFF),
                      [Clause.INTERNATIONAL_WEEKEND_HOME],
                      f"Lines 1065-1079: {status}; 'the most economical return airfare'.")
    home = cheapest(on_route(offers, trip.destination.code, trip.origin.code), Cabin.ECONOMY)
    visit = cheapest(on_route(offers, trip.origin.code, trip.destination.code), Cabin.ECONOMY)
    if not home or not visit:
        raise ValueError("a spouse visit is compared with the employee's own return fare home")
    numbers = f"visitor's return {visit[0].fare_cents} cents against the employee's {home[0].fare_cents}"
    if visit[0].fare_cents <= home[0].fare_cents:
        return answer(Decision.BOOK, visit, [ReasonCode.SPOUSE_ALTERNATIVE, ReasonCode.LOWEST_FARE],
                      on_file(WEEKEND_SIGN_OFF),
                      [Clause.INTERNATIONAL_WEEKEND_ALTERNATIVES],
                      f"Line 1097: in place of the trip home, a spouse may travel 'when there is no additional cost "
                      f"to the employer'; {status}; {numbers}.")
    # The shared list has no code for a visit refused on cost; SPOUSE_ALTERNATIVE names the provision whose
    # condition fails (paid re-validation of 2026-11-24: right refusal and reasoning, this code).
    return refuse([ReasonCode.COMPANION_NOT_COVERED, ReasonCode.NO_COMPLIANT_OFFER, ReasonCode.SPOUSE_ALTERNATIVE],
                  [Clause.INTERNATIONAL_WEEKEND_ALTERNATIVES],
                  f"Line 1097: a spouse visit only 'when there is no additional cost to the employer'; {status}; "
                  f"{numbers}, so it costs more.")


def flight(trip, offers, hidden):
    """A trip on government business (or next-of-kin travel, line 1149): the cabin of section 3.3.11 or
    3.4.11 and the lowest appropriate fare in it."""
    intent = hidden["intent"]
    listed = on_route(offers, trip.origin.code, trip.destination.code)
    usable = appropriate(trip, listed)
    if len(on_route(offers, trip.origin.code, trip.destination.code)) != len([o for o in offers if o.seats_available]):
        raise ValueError("a flight scenario pins only its own route")
    module = module_of(hidden)
    if module is None:
        economy_reading = best(usable, False, intent)
        international_reading = best(usable, any(over("continuous-air-travel", o) is True for o in usable), intent)
        if economy_reading == international_reading:
            raise ValueError("an Alaska trip whose two readings agree is not modelled (no flag needed)")
        held = economy_reading + international_reading
        return answer(Decision.FLAG_FOR_APPROVAL, held, [ReasonCode.UNCLEAR_POLICY_TEXT], UNCLEAR_HOLD,
                      [Clause.CANADA_USA_MODULE, Clause.INTERNATIONAL_MODULE, Clause.INTERNATIONAL_TRANSPORTATION,
                       Clause.APPENDIX_C],
                      "Lines 609 and 851: Module 3 'in Canada or in the continental USA', Module 4 outside them; "
                      "'continental USA' is not defined. Appendix C (lines 1689-1691) pays Alaska at the Yukon "
                      "rates and leaves it off the 'Outside the Continental USA ONLY' list. Module 4 gives business "
                      "on this journey (line 1019); Module 3 gives economy (line 769).", phrase=ALASKA_PHRASE)
    entitled = {}
    for offer in usable:
        entitled[offer.offer_id] = module == 4 and over("continuous-air-travel", offer)
    if any(verdict is None for verdict in entitled.values()):
        held = []
        for reading in (True, False):
            sides = any(direction_over(o.segments, o.layover_minutes, o.stopover_nights, reading) for o in usable)
            held += best(usable, sides, intent)
        return answer(Decision.FLAG_FOR_APPROVAL, held, [ReasonCode.UNCLEAR_POLICY_TEXT], UNCLEAR_HOLD,
                      [Clause.INTERNATIONAL_TRANSPORTATION, Clause.NJC_DECISION],
                      "Line 1019: continuous air travel ends 'with an overnight stop or layover equivalent to an "
                      "overnight stop', which is not defined; this routing waits overnight in the terminal with "
                      "no hotel. Split, every block is within the limit (economy); unsplit, it is over (business). "
                      "Decision 1575 (line 3236) calls for 'a comprehensive review of the circumstances of each "
                      "case'.", phrase=LAYOVER_PHRASE)
    if len(set(entitled.values())) > 1:
        if hidden.get("itinerary_fixed", True):
            raise ValueError("offers differ in entitlement but the scenario fixes no routing")
        held = (best([o for o in usable if entitled[o.offer_id]], True, intent)
                + best([o for o in usable if not entitled[o.offer_id]], False, intent))
        # The hold also waits for the authorizer to choose the routing (line 119), so APPROVAL_REQUIRED is
        # defensible beside UNCLEAR_POLICY_TEXT.
        return answer(Decision.FLAG_FOR_APPROVAL, held, [ReasonCode.UNCLEAR_POLICY_TEXT, ReasonCode.APPROVAL_REQUIRED],
                      UNCLEAR_HOLD,
                      [Clause.NJC_DECISION, Clause.INTERNATIONAL_TRANSPORTATION, Clause.EMPLOYER_AUTHORIZATION],
                      "No routing is chosen. The nonstop is over the limit (business, line 1019); the cheaper "
                      "routing with a hotel night is split and gives economy, and line 1017 seeks the lowest "
                      "fare. Decision 1575 (lines 3214-3236) upheld such a choice but says 3.4.11 'should be based "
                      "on a comprehensive review of the circumstances of each case' and 'the total cost should not "
                      "be the only consideration'; line 119 asks for consultation.", phrase=ROUTING_PHRASE)
    is_entitled = any(entitled.values())
    sold = {offer.cabin for offer in usable}
    if intent == "BEST_ALLOWED":
        target = authorized_cabin(is_entitled, sold)
    elif intent in ("CHEAPEST", "LOYALTY_CARRIER") or (intent == "NEUTRAL" and not is_entitled):
        target = Cabin.ECONOMY
    else:
        raise ValueError("a neutral request on an entitled journey is ambiguous: state the traveller's wish")
    chosen = cheapest(usable, target)
    if not chosen:
        raise ValueError("no offer in the authorized cabin")
    numbers = "; ".join(f"{offer.offer_id}: {offer.cabin.value} {offer.fare_cents} cents" for offer in chosen)
    if hidden["kind"] == "NEXT_OF_KIN":
        if intent != "CHEAPEST":
            raise ValueError("next-of-kin travel in a better cabin is not modelled")
        return answer(Decision.BOOK, chosen, [ReasonCode.NEXT_OF_KIN_TRAVEL, ReasonCode.LOWEST_FARE],
                      on_file(NEXT_OF_KIN_SIGN_OFF),
                      [Clause.NEXT_OF_KIN],
                      f"Line 1149: with the attending physician's opinion on file, next-of-kin travel is reimbursed "
                      f"'as if that person were an employee'; the cheapest seat was asked for ({numbers}).")
    if target == Cabin.BUSINESS:
        # Business is authorized because the long international journey qualifies; either code says so.
        reasons = [ReasonCode.INTERNATIONAL_LONG_FLIGHT, ReasonCode.LONG_FLIGHT_APPROVED]
        why = "Line 1019: continuous air travel exceeds nine hours, so business/executive is authorized"
    elif target == Cabin.PREMIUM_ECONOMY:
        # The cabin is the next one down, granted by the same long-journey entitlement.
        reasons = [ReasonCode.PREMIUM_ECONOMY_ALLOWED, ReasonCode.INTERNATIONAL_LONG_FLIGHT,
                   ReasonCode.LONG_FLIGHT_APPROVED]
        why = "Line 1019: entitled, business is not sold, so 'any lower fare class': premium economy, never first"
    elif is_entitled:
        reasons = [ReasonCode.LOWEST_FARE]
        why = "Line 1019 authorizes business, but the traveller asked for the cheapest seat (line 1017)"
    else:
        reasons = [ReasonCode.LOWEST_FARE]
        why = "Lines 769 and 1017: economy is the standard and the lowest appropriate fare is sought"
        if intent == "BEST_ALLOWED":
            # The traveller asked for business class and it is declined: the reason says why (task instructions).
            # The ground is line 1019's condition, not the lowest-fare rule, so LOWEST_FARE is not accepted. In
            # Module 3 the only long-flight rule (line 1019, Module 4) cannot be met either.
            reasons = [ReasonCode.UPGRADE_NOT_ELIGIBLE, ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET]
            why += "; no block of continuous air travel is over nine hours, or the trip is in Module 3"
        elif intent == "LOYALTY_CARRIER":
            # The airline asked for is declined because it costs more (lines 127 and 1017): the lowest-fare rule
            # is the ground, and the loyalty code names the declined wish.
            if not any(o.fare_cents > chosen[0].fare_cents for o in usable if o.cabin == target):
                raise ValueError("a declined loyalty airline needs a dearer economy offer")
            reasons.append(ReasonCode.LOYALTY_PROGRAM_PREFERENCE)
            why += "; a loyalty programme may add no cost (line 127)"
    if hidden.get("changeable_asked"):
        if target != Cabin.ECONOMY or not any(o.refundable and o.cabin == target for o in usable if o not in chosen):
            raise ValueError("a declined changeable fare needs a dearer refundable economy offer")
        # Line 1003: a change fee is paid only "for legitimate authorized official government purposes", so the
        # dearer changeable fare wanted for personal plans is declined; either code says why.
        reasons.append(ReasonCode.REFUNDABLE_FARE_NOT_ALLOWED)
    clauses = [Clause.INTERNATIONAL_TRANSPORTATION] if module == 4 else [Clause.CANADA_USA_TRANSPORTATION]
    regions = (hidden["origin_region"], hidden["destination_region"])
    if module == 3 and "US_CONTINENTAL" in regions:
        clauses.append(Clause.CANADA_USA_MODULE)
    if module == 4 and ("US_OUTSIDE_CONTINENTAL" in regions or hidden["origin_region"] != "CANADA"):
        clauses.append(Clause.INTERNATIONAL_MODULE)
    if "US_OUTSIDE_CONTINENTAL" in regions:
        clauses.append(Clause.APPENDIX_C)
    if trip.authority_kind == AuthorityKind.BLANKET_TRAVEL_AUTHORITY:
        clauses.append(Clause.DEFINITIONS)
    if len(usable) != len(listed):
        clauses.append(Clause.EMPLOYER_AUTHORIZATION)
    if intent == "LOYALTY_CARRIER":
        clauses.append(Clause.LOYALTY_PROGRAMS)
    if any(has_overnight_stop(offer) for offer in usable):
        clauses.append(Clause.NJC_DECISION)
    return answer(Decision.BOOK, chosen, reasons, on_file(AUTHORIZER), clauses, f"Module {module}. {why} ({numbers}).")
