import math
import numpy as np
import tkinter as tk
from tkinter import ttk
import sys
import platform
from OpenGL import GL, GLU
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageTk
import time

class RobotView3D:
    """Renders the robot and environment in 3D using OpenGL."""
    
    def __init__(self, parent, sim_controller):
        """
        Initializes the 3D robot view.
        
        Args:
            parent: The parent widget
            sim_controller: The simulation controller
        """
        self.parent = parent
        self.sim_controller = sim_controller
        self.width = 800
        self.height = 600
        self.wheel_base_width = sim_controller.robot_model.WHEEL_BASE_WIDTH
        self.robot_height = sim_controller.robot_model.HEIGHT
        
        # Rendering texture
        self.texture_id = None
        
        # Camera parameters
        self.camera_distance = 150.0
        self.camera_height = 100.0
        self.camera_angle_x = 30.0  # pitch
        self.camera_angle_y = 0.0   # yaw
        self.follow_robot = True    # Whether camera follows the robot
        
        # Trail points to show robot path
        self.trail_points = []
        self.max_trail_points = 5000  # Increased from 100 to 5000 for much longer trails
        
        # Create a frame for the OpenGL rendering
        self.frame = tk.Frame(parent, width=self.width, height=self.height)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a canvas for drawing the rendered image
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Bind mouse click event to set beacon
        self.canvas.bind("<Button-1>", self.handle_click)
        
        # Create a label for displaying robot state
        self.info_label = tk.Label(parent, text="", justify=tk.LEFT, anchor="w")
        self.info_label.pack(fill=tk.X)
        
        # Create a PIL Image to render to
        self.image = Image.new("RGB", (self.width, self.height))
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        # Since we can't use OpenGL directly with Tkinter on macOS easily,
        # we'll simulate the 3D rendering with a simpler approach
        print("3D rendering is simulated due to OpenGL integration limitations")
        
        # Add state listener
        sim_controller.add_state_listener(self.update_display)
        
        # Start render loop
        self._render_loop()
        
    def _init_opengl(self):
        """This is a dummy function as we're not using real OpenGL in this version."""
        pass
        
    def update_display(self, state):
        """Updates the display with the new robot state."""
        # Add new trail point
        self.trail_points.append((state['x'], state['y'], state['z']))
        if len(self.trail_points) > self.max_trail_points:
            self.trail_points.pop(0)
            
        # Update info label
        angle_yaw = math.degrees(state['yaw'])
        angle_pitch = math.degrees(state['pitch'])
        angle_roll = math.degrees(state['roll'])
        
        info_text = (
            f"X: {state['x']:.1f} | Y: {state['y']:.1f} | Z: {state['z']:.1f} | "
            f"Pitch: {angle_pitch:.1f}° | Yaw: {angle_yaw:.1f}° | Roll: {angle_roll:.1f}° | "
            f"Left: {state['left_speed']:.1f}°/s | Right: {state['right_speed']:.1f}°/s"
        )
        self.info_label.config(text=info_text)
        
    def _render_loop(self):
        """Main render loop for the 3D view."""
        self._render_scene()
        self.parent.after(16, self._render_loop)  # ~60 FPS
        
    def _render_scene(self):
        """Renders a simplified 2D representation instead of 3D."""
        # Create a new image
        image = Image.new("RGB", (self.width, self.height), (50, 50, 50))
        
        # Get current robot state
        state = self.sim_controller.robot_model.get_state()
        robot_x = state['x']
        robot_y = state['y']
        robot_z = state['z']
        pitch = state['pitch']
        yaw = state['yaw']
        roll = state['roll']
        
        # Draw a grid (simplified)
        self._draw_simplified_grid(image)
        
        # Draw a simple path for the robot trail (simplified)
        self._draw_simplified_trail(image)
        
        # Draw a simple representation of obstacles (simplified)
        self._draw_simplified_obstacles(image)
        
        # Draw the beacon (end position) if it exists
        self._draw_beacon(image)
        
        # Draw a simple representation of the robot (simplified)
        self._draw_simplified_robot(image, robot_x, robot_y, robot_z, pitch, yaw, roll)
        
        # Update the canvas with the new image
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
    def _draw_simplified_grid(self, image):
        """Draws a simplified grid on the image."""
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Draw grid lines
        grid_size = 50
        for x in range(0, self.width, grid_size):
            draw.line([(x, 0), (x, self.height)], fill=(70, 70, 70), width=1)
        for y in range(0, self.height, grid_size):
            draw.line([(0, y), (self.width, y)], fill=(70, 70, 70), width=1)
            
        # Draw coordinate axes
        draw.line([(0, self.height//2), (self.width, self.height//2)], fill=(150, 150, 150), width=2)
        draw.line([(self.width//2, 0), (self.width//2, self.height)], fill=(150, 150, 150), width=2)
        
    def _draw_simplified_trail(self, image):
        """Draws a simplified trail on the image."""
        if len(self.trail_points) < 2:
            return
            
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Transform 3D trail points to 2D screen coordinates
        screen_points = []
        for point in self.trail_points:
            x, y, z = point
            # Simple projection (ignoring z for simplicity)
            screen_x = int(self.width/2 + x - self.sim_controller.robot_model.x)
            screen_y = int(self.height/2 - y + self.sim_controller.robot_model.y)
            if 0 <= screen_x < self.width and 0 <= screen_y < self.height:
                screen_points.append((screen_x, screen_y))
        
        # Draw trail
        if len(screen_points) >= 2:
            draw.line(screen_points, fill=(255, 215, 0), width=3)
            
    def _draw_simplified_obstacles(self, image):
        """Draws simplified obstacles on the image."""
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Draw 3D obstacles as rectangles
        for min_point, max_point, _ in self.sim_controller.map_model.obstacles_3d.values():
            x1, y1, z1 = min_point
            x2, y2, z2 = max_point
            
            # Convert to screen coordinates
            screen_x1 = int(self.width/2 + x1 - self.sim_controller.robot_model.x)
            screen_y1 = int(self.height/2 - y2 + self.sim_controller.robot_model.y)
            screen_x2 = int(self.width/2 + x2 - self.sim_controller.robot_model.x)
            screen_y2 = int(self.height/2 - y1 + self.sim_controller.robot_model.y)
            
            # Draw rectangle
            draw.rectangle([(screen_x1, screen_y1), (screen_x2, screen_y2)], 
                           fill=(200, 50, 50), outline=(255, 100, 100))
            
        # Draw 2D obstacles as polygons
        for obstacle_data in self.sim_controller.map_model.obstacles.values():
            points = obstacle_data[0]  # Extract points from the tuple
            if not points or len(points) < 3:
                continue
                
            # Convert to screen coordinates
            screen_points = []
            for point in points:
                screen_x = int(self.width/2 + point[0] - self.sim_controller.robot_model.x)
                screen_y = int(self.height/2 - point[1] + self.sim_controller.robot_model.y)
                screen_points.append((screen_x, screen_y))
                
            # Draw polygon
            draw.polygon(screen_points, fill=(200, 50, 50), outline=(255, 100, 100))
            
    def _draw_simplified_robot(self, image, x, y, z, pitch, yaw, roll):
        """Draws a simplified robot on the image."""
        from PIL import ImageDraw
        draw = ImageDraw.Draw(image)
        
        # Robot dimensions
        robot_size = 30
        
        # Draw a triangle for the robot
        # Calculate vertices based on robot position and yaw
        x1 = self.width/2
        y1 = self.height/2
        x2 = x1 + robot_size * math.cos(yaw + math.pi*2/3)
        y2 = y1 - robot_size * math.sin(yaw + math.pi*2/3)
        x3 = x1 + robot_size * math.cos(yaw + math.pi*4/3)
        y3 = y1 - robot_size * math.sin(yaw + math.pi*4/3)
        
        # Draw robot body
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(0, 0, 200), outline=(100, 100, 255))
        
        # Draw direction indicator
        dir_x = x1 + robot_size * math.cos(yaw)
        dir_y = y1 - robot_size * math.sin(yaw)
        draw.line([(x1, y1), (dir_x, dir_y)], fill=(255, 255, 0), width=3)
        
    def _draw_beacon(self, image):
        """Draws the beacon (end position) on the image if it exists."""
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(image)
        
        # Get the beacon position from the map model
        beacon_pos = self.sim_controller.map_model.end_position
        
        if beacon_pos is not None:
            beacon_x, beacon_y = beacon_pos
            robot_x = self.sim_controller.robot_model.x
            robot_y = self.sim_controller.robot_model.y
            
            # Transform to screen coordinates
            screen_x = int(self.width/2 + beacon_x - robot_x)
            screen_y = int(self.height/2 - beacon_y + robot_y)
            
            # Draw a distinctive beacon marker (a star-like shape)
            radius = 15
            inner_radius = 7
            points = []
            
            # Create a star shape with 5 points
            for i in range(10):
                angle = math.pi/2 + i * math.pi * 2 / 10
                r = radius if i % 2 == 0 else inner_radius
                points.append((
                    screen_x + r * math.cos(angle),
                    screen_y + r * math.sin(angle)
                ))
            
            # Draw the star in bright green
            draw.polygon(points, fill=(0, 255, 100), outline=(0, 200, 0))
            
            # Add a dot in the center
            draw.ellipse((screen_x-3, screen_y-3, screen_x+3, screen_y+3), fill=(0, 100, 0))
            
            # Add a "BEACON" text below the marker
            try:
                # Try to get a font, fall back to default if not available
                font = ImageFont.truetype("Arial", 12)
            except IOError:
                font = ImageFont.load_default()
                
            text = "BEACON"
            text_width = draw.textlength(text, font=font)
            draw.text((screen_x - text_width/2, screen_y + radius + 5), text, font=font, fill=(0, 255, 100))
        
    def clear_robot(self, clear_trail=True):
        """
        Clears the robot and optionally the trail.
        
        Args:
            clear_trail: If True, clears the trail. If False, preserves the trail.
        """
        if clear_trail:
            self.trail_points = []
        
    def toggle_follow_mode(self, follow=None):
        """Toggles camera follow mode."""
        if follow is not None:
            self.follow_robot = follow
        else:
            self.follow_robot = not self.follow_robot
            print(f"Follow mode: {'Enabled' if self.follow_robot else 'Disabled'}")

    def handle_click(self, event):
        """Handle mouse click to set the beacon (end position)."""
        x, y = event.x, event.y
        
        # Convert screen coordinates to world coordinates
        robot_x = self.sim_controller.robot_model.x
        robot_y = self.sim_controller.robot_model.y
        
        # Calculate world coordinates from screen position
        world_x = robot_x + (x - self.width/2)
        world_y = robot_y - (y - self.height/2)
        
        # Store previous beacon position to detect changes
        previous_beacon = self.sim_controller.map_model.end_position
        
        # Set the beacon position in the map model
        self.sim_controller.map_model.set_end_position((world_x, world_y))
        
        # Show a message that beacon has been set
        self.info_label.config(text=f"Beacon set at ({world_x:.1f}, {world_y:.1f})")
        
        # If a strategy is currently running, check if it's a FollowBeaconStrategy
        # and trigger an update to the beacon position
        if self.sim_controller.is_strategy_running():
            strategy_executor = self.sim_controller.strategy_executor
            current_strategy = strategy_executor.current_strategy
            
            # If we've interrupted something like a triangle strategy, start following the beacon
            if not isinstance(current_strategy, FollowBeaconStrategy):
                self.sim_controller.strategy_executor.stop()
                self.sim_controller.position_logger.info(f"Stopped existing strategy to follow new beacon at ({world_x:.1f}, {world_y:.1f})")
                # Start following the beacon after a brief pause to ensure the robot has stopped
                self.after(100, self.sim_controller.follow_beacon)
            else:
                # If already following a beacon, just reset the state to pick up the new position
                current_strategy.reset_state()
                self.sim_controller.position_logger.info(f"Updating beacon target to ({world_x:.1f}, {world_y:.1f})")
        
        # Force immediate redraw to show the beacon
        self._render_scene() 