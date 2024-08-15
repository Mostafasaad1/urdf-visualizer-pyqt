# scene_manager.py
"""Manages scene bounds and camera positioning"""
import numpy as np
from typing import Optional
from .urdf_model import URDFModel
from .mesh_manager import MeshManager

class SceneManager:
    """Manages scene bounds and camera positioning"""
    def __init__(self):
        self.center = np.zeros(3)
        self.scene_radius = 1.0

    def calculate_scene_bounds(self, model: URDFModel, mesh_manager: MeshManager):
        """Calculate scene bounds from all visuals"""
        mins, maxs = [], []
        if not model:
            return
        for link in model.links.values():
            if not link.visual:
                continue
            geom = link.visual.geometry
            # Access attributes directly from your Geometry class
            if geom.type == "mesh" and geom.filename:
                mesh = mesh_manager.get_mesh(geom.filename)
                if mesh is not None:
                    b = mesh.bounds
                    mins.append(b[0])
                    maxs.append(b[1])
            elif geom.type == "box" and geom.size:
                 try:
                    size = [float(x) for x in geom.size]
                    half = np.array(size) / 2.0
                    mins.append(-half)
                    maxs.append(half)
                 except Exception as e:
                     print(f"Warning: Failed to parse box size '{geom.size}': {e}")
            elif geom.type == "sphere" and geom.size: # sphere uses size[0] for radius
                 try:
                    r = float(geom.size[0])
                    mins.append([-r, -r, -r])
                    maxs.append([r, r, r])
                 except Exception as e:
                     print(f"Warning: Failed to parse sphere radius '{geom.size[0]}': {e}")
            elif geom.type == "cylinder" and geom.size and len(geom.size) >= 2: # cylinder uses size[0] for radius, size[1] for length
                 try:
                    r = float(geom.size[0])
                    l = float(geom.size[1])
                    mins.append([-r, -r, -l/2])
                    maxs.append([r, r, l/2])
                 except Exception as e:
                     print(f"Warning: Failed to parse cylinder dimensions '{geom.size}': {e}")
        if mins and maxs:
            mins, maxs = np.min(mins, axis=0), np.max(maxs, axis=0)
            self.center = (mins + maxs) / 2.0
            self.scene_radius = np.linalg.norm(maxs - mins) / 2.0
        else:
            self.center = np.zeros(3)
            self.scene_radius = 1.0

    def auto_fit_camera(self, camera):
        """Auto-fit camera to scene"""
        camera.distance = self.scene_radius * 2.0
        camera.distance = np.clip(camera.distance, 0.1, 5000.0)
        camera.yaw = 45
        camera.pitch = 20