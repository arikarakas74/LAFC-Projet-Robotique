import math
from typing import Dict, List, Tuple, Optional, Callable, Any
from copy import deepcopy

class MapModel:
    """Stores map data (obstacles, start/end positions) in 3D."""
    
    def __init__(self):
        """Initialize the map model with empty data structures."""
        # 3D bounding boxes for obstacles: { id: (min_point, max_point, model_id) }
        self.obstacles_3d = {}
        
        # Start position (x, y, z) - default is center of map
        self.start_position = None
        
        # End position (x, y, z) - initially not set
        self.end_position = None
        
        # Map boundaries (default values for a 800x600 map)
        self.width = 800
        self.height = 600
        self.depth = 200  # Height limit for 3D
        
        # Event listeners
        self.event_listeners = []
    
    def add_event_listener(self, callback: Callable[[str, Dict[str, Any]], None]) -> None:
        """Add an event listener to be notified of map changes."""
        self.event_listeners.append(callback)
    
    def notify_event_listeners(self, event_type: str, **kwargs) -> None:
        """Notify all event listeners of an event."""
        for listener in self.event_listeners:
            try:
                listener(event_type, kwargs)
            except Exception as e:
                print(f"Error notifying listener: {e}")
    
    def set_start_position(self, position):
        """Sets the start position in 3D space."""
        if len(position) == 2:
            x, y = position
            z = 0  # Default z position is ground level
        else:
            x, y, z = position
        
        self.start_position = (x, y, z)
        self.notify_event_listeners("start_position_changed", position=(x, y, z))

    def set_end_position(self, position):
        """Sets the end position (beacon) in 3D space."""
        if len(position) == 2:
            x, y = position
            z = 0  # Default z position is ground level
        else:
            x, y, z = position
        
        self.end_position = (x, y, z)
        self.notify_event_listeners("end_position_changed", position=(x, y, z))

    def add_obstacle_3d(self, obstacle_id, min_point, max_point, model_id=None):
        """Adds a 3D obstacle defined by its bounding box and notifies listeners."""
        self.obstacles_3d[obstacle_id] = (min_point, max_point, model_id)
        self.notify_event_listeners("obstacle_3d_added", obstacle_id=obstacle_id, 
                                   min_point=min_point, max_point=max_point, model_id=model_id)
    
    def remove_obstacle_3d(self, obstacle_id):
        """Removes a 3D obstacle by ID."""
        if obstacle_id in self.obstacles_3d:
            del self.obstacles_3d[obstacle_id]
            self.notify_event_listeners("obstacle_3d_removed", obstacle_id=obstacle_id)
    
    def is_collision_3d(self, x, y, z):
        """Check if the given position collides with any 3D obstacle."""
        # Robot dimensions (approximated as a sphere for simplicity)
        robot_radius = 10.0  # cm
        
        for min_point, max_point, _ in self.obstacles_3d.values():
            # Expand the obstacle by the robot's radius for collision detection
            expanded_min = (min_point[0] - robot_radius, min_point[1] - robot_radius, min_point[2] - robot_radius)
            expanded_max = (max_point[0] + robot_radius, max_point[1] + robot_radius, max_point[2] + robot_radius)
            
            # Check if the robot's center point is inside the expanded obstacle
            if (expanded_min[0] <= x <= expanded_max[0] and
                expanded_min[1] <= y <= expanded_max[1] and
                expanded_min[2] <= z <= expanded_max[2]):
                return True
        
        return False
    
    def is_out_of_bounds_3d(self, x, y, z):
        """Check if the given position is outside the map boundaries."""
        # Add a small buffer to prevent the robot from going exactly to the edge
        buffer = 10.0  # cm
        
        return (x < buffer or x > self.width - buffer or
                y < buffer or y > self.height - buffer or
                z < 0 or z > self.depth)
    
    def clear(self):
        """Clear all objects and positions from the map."""
        self.obstacles_3d.clear()
        self.start_position = None
        self.end_position = None
        self.notify_event_listeners("map_cleared")