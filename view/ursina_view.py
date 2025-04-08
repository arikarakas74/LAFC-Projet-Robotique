from ursina import *
from panda3d.core import Texture, GraphicsOutput, GraphicsPipe, WindowProperties, FrameBufferProperties
import time
from controller.StrategyAsync import FollowBeaconByImageStrategy
import numpy as np
from PIL import Image


class UrsinaView(Entity):
    def __init__(self, simulation_controller, control_panel):
        super().__init__()
        self.simulation_controller = simulation_controller
        self.control_panel = control_panel
        self.control_panel.ursina_view = self  # Injecter le panneau de contrôle
        self.create_scene()
        self.trail_points = []
        self.trail_entity = None
        self.create_robot_camera_window()

        self.speed_label = Text(text='Speed: L=0°/s  R=0°/s\nAngle: 0°', position=(-0.68,-0.45), origin=(0,0), scale=1, color=color.black)

    def create_scene(self):
        # le sol
        self.floor = Entity(model='quad', scale=(80, 60), rotation=(90, 0, 0), collider='box', texture='floor')
        self.floor.on_click = self.handle_floor_click

        # Créer le conteneur principal du robot
        self.robot_entity = Entity(model=None, position=(0, 0.4, 0))

        # le corps en parallélépipède rectangle
        self.robot_body = Entity(
            parent=self.robot_entity,
            model='cube',
            color=color.red,
            scale=(1, 0.5, 1),
            position=(0, 0, 0)
        )

        # la roue gauche
        self.wheel_left = Entity(
            parent=self.robot_entity,
            model='cube',
            color=color.black,
            scale=(0.2, 0.2, 0.5),
            position=(0, -0.15, 0.6),
            rotation=(90, 0, 0)
        )

        # la roue droite
        self.wheel_right = Entity(
            parent=self.robot_entity,
            model='cube',
            color=color.black,
            scale=(0.2, 0.2, 0.5),
            position=(0, -0.15, -0.6),
            rotation=(90, 0, 0)
        )

        # le cube de repère frontal
        self.front_marker = Entity(
            parent=self.robot_entity,
            model='cube',
            color=color.blue,
            scale=(0.2, 0.2, 0.2),
            position=(0.6, 0.1, 0)
        )

        # camera
        self.camera = EditorCamera(rotation_x=60, rotation_y=0)
        self.camera.position = (0, 30, -15)

    def create_robot_camera_window(self):
        props = WindowProperties()
        props.setSize(400, 300)
        props.setTitle("🤖 Robot First-Person View")

        fb_props = FrameBufferProperties()
        fb_props.setRgbColor(True)
        fb_props.setDepthBits(1)

        self.robot_cam_texture = Texture()

        self.robot_cam_window = base.graphicsEngine.makeOutput(
            base.pipe, "RobotView", -2,
            fb_props, props,
            0,  
            base.win.getGsg(), base.win
        )

        self.robot_cam = base.makeCamera(self.robot_cam_window)
        self.robot_cam.reparentTo(self.robot_entity)
        self.robot_cam.setPos(1.0, 0.5, 0.0)
        self.robot_cam.setHpr(-90, 0, 0)
        self.robot_cam_window.addRenderTexture(self.robot_cam_texture, GraphicsOutput.RTMCopyRam)
    
    def get_robot_camera_image(self):
        texture = self.robot_cam_texture

        if texture.hasRamImage():
            data = texture.getRamImageAs('RGB')
            width = texture.getXSize()
            height = texture.getYSize()
            try:
                img_array = np.frombuffer(data, dtype=np.uint8)
                img_array = img_array.reshape((height,width,3))
            except Exception as e:
                print("Error while capturing image:",e)
                return None
            return img_array
        else:
            return None
    
    def save_robot_camera_image(self, filename_prefix='robot_camera'):
        """
        Converts the image from the texture to PIL Image and saves it to disk
        """
        img_array = self.get_robot_camera_image()
        if img_array is not None:
            pil_img = Image.fromarray(img_array)
            pil_img = pil_img.transpose(Image.FLIP_TOP_BOTTOM)
            filename = f"{filename_prefix}_{int(time.time())}.png"
            pil_img.save(filename)
            print(f"Image saved as '{filename}'.")
        else:
            print("No image.")

    def update(self):
        # Mettre à jour la position de l'entité du robot
        robot_model = self.simulation_controller.robot_model
        robot_posx = robot_model.x
        robot_posy = robot_model.y
        robot_angle = robot_model.direction_angle

        # Translation globale du robot
        self.robot_entity.position = (robot_posx / 100 - 40, 0.4, robot_posy / 100 - 30)

        # Rotation globale du robot
        self.robot_entity.rotation_y = -math.degrees(robot_angle)

        left_speed = self.simulation_controller.robot_model.motor_speeds.get("left", 0)
        right_speed = self.simulation_controller.robot_model.motor_speeds.get("right", 0)
        angle_deg = math.degrees(self.simulation_controller.robot_model.direction_angle)
        self.speed_label.text = f"Speed: L={left_speed:.2f}°/s  R={right_speed:.2f}°/s\nAngle: {angle_deg:.1f}°"

        if not self.simulation_controller.simulation_running:
            return
            
        rc = self.simulation_controller.robot_controller
        if held_keys['q']:
            rc.increase_left_speed()
        if held_keys['a']:
            rc.decrease_left_speed()
        if held_keys['e']:
            rc.increase_right_speed()
        if held_keys['d']:
            rc.decrease_right_speed()
        if held_keys['w']:
            rc.move_forward()
        if held_keys['s']:
            rc.move_backward()

        if isinstance(self.control_panel.current_strategy, FollowBeaconByImageStrategy):
            end = self.simulation_controller.map_model.end_position
            if self.control_panel.end_box:
                self.control_panel.end_box.position = (end[0] / 100 - 40, 1, end[1] / 100 - 30)
                
        current_pos = (self.robot_entity.position.x, 0.1, self.robot_entity.position.z)
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
        if key == 'p':
            self.save_robot_camera_image()

    def handle_floor_click(self):
        pos = mouse.world_point
        x = (pos.x + 40) * 100
        y = (pos.z + 30) * 100
        cp = self.control_panel

        if cp.mode == 'set_start':
            if cp.start_box:
                cp.start_box.disable()
            cp.start_box = Entity(model='cube', color=color.red, scale=0.5, position=(pos.x, 0.25, pos.z))
            cp.map_model.set_start_position((x, y))
            print(f"✅ Start position set: ({x}, {y})")
            cp.mode = None

        elif cp.mode == 'set_end':
            if cp.end_box:
                cp.end_box.disable()
            cp.end_box = Entity(model='cube', color=color.blue, scale=0.5, position=(pos.x, 1, pos.z))
            cp.map_model.set_end_position((x, y))
            print(f"✅ End position set: ({x}, {y})")

    def reset_ursina_view(self):
        self.simulation_controller.reset_simulation()
        self.trail_points = []
        if self.trail_entity is not None:
            self.trail_entity.disable()
            self.trail_entity = None

        # Supprimer les entités de départ et d’arrivée
        if self.control_panel.start_box:
            destroy(self.control_panel.start_box)
            self.control_panel.start_box = None

        if self.control_panel.end_box:
            destroy(self.control_panel.end_box)
            self.control_panel.end_box = None
