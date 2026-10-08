"""
TrafficVision AI — Congestion Calculation Logic (Day 2)
Owner: Intern 2 (Data Engineering & Traffic Monitoring)

Purpose:
    A single, reusable place for the density -> congestion_level rule.
    Used by:
      - ingest_live_data.py (this module, Day 2)
      - Intern 3's heuristic prediction stub may reuse the same thresholds
        as a starting point (Day 3-4)

Why a separate file?
    Keeping this logic in its own module means if the thresholds ever
    change, we update ONE place instead of hunting through multiple
    scripts. This also makes it easy to unit test on its own (Day 6).
"""


def calculate_congestion_level(density: float) -> str:
    """
    Convert a density value (0-100) into a congestion category.

    Thresholds (placeholder — can be recalibrated later with real data):
        density < 30   -> LOW
        30 <= d < 60   -> MODERATE
        60 <= d < 85   -> HIGH
        d >= 85        -> SEVERE
    """
    if density < 30:
        return "LOW"
    elif density < 60:
        return "MODERATE"
    elif density < 85:
        return "HIGH"
    else:
        return "SEVERE"


def calculate_avg_speed(density: float) -> float:
    """
    Rough simulated relationship: as density goes up, average speed goes
    down. In real sensor data this would come from the sensor itself;
    here we derive it so simulated data still 'behaves' realistically.
    """
    import random
    base_speed = 60 - (density * 0.5)
    noisy_speed = base_speed + random.uniform(-5, 5)
    return round(max(5, noisy_speed), 1)


# ---------------------------------------------------------
# Quick self-test — run this file directly to sanity check
# ---------------------------------------------------------
if __name__ == "__main__":
    test_values = [10, 29, 30, 59, 60, 84, 85, 99]
    print(f"{'Density':<10}{'Congestion Level':<20}{'Sample Speed'}")
    for d in test_values:
        print(f"{d:<10}{calculate_congestion_level(d):<20}{calculate_avg_speed(d)}")
