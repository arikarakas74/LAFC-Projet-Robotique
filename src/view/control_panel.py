import tkinter as tk
import math
import time
import inspect

class ControlPanel:
    """Panneau de contrôle pour les interactions utilisateur."""
    
    def __init__(self, parent, map_controller, simulation_controller):
        self.parent = parent
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        
        # Frame pour les boutons
        self.control_frame = tk.Frame(parent)
        self.control_frame.pack()
        
        # Boutons
        self._create_buttons()

    def _create_buttons(self):
        # Common buttons for both 2D and 3D modes
        buttons = [
            ("Run Simulation", self.simulation_controller.run_simulation),
            ("Reset", self.reset_all),
        ]
        
        # Add map-specific buttons only if we have a map controller (2D mode)
        if self.map_controller is not None:
            map_buttons = [
                ("Set Start", self.map_controller.set_start_mode),
                ("Set Obstacles", self.map_controller.set_obstacles_mode),
                ("Set Beacon", self.map_controller.set_end_mode),
            ]
            buttons = map_buttons + buttons
        else:
            # In 3D mode, add a message to instruct how to set the beacon
            self.parent.after(500, lambda: self._show_beacon_instructions())
        
        # Add strategy buttons
        strategy_buttons = [
            ("Triangle", self.draw_triangle),
            ("Square", self.draw_square),
            ("Pentagon", self.draw_pentagon),
            ("Stop", self.stop_strategy)
        ]
        
        # Combine all buttons
        buttons.extend(strategy_buttons)
        
        for text, cmd in buttons:
            btn = tk.Button(self.control_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5)

    def _show_beacon_instructions(self):
        """Show a temporary instruction about how to set beacons"""
        instruction_label = tk.Label(
            self.parent, 
            text="Click anywhere on the screen to set a beacon. Robot will automatically follow it when you click 'Run Simulation'.",
            fg="blue"
        )
        instruction_label.pack(pady=5)
        # Hide the message after 10 seconds
        self.parent.after(10000, instruction_label.destroy)

    def draw_triangle(self):
        """Draw a triangle with a side length of 50cm."""
        self.simulation_controller.draw_triangle(50)
        
    def draw_square(self):
        """Draw a square with a side length of 50cm."""
        self.simulation_controller.draw_square(50)
        
    def draw_pentagon(self):
        """Draw a pentagon with a side length of 50cm."""
        self.simulation_controller.draw_pentagon(50)
        
    def stop_strategy(self):
        """Stop the currently running strategy."""
        self.simulation_controller.stop_strategy()

    def reset_all(self):
        """Réinitialise l'application. Force complete stop of robot motion."""
        # Stop the simulation with a hard stop
        self.simulation_controller.stop_simulation()
        
        # Small pause to ensure everything stops
        time.sleep(0.1)
        
        # Get direct access to models
        robot_model = self.simulation_controller.robot_model
        map_model = self.simulation_controller.map_model
        
        # FORCE COMPLETE STOP: Reset ALL possible motion variables
        
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
            # Skip motor_speeds, methods, functions, and special attributes
            if (attr != 'motor_speeds' and 
                not attr.startswith('__') and 
                not callable(getattr(robot_model, attr)) and
                ('velocity' in attr or 'speed' in attr or 'momentum' in attr or 'accel' in attr)):
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
        if hasattr(map_model, 'start_position') and map_model.start_position:
            start_x, start_y = map_model.start_position
            robot_model.x = start_x
            robot_model.y = start_y
            # Reset direction to default (facing east)
            robot_model.theta = 0
        
        # -- Force a physics state update if controller has this method --
        if hasattr(self.simulation_controller, 'update_physics'):
            self.simulation_controller.update_physics(0)
        
        # -- Ensure the robot knows it's not moving --
        if hasattr(robot_model, 'is_moving'):
            robot_model.is_moving = False
        
        # Reset map if in 2D mode
        if self.map_controller is not None:
            self.map_controller.reset()
        
        # Clear any cached motion data or trail history
        if hasattr(self.simulation_controller, 'clear_cache'):
            self.simulation_controller.clear_cache()
            
        # Restart the simulation only after confirming all motion is stopped
        self.simulation_controller.run_simulation()
        
        # Force update all views if controller has this method
        if hasattr(self.simulation_controller, 'update_views'):
            self.simulation_controller.update_views()

    def export_movements(self):
        """Export recorded robot movements to a CSV file."""
        success = self.simulation_controller.export_movements_to_file()
        if success:
            self.export_status.set("Movements exported to robot_movements.csv")
            # Schedule the message to disappear after 3 seconds
            self.parent.after(3000, lambda: self.export_status.set(""))
        else:
            self.export_status.set("Export failed. See logs for details.")
            # Schedule the message to disappear after 3 seconds
            self.parent.after(3000, lambda: self.export_status.set(""))