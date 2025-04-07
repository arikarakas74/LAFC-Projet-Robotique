#!/usr/bin/env python3
"""
TME Solo - Robot Simulation Exercises
This file contains the implementation of various exercises for the robot simulation project.
Each function qX.Y() corresponds to question X.Y from the exercise sheet.
"""

import sys
import os
from src.model.robot import RobotModel
from src.model.map_model import MapModel
from src.view.robot_view import RobotView
from src.view.map_view import MapView
from src.view.control_panel import ControlPanel
from src.controller.simulation_controller import SimulationController
import tkinter as tk

def q1_1():
    """
    Question 1.1: Create a simulation with 3 aligned obstacles (any shape: square, rectangle, or round):
    one in the center, one in the upper middle, and one in the lower middle.
    Place your robot in the bottom-left corner.
    """
    # Create the main window
    root = tk.Tk()
    root.title("Robot Simulation - Q1.1")
    
    # Create the map model with default settings
    map_model = MapModel()
    
    # Set the robot's starting position in the bottom-left corner
    map_model.set_start_position((50, 550))  # 50 pixels from left, 550 pixels from top
    
    # Create three rectangular obstacles
    # Center obstacle
    center_obstacle = [
        (375, 275),  # Top-left
        (425, 275),  # Top-right
        (425, 325),  # Bottom-right
        (375, 325)   # Bottom-left
    ]
    map_model.add_obstacle("center", center_obstacle, None, None)
    
    # Upper middle obstacle
    upper_obstacle = [
        (375, 175),  # Top-left
        (425, 175),  # Top-right
        (425, 225),  # Bottom-right
        (375, 225)   # Bottom-left
    ]
    map_model.add_obstacle("upper", upper_obstacle, None, None)
    
    # Lower middle obstacle
    lower_obstacle = [
        (375, 375),  # Top-left
        (425, 375),  # Top-right
        (425, 425),  # Bottom-right
        (375, 425)   # Bottom-left
    ]
    map_model.add_obstacle("lower", lower_obstacle, None, None)
    
    # Create the robot model
    robot_model = RobotModel(map_model)
    
    # Create the simulation controller
    sim_controller = SimulationController(robot_model, map_model)
    
    # Create the robot view
    robot_view = RobotView(root, sim_controller)
    robot_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Create the map view
    map_view = MapView(root, robot_view)
    map_view.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    # Create the control panel
    control_panel = ControlPanel(root, map_model, sim_controller)
    control_panel.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Start the simulation
    sim_controller.start()
    
    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    # You can test individual questions by calling their functions here
    q1_1() 