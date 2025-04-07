import math
import tkinter as tk
from tkinter import ttk

class RobotView:
    def __init__(self, parent, sim_controller):

        self.parent = parent
        self.canvas = tk.Canvas(parent, width=800, height=600)
        self.canvas.pack()
        
        self.speed_label = tk.Label(parent)
        self.speed_label.pack()

        # Use a dictionary to store last known positions for path drawing
        self.last_positions = {} # Will store {'mouse': (x, y), 'cat': (x, y)}

        # Store wheel base width for drawing (assuming same for both robots for now)
        # Get it from one of the models via sim_controller
        self.WHEEL_BASE_WIDTH = 20.0 # Default value
        if sim_controller and hasattr(sim_controller, 'robot_models') and 'mouse' in sim_controller.robot_models:
             # Safely access the width from the mouse model
             self.WHEEL_BASE_WIDTH = sim_controller.robot_models['mouse'].WHEEL_BASE_WIDTH
        # else: 
        #     print("Warning: Could not get WHEEL_BASE_WIDTH from sim_controller. Using default.")

        if sim_controller:
            sim_controller.add_state_listener(self.update_display)
        self.last_x = None
        self.last_y = None

    def update_display(self, state):
        self.parent.after(0, self._safe_update, state)

    def _safe_update(self, combined_state: dict):
        # Clear previous drawings for all robots first
        self.canvas.delete("robot") # Correct: Delete all using common tag

        # Draw each robot
        for robot_id, state in combined_state.items():
            if state: # Ensure state exists
                 self._draw_robot(robot_id, state) # Pass individual state
        
        # Update labels (e.g., for the mouse)
        if 'mouse' in combined_state and combined_state['mouse']:
            self._update_labels(combined_state['mouse']) # Pass mouse state

    def _draw_robot(self, robot_id: str, state: dict):
        """Dessiner le robot avec son ID et son état"""
        x = state['x']
        y = state['y']
        angle = state['angle']
        pen_down = state.get('pen_down', False)
        pen_color = state.get('pen_color', 'black') # Default color if not specified
        
        # Get last known position for this specific robot
        last_pos = self.last_positions.get(robot_id, (None, None))
        last_x, last_y = last_pos

        # Draw path segment only if pen down and previous position exists
        path_tag = f"path_{robot_id}" # Specific tag for path
        if pen_down and last_x is not None and last_y is not None:
            self.canvas.create_line(last_x, last_y, x, y, fill=pen_color, tags=path_tag)
        elif not pen_down:
            # If pen is up, reset last position to prevent jumps
            last_x, last_y = None, None

        # Update last position for this robot if pen is down
        if pen_down:
             self.last_positions[robot_id] = (x, y)
        else:
             # Ensure we reset if pen was lifted
             if robot_id in self.last_positions:
                 self.last_positions[robot_id] = (None, None)

        # Calculate triangle points
        size = 30 # Visual size
        front = (x + size * math.cos(angle), y + size * math.sin(angle))
        left = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(angle + math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(angle + math.pi / 2))
        right = (x + (self.WHEEL_BASE_WIDTH / 2) * math.cos(angle - math.pi / 2), y + (self.WHEEL_BASE_WIDTH / 2) * math.sin(angle - math.pi / 2))
        
        # Determine fill color based on ID (or state if needed later)
        fill_color = "gray" # Default
        if robot_id == 'mouse':
             fill_color = "blue"
        elif robot_id == 'cat':
             fill_color = "orange" # Cat color

        # Draw the robot polygon with ID-specific tag AND the general "robot" tag
        # Correct: Use tuple of tags
        self.canvas.create_polygon(front, left, right, fill=fill_color, tags=(robot_id, "robot"))

    def _update_labels(self, state: dict):
        angle_deg = math.degrees(state['angle'])
        text = f"Left: {state['left_speed']:.1f}°/s | Right: {state['right_speed']:.1f}°/s | Angle: {angle_deg:.2f}°"
        self.speed_label.config(text=text)

    def clear_robot(self):
        """Clears all robots and paths from the canvas."""
        self.canvas.delete("robot") # Correct: Clear all robot drawings via common tag
        self.canvas.delete("path_mouse") # Clear mouse path by specific tag
        self.canvas.delete("path_cat") # Clear cat path by specific tag
        # Add deletion for any other potential robot IDs if needed
        # self.canvas.delete("path_other_robot") 
        self.last_positions = {} # Reset last positions
        self.speed_label.config(text="")
