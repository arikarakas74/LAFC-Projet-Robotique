import tkinter as tk
from tkinter import ttk
from controller.map_controller import MapController
from view.robot_view import RobotView
from view.robot_view_3d import RobotView3D
from view.map_view import MapView
from view.control_panel import ControlPanel
from model.map_model import MapModel
from model.robot import RobotModel
from controller.simulation_controller import SimulationController
import time

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Robot Simulation MVC - 3D")
        self._create_menu()

        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Canvas frame (for drawing)
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(side="top", fill="both", expand=True)

        # Controls frame
        controls_frame = ttk.Frame(main_frame, padding=10)
        controls_frame.pack(side="bottom", fill="x")

        # Initialize models and simulation controller
        self.map_model = MapModel()
        self.robot_model = RobotModel(self.map_model)
        
        # Set default starting position
        self.map_model.set_start_position((400, 300))
        
        # Create a 3D obstacle for testing
        self.map_model.add_obstacle_3d(
            "cube1", 
            (100, 100, 0),   # min point
            (150, 150, 50),  # max point
        )
        
        # Pass cli_mode=False to avoid launching the CLI input thread.
        self.sim_controller = SimulationController(self.map_model, self.robot_model, False)
        
        # Setting 3D mode to enabled
        self.sim_controller.toggle_3d_mode(True)

        # Create the views - use the 3D view by default
        self.use_3d_view = True
        self.map_controller = None  # Initialize to None
        
        if self.use_3d_view:
            # Create 3D view
            self.robot_view = RobotView3D(canvas_frame, self.sim_controller)
            # In 3D mode we don't need a separate map view or map controller
            self.map_view = None
        else:
            # Create 2D views for backward compatibility
            self.robot_view = RobotView(canvas_frame, self.sim_controller)
            self.robot_view.canvas.pack(fill="both", expand=True)
            self.map_view = MapView(
                parent=canvas_frame,
                robot_view=self.robot_view
            )
            # Create the map controller (only in 2D mode)
            self.map_controller = MapController(self.map_model, self.map_view, self)

        # Create a sub-frame to center the control panel
        inner_frame = ttk.Frame(controls_frame)
        inner_frame.pack(anchor='center')

        # Control panel for simulation commands (start, reset, etc.)
        self.control_panel = ControlPanel(inner_frame, self.map_controller, self.sim_controller)
        self.control_panel.control_frame.pack(pady=5)

        # Create view toggle button
        self.view_toggle_button = ttk.Button(
            inner_frame,
            text="Toggle Follow Mode" if self.use_3d_view else "Switch to 3D View",
            command=self.toggle_view
        )
        self.view_toggle_button.pack(pady=5)

        # Bind keyboard events for the 3D view mode
        self._bind_3d_keys()

    def _create_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=False)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Toggle View", command=self.toggle_view)
        file_menu.add_command(label="Reset", command=self.reset_simulation)
        file_menu.add_command(label="Quit", command=self.quit)

    def toggle_view(self):
        """Toggle between follow mode and free camera mode in 3D view."""
        if self.use_3d_view and hasattr(self.robot_view, 'toggle_follow_mode'):
            self.robot_view.toggle_follow_mode()
            
    def reset_simulation(self):
        """Reset the simulation with a complete hard stop."""
        # Hard stop the simulation
        self.sim_controller.stop_simulation()
        
        # Small pause to ensure everything stops
        time.sleep(0.1)
        
        # FORCE COMPLETE STOP: Reset ALL possible motion variables
        robot_model = self.robot_model
        
        # -- Primary motion variables --
        # Handle both possible ways motor speeds might be stored
        if hasattr(robot_model, 'motor_speeds'):
            # If motor_speeds is a dictionary
            if isinstance(robot_model.motor_speeds, dict):
                robot_model.motor_speeds["left"] = 0
                robot_model.motor_speeds["right"] = 0
            # If motor_speeds is something else but has left/right attributes
            elif hasattr(robot_model.motor_speeds, 'left') and hasattr(robot_model.motor_speeds, 'right'):
                robot_model.motor_speeds.left = 0
                robot_model.motor_speeds.right = 0
            else:
                # Just reset it to an appropriate default structure
                robot_model.motor_speeds = {"left": 0, "right": 0}
                
        # Also reset left_speed and right_speed for compatibility
        if hasattr(robot_model, 'left_speed'):
            robot_model.left_speed = 0
        if hasattr(robot_model, 'right_speed'):
            robot_model.right_speed = 0
        
        # -- Ensure any internal velocity tracking is reset --
        if hasattr(robot_model, 'left_wheel_pos'):
            robot_model.left_wheel_pos = 0
        if hasattr(robot_model, 'right_wheel_pos'):
            robot_model.right_wheel_pos = 0
        if hasattr(robot_model, 'linear_velocity'):
            robot_model.linear_velocity = 0
        if hasattr(robot_model, 'angular_velocity'):
            robot_model.angular_velocity = 0
            
        # -- Additional velocity components that might exist --
        for attr in dir(robot_model):
            # Exclude 'motor_speeds' to prevent overwriting the dictionary
            if attr != 'motor_speeds' and ('velocity' in attr or 'speed' in attr or 'momentum' in attr or 'accel' in attr):
                try:
                    setattr(robot_model, attr, 0)
                except:
                    pass
        
        # -- Reset 3D specific variables --
        if hasattr(robot_model, 'pitch'):
            robot_model.pitch = 0
        if hasattr(robot_model, 'roll'):
            robot_model.roll = 0
        if hasattr(robot_model, 'yaw'):
            robot_model.yaw = 0
        if hasattr(robot_model, 'z'):
            robot_model.z = 0  # Reset height to ground level
            
        # -- Force robot back to start position --
        if hasattr(self.map_model, 'start_position') and self.map_model.start_position:
            start_x, start_y = self.map_model.start_position
            robot_model.x = start_x
            robot_model.y = start_y
            # Reset direction to default (facing east)
            robot_model.theta = 0
        
        # -- Force a physics state update if controller has this method --
        if hasattr(self.sim_controller, 'update_physics'):
            self.sim_controller.update_physics(0)
        
        # -- Ensure the robot knows it's not moving --
        if hasattr(robot_model, 'is_moving'):
            robot_model.is_moving = False
            
        # Clear robot view if needed
        if hasattr(self.robot_view, 'clear_robot'):
            self.robot_view.clear_robot()
        
        # Clear any cached motion data or trail history
        if hasattr(self.sim_controller, 'clear_cache'):
            self.sim_controller.clear_cache()
            
        # Restart the simulation only after confirming all motion is stopped
        self.sim_controller.run_simulation()
        
        # Force update all views if controller has this method
        if hasattr(self.sim_controller, 'update_views'):
            self.sim_controller.update_views()

    def _bind_3d_keys(self):
        """Bind keyboard events for 3D robot control."""
        # WASD for basic movement
        self.bind("<w>", lambda event: self.sim_controller.robot_controller.move_forward())
        self.bind("<s>", lambda event: self.sim_controller.robot_controller.move_backward())
        self.bind("<a>", lambda event: self.sim_controller.robot_controller.decrease_right_speed())
        self.bind("<d>", lambda event: self.sim_controller.robot_controller.increase_right_speed())
        
        # QE for left wheel control
        self.bind("<q>", lambda event: self.sim_controller.robot_controller.increase_left_speed())
        self.bind("<e>", lambda event: self.sim_controller.robot_controller.decrease_left_speed())
        
        # RF for up/down in 3D
        self.bind("<r>", lambda event: self.sim_controller.robot_controller.move_up())
        self.bind("<f>", lambda event: self.sim_controller.robot_controller.move_down())
        
        # Arrow keys for 3D rotation
        self.bind("<Up>", lambda event: self.sim_controller.robot_controller.pitch_up())
        self.bind("<Down>", lambda event: self.sim_controller.robot_controller.pitch_down())
        self.bind("<Left>", lambda event: self.sim_controller.robot_controller.roll_left())
        self.bind("<Right>", lambda event: self.sim_controller.robot_controller.roll_right())
        
        # Add a key for toggling follow mode (using F1)
        self.bind("<F1>", lambda event: self.toggle_view())

def run_gui():
    app = MainApplication()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
