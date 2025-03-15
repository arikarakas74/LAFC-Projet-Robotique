import math
import numpy as np
import tkinter as tk
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
        self.max_trail_points = 100
        
        # Create OpenGL-compatible canvas
        self.canvas = tk.Canvas(parent, width=self.width, height=self.height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create a label for displaying robot state
        self.info_label = tk.Label(parent, text="", justify=tk.LEFT, anchor="w")
        self.info_label.pack(fill=tk.X)
        
        # Initialize OpenGL context
        self._init_opengl()
        
        # Add state listener
        sim_controller.add_state_listener(self.update_display)
        
        # Start render loop
        self._render_loop()
        
    def _init_opengl(self):
        """Initializes the OpenGL context and settings."""
        # Create a PIL Image to render to
        self.image = Image.new("RGB", (self.width, self.height))
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
        # Initialize OpenGL
        self.context = GL.glContext(self.width, self.height)
        self.context.makeCurrent()
        
        # Set up initial OpenGL state
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        
        # Set up projection matrix
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, self.width / self.height, 0.1, 1000.0)
        
        # Set up view matrix
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        # Set up light
        light_position = [0.0, 10.0, 10.0, 1.0]
        light_ambient = [0.2, 0.2, 0.2, 1.0]
        light_diffuse = [1.0, 1.0, 1.0, 1.0]
        light_specular = [1.0, 1.0, 1.0, 1.0]
        
        glLightfv(GL_LIGHT0, GL_POSITION, light_position)
        glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
        glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
        glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
        
        # Create checkerboard texture for the ground
        self._create_ground_texture()
        
    def _create_ground_texture(self):
        """Creates a checkerboard texture for the ground plane."""
        tex_size = 64
        texture_data = []
        
        for y in range(tex_size):
            for x in range(tex_size):
                if (x // 8 + y // 8) % 2 == 0:
                    texture_data.extend([0.9, 0.9, 0.9])  # Light gray
                else:
                    texture_data.extend([0.4, 0.4, 0.4])  # Dark gray
                    
        texture_data = np.array(texture_data, dtype=np.float32)
        
        self.texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, tex_size, tex_size, 0, GL_RGB, GL_FLOAT, texture_data)
        
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
        """Renders the 3D scene with robot and environment."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        # Get current robot state
        state = self.sim_controller.robot_model.get_state()
        robot_x = state['x']
        robot_y = state['y']
        robot_z = state['z']
        pitch = state['pitch']
        yaw = state['yaw']
        roll = state['roll']
        
        # Set up camera
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        
        if self.follow_robot:
            # Position camera relative to robot
            camera_x = robot_x - self.camera_distance * math.sin(yaw)
            camera_y = robot_y - self.camera_distance * math.cos(yaw)
            camera_z = robot_z + self.camera_height
            
            # Look at robot
            gluLookAt(
                camera_x, camera_y, camera_z,  # Camera position
                robot_x, robot_y, robot_z,     # Look at point (robot position)
                0.0, 0.0, 1.0                  # Up vector
            )
        else:
            # Fixed camera with orbit controls
            glRotatef(self.camera_angle_x, 1.0, 0.0, 0.0)
            glRotatef(self.camera_angle_y, 0.0, 1.0, 0.0)
            glTranslatef(-robot_x, -robot_y, -robot_z - self.camera_height)
            
        # Draw grid ground
        self._draw_ground()
        
        # Draw axes
        self._draw_axes()
        
        # Draw robot trail
        self._draw_trail()
        
        # Draw obstacles
        self._draw_obstacles()
        
        # Draw robot
        self._draw_robot(robot_x, robot_y, robot_z, pitch, yaw, roll)
        
        # Swap buffers to display the rendered image
        self.context.swapBuffers()
        
        # Update the Tkinter canvas with the OpenGL rendered image
        glReadBuffer(GL_FRONT)
        pixels = glReadPixels(0, 0, self.width, self.height, GL_RGB, GL_UNSIGNED_BYTE)
        image = Image.frombytes("RGB", (self.width, self.height), pixels)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        
    def _draw_ground(self):
        """Draws the ground plane with a grid texture."""
        grid_size = 800
        grid_step = 50
        
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        
        glBegin(GL_QUADS)
        glColor3f(0.7, 0.7, 0.7)
        glNormal3f(0.0, 0.0, 1.0)
        
        glTexCoord2f(0.0, 0.0)
        glVertex3f(-grid_size/2, -grid_size/2, 0.0)
        
        glTexCoord2f(grid_size/grid_step, 0.0)
        glVertex3f(grid_size/2, -grid_size/2, 0.0)
        
        glTexCoord2f(grid_size/grid_step, grid_size/grid_step)
        glVertex3f(grid_size/2, grid_size/2, 0.0)
        
        glTexCoord2f(0.0, grid_size/grid_step)
        glVertex3f(-grid_size/2, grid_size/2, 0.0)
        
        glEnd()
        
        glDisable(GL_TEXTURE_2D)
        
    def _draw_axes(self):
        """Draws the coordinate system axes."""
        axis_length = 50.0
        
        glBegin(GL_LINES)
        
        # X-axis (red)
        glColor3f(1.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(axis_length, 0.0, 0.0)
        
        # Y-axis (green)
        glColor3f(0.0, 1.0, 0.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, axis_length, 0.0)
        
        # Z-axis (blue)
        glColor3f(0.0, 0.0, 1.0)
        glVertex3f(0.0, 0.0, 0.0)
        glVertex3f(0.0, 0.0, axis_length)
        
        glEnd()
        
    def _draw_trail(self):
        """Draws the robot's movement trail."""
        if len(self.trail_points) < 2:
            return
            
        glColor3f(0.5, 0.5, 0.8)
        glBegin(GL_LINE_STRIP)
        
        for point in self.trail_points:
            glVertex3f(point[0], point[1], point[2] + 1.0)  # Slightly above ground
            
        glEnd()
        
    def _draw_obstacles(self):
        """Draws obstacles from the map model."""
        # Draw 3D obstacles
        for min_point, max_point, _ in self.sim_controller.map_model.obstacles_3d.values():
            self._draw_cuboid(min_point, max_point, (1.0, 0.0, 0.0))  # Red for obstacles
            
        # Draw 2D obstacles as extruded polygons (for backwards compatibility)
        glColor3f(1.0, 0.0, 0.0)  # Red
        for obstacle_data in self.sim_controller.map_model.obstacles.values():
            points = obstacle_data[0]  # Extract points from the tuple
            if not points or len(points) < 3:
                continue
                
            # Draw the base (bottom face)
            glBegin(GL_POLYGON)
            glNormal3f(0.0, 0.0, -1.0)
            for point in points:
                glVertex3f(point[0], point[1], 0.0)
            glEnd()
            
            # Draw the top face
            height = 30.0  # Arbitrary height for 2D obstacles
            glBegin(GL_POLYGON)
            glNormal3f(0.0, 0.0, 1.0)
            for point in points:
                glVertex3f(point[0], point[1], height)
            glEnd()
            
            # Draw the side faces
            glBegin(GL_QUADS)
            for i in range(len(points)):
                p1 = points[i]
                p2 = points[(i + 1) % len(points)]
                
                # Calculate normal (perpendicular to the side face)
                dx = p2[0] - p1[0]
                dy = p2[1] - p1[1]
                length = math.sqrt(dx*dx + dy*dy)
                if length > 0:
                    nx, ny = dy/length, -dx/length
                else:
                    nx, ny = 0, 1
                    
                glNormal3f(nx, ny, 0.0)
                glVertex3f(p1[0], p1[1], 0.0)
                glVertex3f(p2[0], p2[1], 0.0)
                glVertex3f(p2[0], p2[1], height)
                glVertex3f(p1[0], p1[1], height)
            glEnd()
            
    def _draw_cuboid(self, min_point, max_point, color):
        """Draws a 3D cuboid from min and max points."""
        x1, y1, z1 = min_point
        x2, y2, z2 = max_point
        
        glColor3f(*color)
        
        # Define the 8 vertices of the cube
        vertices = [
            (x1, y1, z1),  # 0: bottom-left-back
            (x2, y1, z1),  # 1: bottom-right-back
            (x2, y2, z1),  # 2: bottom-right-front
            (x1, y2, z1),  # 3: bottom-left-front
            (x1, y1, z2),  # 4: top-left-back
            (x2, y1, z2),  # 5: top-right-back
            (x2, y2, z2),  # 6: top-right-front
            (x1, y2, z2),  # 7: top-left-front
        ]
        
        # Define the 6 faces using vertices indices
        faces = [
            (0, 1, 2, 3),  # bottom
            (4, 5, 6, 7),  # top
            (0, 1, 5, 4),  # back
            (2, 3, 7, 6),  # front
            (0, 3, 7, 4),  # left
            (1, 2, 6, 5),  # right
        ]
        
        # Define normals for each face
        normals = [
            (0, 0, -1),  # bottom
            (0, 0, 1),   # top
            (0, -1, 0),  # back
            (0, 1, 0),   # front
            (-1, 0, 0),  # left
            (1, 0, 0),   # right
        ]
        
        glBegin(GL_QUADS)
        for i, face in enumerate(faces):
            glNormal3f(*normals[i])
            for vertex_idx in face:
                glVertex3f(*vertices[vertex_idx])
        glEnd()
            
    def _draw_robot(self, x, y, z, pitch, yaw, roll):
        """Draws the robot as a 3D model."""
        # Save current matrix
        glPushMatrix()
        
        # Position and orient the robot
        glTranslatef(x, y, z)
        glRotatef(math.degrees(yaw), 0.0, 0.0, 1.0)   # Rotate around Z (yaw)
        glRotatef(math.degrees(pitch), 1.0, 0.0, 0.0) # Rotate around X (pitch)
        glRotatef(math.degrees(roll), 0.0, 1.0, 0.0)  # Rotate around Y (roll)
        
        # Robot dimensions
        body_width = self.wheel_base_width
        body_length = body_width * 1.5
        body_height = self.robot_height
        
        # Draw robot body (main rectangle)
        glColor3f(0.0, 0.0, 0.8)  # Blue
        
        glBegin(GL_QUADS)
        
        # Bottom face
        glNormal3f(0.0, 0.0, -1.0)
        glVertex3f(-body_length/2, -body_width/2, 0.0)
        glVertex3f(body_length/2, -body_width/2, 0.0)
        glVertex3f(body_length/2, body_width/2, 0.0)
        glVertex3f(-body_length/2, body_width/2, 0.0)
        
        # Top face
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(-body_length/2, -body_width/2, body_height)
        glVertex3f(body_length/2, -body_width/2, body_height)
        glVertex3f(body_length/2, body_width/2, body_height)
        glVertex3f(-body_length/2, body_width/2, body_height)
        
        # Front face
        glNormal3f(1.0, 0.0, 0.0)
        glVertex3f(body_length/2, -body_width/2, 0.0)
        glVertex3f(body_length/2, body_width/2, 0.0)
        glVertex3f(body_length/2, body_width/2, body_height)
        glVertex3f(body_length/2, -body_width/2, body_height)
        
        # Back face
        glNormal3f(-1.0, 0.0, 0.0)
        glVertex3f(-body_length/2, -body_width/2, 0.0)
        glVertex3f(-body_length/2, body_width/2, 0.0)
        glVertex3f(-body_length/2, body_width/2, body_height)
        glVertex3f(-body_length/2, -body_width/2, body_height)
        
        # Left face
        glNormal3f(0.0, -1.0, 0.0)
        glVertex3f(-body_length/2, -body_width/2, 0.0)
        glVertex3f(body_length/2, -body_width/2, 0.0)
        glVertex3f(body_length/2, -body_width/2, body_height)
        glVertex3f(-body_length/2, -body_width/2, body_height)
        
        # Right face
        glNormal3f(0.0, 1.0, 0.0)
        glVertex3f(-body_length/2, body_width/2, 0.0)
        glVertex3f(body_length/2, body_width/2, 0.0)
        glVertex3f(body_length/2, body_width/2, body_height)
        glVertex3f(-body_length/2, body_width/2, body_height)
        
        glEnd()
        
        # Draw wheels
        self._draw_wheel(-body_length/4, -body_width/2 - 3, body_height/4, 90, 0, 0)  # Left wheel
        self._draw_wheel(-body_length/4, body_width/2 + 3, body_height/4, 90, 0, 0)   # Right wheel
        
        # Draw direction indicator (arrow)
        glColor3f(1.0, 1.0, 0.0)  # Yellow
        glBegin(GL_TRIANGLES)
        glNormal3f(0.0, 0.0, 1.0)
        glVertex3f(body_length/2 + 5, 0, body_height/2)
        glVertex3f(body_length/2, -5, body_height/2)
        glVertex3f(body_length/2, 5, body_height/2)
        glEnd()
        
        # Restore matrix
        glPopMatrix()
        
    def _draw_wheel(self, x, y, z, rx, ry, rz):
        """Draws a wheel at the specified position and rotation."""
        glPushMatrix()
        
        glTranslatef(x, y, z)
        glRotatef(rx, 1.0, 0.0, 0.0)
        glRotatef(ry, 0.0, 1.0, 0.0)
        glRotatef(rz, 0.0, 0.0, 1.0)
        
        wheel_radius = self.sim_controller.robot_model.WHEEL_RADIUS
        wheel_width = 3.0
        
        # Draw the wheel as a cylinder
        glColor3f(0.2, 0.2, 0.2)  # Dark gray
        
        # Create a cylinder
        quadric = gluNewQuadric()
        gluCylinder(quadric, wheel_radius, wheel_radius, wheel_width, 16, 1)
        
        # Draw the wheel caps
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)
        for i in range(17):
            angle = 2.0 * math.pi * i / 16
            glVertex3f(wheel_radius * math.cos(angle), wheel_radius * math.sin(angle), 0)
        glEnd()
        
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, wheel_width)
        for i in range(17):
            angle = 2.0 * math.pi * i / 16
            glVertex3f(wheel_radius * math.cos(angle), wheel_radius * math.sin(angle), wheel_width)
        glEnd()
        
        glPopMatrix()
        
    def clear_robot(self):
        """Clears the robot and trail."""
        self.trail_points = []
        
    def toggle_follow_mode(self, follow=None):
        """Toggles camera follow mode."""
        if follow is not None:
            self.follow_robot = follow
        else:
            self.follow_robot = not self.follow_robot 