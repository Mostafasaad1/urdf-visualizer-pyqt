# opengl_widget.py
"""Main OpenGL widget for URDF visualization"""
import sys
import math
import numpy as np
from typing import Optional, Dict
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtCore import Qt
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import glutInit
from .urdf_model import URDFModel, URDFJoint
from .mesh_manager import MeshManager, HAS_TRIMESH
from .scene_manager import SceneManager
from .camera import Camera
from .geometry_renderer import GeometryRenderer
from .math_utils import MathUtils

class URDFGLWidget(QGLWidget):
    """Main OpenGL widget for URDF visualization"""
    def __init__(self, parent=None):
        super().__init__(parent)
        glutInit()
        # Core components
        self.urdf_model: Optional[URDFModel] = None
        self.mesh_manager = MeshManager()
        self.scene_manager = SceneManager()
        self.camera = Camera()
        self.renderer = None
        # State
        self.joint_angles: Dict[str, float] = {}
        self.last_mouse_pos = None
        self.initialized = False
        # Set widget properties
        self.setMinimumSize(400, 300)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Requires import

    def load_model(self, urdf_model: URDFModel):
        """Load URDF model for visualization"""
        # Clean up previous model
        if self.renderer:
            self.renderer.cleanup()
        self.mesh_manager.clear_cache()
        self.urdf_model = urdf_model
        # Initialize joint angles based on your Joint structure
        self.joint_angles = {j.name: 0.0 for j in self.urdf_model.get_joints() if j.type != "fixed"}
        if HAS_TRIMESH and self.urdf_model:
            for link in self.urdf_model.links.values():
                if link and link.visual and link.visual.geometry.type == "mesh" and link.visual.geometry.filename:
                    self.mesh_manager.preload_mesh_for_bounds(
                        link.visual.geometry.filename,
                        link.visual.geometry.scale # Can be None, handled in MeshManager
                    )
        self.scene_manager.calculate_scene_bounds(self.urdf_model, self.mesh_manager)
        self.scene_manager.auto_fit_camera(self.camera)
        self.update()

    def initializeGL(self):
        """Initialize OpenGL context"""
        if self.initialized:
            return
        glClearColor(0.15, 0.15, 0.2, 1.0)  # Darker blue-gray background
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glEnable(GL_NORMALIZE)
        # Light 0 (main directional light)
        glLightfv(GL_LIGHT0, GL_POSITION, [5, 5, 10, 0])
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        # Light 1 (fill light)
        glLightfv(GL_LIGHT1, GL_POSITION, [-5, -5, 5, 0])
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.4, 0.4, 0.4, 1.0])
        glLightfv(GL_LIGHT1, GL_SPECULAR, [0.2, 0.2, 0.2, 1.0])
        # Material properties
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, [0.3, 0.3, 0.3, 1.0])
        glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 32.0)
        # Initialize renderer
        self.renderer = GeometryRenderer(self.mesh_manager)
        self.initialized = True

    def resizeGL(self, w, h):
        """Handle window resize"""
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, w / float(h or 1), 0.1, 10000.0)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        """Render the scene"""
        if not self.initialized:
            return
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Setup camera
        self.camera.setup_view()
        # Render model if available
        if self.urdf_model and self.renderer:
            root = self.urdf_model.get_root()
            if root:
                self._draw_link(root, np.eye(4))

    def _draw_link(self, link_name: str, parent_transform: np.ndarray):
        """Recursively draw link and its children"""
        # Find the link object
        link = self.urdf_model.links.get(link_name)
        current_transform = parent_transform
        # Draw visual if present
        if link and link.visual and link.visual.geometry:
            try:
                xyz = MathUtils.parse_vector3(link.visual.origin.xyz) if link.visual.origin and link.visual.origin.xyz else np.zeros(3)
                rpy = MathUtils.parse_vector3(link.visual.origin.rpy) if link.visual.origin and link.visual.origin.rpy else np.zeros(3)
                current_transform = parent_transform @ MathUtils.create_transform(xyz, rpy)
            except Exception as e:
                print(f"Error applying visual origin for link {link_name}: {e}")
                pass # Use parent transform if origin is invalid
            glPushMatrix()
            glMultMatrixf(current_transform.T)
            # Pass the material object directly to the renderer
            self.renderer.render_geometry(link.visual.geometry, link.visual.material)
            glPopMatrix()
        # Draw children
        for joint in self.urdf_model.get_joints():
            if joint.parent == link_name:
                child_transform = self._compute_joint_transform(joint, current_transform)
                self._draw_link(joint.child, child_transform) # Recurse for child link

    def _compute_joint_transform(self, joint: URDFJoint, parent_transform: np.ndarray) -> np.ndarray:
        """Compute transformation for joint"""
        try:
            j_xyz = MathUtils.parse_vector3(joint.origin.xyz) if joint.origin and joint.origin.xyz else np.zeros(3)
            j_rpy = MathUtils.parse_vector3(joint.origin.rpy) if joint.origin and joint.origin.rpy else np.zeros(3)
            transform = parent_transform @ MathUtils.create_transform(j_xyz, j_rpy)
        except Exception as e:
            print(f"Error applying joint origin for joint {joint.name}: {e}")
            transform = parent_transform
        angle = self.joint_angles.get(joint.name, 0.0)
        # Parse axis string
        try:
            axis = MathUtils.parse_vector3(joint.axis) if joint.axis else np.array([0, 0, 1])
        except:
            axis = np.array([0, 0, 1])
        if joint.type in ["revolute", "continuous", "prismatic"]:
            if joint.type in ["revolute", "continuous"]:
                # Rotation transform
                c, s = math.cos(angle), math.sin(angle)
                # Normalize axis vector
                axis_norm = np.linalg.norm(axis)
                if axis_norm > 1e-6:
                    ux, uy, uz = axis / axis_norm
                else:
                    ux, uy, uz = 0, 0, 1 # Default to Z-axis if axis is zero
                R = np.array([
                    [c+ux*ux*(1-c), ux*uy*(1-c)-uz*s, ux*uz*(1-c)+uy*s, 0],
                    [uy*ux*(1-c)+uz*s, c+uy*uy*(1-c), uy*uz*(1-c)-ux*s, 0],
                    [uz*ux*(1-c)-uy*s, uz*uy*(1-c)+ux*s, c+uz*uz*(1-c), 0],
                    [0, 0, 0, 1]
                ], dtype=np.float32)
                transform = transform @ R
            elif joint.type == "prismatic":
                # Translation transform
                d = angle
                trans = np.eye(4)
                trans[:3, 3] = axis * d
                transform = transform @ trans
        return transform

    # --- Improved and Stabilized Mouse Interaction ---
    def mousePressEvent(self, event):
        """Handle mouse press events - Store the initial mouse position"""
        self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event):
        """Handle mouse move events"""
        if self.last_mouse_pos is None:
            return
        # Calculate mouse movement delta
        dx = event.x() - self.last_mouse_pos.x()
        dy = event.y() - self.last_mouse_pos.y()
        if event.buttons() & Qt.LeftButton:
            # --- Rotation (Left Mouse Button) - Keep as is ---
            self.camera.yaw += dx * 0.5
            self.camera.pitch += dy * 0.5
            self.camera.pitch = np.clip(self.camera.pitch, -89, 89)
        elif event.buttons() & Qt.RightButton:
            # --- Fixed Panning (Right Mouse Button) ---
            # Sensitivity factor for panning, scaled by camera distance for consistency
            pan_sensitivity = 0.01 * self.camera.distance
            # Get the camera's current yaw (horizontal rotation)
            yaw_rad = math.radians(self.camera.yaw)
            # Calculate the "Right" and "Up" vectors for panning relative to the camera's horizontal plane (Z=0 plane)
            # These define how screen X/Y movements map to world X/Y movements.
            # World X component of the screen's "right" direction
            pan_right_x = math.cos(yaw_rad)
            # World Y component of the screen's "right" direction
            pan_right_y = math.sin(yaw_rad)
            # World X component of the screen's "up" direction (perpendicular to right in XY plane)
            # Rotate (pan_right_x, pan_right_y) by 90 degrees counter-clockwise
            pan_up_x = -math.sin(yaw_rad)
            # World Y component of the screen's "up" direction
            pan_up_y = math.cos(yaw_rad)
            # Calculate the total world space movement based on mouse delta (dx, dy)
            # Move along the calculated panning axes
            delta_world_x = (dx * pan_right_x + dy * pan_up_x) * pan_sensitivity
            delta_world_y = (dx * pan_right_y + dy * pan_up_y) * pan_sensitivity
            # Apply the movement to the camera's center point
            # Subtracting the delta makes the panning feel natural (drag left -> scene moves right)
            self.camera.center[0] -= delta_world_x
            self.camera.center[1] -= delta_world_y
        # Update the last mouse position for the next event
        self.last_mouse_pos = event.pos()
        # Trigger a redraw
        self.update()

    def wheelEvent(self, event):
        """Handle mouse wheel events for zooming with improved sensitivity"""
        # Get the scroll delta (typically in 1/8 degree steps, hence / 120.0 for lines)
        delta = event.angleDelta().y() / 120.0
        # Adjust sensitivity for zoom (value closer to 1 = less sensitive)
        zoom_sensitivity = 0.9
        # Apply zoom: Multiply distance by a factor < 1 for zoom in, > 1 for zoom out
        # Using exponentiation makes it smoother and more predictable
        self.camera.distance *= zoom_sensitivity ** delta
        # Clamp the distance to reasonable limits
        self.camera.distance = np.clip(self.camera.distance, 0.1, 5000.0)
        # Trigger a redraw
        self.update()

    def mouseReleaseEvent(self, event):
        """Handle mouse release events - Reset stored state"""
        # Reset stored state on release for clean start on next drag
        self.last_mouse_pos = None
        # --- Optional: Reset View with Middle Mouse Button ---
        # Uncomment the lines below if you want to use the middle mouse button for reset
        # if event.button() == Qt.MiddleButton:
        #     self.scene_manager.auto_fit_camera(self.camera)
        #     self.update()

    def cleanup(self):
        """Clean up OpenGL resources"""
        if self.renderer:
            self.renderer.cleanup()
        self.mesh_manager.clear_cache()

    def reset_view(self):
        """Reset view to default"""
        self.camera.reset()
        self.scene_manager.auto_fit_camera(self.camera)
        self.update()

    def auto_fit_view(self):
        """Auto-fit view to ensure entire model fits the screen"""
        if self.urdf_model:
            self.scene_manager.calculate_scene_bounds(self.urdf_model, self.mesh_manager)
            self.scene_manager.auto_fit_camera(self.camera)
            self.update()