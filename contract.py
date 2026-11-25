"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-njc-v328-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    WEEKEND_TRAVEL_HOME = "WEEKEND_TRAVEL_HOME"
    SPOUSE_ALTERNATIVE = "SPOUSE_ALTERNATIVE"
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    WEEKEND_TRIP_NOT_EARNED = "WEEKEND_TRIP_NOT_EARNED"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    EXTENDED_TRAVEL_SAVINGS = "EXTENDED_TRAVEL_SAVINGS"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    AGENCY_EXEMPTION_NOT_MET = "AGENCY_EXEMPTION_NOT_MET"
    CANDIDATE_TRIP_NOT_COVERED = "CANDIDATE_TRIP_NOT_COVERED"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    SAME_CLASS_AS_CUSTOMER = "SAME_CLASS_AS_CUSTOMER"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: National Joint Council Travel Directive, version 328, with NJC Decision 1575.
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    ALDER_FIDDLE = "alder-fiddle"
    ARCTIC_LUPINE = "arctic-lupine"
    BASIN_LOON = "basin-loon"
    BOREAL_QUILL = "boreal-quill"
    CAIRN_THISTLE = "cairn-thistle"
    COBALT_HERON = "cobalt-heron"
    DAWN_TRILLIUM = "dawn-trillium"
    DELTA_MOSS = "delta-moss"
    EASTERN_LARCH = "eastern-larch"
    ESKER_FINCH = "esker-finch"
    FERN_GABLE = "fern-gable"
    FJORD_CLOVER = "fjord-clover"
    GLACIER_VETCH = "glacier-vetch"
    GRANITE_WREN = "granite-wren"
    HARBOUR_SUMAC = "harbour-sumac"
    HEATH_SCULPIN = "heath-sculpin"
    IRON_PLOVER = "iron-plover"
    JADE_TAMARACK = "jade-tamarack"
    KELP_LANTERN = "kelp-lantern"
    LICHEN_ARCH = "lichen-arch"
    MAPLE_OSPREY = "maple-osprey"
    NETTLE_BRAMBLE = "nettle-bramble"
    OCHRE_MARTEN = "ochre-marten"
    PINE_CORMORANT = "pine-cormorant"
    QUARRY_TERN = "quarry-tern"
    RAPIDS_ASTER = "rapids-aster"
    SLATE_YARROW = "slate-yarrow"
    TALUS_CEDAR = "talus-cedar"
    UPLAND_SORREL = "upland-sorrel"
    VIOLET_MUSKEG = "violet-muskeg"
    WHEAT_BITTERN = "wheat-bittern"
    YEW_COULEE = "yew-coulee"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    MANAGER_DELEGATED_AUTHORITY = "MANAGER_DELEGATED_AUTHORITY"
    IMMEDIATE_SUPERVISOR = "IMMEDIATE_SUPERVISOR"
    EMPLOYER = "EMPLOYER"
    DEPUTY_HEAD = "DEPUTY_HEAD"
    TRAVEL_COORDINATOR = "TRAVEL_COORDINATOR"
    NJC_EXECUTIVE_COMMITTEE = "NJC_EXECUTIVE_COMMITTEE"
    TREASURY_BOARD = "TREASURY_BOARD"
    ATTENDING_PHYSICIAN = "ATTENDING_PHYSICIAN"


class Clause(Enum):
    """The handbook's sections, by heading or paragraph."""

    EFFECTIVE_DATE = "EFFECTIVE_DATE"
    APPLICATION = "APPLICATION"
    DEFINITIONS = "DEFINITIONS"
    EMPLOYER_AUTHORIZATION = "EMPLOYER_AUTHORIZATION"
    WRITTEN_AUTHORIZATION = "WRITTEN_AUTHORIZATION"
    LOYALTY_PROGRAMS = "LOYALTY_PROGRAMS"
    RESPONSIBILITIES = "RESPONSIBILITIES"
    SUPPLIERS = "SUPPLIERS"
    CANADA_USA_MODULE = "CANADA_USA_MODULE"
    CANADA_USA_REST_PERIODS = "CANADA_USA_REST_PERIODS"
    CANADA_USA_TRANSPORTATION = "CANADA_USA_TRANSPORTATION"
    CANADA_USA_WEEKEND_HOME = "CANADA_USA_WEEKEND_HOME"
    CANADA_USA_WEEKEND_ALTERNATIVES = "CANADA_USA_WEEKEND_ALTERNATIVES"
    INTERNATIONAL_MODULE = "INTERNATIONAL_MODULE"
    INTERNATIONAL_REST_PERIODS = "INTERNATIONAL_REST_PERIODS"
    INTERNATIONAL_TRANSPORTATION = "INTERNATIONAL_TRANSPORTATION"
    INTERNATIONAL_WEEKEND_HOME = "INTERNATIONAL_WEEKEND_HOME"
    INTERNATIONAL_WEEKEND_ALTERNATIVES = "INTERNATIONAL_WEEKEND_ALTERNATIVES"
    ESCORT_OFFICERS = "ESCORT_OFFICERS"
    NEXT_OF_KIN = "NEXT_OF_KIN"
    EARLY_OR_LATE_RETURN = "EARLY_OR_LATE_RETURN"
    APPENDIX_C = "APPENDIX_C"
    APPENDIX_D = "APPENDIX_D"
    NJC_DECISION = "NJC_DECISION"


