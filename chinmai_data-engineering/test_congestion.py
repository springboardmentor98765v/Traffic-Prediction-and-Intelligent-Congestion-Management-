import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
from congestion_calculator import calculate_congestion


def test_low_congestion():
    assert calculate_congestion(40, 100) == "Low"


def test_medium_congestion():
    assert calculate_congestion(60, 100) == "Medium"


def test_high_congestion():
    assert calculate_congestion(90, 100) == "High"


def test_severe_congestion():
    assert calculate_congestion(101, 100) == "Severe"


def test_boundary_50_percent_is_medium():
    assert calculate_congestion(50, 100) == "Medium"


def test_boundary_80_percent_is_medium():
    assert calculate_congestion(80, 100) == "Medium"


def test_boundary_100_percent_is_high():
    assert calculate_congestion(100, 100) == "High"


def test_invalid_capacity_rejected():
    with pytest.raises(ValueError):
        calculate_congestion(10, 0)
