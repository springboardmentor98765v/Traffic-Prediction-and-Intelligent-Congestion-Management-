"""
TrafficVision AI — Unit Tests for simulate_road_conditions.py (Milestone 2, Day 6)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Run:
    pytest test_simulate_road_conditions.py -v
"""

from collections import Counter
import pytest

from simulate_road_conditions import pick_scenario, CONDITION_SCENARIOS


class TestPickScenario:

    def test_only_returns_known_statuses(self):
        valid_statuses = {status for status, _, _ in CONDITION_SCENARIOS}
        for _ in range(200):
            status, notes = pick_scenario()
            assert status in valid_statuses

    def test_returns_a_status_and_matching_note(self):
        status, notes = pick_scenario()
        assert isinstance(status, str)
        assert isinstance(notes, str)
        assert len(notes) > 0

    def test_clear_is_the_most_common_outcome(self):
        """
        Verifies the weighting actually works as intended — CLEAR should
        dominate since most roads are fine most of the time in real life.
        This is the same kind of "verify the randomness behaves as
        designed" test used for the speed simulation in Milestone 1.
        """
        results = [pick_scenario()[0] for _ in range(5000)]
        counts = Counter(results)

        assert counts["CLEAR"] == max(counts.values())

    def test_distribution_roughly_matches_configured_weights(self):
        """
        Checks the actual output percentages land within a reasonable
        tolerance of the configured weights (60/15/15/10), rather than
        wildly off — catches a bug like weights being applied backwards.
        """
        results = [pick_scenario()[0] for _ in range(10000)]
        counts = Counter(results)

        clear_pct = counts["CLEAR"] / len(results) * 100
        closed_pct = counts["CLOSED"] / len(results) * 100

        # Allow some tolerance since this is randomness, not exact math
        assert 50 <= clear_pct <= 70, f"CLEAR should be ~60%, got {clear_pct:.1f}%"
        assert 5 <= closed_pct <= 15, f"CLOSED should be ~10%, got {closed_pct:.1f}%"

    def test_scenarios_config_is_well_formed(self):
        """Sanity check on the CONDITION_SCENARIOS constant itself."""
        for status, notes, weight in CONDITION_SCENARIOS:
            assert isinstance(status, str) and len(status) > 0
            assert isinstance(notes, str) and len(notes) > 0
            assert 0 < weight <= 1

        total_weight = sum(w for _, _, w in CONDITION_SCENARIOS)
        assert abs(total_weight - 1.0) < 0.01, "Weights should sum to ~1.0"
