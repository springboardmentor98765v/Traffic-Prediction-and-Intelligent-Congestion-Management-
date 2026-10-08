import sys
from pathlib import Path

import pytest


# Allow imports from ai-engine/src
AI_ENGINE_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = AI_ENGINE_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from recommendation_engine import RecommendationEngine


@pytest.fixture(scope="module")
def engine():
    return RecommendationEngine()


def test_engine_initializes(engine):
    """Recommendation engine loads model and historical data."""
    assert engine.model is not None
    assert not engine.traffic.empty


def test_known_road_returns_recommendations(engine):
    """A known road should produce a recommendation list."""
    result = engine.generate("R001")

    assert isinstance(result, list)
    assert len(result) > 0


def test_recommendation_schema(engine):
    """Every recommendation must contain the required fields."""
    result = engine.generate("R001")

    for recommendation in result:
        assert "recommendation_text" in recommendation
        assert "based_on" in recommendation

        assert isinstance(
            recommendation["recommendation_text"],
            str,
        )

        assert isinstance(
            recommendation["based_on"],
            str,
        )


def test_invalid_road_returns_empty_list(engine):
    """Unknown roads should not generate recommendations."""
    result = engine.generate("INVALID")

    assert result == []


def test_peak_hours_are_valid(engine):
    """Peak-hour analysis should return valid hour values."""
    peak_hours = engine._find_peak_hours("R001")

    assert isinstance(peak_hours, list)
    assert len(peak_hours) <= 3

    for hour in peak_hours:
        assert 0 <= hour <= 23