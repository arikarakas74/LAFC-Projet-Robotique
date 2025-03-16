import tkinter as tk
from tkinter import simpledialog, messagebox
import math
import time
import logging

class ControlPanel:
    """Control panel for user interactions with the 3D simulation."""
    
    def __init__(self, parent, map_controller, simulation_controller):
        """
        Initialize the control panel.
        
        Args:
            parent: The parent widget
            map_controller: The map controller (can be None)
            simulation_controller: The simulation controller
        """
        self.parent = parent
        self.map_controller = map_controller
        self.simulation_controller = simulation_controller
        self.strategy_manager = simulation_controller.strategy_manager
        
        # Frame for buttons
        self.control_frame = tk.Frame(parent)
        self.control_frame.pack()
        
        # Create buttons
        self._create_buttons()

    def _create_buttons(self):
        """Create the control buttons."""
        # Simulation and strategy buttons
        buttons = [
            ("Run Simulation", self.simulation_controller.run_simulation),
            ("Draw Polygon", self.draw_polygon),
            ("Stop", self.stop_strategy),
            ("Reset", self.reset_all),
        ]
        
        # Display beacon instruction message after a short delay
        self.parent.after(500, self._show_beacon_instructions)
        
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
    
    def draw_polygon(self):
        """Open a dialog to input sides and draw a polygon."""
        sides = simpledialog.askinteger(
            "Draw Polygon", 
            "Enter number of sides (minimum 3):",
            minvalue=3,
            maxvalue=20,
            initialvalue=4,
            parent=self.parent
        )
        
        if sides is not None:  # User didn't cancel
            logging.info(f"Starting to draw a {sides}-sided polygon")
            self.strategy_manager.draw_polygon(sides, side_length=100)
    
    def stop_strategy(self):
        """Stop the current strategy."""
        logging.info("Stopping current strategy")
        self.strategy_manager.stop_strategy()
    
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
        self.strategy_manager.stop_strategy()
        
        # Reset motor speeds
        robot_model.set_motor_speed("left", 0)
        robot_model.set_motor_speed("right", 0)
        
        # Reset position to start if available
        if map_model.start_position:
            if len(map_model.start_position) == 3:
                x, y, z = map_model.start_position
            else:
                x, y = map_model.start_position
                z = 0
                
            robot_model.set_position(x, y, z)
            
        # Reset orientation
        robot_model.update_position(
            robot_model.x, 
            robot_model.y, 
            robot_model.z,
            0.0,  # Reset pitch
            0.0,  # Reset yaw
            0.0   # Reset roll
        )
        
        # Restart the simulation
        self.simulation_controller.run_simulation()
        logging.info("Simulation reset and restarted")