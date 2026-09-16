from route_ranker import rank_routes


routes = [
    {
        "route_id": "R1",
        "distance_km": 8.0,
        "estimated_delay_minutes": 10,
        "predicted_congestion": "HIGH"
    },
    {
        "route_id": "R2",
        "distance_km": 9.0,
        "estimated_delay_minutes": 4,
        "predicted_congestion": "LOW"
    },
    {
        "route_id": "R3",
        "distance_km": 7.0,
        "estimated_delay_minutes": 7,
        "predicted_congestion": "MEDIUM"
    }
]


ranked = rank_routes(routes)

for route in ranked:
    print(route)
assert ranked[0]["route_id"] == "R2"
assert ranked[0]["rank"] == 1

assert ranked[1]["route_id"] == "R3"
assert ranked[1]["rank"] == 2

assert ranked[2]["route_id"] == "R1"
assert ranked[2]["rank"] == 3

print("All route ranking tests passed!")