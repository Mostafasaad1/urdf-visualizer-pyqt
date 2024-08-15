# urdf_visualizer/__init__.py

"""
URDF Visualizer Package

A package for visualizing URDF (Unified Robot Description Format) files using PyQt5 and OpenGL.
"""

# Optionally expose main classes/functions at the package level for easier imports
# from .urdf_model import URDFModel, URDFLink, URDFJoint, URDFGeometry, URDFMaterial, URDFVisual, URDFOrigin
# from .urdf_parser import URDFParser
# from .main import main # If you want to expose the main function directly

# Define package version
__version__ = '1.0.0'
__author__ = 'Your Name' # Replace with your name or organization

# This makes the main application callable when the package is run
from .main import main

if __name__ == "__main__":
    main()