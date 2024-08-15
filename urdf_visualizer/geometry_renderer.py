# geometry_renderer.py
"""Renders different geometry types"""
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutSolidCube
from typing import Optional
from .urdf_model import URDFGeometry, URDFMaterial
from .mesh_manager import MeshManager, HAS_TRIMESH

class GeometryRenderer:
    """Renders different geometry types"""
    def __init__(self, mesh_manager: MeshManager):
        self.mesh_manager = mesh_manager
        self.quadric_cache = {}  # Cache for quadrics to avoid recreating them

    def _get_quadric(self, key: str):
        """Get or create a quadric object"""
        if key not in self.quadric_cache:
            self.quadric_cache[key] = gluNewQuadric()
            gluQuadricNormals(self.quadric_cache[key], GLU_SMOOTH)
        return self.quadric_cache[key]

    def render_geometry(self, geom: URDFGeometry, material: Optional[URDFMaterial]):
        """Render geometry with appropriate OpenGL calls"""
        # Set material color - now correctly uses the URDFMaterial object
        if material:
            # print(f"Applying material color: {material.color} for material {material.name}") # Debug
            glColor4f(*material.color)
        else:
            # print("Applying default color") # Debug
            glColor4f(0.8, 0.8, 0.8, 1.0)  # Default light gray with alpha
        if geom.type == "box" and geom.size:
             try:
                size = [float(x) for x in geom.size]
                glScalef(*size)
                glutSolidCube(1.0)
             except Exception as e:
                 print(f"Warning: Failed to render box with size '{geom.size}': {e}")
                 glutSolidCube(1.0) # Default size on error
        elif geom.type == "sphere" and geom.size:
             try:
                r = float(geom.size[0])
                quad = self._get_quadric("sphere")
                gluSphere(quad, r, 20, 20)
             except Exception as e:
                 print(f"Warning: Failed to render sphere with radius '{geom.size[0]}': {e}")
                 gluSphere(self._get_quadric("sphere_default"), 0.5, 20, 20) # Default radius
        elif geom.type == "cylinder" and geom.size and len(geom.size) >= 2:
             try:
                r = float(geom.size[0])
                l = float(geom.size[1])
                quad = self._get_quadric("cylinder")
                glPushMatrix()
                glTranslatef(0, 0, -l/2)
                gluCylinder(quad, r, r, l, 20, 20)
                glPopMatrix()
             except Exception as e:
                 print(f"Warning: Failed to render cylinder with dimensions '{geom.size}': {e}")
                 quad = self._get_quadric("cylinder_default")
                 glPushMatrix()
                 glTranslatef(0, 0, -0.5)
                 gluCylinder(quad, 0.1, 0.1, 1.0, 20, 20)
                 glPopMatrix()
        elif geom.type == "mesh" and geom.filename and HAS_TRIMESH:
            # Use display list for better performance
            display_list = self.mesh_manager.create_display_list(geom.filename)
            if display_list is not None:
                glCallList(display_list)
        # Handle 'none' or 'unknown' types gracefully (render nothing)

    def cleanup(self):
        """Clean up OpenGL resources"""
        for quadric in self.quadric_cache.values():
            gluDeleteQuadric(quadric)
        self.quadric_cache.clear()