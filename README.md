# URDF Visualizer

A Python application for visualizing URDF (Unified Robot Description Format) files using PyQt5 and OpenGL.

## Features

*   3D visualization of robot models defined in URDF.
*   Interactive camera controls (rotate, pan, zoom).
*   Joint manipulation via sliders.
*   Automatic view fitting.
*   Support for basic URDF primitives (box, sphere, cylinder).
*   Support for mesh visualization (requires `trimesh`).
*   Material color rendering from URDF.

## Installation

### Prerequisites

*   Python 3.8 or higher.

### Install from Source (Recommended for Development)

1.  Clone or download this repository.
2.  Navigate to the `urdf_visualizer_pkg` directory (the one containing `setup.py`).
3.  It's highly recommended to use a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
4.  Install the package in editable mode:
    ```bash
    pip install -e .
    ```
    This installs the package and its dependencies. The `-e` flag means "editable", so changes to the source code are immediately reflected without needing to reinstall.

### Install Optional Mesh Support

For mesh visualization, install the optional `trimesh` dependency:

```bash
pip install trimesh
# Or, if you installed the package already:
pip install urdf_visualizer[mesh]
```