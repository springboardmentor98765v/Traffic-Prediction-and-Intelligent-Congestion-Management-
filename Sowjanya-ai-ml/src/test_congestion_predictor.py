import pytest
import sys
from pathlib import Path

SRC_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC_DIR))

from congestion_predictor import predict_by_density, adjust_for_time, predict_congestion


def test_predict_by_density():
    # Density < 20: LOW
    assert predict_by_density(0) == "LOW"
    assert predict_by_density(10) == "LOW"
    assert predict_by_density(19.9) == "LOW"

    # Density 20..50: MEDIUM
    assert predict_by_density(20) == "MEDIUM"
    assert predict_by_density(35) == "MEDIUM"
    assert predict_by_density(50) == "MEDIUM"

    # Density > 50: HIGH
    assert predict_by_density(50.1) == "HIGH"
    assert predict_by_density(80) == "HIGH"


def test_adjust_for_time_peak_hours():
    # Morning peak: 7..10
    assert adjust_for_time("LOW", 8) == "MEDIUM"
    assert adjust_for_time("MEDIUM", 9) == "HIGH"
    assert adjust_for_time("HIGH", 8) == "HIGH"

    # Evening peak: 17..20
    assert adjust_for_time("LOW", 18) == "MEDIUM"
    assert adjust_for_time("MEDIUM", 19) == "HIGH"

    # Off-peak hours
    assert adjust_for_time("LOW", 14) == "LOW"
    assert adjust_for_time("MEDIUM", 14) == "MEDIUM"
    assert adjust_for_time("HIGH", 14) == "HIGH"
    assert adjust_for_time("LOW", 2) == "LOW"


def test_predict_congestion_combined():
    # Off-peak low density
    assert predict_congestion(15, 12) == "LOW"
    # Peak hour low density -> elevated to MEDIUM
    assert predict_congestion(15, 8) == "MEDIUM"
    # Off-peak medium density
    assert predict_congestion(35, 14) == "MEDIUM"
    # Peak hour medium density -> elevated to HIGH
    assert predict_congestion(35, 18) == "HIGH"
    # High density stays HIGH
    assert predict_congestion(70, 8) == "HIGH"
    assert predict_congestion(70, 14) == "HIGH"
