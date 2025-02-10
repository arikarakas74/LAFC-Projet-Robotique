class MapModel:
    """Stores the map data: obstacles, start/end positions."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.robot_x = 0
        self.robot_y = 0
        self.robot_theta = 0
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
        self.notify_event_listeners("start_position_changed", position=position)

    def set_end_position(self, position):
        """Sets the end position and notifies listeners."""
        self.end_position = position
        self.notify_event_listeners("end_position_changed", position=position)

    def add_obstacle(self, obstacle_id, points, polygon_id, line_ids):
        """Adds an obstacle and notifies listeners."""
        self.obstacles[obstacle_id] = (points, polygon_id, line_ids)
        self.notify_event_listeners("obstacle_added", obstacle_id=obstacle_id, points=points, polygon_id=polygon_id, line_ids=line_ids)

    def delete_obstacle(self, obstacle_id):
        """Deletes an obstacle and notifies listeners."""
        if obstacle_id in self.obstacles:
            del self.obstacles[obstacle_id]
            self.notify_event_listeners("obstacle_deleted", obstacle_id=obstacle_id)

    def remove_obstacle(self, obstacle_id):
        """Removes an obstacle and notifies listeners."""
        if obstacle_id in self.obstacles:
            del self.obstacles[obstacle_id]
            self.notify_event_listeners("obstacle_removed", obstacle_id=obstacle_id)
