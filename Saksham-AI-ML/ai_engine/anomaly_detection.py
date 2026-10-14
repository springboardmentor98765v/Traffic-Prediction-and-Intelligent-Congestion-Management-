"""
Milestone 3 — Day 2
Anomaly detection prototype for unusual traffic patterns.
"""


def detect_anomaly(expected_level, observed_level):
    """
    Detect whether observed congestion differs significantly
    from the expected congestion level.
    """

    congestion_levels = {
        "LOW": 1,
        "MEDIUM": 2,
        "HIGH": 3,
        "SEVERE": 4
    }

    expected = congestion_levels.get(expected_level.upper())
    observed = congestion_levels.get(observed_level.upper())

    if expected is None or observed is None:
        return False

    difference = observed - expected

    return difference >= 2