import pandas as pd


DATA_PATH = "ai-engine/data/traffic.csv"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading traffic dataset...")

df = pd.read_csv(DATA_PATH)

df["timestamp"] = pd.to_datetime(df["timestamp"])


# ============================================================
# BASIC LABEL ANALYSIS
# ============================================================

print("\n===== CONGESTION LEVEL COUNTS =====")

print(
    df["congestion_level"].value_counts()
)


# ============================================================
# STATISTICS BY CONGESTION LEVEL
# ============================================================

print("\n===== FEATURE STATISTICS BY CONGESTION LEVEL =====")

stats = (
    df.groupby("congestion_level")[
        [
            "vehicle_count",
            "avg_speed_kmph",
            "road_capacity",
            "road_length_km",
            "traffic_density_vehicles_per_km",
        ]
    ]
    .agg(["min", "max", "mean", "median"])
)

print(stats)


# ============================================================
# DENSITY RANGES
# ============================================================

print("\n===== TRAFFIC DENSITY RANGE BY LEVEL =====")

density_stats = (
    df.groupby("congestion_level")[
        "traffic_density_vehicles_per_km"
    ]
    .agg(["min", "max", "mean", "median"])
    .sort_values("min")
)

print(density_stats)


# ============================================================
# SPEED RANGES
# ============================================================

print("\n===== AVERAGE SPEED RANGE BY LEVEL =====")

speed_stats = (
    df.groupby("congestion_level")[
        "avg_speed_kmph"
    ]
    .agg(["min", "max", "mean", "median"])
    .sort_values("mean", ascending=False)
)

print(speed_stats)


# ============================================================
# VEHICLE COUNT RANGES
# ============================================================

print("\n===== VEHICLE COUNT RANGE BY LEVEL =====")

vehicle_stats = (
    df.groupby("congestion_level")[
        "vehicle_count"
    ]
    .agg(["min", "max", "mean", "median"])
    .sort_values("mean")
)

print(vehicle_stats)


# ============================================================
# CHECK DENSITY OVERLAP
# ============================================================

print("\n===== DENSITY OVERLAP CHECK =====")

levels = ["Low", "Medium", "High", "Severe"]

for level in levels:

    values = df.loc[
        df["congestion_level"] == level,
        "traffic_density_vehicles_per_km"
    ]

    if len(values) == 0:
        continue

    print(
        f"{level:8} : "
        f"{values.min():.2f} → "
        f"{values.max():.2f}"
    )


# ============================================================
# CHECK SPEED OVERLAP
# ============================================================

print("\n===== SPEED OVERLAP CHECK =====")

for level in levels:

    values = df.loc[
        df["congestion_level"] == level,
        "avg_speed_kmph"
    ]

    if len(values) == 0:
        continue

    print(
        f"{level:8} : "
        f"{values.min():.2f} → "
        f"{values.max():.2f}"
    )


print("\nLabel analysis completed successfully.")
