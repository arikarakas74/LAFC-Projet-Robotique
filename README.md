# LAFC-Projet-Robotique - LU2IN013

A 3D robot simulation program that allows users to control and simulate a robot in a 3D environment. The robot can navigate through the environment, follow beacons, and execute various movement patterns while providing real-time position and orientation information.

## Project Structure

The project follows an MVC (Model-View-Controller) architecture:

```
src/
├── controller/     # Contains simulation control logic and strategies
├── model/          # Contains robot and map models
├── utils/          # Utility functions for geometry and 3D calculations
├── view/           # GUI and 3D visualization components
└── main.py         # Main entry point
```

## Requirements

- Python 3.8 or newer
- Tkinter (usually comes with Python installation)
- PyOpenGL (for 3D rendering)
- Pillow (PIL fork for image processing)
- NumPy (for numerical calculations)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/arikarakas74/LAFC-Projet-Robotique.git
    ```

2. Navigate to the project directory:
    ```bash
    cd LAFC-Projet-Robotique
    ```

3. Set up a virtual environment (recommended):
    ```bash
    # Create a virtual environment
    python3 -m venv venv
    
    # Activate the virtual environment
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    # venv\Scripts\activate
    ```

4. Install required packages:
    ```bash
    pip install numpy pillow pyopengl
    ```

## Running the Program

The program now includes a 3D simulation mode with beacon-following capabilities:

### Starting the 3D Simulation

```bash
python3 src/main.py
```

This will start the program in 3D GUI mode by default.

### Robot Control in 3D Environment

The 3D simulation offers several control methods:

#### Keyboard Controls:
- **W**: Move forward
- **S**: Move backward
- **A**: Decrease right wheel speed (turn left)
- **D**: Increase right wheel speed (turn right)
- **Q**: Increase left wheel speed
- **E**: Decrease left wheel speed
- **R**: Move up (for 3D movement)
- **F**: Move down (for 3D movement)
- **Arrow Keys**: Control pitch and roll in 3D space
- **Ctrl+T**: Clear the robot's trail

#### Movement Patterns:
- **Draw Polygon**: Create regular polygons with any number of sides (3 or more)
  - When clicked, a dialog will appear asking for the number of sides
  - The robot will then draw the specified polygon

#### Beacon Following:
1. Click anywhere in the 3D view to set a beacon position
2. The robot will automatically navigate toward the beacon
3. Click again to set a new beacon position, and the robot will update its path

## Advanced Features

### Polygon Drawing
The simulation includes a flexible polygon drawing feature that allows the robot to:
- Draw any regular polygon with 3 or more sides
- Automatically calculate the angles needed for each corner
- Maintain consistent side lengths and movement speeds

### Beacon Following
The simulation includes a dynamic beacon following strategy that allows the robot to:
- Track and move toward beacon positions
- Respond in real-time to beacon position changes
- Handle collisions and obstacles automatically
- Maintain pursuit of the beacon until a new goal is set

### 3D Visualization
- Camera follows the robot by default
- Robot leaves a trail showing its path
- Obstacles and beacons are displayed in 3D space
- Real-time information display shows position, orientation, and motor speeds

## Troubleshooting

### Common Installation Issues:
- **Missing PyOpenGL**: If you encounter errors related to OpenGL, ensure PyOpenGL is installed correctly with `pip install pyopengl`
- **Tkinter not found**: On some Linux distributions, Tkinter needs to be installed separately with `sudo apt-get install python3-tk`
- **Python version incompatibility**: Ensure you're using Python 3.8 or newer

### Runtime Issues:
- If the simulation seems frozen after clicking "Run Simulation," try clicking "Reset" and then "Run Simulation" again
- If the robot doesn't respond to keyboard controls, click on the simulation window to ensure it has focus

## Development

### Adding New Features:
1. For new movement strategies, extend the `AsyncCommand` class in `src/controller/strategy.py`
2. For UI components, modify or extend classes in the `src/view/` directory

### Testing:
- Ensure the simulation runs correctly after your changes
- Check that existing functionality like beacon following continues to work

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

## Project Resources

- [Documentation](./Documentation/) - Additional detailed documentation
- [Trello Board](https://trello.com/invite/b/6790cac1e266a0256f541dae/ATTIf9a8031f4e259cceb72fa6d61ba8627b61608668/robot-project) - Project management

