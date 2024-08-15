# urdf_visualizer_app.py
"""Main application window with enhanced UI/UX"""
import os
import sys
import math
from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget,
    QFileDialog, QLabel, QSlider, QHBoxLayout, QMessageBox,
    QPushButton, QAction, QStatusBar, QSplitter, QGroupBox,
    QGridLayout, QFrame, QSizePolicy, QApplication, QScrollArea
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPalette, QColor
from .opengl_widget import URDFGLWidget
from .urdf_parser import URDFParser
from .joint_slider_widget import JointSliderWidget

class URDFVisualizerWindow(QMainWindow):
    """Main application window with enhanced UI/UX"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("URDF Visualizer")
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)
        # Create UI components
        self.gl_widget = URDFGLWidget(self)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # Store slider references for proper cleanup
        self.joint_sliders = {}  # Dictionary to store slider references
        # Create main layout
        self.create_main_layout()
        # Create menu
        self.create_menu()
        # Set initial status
        self.update_status("Ready. Click 'Load URDF' to begin.")
        # State
        self.urdf_model = None

    def create_main_layout(self):
        """Create the main application layout"""
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setHandleWidth(1)
        # Left panel (controls)
        left_panel = self.create_control_panel()
        # Right panel (3D view)
        right_panel = self.create_view_panel()
        # Add panels to splitter
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 900])  # Default sizes
        # Set central widget
        self.setCentralWidget(main_splitter)

    def create_control_panel(self):
        """Create the control panel"""
        panel = QWidget()
        panel.setMinimumWidth(400)
        panel.setMaximumWidth(600)
        layout = QVBoxLayout(panel)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        # Control panel title
        title = QLabel("Model Controls")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        # View controls group
        view_group = QGroupBox("View Controls")
        view_layout = QVBoxLayout(view_group)
        # View control buttons
        btn_layout = QHBoxLayout()
        self.load_btn = QPushButton("📂 Load URDF")
        self.load_btn.clicked.connect(self.load_urdf_dialog)
        self.load_btn.setStyleSheet(self.get_button_style("#3498db"))
        self.reset_btn = QPushButton("↺ Reset View")
        self.reset_btn.clicked.connect(self.reset_view)
        self.reset_btn.setStyleSheet(self.get_button_style("#95a5a6"))
        self.autofit_btn = QPushButton("🔍 Auto-fit")
        self.autofit_btn.clicked.connect(self.auto_fit_view)
        self.autofit_btn.setStyleSheet(self.get_button_style("#2ecc71"))
        btn_layout.addWidget(self.load_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.autofit_btn)
        view_layout.addLayout(btn_layout)
        layout.addWidget(view_group)
        # Joint controls group
        self.joints_group = QGroupBox("Joint Controls")
        self.joints_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        joints_layout = QVBoxLayout(self.joints_group)
        # Scroll area for joint sliders
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
        self.joint_sliders_widget = QWidget()
        self.joint_sliders_layout = QVBoxLayout(self.joint_sliders_widget)
        self.joint_sliders_layout.setSpacing(2)
        self.joint_sliders_layout.setContentsMargins(5, 5, 5, 5)
        self.scroll_area.setWidget(self.joint_sliders_widget)
        joints_layout.addWidget(self.scroll_area)
        layout.addWidget(self.joints_group)
        # Spacer
        layout.addStretch()
        # Info panel
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout(info_group)
        self.info_label = QLabel("No model loaded")
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet("color: #666666;")
        info_layout.addWidget(self.info_label)
        layout.addWidget(info_group)
        return panel

    def create_view_panel(self):
        """Create the 3D view panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        # Add OpenGL widget with border
        self.gl_widget.setStyleSheet("""
            QGLWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: #2c3e50;
            }
        """)
        layout.addWidget(self.gl_widget)
        return panel

    def create_menu(self):
        """Create application menu"""
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #f8f9fa;
                border-bottom: 1px solid #dee2e6;
            }
            QMenuBar::item {
                padding: 8px 12px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #e9ecef;
            }
            QMenuBar::item:pressed {
                background: #dde0e3;
            }
        """)
        # File menu
        file_menu = menubar.addMenu("File")
        load_action = QAction("Load URDF...", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_urdf_dialog)
        file_menu.addAction(load_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        # View menu
        view_menu = menubar.addMenu("View")
        reset_action = QAction("Reset View", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self.reset_view)
        view_menu.addAction(reset_action)
        autofit_action = QAction("Auto-fit View", self)
        autofit_action.setShortcut("Ctrl+F")
        autofit_action.triggered.connect(self.auto_fit_view)
        view_menu.addAction(autofit_action)
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def get_button_style(self, color):
        """Get standardized button style"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color, 20)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 40)};
            }}
            QPushButton:disabled {{
                background-color: #bdc3c7;
            }}
        """

    def darken_color(self, hex_color, percent):
        """Darken a hex color by percentage"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def load_urdf_dialog(self):
        """Show file dialog and load URDF"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open URDF File", "", "URDF Files (*.urdf);;All Files (*)"
        )
        if file_path:
            try:
                self.update_status("Loading URDF...")
                QApplication.processEvents()
                model = URDFParser.load_model(file_path)
                if model and model.links:
                    self.urdf_model = model
                    self.gl_widget.load_model(self.urdf_model)
                    self.populate_joint_sliders()
                    self.update_info(f"Loaded: {os.path.basename(file_path)}")
                    self.update_status(f"Successfully loaded {os.path.basename(file_path)}")
                else:
                    self.update_info("URDF loaded but has no links or visuals.")
                    self.update_status("Model has no visual elements")
            except Exception as e:
                self.update_info("Error loading URDF.")
                self.update_status("Error loading model")
                QMessageBox.critical(self, "Load Error", f"An error occurred while loading the URDF:\n{e}")

    def populate_joint_sliders(self):
        """Create sliders for joint control"""
        # Clear existing sliders properly
        self.clear_joint_sliders()
        if not self.urdf_model:
            return
        # Update info
        joint_count = len([j for j in self.urdf_model.get_joints() if j.type in ["revolute", "continuous", "prismatic"]])
        self.update_info(f"Model: {len(self.urdf_model.links)} links, {joint_count} controllable joints")
        # Create sliders for each joint
        for joint in self.urdf_model.get_joints():
            if joint.type in ["revolute", "continuous", "prismatic"]:
                # Create custom slider widget (using default range for simplicity here,
                # but you could parse limits from the URDF if needed)
                slider_widget = JointSliderWidget(joint.name, joint.type)
                # Store reference to slider
                self.joint_sliders[joint.name] = slider_widget
                # Connect slider with proper closure
                def make_callback(joint_name):
                    return lambda val: self.on_slider_changed(joint_name, val)
                slider_widget.slider.valueChanged.connect(make_callback(joint.name))
                # Add to layout
                self.joint_sliders_layout.addWidget(slider_widget)
        # Add stretch to keep sliders at top
        self.joint_sliders_layout.addStretch()

    def clear_joint_sliders(self):
        """Clear all joint sliders properly"""
        # Clear the dictionary
        self.joint_sliders.clear()
        # Remove all widgets from layout
        while self.joint_sliders_layout.count():
            child = self.joint_sliders_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def on_slider_changed(self, joint_name: str, value: int):
        """Handle joint slider changes"""
        if self.gl_widget.urdf_model:
            self.gl_widget.joint_angles[joint_name] = math.radians(value)
            self.gl_widget.update()

    def reset_view(self):
        """Reset the 3D view"""
        self.gl_widget.reset_view()
        self.update_status("View reset to default position")

    def auto_fit_view(self):
        """Auto-fit the 3D view to show the entire model"""
        if self.urdf_model:
            self.gl_widget.auto_fit_view()
            self.update_status("View auto-fitted to show entire model")
        else:
            self.update_status("No model loaded to auto-fit")

    def update_status(self, message: str):
        """Update status bar message"""
        self.statusBar().showMessage(message)

    def update_info(self, message: str):
        """Update info panel message"""
        self.info_label.setText(message)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About URDF Visualizer",
                         "URDF Visualizer v1.0\n"
                         "A powerful tool for visualizing URDF robot models.\n"
                         "Features:\n"
                         "• 3D visualization with OpenGL\n"
                         "• Joint manipulation\n"
                         "• Auto-fit view\n"
                         "• Material support\n"
                         "• Mesh rendering")

    def closeEvent(self, event):
        """Handle window close event"""
        self.gl_widget.cleanup()
        event.accept()