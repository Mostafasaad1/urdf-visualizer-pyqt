# setup.py
from setuptools import setup, find_packages

# Read the contents of your README file for the long description
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='urdf_visualizer',
    version='1.0.0',
    author='Your Name', # Replace with your name
    author_email='your.email@example.com', # Replace with your email
    description='A URDF (Unified Robot Description Format) visualizer using PyQt5 and OpenGL.',
    long_description=long_description,
    long_description_content_type='text/markdown', # Assuming README is in Markdown
    url='https://github.com/yourusername/urdf_visualizer', # Replace with your repo URL if applicable
    # Find all packages automatically within the urdf_visualizer_pkg directory
    packages=find_packages(where='.'),
    # Specify where the main package is located if it's not directly in the root of the repo
    # package_dir={'': 'urdf_visualizer_pkg'}, # Uncomment if needed, but usually not with this structure
    classifiers=[
        'Development Status :: 4 - Beta', # Adjust as needed (e.g., 3 - Alpha, 5 - Production/Stable)
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License', # Choose your license
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8', # Specify minimum Python version
    # List your package's dependencies
    install_requires=[
        'PyQt5',
        'PyOpenGL',
        'numpy',
        # 'trimesh', # Optional, make it optional in code as well
    ],
    # Optional dependencies (extras)
    extras_require={
        'mesh': ['trimesh'], # Install with `pip install urdf_visualizer[mesh]`
    },
    # Entry point script - this creates a command-line script
    entry_points={
        'console_scripts': [
            'urdfviz=urdf_visualizer.main:main', # Command 'urdfviz' will run urdf_visualizer/main.py::main
        ],
    },
    # Include package data (if you have non-Python files like icons, you'd list them here or use MANIFEST.in)
    include_package_data=True,
    # Keywords to help people find your package
    keywords=['urdf', 'robotics', 'visualization', 'opengl', 'pyqt5', '3d'],
)