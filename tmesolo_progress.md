# SOLO TME Progress - Salim

This file tracks the questions addressed during the SOLO TME and the files modified for each question.

## Q 1.1: Create simulation with 3 aligned obstacles

- **Status:** Answered
- **Files Modified:**
    - `tmesolo.py` (Created file, added `q1_1` function)
    - `src/model/map_model.py` (Fixed relative import)
    - `src/model/robot.py` (Fixed relative imports)
    - `src/controller/map_controller.py` (Fixed relative imports)
    - `src/controller/robot_controller.py` (Fixed relative imports)
    - `src/controller/simulation_controller.py` (Fixed relative imports)
    - `src/controller/StrategyAsync.py` (Fixed relative import)
    - `src/gui_main.py` (Fixed relative imports)
    - `src/vpython_main.py` (Fixed relative imports)
    - `src/view/control_panel.py` (Fixed relative imports, corrected `FollowBeaconByImageStrategy` usage, imported `time`)
    - `src/view/vpython_control_panel.py` (Fixed relative imports)

## Q 1.2: Horizontal U-Turn Strategy

- **Status:** In Progress (Robot turns indefinitely)
- **Files Modified:**
    - `tmesolo.py` (Added `q1_2` function, argparse, logging, angle fix for strategy start, initial render fix for Q1.1)
    - `src/controller/StrategyAsync.py` (Added `HorizontalUTurnStrategy`, refactored, added debug logging)
    - `src/model/robot.py` (Corrected `decide_turn_direction`, `calcule_angle`) 