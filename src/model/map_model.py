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