class PersonKind(Enum):
    EMPLOYEE = "EMPLOYEE"
    FAMILY_MEMBER = "FAMILY_MEMBER"
    OTHER_PERSON = "OTHER_PERSON"


class AuthorityKind(Enum):
    """WRITTEN_TRIP_AUTHORITY: a written authorization for this trip. BLANKET_TRAVEL_AUTHORITY: a standing
    authorization for repeated trips. NONE: no authorization on file."""

    WRITTEN_TRIP_AUTHORITY = "WRITTEN_TRIP_AUTHORITY"
    BLANKET_TRAVEL_AUTHORITY = "BLANKET_TRAVEL_AUTHORITY"
    NONE = "NONE"


class IssuedTo(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    GROUP = "GROUP"


@dataclass
class Trip(Output):
    traveller_title: Annotated[str, "The traveller's job title, or their relation to the employee"]
    traveller_kind: Annotated[PersonKind, "What the person flying is to the employer"]
    workplace: Annotated[str, "Where the traveller normally works; empty for a family member"]
    companions: Annotated[list[str], "Others booked together with the traveller, by job title; empty when alone"]
    origin: Annotated[Airport, "Where the trip's flight leaves from"]
    origin_state_or_province: Annotated[str, "The state, province or territory of the origin city; empty when none"]
    destination: Annotated[Airport, "Where the trip's flight goes"]
    destination_state_or_province: Annotated[str, "The state, province or territory of the destination city; empty when none"]
    depart_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    return_date: Annotated[
        str, "For a round-trip ticket (a trip home or a visit), the day to fly back, YYYY-MM-DD, local at the "
        "destination airport; empty for a one-way ticket, whose return is booked separately"
    ]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    authority_kind: Annotated[AuthorityKind, "The kind of authorization on file for this travel"]
    authority_issued_to: Annotated[IssuedTo, "Whether that authorization names one person or a group of people"]
    authority_given_by: Annotated[str, "Who gave the authorization; empty when there is none"]
    authority_covers: Annotated[str, "What the authorization says it covers; empty when it says nothing more"]
    assignment_location: Annotated[str, "Where the employee is posted for a longer assignment away from home; empty when none"]
    travel_status_start: Annotated[str, "First day of that assignment away from home, YYYY-MM-DD; empty when none"]
    travel_status_end: Annotated[str, "Last day of that assignment away from home, YYYY-MM-DD; empty when none"]
    continuous_travel_status: Annotated[bool, "Whether the employee stays away for the whole assignment without a break"]
    weekend_trips_home_taken: Annotated[int, "How many trips home the employee has already made during the assignment"]
    must_stay_at_duty_location: Annotated[bool, "Whether the employer requires the employee to stay at the assignment city over weekends"]
    visitor_relationship: Annotated[str, "For a ticket bought for a visitor, how they are related to the employee; empty otherwise"]
    visitor_home: Annotated[str, "That visitor's home city; empty otherwise"]
    physician_opinion: Annotated[str, "A doctor's written statement on file about this trip; empty when none"]
    ground_minutes_to_departure_terminal: Annotated[int, "Minutes from the traveller's start point to the airport; zero when not on file"]
    ground_minutes_from_arrival_terminal: Annotated[int, "Minutes from the arrival airport to the final address; zero when not on file"]
    rest_period_on_arrival: Annotated[str, "The rest the traveller has after landing before work, as planned; empty when not on file"]
    meeting_starts_local: Annotated[str, "When the event the traveller must attend starts, YYYY-MM-DD HH:MM local time at the destination; empty when none"]
    airport_to_venue_minutes: Annotated[int, "Minutes from the arrival airport to that event; zero when none"]
    loyalty_programs: Annotated[list[str], "Airlines whose frequent-flyer scheme the traveller belongs to; empty when none"]
    itinerary_note: Annotated[str, "What has been decided about the routing; empty when nothing"]
    other_notes: Annotated[list[str], "Other notes on file for this trip"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
