import time
import random
import psycopg
import redis

# ==============================
# PostgreSQL connection
# ==============================

conn = psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="postgres",
    user="postgres",
    password="A"
)

# ==============================
# Redis / Memurai connection
# ==============================

cache = redis.Redis(
    host="127.0.0.1",
    port=6379,
    decode_responses=True
)

# Test Redis
try:
    cache.ping()
    print("Connected to Redis/Memurai")
except redis.RedisError as e:
    print("Redis connection failed:", e)
    cache = None

print("Connected to PostgreSQL")
print("Starting live traffic feed...")

try:

    while True:

        # ----------------------------------
        # Get ALL sensors and their roads
        # ----------------------------------

        with conn.cursor() as cur:

            cur.execute("""
                SELECT sensor_id, road_id
                FROM sensors
                WHERE status IS NULL OR status = 'ACTIVE'
                ORDER BY sensor_id;
            """)

            sensors = cur.fetchall()

        if not sensors:
            print("No sensors found.")
            break

        # ----------------------------------
        # Generate traffic for every sensor
        # ----------------------------------

        for sensor_id, road_id in sensors:

            # Get road capacity
            with conn.cursor() as cur:

                cur.execute("""
                    SELECT vehicle_capacity
                    FROM road_capacity
                    WHERE road_id = %s
                    ORDER BY effective_from DESC
                    LIMIT 1;
                """, (road_id,))

                capacity_result = cur.fetchone()

            if capacity_result is None:
                print(
                    f"No capacity found for road {road_id}. "
                    f"Skipping sensor {sensor_id}."
                )
                continue

            capacity = capacity_result[0]

            # ----------------------------------
            # Generate simulated traffic
            # ----------------------------------

            vehicle_count = random.randint(
                10,
                max(10, int(capacity * 1.10))
            )

            # Density = vehicles / capacity
            density = round(
                vehicle_count / capacity,
                2
            )

            # Keep density between 0 and 1
            density = min(density, 1.0)

            # ----------------------------------
            # Determine congestion
            # ----------------------------------

            if density >= 0.85:
                congestion_level = "SEVERE"

            elif density >= 0.65:
                congestion_level = "HIGH"

            elif density >= 0.40:
                congestion_level = "MEDIUM"

            else:
                congestion_level = "LOW"

            # ----------------------------------
            # Insert traffic reading
            # ----------------------------------

            source_record_id = int(time.time() * 1000000) + sensor_id

            with conn.cursor() as cur:

                cur.execute("""
                    INSERT INTO traffic_readings
                    (
                        sensor_id,
                        source_record_id,
                        timestamp,
                        vehicle_count,
                        density,
                        congestion_level
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        CURRENT_TIMESTAMP,
                        %s,
                        %s,
                        %s
                    );
                """, (
                    sensor_id,
                    source_record_id,
                    vehicle_count,
                    density,
                    congestion_level
                ))

            # ----------------------------------
            # Check previous congestion state
            # ----------------------------------

            with conn.cursor() as cur:

                cur.execute("""
                    SELECT congestion_level
                    FROM congestion_history
                    WHERE road_id = %s
                    ORDER BY recorded_at DESC
                    LIMIT 1;
                """, (road_id,))

                previous = cur.fetchone()

            previous_level = previous[0] if previous else None

            # ----------------------------------
            # Store congestion state change
            # ----------------------------------

            if previous_level != congestion_level:

                with conn.cursor() as cur:

                    cur.execute("""
                        INSERT INTO congestion_history
                        (
                            road_id,
                            congestion_level,
                            density,
                            recorded_at
                        )
                        VALUES
                        (
                            %s,
                            %s,
                            %s,
                            CURRENT_TIMESTAMP
                        );
                    """, (
                        road_id,
                        congestion_level,
                        density
                    ))

                print(
                    f"Road {road_id}: "
                    f"Congestion changed "
                    f"{previous_level} -> {congestion_level}"
                )

            # ----------------------------------
            # Redis cache
            # ----------------------------------

            if cache:

                live_data = {
                    "road_id": road_id,
                    "sensor_id": sensor_id,
                    "vehicle_count": vehicle_count,
                    "density": density,
                    "congestion_level": congestion_level
                }

                cache.hset(
                    f"traffic:road:{road_id}",
                    mapping=live_data
                )

                # Automatically expire after 60 seconds
                cache.expire(
                    f"traffic:road:{road_id}",
                    60
                )

                # ----------------------------------
                # M3 Day 2:
                # Congestion threshold monitoring
                # ----------------------------------

                if congestion_level in ("HIGH", "SEVERE"):

                    threshold_event = {
                        "road_id": road_id,
                        "sensor_id": sensor_id,
                        "vehicle_count": vehicle_count,
                        "density": density,
                        "congestion_level": congestion_level,
                        "threshold": "HIGH"
                    }

                    # Store current threshold breach
                    cache.hset(
                        f"congestion:threshold:road:{road_id}",
                        mapping=threshold_event
                    )

                    # Keep threshold event temporary
                    cache.expire(
                        f"congestion:threshold:road:{road_id}",
                        60
                    )

                    # Publish threshold-breach event
                    cache.publish(
                        "congestion_threshold_breach",
                        str(threshold_event)
                    )

                    print(
                        f"THRESHOLD BREACH | "
                        f"Road {road_id} | "
                        f"Sensor {sensor_id} | "
                        f"Level: {congestion_level} | "
                        f"Density: {density}"
                    )

                else:

                    # Remove old threshold breach when
                    # congestion falls below HIGH
                    cache.delete(
                        f"congestion:threshold:road:{road_id}"
                    )

            # ----------------------------------
            # Display live traffic information
            # ----------------------------------

            print(
                f"Road {road_id} | "
                f"Sensor {sensor_id} | "
                f"Vehicles: {vehicle_count} | "
                f"Density: {density} | "
                f"Congestion: {congestion_level}"
            )

        # ----------------------------------
        # Commit complete cycle
        # ----------------------------------

        conn.commit()

        print("--------------------------------")

        # Wait before next complete cycle
        time.sleep(5)

except KeyboardInterrupt:

    print("\nLive traffic feed stopped.")

finally:

    conn.close()

    print("Database connection closed.")