import math
import numpy as np
from typing import Tuple, List, Union

def normalize_angle_3d(pitch: float, yaw: float, roll: float) -> Tuple[float, float, float]:
    """Normalizes 3D Euler angles (pitch, yaw, roll) to standard ranges.
    
    Args:
        pitch: Rotation around the X-axis (up/down) in radians
        yaw: Rotation around the Y-axis (left/right) in radians
        roll: Rotation around the Z-axis (tilt) in radians
        
    Returns:
        Tuple of normalized angles (pitch, yaw, roll)
    """
    # Normalize pitch to [-π/2, π/2]
    while pitch > math.pi/2:
        pitch -= math.pi
    while pitch < -math.pi/2:
        pitch += math.pi
        
    # Normalize yaw to [-π, π]
    while yaw > math.pi:
        yaw -= 2 * math.pi
    while yaw < -math.pi:
        yaw += 2 * math.pi
        
    # Normalize roll to [-π, π]
    while roll > math.pi:
        roll -= 2 * math.pi
    while roll < -math.pi:
        roll += 2 * math.pi
        
    return (pitch, yaw, roll)

def rotation_matrix_from_angles(pitch: float, yaw: float, roll: float) -> np.ndarray:
    """Creates a 3D rotation matrix from Euler angles.
    
    Args:
        pitch: Rotation around the X-axis in radians
        yaw: Rotation around the Y-axis in radians
        roll: Rotation around the Z-axis in radians
        
    Returns:
        4x4 rotation matrix as numpy array
    """
    # X-axis rotation (pitch)
    c1 = math.cos(pitch)
    s1 = math.sin(pitch)
    rot_x = np.array([
        [1, 0, 0, 0],
        [0, c1, -s1, 0],
        [0, s1, c1, 0],
        [0, 0, 0, 1]
    ])
    
    # Y-axis rotation (yaw)
    c2 = math.cos(yaw)
    s2 = math.sin(yaw)
    rot_y = np.array([
        [c2, 0, s2, 0],
        [0, 1, 0, 0],
        [-s2, 0, c2, 0],
        [0, 0, 0, 1]
    ])
    
    # Z-axis rotation (roll)
    c3 = math.cos(roll)
    s3 = math.sin(roll)
    rot_z = np.array([
        [c3, -s3, 0, 0],
        [s3, c3, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ])
    
    # Combined rotation matrix: R = Rz * Ry * Rx
    return np.matmul(np.matmul(rot_z, rot_y), rot_x)

def point_in_cuboid(x: float, y: float, z: float, 
                   cuboid_min: Tuple[float, float, float], 
                   cuboid_max: Tuple[float, float, float]) -> bool:
    """Check if a 3D point is inside a cuboid (axis-aligned bounding box).
    
    Args:
        x, y, z: Coordinates of the point to check
        cuboid_min: Minimum coordinates (x_min, y_min, z_min) of the cuboid
        cuboid_max: Maximum coordinates (x_max, y_max, z_max) of the cuboid
        
    Returns:
        True if the point is inside the cuboid, False otherwise
    """
    x_min, y_min, z_min = cuboid_min
    x_max, y_max, z_max = cuboid_max
    
    return (x_min <= x <= x_max and 
            y_min <= y <= y_max and 
            z_min <= z <= z_max)

def transform_point(point: Tuple[float, float, float], 
                  matrix: np.ndarray) -> Tuple[float, float, float]:
    """Transforms a 3D point using a transformation matrix.
    
    Args:
        point: Tuple (x, y, z) representing the point
        matrix: 4x4 transformation matrix
        
    Returns:
        Transformed point as a tuple (x', y', z')
    """
    x, y, z = point
    p = np.array([x, y, z, 1.0])
    transformed = np.matmul(matrix, p)
    return (transformed[0], transformed[1], transformed[2]) 