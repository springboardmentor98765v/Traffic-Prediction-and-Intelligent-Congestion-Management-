def predict_by_density(density):
    if density < 20:
        return "LOW"
    elif density <= 50:
        return "MEDIUM"
    else:
        return "HIGH"


def adjust_for_time(congestion, hour):
    if 7 <= hour <= 10 or 17 <= hour <= 20:
        if congestion == "LOW":
            return "MEDIUM"
        elif congestion == "MEDIUM":
            return "HIGH"

    return congestion


def predict_congestion(density, hour):
    congestion = predict_by_density(density)
    congestion = adjust_for_time(congestion, hour)

    return congestion