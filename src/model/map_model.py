from utils.geometry import point_in_polygon

class MapModel:
    """Stores the map data: obstacles, start/end positions."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.obstacles = {}  # Store obstacles as {id: (points, polygon_id, line_ids)}
        self.start_position = None
        self.end_position = None
        self.current_shape = None
        self.current_points = []
        self.current_lines = []  # Track lines created during drawing
        self.dragging_obstacle = None  # Track which obstacle is being dragged
        self.drag_start = None  # Track the starting point of the drag
        self.event_listeners = []  # List to store event listeners



    def add_event_listener(self, listener):
        """Adds an event listener to the map model."""
        self.event_listeners.append(listener)

    def notify_event_listeners(self, event_type, **kwargs):
        """Notifies all event listeners of an event."""
        for listener in self.event_listeners:
            listener(event_type, **kwargs)

    def reset(self):
        """Resets the map data."""
        self.obstacles.clear()
        self.start_position = None
        self.end_position = None
        self.current_points = []
        self.current_shape = None
        self.current_lines = []
        self.dragging_obstacle = None
        self.drag_start = None
        self.notify_event_listeners("map_reset")

    def set_start_position(self, position):
        """Sets the start position and notifies listeners."""
        self.start_position = position
        self.robot_x, self.robot_y = position
        self.notify_event_listeners("start_position_changed", position=position)

    def set_end_position(self, position):
        """Sets the end position and notifies listeners."""
        self.end_position = position
        self.notify_event_listeners("end_position_changed", position=position)

    def add_obstacle(self, obstacle_id, points, polygon_id, line_ids):
        """Adds an obstacle and notifies listeners."""
        self.obstacles[obstacle_id] = (points, polygon_id, line_ids)
        self.notify_event_listeners("obstacle_added", obstacle_id=obstacle_id, points=points, polygon_id=polygon_id, line_ids=line_ids)

    def remove_obstacle(self, obstacle_id):
        """Removes an obstacle and notifies listeners."""
        if obstacle_id in self.obstacles:
            del self.obstacles[obstacle_id]
            self.notify_event_listeners("obstacle_removed", obstacle_id=obstacle_id)
    
    def is_collision(self, x, y):
        """Only check whether it affects translation, without affecting rotation."""
        for obstacle_id, (points, _, _) in self.obstacles.items():
            if point_in_polygon(x, y, points):
                return True  
        return False  
    
    def is_out_of_bounds(self, x, y):
        """Check whether the robot exceeds the map boundaries."""
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

