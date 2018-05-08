import math


def distance_on_unit_sphere(lat1, long1, lat2, long2):
    """
    This function return the distance between two latitude-longitude points.

    Args:
        lat1: latitudinal position of first location
        long1: longitudinal position of first location
        lat2: latitudinal position of second location
        long2: longitudinal position of second location

    Returns:
        A tuple that contains the distance between the two locations in miles and kilometers, respectively

        Output = (distance in miles, distance in kilometes)
    """

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    lat1 = float(lat1)
    lat2 = float(lat2)
    long1 = float(long1)
    long2 = float(long2)

    # import pdb; pdb.set_trace()
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = long1*degrees_to_radians
    theta2 = long2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    arc = math.acos( cos )
    mile = 3960*arc
    km = 6373*arc

    # Remember to multiply arc by the radius of the earth
    # in your favorite set of units to get length.
    return mile, km


def recommended_items_based_on_location(profile, recommended_items):
    items = []

    for item in recommended_items:
        if item.latitude and item.longitude:
            distance = distance_on_unit_sphere(item.latitude, item.longitude, profile.current_latitude, profile.current_longitude)[1]

            if float(distance) <= float(profile.distance_range):
                items.append(item)

    return items
