from ursina import *
from panda3d.core import Texture, GraphicsOutput, GraphicsPipe, WindowProperties, FrameBufferProperties
import time
from controller.StrategyAsync import FollowBeaconByCommandsStrategy
import numpy as np
from PIL import Image
import cv2


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
        self.frame_counter = 0
        self.img_array = None

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
        self.robot_cam.setPos(0.0, 0.4, 0.0)
        self.robot_cam.setHpr(-90, 0, 0)
        self.robot_cam_window.addRenderTexture(self.robot_cam_texture, GraphicsOutput.RTMCopyRam)
        self.robot_cam.node().getLens().setFov(50)
    
    def get_robot_camera_image(self):
        texture = self.robot_cam_texture

        if texture.hasRamImage():
            data = texture.getRamImageAs('RGB')
            width = texture.getXSize()
            height = texture.getYSize()
            try:
                self.img_array = np.frombuffer(data, dtype=np.uint8)
                self.img_array = self.img_array.reshape((height,width,3))
            except Exception as e:
                print("Error while capturing image:",e)
                return None
            return self.img_array
        else:
            return None
    
    def save_robot_camera_image(self):
        """
        Converts the image from the texture to PIL Image and saves it to disk
        """
        if self.img_array is not None:
            pil_img = Image.fromarray(self.img_array)
            pil_img = pil_img.transpose(Image.FLIP_TOP_BOTTOM)
            filename = f"robot_camera_{self.frame_counter}.png"
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

        self.frame_counter += 1
        self.img_array = self.get_robot_camera_image()
        beacon_pos = self.detect_blue_beacon()
        if beacon_pos:
            print(f"Beacon bleu détecté en pixel : {beacon_pos}")

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

        self.img_array = self.get_robot_camera_image()
    # 2. Sauvegarder immédiatement, si présence d'image (pas obligatoire comme les images sont conservés dans la mémoire)
        # if self.img_array is not None:
        #     self.save_robot_camera_image()

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
            
        elif cp.mode == 'set_obstacle':
            size_x = 25
            size_z = 100
            points = [
                (x - size_x, y - size_z),
                (x + size_x, y - size_z),
                (x + size_x, y + size_z), 
                (x - size_x, y + size_z)
            ]
            
            obstacle = Entity(
                model='cube',
                color=color.black,
                scale=(0.5, 2, 2), 
                position=(pos.x, 0.25, pos.z),
                collider='box'
            )
            
            obstacle_id = f"obstacle_{len(cp.map_model.obstacles)}"
            cp.map_model.add_obstacle(obstacle_id, points, obstacle, [])
            print(f"✅ Obstacle added at: ({x}, {y})")

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

        # Supprimer les obstacles
        for obstacle_id in list(self.control_panel.map_model.obstacles.keys()):
            points, obstacle_entity, line_ids = self.control_panel.map_model.obstacles[obstacle_id]
            if obstacle_entity:
                destroy(obstacle_entity)
            self.control_panel.map_model.remove_obstacle(obstacle_id)

    def detect_blue_beacon(self, img_array=None):
        """
        Renvoie (radius, cx, cy) du plus grand spot bleu détecté,
        ou None s'il n'y en a pas.
        """
        if img_array is None:
            img_array = self.img_array
        if img_array is None:
            return None

        # Flip vertical si nécessaire
        frame = np.flipud(img_array)

        # Conversion RGB→BGR puis HSV
        bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

        # Masque pour le bleu
        lower_blue = np.array([100, 150, 50])
        upper_blue = np.array([140, 255, 255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)

        # Nettoyage du masque
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # Contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        # Plus grand contour
        c = max(contours, key=cv2.contourArea)

        # Cercle minimal englobant
        (cx, cy), radius = cv2.minEnclosingCircle(c)
        if radius < 5:    # filtre optionnel des petits bruits
            return None

        return radius, int(cx), int(cy)