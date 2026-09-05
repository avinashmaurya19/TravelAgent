"""Deterministic flight ranking and recommendation engine."""

from typing import List, Dict, Any


class FlightRankingEngine:
    """Ranks flight search results deterministically using composite scoring."""

    @staticmethod
    def rank_flights(
        flights: List[Dict[str, Any]],
        price_weight: float = 0.50,
        duration_weight: float = 0.35,
        stops_weight: float = 0.15,
    ) -> List[Dict[str, Any]]:
        """Compute composite scores, assign recommendation badges, and sort flights."""
        if not flights:
            return []

        if len(flights) == 1:
            flight = dict(flights[0])
            flight["badge"] = "Only Option"
            flight["ranking_score"] = 1.0
            flight["ranking_explanation"] = "Only available option matching your search criteria."
            return [flight]

        prices = [float(f.get("price", 0)) for f in flights]
        durations = [float(f.get("duration_minutes", 0)) for f in flights]

        min_price, max_price = min(prices), max(prices)
        min_dur, max_dur = min(durations), max(durations)

        price_range = max_price - min_price if max_price > min_price else 1.0
        dur_range = max_dur - min_dur if max_dur > min_dur else 1.0

        ranked_flights = []
        for f in flights:
            item = dict(f)
            p = float(item.get("price", 0))
            d = float(item.get("duration_minutes", 0))
            stops = int(item.get("stops", 0))

            norm_price = (p - min_price) / price_range if max_price > min_price else 0.0
            norm_dur = (d - min_dur) / dur_range if max_dur > min_dur else 0.0
            stops_penalty = 0.0 if stops == 0 else (0.5 if stops == 1 else 1.0)

            composite_score = (
                (price_weight * norm_price)
                + (duration_weight * norm_dur)
                + (stops_weight * stops_penalty)
            )

            item["ranking_score"] = round(composite_score, 3)
            ranked_flights.append(item)

        # Sort by composite score (lowest / best first)
        ranked_flights.sort(key=lambda x: x["ranking_score"])

        # Assign unique badges
        cheapest_idx = min(range(len(ranked_flights)), key=lambda i: ranked_flights[i]["price"])
        fastest_idx = min(range(len(ranked_flights)), key=lambda i: ranked_flights[i]["duration_minutes"])

        for i, flight in enumerate(ranked_flights):
            if i == 0 and i == cheapest_idx and flight["stops"] == 0:
                flight["badge"] = "Best Overall"
            elif i == 0:
                flight["badge"] = "Best Overall"
            elif i == cheapest_idx:
                flight["badge"] = "Cheapest"
            elif i == fastest_idx:
                flight["badge"] = "Fastest"
            elif flight["stops"] == 0:
                flight["badge"] = "Non-stop"
            else:
                flight["badge"] = None

            flight["ranking_explanation"] = FlightRankingEngine._generate_explanation(
                flight, min_price, min_dur
            )

        return ranked_flights

    @staticmethod
    def _generate_explanation(
        flight: Dict[str, Any],
        min_price: float,
        min_dur: float,
    ) -> str:
        """Generate human-readable rationale explaining flight value proposition."""
        flight_num = flight.get("flight_number", "Flight")
        airline = flight.get("airline", "")
        price = flight.get("price", 0)
        dur = flight.get("duration_minutes", 0)
        stops = flight.get("stops", 0)

        stops_str = "Non-stop" if stops == 0 else f"{stops} stop"
        h, m = divmod(int(dur), 60)
        time_str = f"{h}h {m}m" if h > 0 else f"{m}m"

        reasons = []
        if price == min_price:
            reasons.append("lowest fare")
        if dur == min_dur:
            reasons.append("quickest flight time")
        if stops == 0:
            reasons.append("direct routing")

        if reasons:
            tag = ", ".join(reasons)
            return f"{flight_num} ({airline}): {tag.capitalize()} ({stops_str}, {time_str}) at ₹{price:,.0f}."

        diff_price = price - min_price
        return f"{flight_num} ({airline}): {stops_str}, {time_str} at ₹{price:,.0f} (+₹{diff_price:,.0f} vs cheapest)."
