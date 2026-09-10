import pandas as pd

# Read the generated historical dataset
input_file = "traffic_history_4weeks.csv"

df = pd.read_csv(input_file)

# Remove duplicate road + timestamp records
df = df.drop_duplicates(subset=["road_id", "timestamp"])

# Remove records with missing required values
df = df.dropna(
    subset=[
        "road_id",
        "timestamp",
        "vehicle_count",
        "density",
        "congestion_level"
    ]
)

# Remove invalid values
df = df[
    (df["vehicle_count"] >= 0) &
    (df["density"] >= 0) &
    (df["congestion_level"].isin(["Low", "Medium", "High"]))
]

# Sort by road and timestamp
df = df.sort_values(["road_id", "timestamp"])

# Save cleaned dataset in the project root
output_file = "traffic_history_clean.csv"
df.to_csv(output_file, index=False)

print("Cleaned dataset created successfully!")
print(f"Records: {len(df)}")
print(f"Roads: {df['road_id'].nunique()}")
print(f"Start: {df['timestamp'].min()}")
print(f"End: {df['timestamp'].max()}")
print(f"Saved to: {output_file}")