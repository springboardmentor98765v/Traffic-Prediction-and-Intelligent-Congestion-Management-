def get_congestion_level(density):
    if density >= 0.85:
        return "SEVERE"
    elif density >= 0.65:
        return "HIGH"
    elif density >= 0.40:
        return "MEDIUM"
    else:
        return "LOW"


def test_low_congestion():
    assert get_congestion_level(0.20) == "LOW"


def test_medium_congestion():
    assert get_congestion_level(0.40) == "MEDIUM"
    assert get_congestion_level(0.64) == "MEDIUM"


def test_high_congestion():
    assert get_congestion_level(0.65) == "HIGH"
    assert get_congestion_level(0.84) == "HIGH"


def test_severe_congestion():
    assert get_congestion_level(0.85) == "SEVERE"
    assert get_congestion_level(1.00) == "SEVERE"