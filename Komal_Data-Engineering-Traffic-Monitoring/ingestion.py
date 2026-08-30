import csv

CSV_FILE = "traffic_dataset.csv"
OUTPUT_FILE = "processed_traffic.csv"


def get_congestion_level(density):
    if density < 20:
        return "Low"
    elif density <= 50:
        return "Medium"
    else:
        return "High"


def ingest_data():

    print("Starting data ingestion...")

    with open(CSV_FILE, "r") as input_file:

        reader = csv.DictReader(input_file)

        fieldnames = reader.fieldnames + ["congestion"]

        with open(OUTPUT_FILE, "w", newline="") as output_file:

            writer = csv.DictWriter(
                output_file,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for row in reader:

                density = float(row["density"])

                congestion = get_congestion_level(density)

                row["congestion"] = congestion

                writer.writerow(row)

                print(
                    f"Road: {row['road_id']} | "
                    f"Sensor: {row['sensor_id']} | "
                    f"Density: {density} | "
                    f"Congestion: {congestion}"
                )

    print("\nData ingestion completed.")
    print(f"Processed data saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    ingest_data()