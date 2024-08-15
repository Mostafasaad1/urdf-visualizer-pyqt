# camera.py
"""3D camera for OpenGL rendering"""
import math
import numpy as np
from OpenGL.GLU import gluLookAt

class Camera:
    """3D camera for OpenGL rendering"""
    def __init__(self):
        self.distance = 5.0
        self.yaw = 45
        self.pitch = 30
        self.center = np.zeros(3)

    def get_position(self) -> tuple:
        """Calculate camera position from spherical coordinates"""
        eye_x = self.center[0] + self.distance * math.cos(math.radians(self.pitch)) * math.cos(math.radians(self.yaw))
        eye_y = self.center[1] + self.distance * math.cos(math.radians(self.pitch)) * math.sin(math.radians(self.yaw))
        eye_z = self.center[2] + self.distance * math.sin(math.radians(self.pitch))
        return eye_x, eye_y, eye_z

    def setup_view(self):
        """Setup OpenGL view matrix"""
        eye_x, eye_y, eye_z = self.get_position()
        gluLookAt(eye_x, eye_y, eye_z,
                  self.center[0], self.center[1], self.center[2],
                  0, 0, 1)

    def reset(self):
        """Reset camera to default position"""
        self.distance = 5.0
        self.yaw = 45
        self.pitch = 30
        self.center = np.zeros(3)