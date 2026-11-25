"""NJC v328 checks beyond the template's suite (MASTER_PLAN section 4, NJC row; NJC_CHECKS.md; the design's
world constraints W2-W11): dates on or after the effective date, the nine-hour rule in Module 4 only, at most
one scenario each on Alaska and on an overnight terminal wait, no background offers, supplier neutrality,
plain connections, routings on one side of the limit, and requests that share no number or 4-word phrase
with any must_keep clause."""

from test_lint import grams, numbers

from contract import Cabin, Decision
from helpers import range_text, scenarios
from plugin import rules
from plugin.answer import answer_key
from plugin.scenarios import handbook
from plugin.world import clock_minutes, days_between

ALL = scenarios()
CANADIAN = {"Air Canada", "WestJet"}
EFFECTIVE = "2026-12-01"  # line 37: "This directive is effective on December 1, 2026."


def keyed():
    for data in ALL:
        trip, offers, slots, key = answer_key(data)
        yield data, trip, offers, slots, key


def test_every_date_is_on_or_after_the_effective_date():
    for data in ALL:
        trip = data["trip"]
        dates = [trip["booking_date"], trip["depart_date"]]
        dates += [trip[name] for name in ("return_date", "travel_status_start", "travel_status_end") if trip[name]]
        for search in data["world"]["searches"]:
            dates += [search["date"]] + ([search["return_date"]] if search["return_date"] else [])
        assert all(days_between(EFFECTIVE, date) >= 0 for date in dates), data["id"]


def test_the_nine_hour_rule_is_international_only():
    module_three_long = 0
    for data, trip, offers, _, key in keyed():
        module = rules.module_of(data["answer_key_inputs"])
        if key["decision"] == Decision.BOOK and set(key["cabins"]) & {Cabin.BUSINESS, Cabin.PREMIUM_ECONOMY}:
            assert module == 4, data["id"]
        if module == 3 and key["decision"] == Decision.BOOK:
            assert key["cabins"] == [Cabin.ECONOMY], data["id"]
            module_three_long += any(rules.over("continuous-air-travel", offer) for offer in offers)
    assert module_three_long >= 1  # a Module 3 journey over the limit still books economy (wheat-bittern)


def test_alaska_and_the_overnight_wait_are_each_at_most_one_flag():
    alaska = [data for data in ALL if "US_ALASKA" in (data["answer_key_inputs"]["origin_region"],
                                                      data["answer_key_inputs"]["destination_region"])]
    assert len(alaska) <= 1 and all(data["expected"]["unclear_phrase"] == rules.ALASKA_PHRASE for data in alaska)
    waits = []
    for data, _, offers, _, _ in keyed():
        if any(None in rules.connection_kinds(o.segments, o.layover_minutes, o.stopover_nights) for o in offers):
            waits.append(data)
    assert len(waits) <= 1 and all(data["expected"]["unclear_phrase"] == rules.LAYOVER_PHRASE for data in waits)


def test_no_background_offers_anywhere():
    assert handbook()["background_offers"] == 0
    for data in ALL:
        assert all(search.get("background", 0) == 0 for search in data["world"]["searches"]), data["id"]


def searches_of(data, offers):
    groups = {}
    for offer in offers:
        groups.setdefault((offer.segments[0].origin, offer.segments[-1].destination), []).append(offer)
    return groups.values()


def test_supplier_neutrality_and_refundable_fares():
    for data, _, offers, _, _ in keyed():
        for group in searches_of(data, offers):
            for cabin in {offer.cabin for offer in group}:
                same = [offer for offer in group if offer.cabin == cabin]
                low = min(offer.fare_cents for offer in same)
                if any(offer.carrier in CANADIAN for offer in same):
                    assert all(offer.carrier in CANADIAN for offer in same if offer.fare_cents == low), data["id"]
                plain = [offer.fare_cents for offer in same if not offer.refundable]
                assert all(offer.fare_cents > min(plain) for offer in same if offer.refundable), data["id"]
            assert any(offer.cabin == Cabin.ECONOMY for offer in group), data["id"]


def test_connections_are_plain_unless_pinned():
    for data, _, offers, _, _ in keyed():
        for offer in offers:
            for direction in ((offer.segments, offer.layover_minutes, offer.stopover_nights),
                              (offer.return_segments, offer.return_layover_minutes, offer.return_stopover_nights)):
                segments, layovers, stopovers = direction
                kinds = rules.connection_kinds(segments, layovers, stopovers) if segments else []
                for index, kind in enumerate(kinds):
                    if kind is not False:
                        continue
                    land, leave = segments[index].arrive_local, segments[index + 1].depart_local
                    assert 45 <= layovers[index] <= 180, (data["id"], layovers[index])
                    assert land[:10] == leave[:10], data["id"]
                    assert 6 * 60 <= clock_minutes(land[11:]) and clock_minutes(leave[11:]) <= 23 * 60, data["id"]


def test_routings_fall_on_one_side_of_the_limit_except_the_routing_flag():
    mixed = []
    for data, _, offers, _, _ in keyed():
        for group in searches_of(data, offers):
            verdicts = {rules.over("continuous-air-travel", offer) for offer in group} - {None}
            if len(verdicts) > 1:
                mixed.append(data["id"])
    assert all(not data["answer_key_inputs"].get("itinerary_fixed", True) for data in ALL if data["id"] in mixed)
    assert len(mixed) <= 1


def test_hidden_regions_agree_with_the_airports():
    def region(code, state):
        if code == "ANC":
            return "US_ALASKA"
        if code == "HNL":
            return "US_OUTSIDE_CONTINENTAL"
        return {"CA": "CANADA", "US": "US_CONTINENTAL"}.get(country[code], "INTERNATIONAL")

    from plugin.world import airport
    for data in ALL:
        trip, hidden = data["trip"], data["answer_key_inputs"]
        country = {code: airport(code).country for code in (trip["origin"], trip["destination"])}
        assert hidden["origin_region"] == region(trip["origin"], trip["origin_state_or_province"]), data["id"]
        assert hidden["destination_region"] == region(trip["destination"], trip["destination_state_or_province"])


def test_requests_share_no_number_or_phrase_with_any_clause():
    clauses = [range_text(entry["lines"]) for data in ALL for entry in data["must_keep"]]
    clause_numbers = set().union(*(numbers(text) for text in clauses))
    clause_grams = set().union(*(grams(text) for text in clauses))
    for data in ALL:
        assert not numbers(data["request"]) & clause_numbers, (data["id"], numbers(data["request"]) & clause_numbers)
        assert not grams(data["request"]) & clause_grams, (data["id"], grams(data["request"]) & clause_grams)

