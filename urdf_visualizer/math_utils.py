# math_utils.py
"""Mathematical utility functions"""
import math
import numpy as np

class MathUtils:
    """Mathematical utility functions"""

    @staticmethod
    def parse_vector3(text: str) -> np.ndarray:
        """Parse a string of 3 numbers into numpy array"""
        try:
            return np.array([float(x) for x in text.strip().split()])
        except Exception:
            return np.zeros(3)

    @staticmethod
    def rpy_to_matrix(rpy: np.ndarray) -> np.ndarray:
        """Convert roll-pitch-yaw to rotation matrix"""
        r, p, y = rpy
        cr, sr = math.cos(r), math.sin(r)
        cp, sp = math.cos(p), math.sin(p)
        cy, sy = math.cos(y), math.sin(y)
        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
        return Rz @ Ry @ Rx

    @staticmethod
    def create_transform(xyz: np.ndarray, rpy: np.ndarray) -> np.ndarray:
        """Create 4x4 transformation matrix from xyz and rpy"""
        T = np.eye(4)
        T[:3, :3] = MathUtils.rpy_to_matrix(rpy)
        T[:3, 3] = xyz
        return T