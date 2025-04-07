import math
import tkinter as tk
from tkinter import ttk

class RobotView:
    # Define default colors, can be overridden by robot state
    DEFAULT_ROBOT_COLOR = "black"
    DEFAULT_TRACE_COLOR = "blue"

    def __init__(self, parent, sim_controller):
        self.parent = parent
        # Store sim_controller to access robot properties if needed later
        self.sim_controller = sim_controller 
        self.canvas = tk.Canvas(parent, width=800, height=600)
        self.canvas.pack()
        
        # Labels might need adjustment for multiple robots, showing first robot for now
        self.speed_label = tk.Label(parent)
        self.speed_label.pack()

        # Data storage for multiple robots (using robot name as key)
        self.robot_shapes = {}
        self.robot_last_positions = {}
        self.robot_drawing_states = {}
        self.robot_trace_tags = {} # Tags for managing trace segments per robot

        # Register listener (expects a list of states now)
        sim_controller.add_state_listener(self.update_display)
        
        # Assuming all robots have the same wheel base for drawing shape
        self.WHEEL_BASE_WIDTH = sim_controller.get_robot_model(0).WHEEL_BASE_WIDTH if sim_controller.get_robot_model(0) else 20.0 

    def update_display(self, states: list):
        """Receives a list of states for all robots."""
        # Use after to schedule the update in the main Tkinter thread
        self.parent.after(0, self._safe_update, states)

    def _safe_update(self, states: list):
        """Updates the display for all robots in the main thread."""
        # Clear previous drawings for all robots managed by this view
        for name in list(self.robot_shapes.keys()): # Iterate over copy of keys
            if not any(s['name'] == name for s in states): # Robot removed?
                self.canvas.delete(f"robot_{name}")
                self.canvas.delete(f"trace_{name}")
                del self.robot_shapes[name]
                del self.robot_last_positions[name]
                del self.robot_drawing_states[name]
                del self.robot_trace_tags[name]
            else:
                self.canvas.delete(f"robot_{name}") # Clear current shape to redraw
        
        # Draw each robot based on its state
        for state in states:
            self._draw_robot(state)
            
        # Update labels (e.g., for the first robot)
        if states:
            self._update_labels(states[0])
        else:
            self._update_labels(None) # Clear labels if no robots

    def _draw_robot(self, state: dict):
        """Draws a single robot based on its state dictionary."""
        name = state.get('name', 'unknown')
        x, y = state['x'], state['y']
        direction_rad = math.radians(state['angle']) # Convert degrees to radians
        drawing_active = state['drawing_active']
        drawing_color = state.get('drawing_color', self.DEFAULT_TRACE_COLOR) # Get color from state
        robot_color = drawing_color # Use drawing color for robot body too, for distinction

        last_pos = self.robot_last_positions.get(name)
        current_trace_tag = f"trace_{name}"

        # Draw trace segment if drawing is active and position changed
        if drawing_active and last_pos:
            last_x, last_y = last_pos
            if abs(x - last_x) > 0.1 or abs(y - last_y) > 0.1:
                self.canvas.create_line(last_x, last_y, x, y, fill=drawing_color, width=2, tags=(current_trace_tag, "trace_all"))
        
        # Update last position for this robot
        self.robot_last_positions[name] = (x, y)
        self.robot_drawing_states[name] = drawing_active
        if name not in self.robot_trace_tags:
             self.robot_trace_tags[name] = current_trace_tag

        # Draw the robot shape (polygon)
        size = 30 # Robot size
        current_robot_tag = f"robot_{name}"
        front = (x + size * math.cos(direction_rad), y + size * math.sin(direction_rad))
        # Calculate left/right points based on wheel base
        left = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_rad + math.pi / 2), 
                y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_rad + math.pi / 2))
        right = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(direction_rad - math.pi / 2), 
                 y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(direction_rad - math.pi / 2))
        
        # Store the canvas ID of the shape if needed, otherwise just draw
        shape_id = self.canvas.create_polygon(front, left, right, fill=robot_color, tags=(current_robot_tag, "robot_all"))
        self.robot_shapes[name] = shape_id # Store the ID

    def _update_labels(self, state: dict | None):
        """Updates labels, showing info for the first robot if available."""
        if state:
            angle_deg = state['angle'] # Angle is already in degrees from model
            text = f"{state.get('name', 'Robot')}: L:{state['left_speed']:.0f} R:{state['right_speed']:.0f} | Angle: {angle_deg:.1f}°"
        else:
            text = "No robots active."
        self.speed_label.config(text=text)

    def clear_robot(self):
        """Clears all robots and traces from the canvas."""
        print("Clearing all robots and traces.")
        self.canvas.delete("robot_all")
        self.canvas.delete("trace_all") 
        self.robot_shapes = {}
        self.robot_last_positions = {}
        self.robot_drawing_states = {}
        self.robot_trace_tags = {}

        if self.speed_label:
            self.speed_label.config(text="")
