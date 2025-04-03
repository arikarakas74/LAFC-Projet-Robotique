import math
def point_in_polygon(x, y, polygon):
    """ Use ray casting to check if a point is inside a polygon """
    
    if isinstance(polygon, tuple):  
        polygon = polygon[0]

    n = len(polygon)
    inside = False
    polygon=scale_polygon(polygon,1.5)
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside
def scale_polygon(polygon, factor):
    # Calculer le centroïde
    cx = sum(x for x, y in polygon) / len(polygon)
    cy = sum(y for x, y in polygon) / len(polygon)
    
    # Appliquer le facteur d'échelle à chaque sommet par rapport au centroïde
    scaled_polygon = [
        (cx + factor * (x - cx), cy + factor * (y - cy))
        for x, y in polygon
    ]
    
    return scaled_polygon




def normalize_angle( angle):
    """ Normalizes an angle to the range [-pi, pi] """
    while angle > math.pi:
        angle -= 2 * math.pi
    while angle < -math.pi:
        angle += 2 * math.pi
    return angle
