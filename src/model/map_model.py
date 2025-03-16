from utils.geometry import point_in_polygon

class MapModel:
    """Stocke les données de la carte (obstacles, positions de départ/arrivée)."""

    def __init__(self):
        
        self.obstacles = {}  # Format: {obstacle_id: points}
        self.start_position = (0,0)
        self.end_position = None
        self.current_shape = None
        self.current_points = []
        self.current_lines = []  # Track lines created during drawing
        self.dragging_obstacle = None  # Track which obstacle is being dragged
        self.drag_start = None  # Track the starting point of the drag
        self.event_listeners = []  # List to store event listeners

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

    def add_obstacle(self, obstacle_id, points, polygon_id, line_ids):
        """Adds an obstacle and notifies listeners."""
        self.obstacles[obstacle_id] = (points, polygon_id, line_ids)
        self.notify_event_listeners("obstacle_added", obstacle_id=obstacle_id, points=points, polygon_id=polygon_id, line_ids=line_ids)

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
            if point_in_polygon(x, y, points):
                return True  
        return False  
    
    def is_out_of_bounds(self, x, y):
        """Vérifie si le robot sort des limites de la carte."""
        MAP_WIDTH = 800  
        MAP_HEIGHT = 600  
         

        if x  < 0:
                return True 
        if x > MAP_WIDTH:
                return True
        if y < 0:
                return True
        if y > MAP_HEIGHT:
                return True