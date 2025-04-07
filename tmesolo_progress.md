# SOLO TME Progress - Salim

This file tracks the questions addressed during the SOLO TME and the files modified for each question.

## Q 1.1: Create simulation with 3 aligned obstacles

- **Status:** Answered
- **Files Modified:**
    - `tmesolo.py` (Created file, added `q1_1` function, initial render fix)
    - `src/model/map_model.py` (Fixed relative import)
    - `src/model/robot.py` (Fixed relative imports)
    - `src/controller/map_controller.py` (Fixed relative imports)
    - `src/controller/robot_controller.py` (Fixed relative imports)
    - `src/controller/simulation_controller.py` (Fixed relative imports)
    - `src/controller/StrategyAsync.py` (Fixed relative import)
    - `src/gui_main.py` (Fixed relative imports)
    - `src/vpython_main.py` (Fixed relative imports)
    - `src/view/control_panel.py` (Fixed relative imports, corrected strategy name, imported `time`)
    - `src/view/vpython_control_panel.py` (Fixed relative imports)

## Q 1.2: Horizontal U-Turn Strategy

- **Status:** In Progress (Robot turns indefinitely)
- **Files Modified:**
    - `tmesolo.py` (Added `q1_2` function, argparse, logging, angle fix)
    - `src/controller/StrategyAsync.py` (Added `HorizontalUTurnStrategy`, refactored multiple times, added debug logging)
    - `src/model/robot.py` (Corrected `decide_turn_direction`, `calcule_angle`)

## Q 1.3: Robot Pen Drawing

- **Status:** Answered
- **Files Modified:**
    - `tmesolo.py` (Added `q1_3` function, `SetPen` class, updated imports and argparse)
    - `src/model/robot.py` (Added `pen_down`, `draw()` method, updated `get_state()`)
    - `src/view/robot_view.py` (Modified `_draw_robot` logic, updated `clear_robot()`)

## Q 1.4: Pen Color Change (Red/Blue)

- **Status:** Answered
- **Files Modified:**
    - `tmesolo.py` (Added `q1_4` function, `SetPenColor` class, updated sequence and argparse)
    - `src/model/robot.py` (Added `pen_color`, `red()`, `blue()` methods, updated `get_state()`)
    - `src/view/robot_view.py` (Modified `_draw_robot` to use `pen_color`)

## Q 1.5: Color-Changing U-Turn Strategy

- **Status:** Answered
- **Files Modified:**
    - `src/controller/StrategyAsync.py` (Added `StrategyRed`, `StrategyBlue`, `StrategyInvisible`, refactored `HorizontalUTurnStrategy` state machine)
    - `tmesolo.py` (Added `q1_5` function, updated argparse)

## Q 2.1: Add Second Robot (Cat)

- **Status:** Answered
- **Files Modified:**
    - `src/controller/simulation_controller.py` (Modified to handle multiple robots/controllers/states)
    - `src/view/robot_view.py` (Modified to draw multiple robots and paths)
    - `tmesolo.py` (Added `q2_1` function, updated argparse)

## Q 2.2: Concurrent Robot Strategies (Mouse Square, Cat Patrol)

- **Status:** Answered
- **Files Modified:**
    - `tmesolo.py` (Added `q2_2` function, strategies for mouse/cat, threading, updated argparse) 