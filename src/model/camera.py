import math
import cv2
import numpy as np
from vpython import scene, vector, canvas, rate
from utils.geometry import normalize_angle

class Camera:
    def __init__(self, resolution=(640, 480), height=10.0, angle=0.0, focal_length=500):
        self.resolution = resolution
        self.height = height  # Camera height from ground in cm
        self.angle = angle  # Camera tilt angle in radians
        self.focal_length = focal_length  # Focal length in pixels
        self.beacon_color = (0, 0, 255)  # Red color for beacon in BGR format
        self.beacon_size = 20  # Size of beacon in pixels
        
        # Initialize camera view
        self.camera_view = canvas(width=resolution[0], 
                                height=resolution[1],
                                background=vector(0.8, 0.8, 0.8))
        # Set up camera view with default position
        self.camera_view.camera.pos = vector(0, self.height, 0)
        self.camera_view.camera.axis = vector(0, 0, 1)  # Looking forward
        self.camera_view.camera.up = vector(0, 1, 0)  # Up vector for proper orientation

    def __del__(self):
        """Cleanup when the object is destroyed"""
        if hasattr(self, 'camera_view'):
            self.camera_view.close()

    def create_camera_image(self, robot_x, robot_y, robot_angle, map_model):
        """Creates a simulated camera image based on the robot's current view"""
        # Create a blank image for the camera view
        image = np.zeros((self.resolution[1], self.resolution[0], 3), dtype=np.uint8)
        
        # Draw ground plane (gray)
        cv2.rectangle(image, (0, 0), (self.resolution[0], self.resolution[1]), (200, 200, 200), -1)
        
        # Draw obstacles in the camera view based on their visibility
        for obstacle_id, (points, _, _) in map_model.obstacles.items():
            # Calculate obstacle position relative to robot
            obstacle_x = sum(p[0] for p in points) / len(points)
            obstacle_y = sum(p[1] for p in points) / len(points)
            
            dx = obstacle_x - robot_x
            dy = obstacle_y - robot_y
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Calculate angle to obstacle relative to robot's direction
            obstacle_angle = math.atan2(dy, dx) - robot_angle
            obstacle_angle = normalize_angle(obstacle_angle)
            
            # Calculate the visible portion of the obstacle
            # Convert angle to degrees for easier comparison
            angle_deg = math.degrees(obstacle_angle)
            
            # Calculate the base size of the obstacle in pixels
            base_size = 20  # cm
            size = int((base_size / distance) * self.focal_length)
            size = max(2, min(size, 100))  # Limit size between 2 and 100 pixels
            
            # Calculate how much of the obstacle is visible
            # If the obstacle is partially in view, we need to clip it
            visible_portion = 1.0
            if abs(angle_deg) > 30:
                continue  # Completely out of view
            elif abs(angle_deg) > 25:  # Partially in view
                visible_portion = (30 - abs(angle_deg)) / 5  # Linear interpolation
            
            # Map the obstacle's position to camera coordinates
            camera_x = int((angle_deg + 30) / 60 * self.resolution[0])
            
            # Calculate vertical position based on distance and height
            camera_y = int(self.resolution[1] * (1 - min(1, distance/200)))  # 200cm max distance
            
            # Draw the obstacle as a black rectangle with perspective effect
            height = int(size * 1.5)  # Make height slightly larger than width for perspective
            
            # Calculate the visible width based on the visible portion
            visible_width = int(size * visible_portion)
            
            # Draw the obstacle with clipping
            if angle_deg > 0:  # Obstacle is to the right
                cv2.rectangle(image, 
                            (camera_x, camera_y - height),
                            (camera_x + visible_width, camera_y),
                            (0, 0, 0), -1)
            else:  # Obstacle is to the left
                cv2.rectangle(image, 
                            (camera_x - visible_width, camera_y - height),
                            (camera_x, camera_y),
                            (0, 0, 0), -1)
        
        # Draw the beacon if it's in view
        beacon_x, beacon_y = map_model.end_position
        dx = beacon_x - robot_x
        dy = beacon_y - robot_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Calculate angle to beacon relative to robot's direction
        beacon_angle = math.atan2(dy, dx) - robot_angle
        beacon_angle = normalize_angle(beacon_angle)
        
        # Calculate the visible portion of the beacon
        angle_deg = math.degrees(beacon_angle)
        
        if abs(angle_deg) > 30:
            return image  # Beacon completely out of view
            
        # Calculate visible portion
        visible_portion = 1.0
        if abs(angle_deg) > 25:  # Partially in view
            visible_portion = (30 - abs(angle_deg)) / 5  # Linear interpolation
        
        # Map the beacon's position to camera coordinates
        camera_x = int((angle_deg + 30) / 60 * self.resolution[0])
        camera_y = int(self.resolution[1] * (1 - min(1, distance/200)))
        
        # Calculate beacon size based on distance
        base_size = 10  # cm
        size = int((base_size / distance) * self.focal_length)
        size = max(5, min(size, 50))  # Limit size between 5 and 50 pixels
        
        # Calculate the visible radius
        visible_radius = int(size * visible_portion)
        
        # Draw the beacon as a red circle with clipping
        if visible_radius > 0:
            # Create a mask for the circle
            mask = np.zeros((self.resolution[1], self.resolution[0]), dtype=np.uint8)
            cv2.circle(mask, (camera_x, camera_y), visible_radius, 255, -1)
            
            # Apply the mask to create a clipped circle
            if angle_deg > 0:  # Beacon is to the right
                mask[:, :camera_x] = 0
            else:  # Beacon is to the left
                mask[:, camera_x:] = 0
            
            # Draw the beacon using the mask
            image[mask > 0] = self.beacon_color
            
            # Add a white border to make it more visible
            cv2.circle(image, (camera_x, camera_y), visible_radius, (255, 255, 255), 2)
        
        # Add a grid pattern to help with depth perception
        grid_spacing = 50  # pixels
        for x in range(0, self.resolution[0], grid_spacing):
            cv2.line(image, (x, 0), (x, self.resolution[1]), (180, 180, 180), 1)
        for y in range(0, self.resolution[1], grid_spacing):
            cv2.line(image, (0, y), (self.resolution[0], y), (180, 180, 180), 1)
        
        return image

    def get_camera_view(self, robot_x, robot_y, robot_angle, map_model):
        """Gets the actual view from the robot's camera and processes it to detect beacon"""
        # Get the camera image
        image = self.create_camera_image(robot_x, robot_y, robot_angle, map_model)
        
        # Process image to detect beacon
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Define color range for red beacon (using two ranges to handle red wrap-around)
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # Create mask for red color using both ranges
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # Apply morphological operations to reduce noise
        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours of red objects
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Get the largest contour (should be our beacon)
            largest_contour = max(contours, key=cv2.contourArea)
            
            # Filter out very small contours
            if cv2.contourArea(largest_contour) < 100:  # Minimum area threshold
                return None
                
            M = cv2.moments(largest_contour)
            
            if M["m00"] != 0:
                # Calculate center of the beacon in image coordinates
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                
                # Calculate relative angle from center of image
                # Map camera x coordinate back to angle (-30 to 30 degrees)
                relative_angle = (cx / self.resolution[0] * math.radians(60)) - math.radians(30)
                
                # Calculate distance using the beacon's apparent size
                # Using the known beacon size (10cm) and focal length
                contour_area = cv2.contourArea(largest_contour)
                known_area = math.pi * (5 ** 2)  # Area of 10cm diameter circle
                distance = math.sqrt((known_area / contour_area) * (self.focal_length ** 2))
                
                # Debug visualization
                debug_image = image.copy()
                # Draw contour
                cv2.drawContours(debug_image, [largest_contour], -1, (0, 255, 0), 2)
                # Draw center point
                cv2.circle(debug_image, (cx, cy), 5, (0, 0, 255), -1)
                # Draw angle lines
                center_x = self.resolution[0] // 2
                cv2.line(debug_image, (center_x, 0), (center_x, self.resolution[1]), (255, 0, 0), 1)
                cv2.line(debug_image, (center_x, cy), (cx, cy), (0, 255, 255), 2)
                
                return {
                    'detected': True,
                    'distance': distance,
                    'angle': relative_angle,
                    'camera_x': cx,
                    'camera_y': cy,
                    'debug_image': debug_image
                }
        
        return None 