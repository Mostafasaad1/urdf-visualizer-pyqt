# urdf_parser.py
"""Parser for URDF files"""
import os
import xml.etree.ElementTree as ET
from typing import Optional
from .urdf_model import URDFModel, URDFGeometry, URDFOrigin, URDFMaterial, URDFVisual, URDFLink, URDFJoint

class URDFParser:
    """Parser for URDF files"""
    @staticmethod
    def load_model(file_path: str) -> URDFModel:
        """Load URDF model from file"""
        tree = ET.parse(file_path)
        root = tree.getroot()
        model = URDFModel()
        # Load materials first
        URDFParser._load_materials(root, model)
        # Load links
        for link_elem in root.findall("link"):
            name = link_elem.attrib["name"]
            visual = URDFParser._parse_visual(link_elem, model)
            model.links[name] = URDFLink(name, visual)
        # Load joints
        for joint_elem in root.findall("joint"):
            joint = URDFParser._parse_joint(joint_elem)
            model.joints[joint.name] = joint
        return model

    @staticmethod
    def _load_materials(root, model: URDFModel):
        """Load materials from URDF"""
        for material_elem in root.findall("material"):
            name = material_elem.attrib["name"]
            color_elem = material_elem.find("color")
            color = [0.8, 0.8, 0.8, 1.0] # Default color
            if color_elem is not None:
                rgba_str = color_elem.attrib.get("rgba")
                if rgba_str:
                    try:
                        rgba_values = [float(x) for x in rgba_str.strip().split()]
                        if len(rgba_values) >= 3:
                            color = rgba_values
                        # URDFMaterial constructor will handle clamping/padding
                    except ValueError:
                        print(f"Warning: Invalid RGBA values '{rgba_str}' for material '{name}'. Using default.")
            model.materials[name] = URDFMaterial(name, color)

    @staticmethod
    def _parse_visual(link_elem, model: URDFModel) -> Optional[URDFVisual]:
        """Parse visual element from link, correctly linking material objects"""
        visual_elem = link_elem.find("visual")
        if visual_elem is None:
            return None
        # Parse origin
        origin_elem = visual_elem.find("origin")
        origin_xyz = origin_elem.attrib.get("xyz", "0 0 0") if origin_elem is not None else "0 0 0"
        origin_rpy = origin_elem.attrib.get("rpy", "0 0 0") if origin_elem is not None else "0 0 0"
        origin = URDFOrigin(xyz=origin_xyz, rpy=origin_rpy)
        # Parse material - look for inline material first, then reference
        material = None
        material_elem = visual_elem.find("material")
        if material_elem is not None:
            material_name = material_elem.attrib.get("name")
            # Check if it's an inline material definition
            color_elem = material_elem.find("color")
            if color_elem is not None:
                # Inline material definition
                rgba_str = color_elem.attrib.get("rgba")
                if rgba_str:
                    try:
                        color = [float(x) for x in rgba_str.strip().split()]
                        # Create a temporary material object for inline definition
                        material = URDFMaterial(material_name, color)
                        # print(f"Created inline material: {material_name} with color {material.color}") # Debug
                    except ValueError:
                        print(f"Warning: Invalid RGBA values '{rgba_str}' for inline material '{material_name}'.")
                else:
                    print(f"Warning: Color element found without RGBA attribute in material '{material_name}'.")
            else:
                # Reference to existing material defined in <material> tags
                # Use the material object directly from the model's materials dict
                if material_name in model.materials:
                    material = model.materials[material_name]
                    # print(f"Linked reference material: {material_name}") # Debug
                else:
                    print(f"Warning: Referenced material '{material_name}' not found in root <material> definitions. Using default.")
        # Parse geometry
        geometry = URDFParser._parse_geometry(visual_elem)
        if geometry is None:
            return None
        # Return URDFVisual with the material OBJECT
        return URDFVisual(geometry, origin, material)

    @staticmethod
    def _parse_geometry(visual_elem) -> Optional[URDFGeometry]:
        """Parse geometry element"""
        geometry_elem = visual_elem.find("geometry")
        if geometry_elem is None:
            return None
        if geometry_elem.find("mesh") is not None:
            mesh_elem = geometry_elem.find("mesh")
            filename = mesh_elem.attrib.get("filename", "")
            scale = mesh_elem.attrib.get("scale", "")
            return URDFGeometry("mesh", filename, scale=scale)
        elif geometry_elem.find("box") is not None:
            size = geometry_elem.find("box").attrib.get("size", "1 1 1")
            return URDFGeometry("box", size=size.split())
        elif geometry_elem.find("cylinder") is not None:
            r = geometry_elem.find("cylinder").attrib.get("radius", "0.1")
            l = geometry_elem.find("cylinder").attrib.get("length", "1.0")
            return URDFGeometry("cylinder", size=[r, l])
        elif geometry_elem.find("sphere") is not None:
            r = geometry_elem.find("sphere").attrib.get("radius", "0.1")
            return URDFGeometry("sphere", size=[r])
        return None

    @staticmethod
    def _parse_joint(joint_elem) -> URDFJoint:
        """Parse joint element"""
        name = joint_elem.attrib["name"]
        type_ = joint_elem.attrib.get("type", "revolute")
        parent = joint_elem.find("parent").attrib["link"]
        child = joint_elem.find("child").attrib["link"]
        axis_elem = joint_elem.find("axis")
        axis = axis_elem.attrib.get("xyz", "0 0 1") if axis_elem is not None else "0 0 1"
        origin_elem = joint_elem.find("origin")
        origin_xyz = origin_elem.attrib.get("xyz", "0 0 0") if origin_elem is not None else "0 0 0"
        origin_rpy = origin_elem.attrib.get("rpy", "0 0 0") if origin_elem is not None else "0 0 0"
        origin = URDFOrigin(xyz=origin_xyz, rpy=origin_rpy)
        return URDFJoint(name, type_, parent, child, axis, origin)