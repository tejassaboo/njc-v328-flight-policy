"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "njc-cabin-meal-allowance" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 32-scenario row).
MIX = {"easy": 6, "boundary_twin": 8, "multi_rule": 5, "hidden_clause": 3, "distractor": 3, "refusal": 3, "flag": 4}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "overnight_stop": 1, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1,
    "multi_traveller": 1, "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "business", "economy", "premium", "first", "spouse", "husband", "wife", "partner", "weekend", "home", "alaska",
    "hawaii", "continental", "layover", "stopover", "connection", "loyalty", "refundable", "changeable", "escort",
    "kin", "physician", "manager", "supervisor", "employer", "blanket", "team", "nonstop", "direct", "routing",
    "module", "international", "domestic", "nine", "hotel", "night", "authority", "visit", "holiday", "rest",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.PersonKind, contract.AuthorityKind, contract.IssuedTo]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section). Economy at the lowest appropriate fare is
# this handbook's standard (lines 769, 1017), so the always-lowest agent passes every case whose right answer
# is the cheapest seat listed; set to what it passes (see README).
# The always-flag agent passes exactly the three holds over unclear words (it is given the held offer).
MAX_PASS_ALWAYS_FLAG = 3
# Its approver is NONE, which every booking accepts (template SYNC_NOTES 4'). Its reason is LOWEST_FARE, which a
# booking that declines the cabin asked for no longer accepts (template APPROVER_REVIEW, declined requests), so
# it passes the 8 cheapest-seat bookings where nothing asked for is declined on another ground: cobalt-heron,
# dawn-trillium, eastern-larch, granite-wren, kelp-lantern, maple-osprey, pine-cormorant, upland-sorrel.
MAX_PASS_ALWAYS_LOWEST = 8

# Hand-built duration cases beyond the automatic both-sides tests: (rule, outbound scheduled minutes per
# flight, layovers, expected True / False / None for unclear). The test itinerary leaves JFK at 08:00 local
# and connects at ORD (one hour behind).
DURATION_CASES = [
    ("continuous-air-travel", [541], [], True),
    ("continuous-air-travel", [540], [], False),
    ("continuous-air-travel", [420, 60], [61], True),  # a connection counts: 541
    ("continuous-air-travel", [420, 60], [60], False),  # 540
    ("continuous-air-travel", [400, 200], [200], True),  # a long daytime wait is still a connection
    ("continuous-air-travel", [200, 200], [100], False),
    ("continuous-air-travel", [540, 100], [500], None),  # 500 minutes across local midnight, no hotel: unclear
    ("continuous-air-travel", [600, 60], [500], True),  # over on both readings
    ("continuous-air-travel", [300, 100], [500], True),  # 500 minutes within one local day: a connection, 900
    ("continuous-air-travel", [400, 100], [30], False),  # 530
]
