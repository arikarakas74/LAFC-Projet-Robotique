from utils.geometry import point_in_polygon
from utils.geometry3d import point_in_cuboid
from typing import Tuple, List, Dict, Any, Optional

class MapModel:
    """Stores map data (obstacles, start/end positions) in 3D."""

    # Map dimensions
    MAP_WIDTH = 800
    MAP_HEIGHT = 600
    MAP_DEPTH = 400  # New depth dimension for 3D

    def __init__(self):
        # 2D obstacles for backward compatibility
        self.obstacles = {}  # Format: {obstacle_id: (points, polygon_id, line_ids)}
        
        # 3D obstacles - stored as cuboids with min/max points
        self.obstacles_3d = {}  # Format: {obstacle_id: (min_point, max_point, model_id)}
        
        # Starting position (x, y) - will be (x, y, 0) in 3D
        self.start_position = (0, 0)
        
        # End position
        self.end_position = None
        
        # Drawing state
        self.current_shape = None
        self.current_points = []
        self.current_lines = []  # Track lines created during drawing
        
        # Dragging state
        self.dragging_obstacle = None  # Track which obstacle is being dragged
        self.drag_start = None  # Track the starting point of the drag
        
        # Event listeners
        self.event_listeners = []  # List to store event listeners

    def add_event_listener(self, listener):
        self.event_listeners.append(listener)

    def notify_event_listeners(self, event_type, **kwargs):
        for listener in self.event_listeners:
            listener(event_type, **kwargs)

    def reset(self):
        self.obstacles.clear()
        self.obstacles_3d.clear()
        self.start_position = None
        self.end_position = None
        self.notify_event_listeners("map_reset")

    def set_start_position(self, position):
        """Sets the start position. In 3D mode, z is assumed to be 0."""
        if len(position) == 2:
            x, y = position
            z = 0  # Default z position is ground level
        else:
            x, y, z = position
        
        self.start_position = (x, y)  # Keep 2D for backward compatibility
        self.notify_event_listeners("start_position_changed", position=(x, y, z))

    def add_obstacle(self, obstacle_id, points, polygon_id=None, line_ids=None):
        """Adds a 2D obstacle and notifies listeners (for backward compatibility)."""
        self.obstacles[obstacle_id] = (points, polygon_id, line_ids)
        self.notify_event_listeners("obstacle_added", obstacle_id=obstacle_id, points=points, 
                                    polygon_id=polygon_id, line_ids=line_ids)

    def add_obstacle_3d(self, obstacle_id, min_point, max_point, model_id=None):
        """Adds a 3D obstacle defined by its bounding box and notifies listeners."""
        self.obstacles_3d[obstacle_id] = (min_point, max_point, model_id)
        self.notify_event_listeners("obstacle_3d_added", obstacle_id=obstacle_id, 
                                    min_point=min_point, max_point=max_point, model_id=model_id)

    def remove_obstacle(self, obstacle_id):
        """Removes an obstacle (either 2D or 3D) and notifies listeners."""
        if obstacle_id in self.obstacles:
            del self.obstacles[obstacle_id]
            self.notify_event_listeners("obstacle_removed", obstacle_id=obstacle_id)
        elif obstacle_id in self.obstacles_3d:
            del self.obstacles_3d[obstacle_id]
            self.notify_event_listeners("obstacle_3d_removed", obstacle_id=obstacle_id)

    def move_obstacle(self, obstacle_id, new_points):
        """Moves a 2D obstacle to new points and notifies listeners."""
        if obstacle_id in self.obstacles:
            self.obstacles[obstacle_id] = new_points
            self.notify_event_listeners("obstacle_moved", obstacle_id=obstacle_id, new_points=new_points)

    def move_obstacle_3d(self, obstacle_id, new_min_point, new_max_point):
        """Moves a 3D obstacle to a new position and notifies listeners."""
        if obstacle_id in self.obstacles_3d:
            old_data = self.obstacles_3d[obstacle_id]
            model_id = old_data[2] if len(old_data) > 2 else None
            self.obstacles_3d[obstacle_id] = (new_min_point, new_max_point, model_id)
            self.notify_event_listeners("obstacle_3d_moved", obstacle_id=obstacle_id, 
                                       min_point=new_min_point, max_point=new_max_point)
    
    def is_collision(self, x, y):
        """Checks for collisions with 2D obstacles."""
        for obstacle_data in self.obstacles.values():
            points = obstacle_data[0]  # Get the points from the obstacle data
            if point_in_polygon(x, y, points):
                return True  
        return False  
    
    def is_collision_3d(self, x, y, z):
        """Checks for collisions with 3D obstacles."""
        # First check 2D obstacles (treat them as extending infinitely in z-direction)
        if self.is_collision(x, y):
            return True
            
        # Then check 3D obstacles
        for min_point, max_point, _ in self.obstacles_3d.values():
            if point_in_cuboid(x, y, z, min_point, max_point):
                return True
        return False
    
    def is_out_of_bounds(self, x, y):
        """Checks if the position is outside the 2D map boundaries."""
        if x < 0 or x > self.MAP_WIDTH:
            return True
        if y < 0 or y > self.MAP_HEIGHT:
            return True
        return False
        
    def is_out_of_bounds_3d(self, x, y, z):
        """Checks if the position is outside the 3D map boundaries."""
        if self.is_out_of_bounds(x, y):
            return True
        if z < 0 or z > self.MAP_DEPTH:
            return True
        return False