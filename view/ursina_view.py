from ursina import *
import time
from controller.StrategyAsync import FollowBeaconByImageStrategy
from ursina import Mesh


class UrsinaView(Entity):
    def __init__(self, simulation_controller, control_panel):
        super().__init__()
        self.simulation_controller = simulation_controller
        self.control_panel = control_panel
        self.control_panel.ursina_view = self  # Injecter le panneau de contrôle
        self.create_scene()
        self.trail_points = []
        self.trail_entity = None

    def create_scene(self):
        # le sol
        self.floor = Entity(model='quad', scale=(80, 60), rotation=(90, 0, 0),
                            color=color.green, collider='box')
        self.floor.on_click = self.handle_floor_click

        # la boule du robot
        self.robot_entity = Entity(model='sphere', color=color.red, scale=1, position=(0, 1, 0))

        # camera
        self.camera = EditorCamera(rotation_x=90, rotation_y=0)
        self.camera.position = (0, 60, 0)


    def update(self):
        # Mettre à jour la position de l'entité du robot
        robot_posx = self.simulation_controller.robot_model.x
        robot_posy = self.simulation_controller.robot_model.y 
        self.robot_entity.position = (robot_posx / 100 - 40, 1, robot_posy / 100 - 30)

        if not self.simulation_controller.simulation_running:
            return
            
        # # Ajustement de la vitesse de la roue gauche
        # if held_keys['q']:
        #     self.simulation_controller.robot_controller.increase_left_speed()
        # if held_keys['a']:
        #     self.simulation_controller.robot_controller.decrease_left_speed()

        # # Ajustement de la vitesse de la roue droit
        # if held_keys['e']:
        #     self.simulation_controller.robot_controller.increase_right_speed()
        # if held_keys['d']:
        #     self.simulation_controller.robot_controller.decrease_right_speed()

        # # Avancer et reculer
        # if held_keys['w']:
        #     self.simulation_controller.robot_controller.move_forward()
        # if held_keys['s']:
        #     self.simulation_controller.robot_controller.move_backward()

        #Synchronisation dynamique du mode Follow Balise
        if isinstance(self.control_panel.current_strategy, FollowBeaconByImageStrategy):
            end = self.simulation_controller.map_model.end_position
            if self.control_panel.end_box:
                self.control_panel.end_box.position = (end[0] / 100 - 40, 1, end[1] / 100 - 30)
                
        current_pos = (self.robot_entity.position.x, 1, self.robot_entity.position.z)
        if not self.trail_points or self.trail_points[-1] != current_pos:
            self.trail_points.append(current_pos)
            if len(self.trail_points) >= 2:
                if self.trail_entity is None:
                    self.trail_entity = Entity(
                        model=Mesh(vertices=self.trail_points, mode='line'),
                        color=color.red
                    )
                else:
                    self.trail_entity.model.vertices = self.trail_points
                    self.trail_entity.model.generate()

    def input(self, key):
        if key == 'w':
            self.simulation_controller.robot_controller.move_forward()
        elif key == 's':
            self.simulation_controller.robot_controller.move_backward()
        elif key == 'q':
            self.simulation_controller.robot_controller.increase_left_speed()
        elif key == 'a':
            self.simulation_controller.robot_controller.decrease_left_speed()
        elif key == 'e':
            self.simulation_controller.robot_controller.increase_right_speed()
        elif key == 'd':
            self.simulation_controller.robot_controller.decrease_right_speed()
    
    def handle_floor_click(self):
        pos = mouse.world_point
        x = (pos.x + 40) * 100
        y = (pos.z + 30) * 100
        cp = self.control_panel

        if cp.mode == 'set_start':
            if cp.start_box:
                cp.start_box.disable()
            cp.start_box = Entity(model='cube', color=color.red, scale=0.5, position=(pos.x, 1, pos.z))
            cp.map_model.set_start_position((x, y))
            self.simulation_controller.reset_simulation()
            self.reset_ursina_view()
            print(f"✅ Start position set: ({x}, {y})")

        elif cp.mode == 'set_end':
            if cp.end_box:
                cp.end_box.disable()
            cp.end_box = Entity(model='cube', color=color.blue, scale=0.5, position=(pos.x, 5, pos.z))
            cp.map_model.set_end_position((x, y))
            print(f"✅ End position set: ({x}, {y})")

    def reset_ursina_view(self):
        self.robot_entity.position = (0, 1, 0)
        self.trail_points = []
        if self.trail_entity is not None:
            self.trail_entity.disable()
            self.trail_entity = None