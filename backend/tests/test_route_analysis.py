import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("route_analysis_main", ROOT / "services" / "route-analysis" / "app" / "main.py")
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def test_coordinate_parser_accepts_lat_lng():
    coordinate = MODULE.parse_coordinate("12.9716,77.5946")
    assert coordinate.lat == 12.9716
    assert coordinate.lng == 77.5946


def test_route_id_is_stable():
    path = [[12.97, 77.59], [12.93, 77.62]]
    assert MODULE.route_id(path) == MODULE.route_id(path)
