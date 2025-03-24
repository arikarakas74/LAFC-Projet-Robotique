import time
import os
import cv2
import tempfile
from vpython import scene, vector, rate  # Make sure rate is imported
import math
import numpy as np

class Camera:
    def __init__(self, resolution=(640, 480), height=10.0, angle=0.0, focal_length=500):
        self.resolution = resolution
        self.height = height  # Camera height from ground in cm
        self.angle = angle  # Camera tilt angle in radians
        self.focal_length = focal_length  # Focal length in pixels
        self.beacon_color = (0, 0, 255)  # Red color for beacon in BGR format
        self.beacon_size = 20  # Size of beacon in pixels
        
        # Set up scene camera with default position
        scene.camera.pos = vector(0, self.height, 0)
        scene.camera.axis = vector(0, 0, 1)  # Looking forward
        scene.camera.up = vector(0, 1, 0)  # Up vector for proper orientation

    def create_camera_image(self, robot_x, robot_y, robot_angle, map_model):
        """Creates a simulated camera image based on the robot's current view with detailed error logging."""
        
        try:
            # Step 1: Update Camera Position
            try:
                scene.camera.pos = vector(robot_x, self.height, robot_y)
                scene.camera.axis = vector(math.cos(robot_angle), 0, math.sin(robot_angle))
            except Exception as e:
                print(f"❌ Error updating camera position: {e}")
                return None
            
            # Step 2: Allow Time for Rendering
            try:
                rate(10)  # Let VPython render with increased rate
                time.sleep(1)  # Wait for 1 second to allow for rendering
            except Exception as e:
                print(f"❌ Error in rate() (VPython rendering delay): {e}")
                return None
            
            # Step 3: Create Temporary File
            try:
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    temp_filename = temp_file.name
            except Exception as e:
                print(f"❌ Error creating temporary file: {e}")
                return None
            
            # Step 4: Capture Scene
            try:
                scene.waitfor('draw_complete')  # Ensure rendering is done
                scene.capture(temp_filename)
                print(f"✅ Scene captured: {temp_filename}")
            except Exception as e:
                print(f"❌ Error capturing scene: {e}")
                return None
            
            # Check if file exists and has non-zero size
            if os.path.exists(temp_filename):
                print(f"✅ File exists: {temp_filename}")
                file_size = os.path.getsize(temp_filename)
                print(f"✅ File size: {file_size} bytes")
            else:
                print(f"❌ File does not exist or failed to save: {temp_filename}")
                return None
            
            # Step 5: Read Captured Image
            try:
                image = cv2.imread(temp_filename)
                if image is None:
                    print(f"❌ Error: cv2.imread('{temp_filename}') returned None")
                else:
                    print(f"✅ Image successfully loaded.")
            except Exception as e:
                print(f"❌ Error reading image with OpenCV: {e}")
                return None
            
            # Step 6: Cleanup Temporary File
            try:
                os.unlink(temp_filename)
            except Exception as e:
                print(f"⚠️ Warning: Could not delete temporary file {temp_filename}: {e}")
            
            return image  # Return image if successful, None otherwise
        
        except Exception as e:
            print(f"🔥 Unexpected error in create_camera_image(): {e}")
            return None

    def get_camera_view(self, robot_x, robot_y, robot_angle, map_model):
        """Gets the actual view from the robot's camera and processes it to detect beacon"""
        # Get the camera image
        image = self.create_camera_image(robot_x, robot_y, robot_angle, map_model)
        
        if image is None:
            return None
            
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