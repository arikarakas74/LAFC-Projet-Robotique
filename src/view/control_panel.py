import tkinter as tk
import math
import time
import inspect

class ControlPanel:
    """Control panel for user interactions with the 3D simulation."""
    
    def __init__(self, parent, map_controller, simulation_controller):
        self.parent = parent
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        
        # Frame for buttons
        self.control_frame = tk.Frame(parent)
        self.control_frame.pack()
        
        # Create buttons
        self._create_buttons()

    def _create_buttons(self):
        # Simulation and strategy buttons
        buttons = [
            ("Run Simulation", self.simulation_controller.run_simulation),
            ("Triangle", self.draw_triangle),
            ("Square", self.draw_square),
            ("Pentagon", self.draw_pentagon),
            ("Stop", self.stop_strategy),
            ("Reset", self.reset_all),
        ]
        
        # Display beacon instruction message
        self.parent.after(500, lambda: self._show_beacon_instructions())
        
        # Create button widgets
        for text, cmd in buttons:
            btn = tk.Button(self.control_frame, text=text, command=cmd)
            btn.pack(side=tk.LEFT, padx=5)
            
    def _show_beacon_instructions(self):
        """Show instructions about how to set the beacon in 3D mode."""
        instruction = "Click anywhere in the 3D view to set a beacon position."
        instruction_window = tk.Toplevel(self.parent)
        instruction_window.title("Beacon Instructions")
        
        # Set window properties
        instruction_window.geometry("400x100")
        instruction_window.resizable(False, False)
        
        # Center the window on the screen
        window_width = 400
        window_height = 100
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))
        instruction_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Add instruction text
        label = tk.Label(
            instruction_window, 
            text=instruction,
            font=("Arial", 12),
            pady=20
        )
        label.pack()
        
        # Add a close button
        close_button = tk.Button(
            instruction_window,
            text="Got it!",
            command=instruction_window.destroy
        )
        close_button.pack()
        
        # Auto-close after 10 seconds
        self.parent.after(10000, instruction_window.destroy)
    
    def draw_triangle(self):
        """Draw an equilateral triangle."""
        self.simulation_controller.draw_triangle(100)
    
    def draw_square(self):
        """Draw a square."""
        self.simulation_controller.draw_square(100)
    
    def draw_pentagon(self):
        """Draw a pentagon."""
        self.simulation_controller.draw_pentagon(100)
    
    def reset_all(self):
        """Reset the application. Forces complete stop of robot motion."""
        # Get models
        robot_model = self.simulation_controller.robot_model
        map_model = self.simulation_controller.map_model
        
        # Get the current state before stopping
        state = robot_model.get_state()
        
        # Stop the simulation
        self.simulation_controller.stop_simulation()
        
        # Stop any running strategy
        if hasattr(self.simulation_controller, 'stop_strategy'):
            self.simulation_controller.stop_strategy()
        
        # Reset motor speeds
        robot_model.set_motor_speed("left", 0)
        robot_model.set_motor_speed("right", 0)
        
        # Also reset left_speed and right_speed for compatibility
        if hasattr(robot_model, 'left_speed'):
            robot_model.left_speed = 0
        if hasattr(robot_model, 'right_speed'):
            robot_model.right_speed = 0
        
        # Reset all possible motion attributes
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
        
        # Reset 3D specific variables
        if hasattr(robot_model, 'pitch'):
            robot_model.pitch = 0
        if hasattr(robot_model, 'roll'):
            robot_model.roll = 0
        if hasattr(robot_model, 'yaw'):
            robot_model.yaw = 0
        if hasattr(robot_model, 'z'):
            robot_model.z = 0  # Reset height to ground level
        
        # Force robot back to start position
        if hasattr(map_model, 'start_position') and map_model.start_position:
            # Handle 3D or 2D start position
            start_pos = map_model.start_position
            if len(start_pos) == 3:
                start_x, start_y, start_z = start_pos
            else:
                start_x, start_y = start_pos
                start_z = 0
            
            robot_model.x = start_x
            robot_model.y = start_y
            robot_model.z = start_z
        
        # Restart the simulation
        self.simulation_controller.run_simulation()
    
    def stop_strategy(self):
        """Stop the current strategy."""
        if hasattr(self.simulation_controller, 'stop_strategy'):
            self.simulation_controller.stop_strategy()

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