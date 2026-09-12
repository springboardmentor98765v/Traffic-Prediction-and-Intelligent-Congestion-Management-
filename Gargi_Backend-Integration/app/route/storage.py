routes = {}


def save_route(route):
    routes[route["route_id"]] = route


def get_route(route_id):
    return routes.get(route_id)
