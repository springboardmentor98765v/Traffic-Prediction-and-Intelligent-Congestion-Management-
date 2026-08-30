from predictor import predict_traffic, get_traffic_condition


def main():

    # Example input
    road_id = 2
    hour = 18
    day_of_week = 3
    month = 11

    # Get traffic prediction
    prediction = predict_traffic(
        road_id,
        hour,
        day_of_week,
        month
    )

    # Determine traffic condition
    condition = get_traffic_condition(prediction)

    # Display result
    print()
    print("Traffic Prediction")
    print("-------------------")
    print("Road ID:", road_id)
    print("Hour:", hour)
    print("Day of Week:", day_of_week)
    print("Month:", month)
    print("Predicted Vehicle Count:", prediction)
    print("Traffic Condition:", condition)


if __name__ == "__main__":
    main()