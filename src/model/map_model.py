from utils.geometry import point_in_polygon

class MapModel:
    """Stocke les données de la carte (obstacles, positions de départ/arrivée)."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.obstacles = {}  # Format: {obstacle_id: points}
        self.start_position = (10, 10)
        self.end_position = None
        self.event_listeners = []

    def add_event_listener(self, listener):
        self.event_listeners.append(listener)

    def notify_event_listeners(self, event_type, **kwargs):
        for listener in self.event_listeners:
            listener(event_type, **kwargs)

    def reset(self):
        self.obstacles.clear()
        self.start_position = None
        self.end_position = None
        self.notify_event_listeners("map_reset")

    def set_start_position(self, position):
        self.start_position = position
        self.notify_event_listeners("start_position_changed", position=position)

    def set_end_position(self, position):
        self.end_position = position
        self.notify_event_listeners("end_position_changed", position=position)

    def add_obstacle(self, obstacle_id, points):
        self.obstacles[obstacle_id] = points
        self.notify_event_listeners("obstacle_added", obstacle_id=obstacle_id, points=points)

    def remove_obstacle(self, obstacle_id):
        if obstacle_id in self.obstacles:
            del self.obstacles[obstacle_id]
            self.notify_event_listeners("obstacle_removed", obstacle_id=obstacle_id)

    def move_obstacle(self, obstacle_id, new_points):
        if obstacle_id in self.obstacles:
            self.obstacles[obstacle_id] = new_points
            self.notify_event_listeners("obstacle_moved", obstacle_id=obstacle_id, new_points=new_points)
    
    def is_collision(self, x, y):
        """Vérifie les collisions avec les obstacles (version corrigée)"""
        for points in self.obstacles.values():
            if point_in_polygon((x, y), points):
                return True  
        return False  
    
    def is_out_of_bounds(self, x, y):
        """Vérifie si le robot sort des limites de la carte."""
        MAP_WIDTH = 800  
        MAP_HEIGHT = 600  
        ROBOT_RADIUS = 10 

        if x - ROBOT_RADIUS < 0:
            return "LEFT" 
        if x + ROBOT_RADIUS > MAP_WIDTH:
            return "RIGHT" 
        if y - ROBOT_RADIUS < 0:
            return "TOP" 
        if y + ROBOT_RADIUS > MAP_HEIGHT:
            return "BOTTOM"