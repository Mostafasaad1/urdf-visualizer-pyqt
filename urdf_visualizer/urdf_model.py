# urdf_model.py
"""URDF Data Models"""
from typing import Dict, Optional, List

class URDFGeometry:
    """Represents geometry data in URDF"""
    def __init__(self, type_: str, filename: Optional[str] = None, size=None, scale=None):
        self.type = type_
        self.filename = filename or ""
        self.size = size or []
        self.scale = scale or ""

class URDFOrigin:
    """Represents origin transform in URDF"""
    def __init__(self, xyz="0 0 0", rpy="0 0 0"):
        self.xyz = xyz
        self.rpy = rpy

class URDFMaterial:
    """Represents material properties in URDF"""
    def __init__(self, name: str, color: Optional[List[float]] = None):
        self.name = name
        # Ensure color is always a 4-element list
        if color and len(color) >= 3:
            # If alpha is missing, assume 1.0
            self.color = list(color[:3]) + [color[3] if len(color) > 3 else 1.0]
        else:
            self.color = [0.8, 0.8, 0.8, 1.0]  # Default light gray

class URDFVisual:
    """Represents visual element in URDF"""
    def __init__(self, geometry: URDFGeometry, origin: URDFOrigin, material: Optional[URDFMaterial] = None):
        self.geometry = geometry
        self.origin = origin
        # Store the actual URDFMaterial object
        self.material = material

class URDFLink:
    """Represents link in URDF"""
    def __init__(self, name: str, visual: Optional[URDFVisual] = None):
        self.name = name
        self.visual = visual

class URDFJoint:
    """Represents joint in URDF"""
    def __init__(self, name: str, type_: str, parent: str, child: str,
                 axis: str = "0 0 1", origin: Optional[URDFOrigin] = None):
        self.name = name
        self.type = type_
        self.parent = parent
        self.child = child
        self.axis = axis
        self.origin = origin or URDFOrigin()

class URDFModel:
    """Main URDF model container"""
    def __init__(self):
        self.links: Dict[str, URDFLink] = {}
        self.joints: Dict[str, URDFJoint] = {}
        self.materials: Dict[str, URDFMaterial] = {}

    def get_root(self) -> Optional[str]:
        """Get the root link name"""
        children = {j.child for j in self.joints.values()}
        for link in self.links.keys():
            if link not in children:
                return link
        return None

    def get_joints(self) -> List[URDFJoint]:
        """Get all joints"""
        return list(self.joints.values())