# mesh_manager.py
"""Manages mesh loading and caching"""
import os
import numpy as np
from typing import Dict, Optional, Any
# --- Corrected Import Statement ---
# Add GL_TRIANGLES and GL_COMPILE to the imported constants
from OpenGL.GL import glGenLists, glNewList, GL_COMPILE, glEnableClientState, glVertexPointer, glNormalPointer, glDrawElements, glDisableClientState, glEndList, glDeleteLists, GL_VERTEX_ARRAY, GL_NORMAL_ARRAY, GL_FLOAT, GL_UNSIGNED_INT, GL_TRIANGLES
# --- End of Import Correction ---
# Try to import trimesh for mesh support
try:
    import trimesh
    HAS_TRIMESH = True
except ImportError:
    HAS_TRIMESH = False
    print("Warning: trimesh not found. Mesh visualization will be disabled.")

class MeshManager:
    """Manages mesh loading and caching"""
    def __init__(self):
        self.mesh_cache: Dict[str, Any] = {}
        self.display_list_cache: Dict[str, int] = {}

    def resolve_filename(self, filename: str) -> str:
        """Resolve package:// URIs and relative paths"""
        if filename.startswith("package://"):
            resolved = filename.replace("package://", "")
            if os.path.exists(resolved):
                return resolved
            basename = os.path.basename(resolved)
            if os.path.exists(basename):
                return basename
            return resolved
        if not os.path.isabs(filename) and not os.path.exists(filename):
            alt = os.path.basename(filename)
            if os.path.exists(alt):
                return alt
        return filename

    def preload_mesh_for_bounds(self, filename: str, scale_str: Optional[str] = None):
        """Preload mesh and cache it for bounds calculation"""
        if not HAS_TRIMESH:
            return
        resolved = self.resolve_filename(filename)
        if not os.path.exists(resolved):
            # print(f"Warning: Mesh file not found: {resolved}") # Optional warning
            return
        if resolved in self.mesh_cache:
            return
        try:
            # print(f"Loading mesh: {resolved}") # Debug print
            mesh = trimesh.load(resolved, process=False, force="mesh")
            if isinstance(mesh, trimesh.Scene):
                geoms = [m for m in mesh.geometry.values() if isinstance(m, trimesh.Trimesh)]
                if geoms:
                    mesh = trimesh.util.concatenate(geoms)
                else:
                    print(f"Warning: No valid meshes found in scene: {resolved}")
                    return
            if not isinstance(mesh, trimesh.Trimesh):
                print(f"Warning: Loaded object is not a Trimesh: {resolved}")
                return
            if scale_str:
                try:
                    parts = [float(x) for x in scale_str.split()]
                    if len(parts) == 1:
                        mesh.apply_scale(parts[0])
                    elif len(parts) == 3:
                        mesh.apply_scale(np.array(parts))
                except Exception as e:
                    print(f"Warning: Failed to apply scale '{scale_str}' to mesh '{resolved}': {e}")
            self.mesh_cache[resolved] = mesh
        except Exception as e:
            print(f"Preload error for {resolved}: {e}")

    def get_mesh(self, filename: str) -> Optional[Any]:
        """Get cached mesh by filename"""
        resolved = self.resolve_filename(filename)
        return self.mesh_cache.get(resolved, None)

    def create_display_list(self, filename: str) -> Optional[int]:
        """Create OpenGL display list for mesh rendering"""
        resolved = self.resolve_filename(filename)
        if resolved in self.display_list_cache:
            return self.display_list_cache[resolved]
        mesh = self.get_mesh(filename)
        if mesh is None:
            return None
        # Create display list
        display_list = glGenLists(1)
        if display_list == 0:
            return None
        glNewList(display_list, GL_COMPILE) # GL_COMPILE is now imported
        # Render mesh
        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_NORMAL_ARRAY)
        glVertexPointer(3, GL_FLOAT, 0, mesh.vertices.astype(np.float32))
        glNormalPointer(GL_FLOAT, 0, mesh.vertex_normals.astype(np.float32))
        # --- GL_TRIANGLES is now imported ---
        if mesh.faces is not None:
            glDrawElements(GL_TRIANGLES, mesh.faces.size, GL_UNSIGNED_INT, mesh.faces.astype(np.uint32))
        # --- End of GL_TRIANGLES usage ---
        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_NORMAL_ARRAY)
        glEndList()
        self.display_list_cache[resolved] = display_list
        return display_list

    def clear_cache(self):
        """Clear all caches"""
        # Delete display lists
        for display_list in self.display_list_cache.values():
            glDeleteLists(display_list, 1)
        self.display_list_cache.clear()
        self.mesh_cache.clear()
