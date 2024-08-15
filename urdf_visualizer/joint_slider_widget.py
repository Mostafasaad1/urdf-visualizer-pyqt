# joint_slider_widget.py
"""Custom widget for joint slider with label and value display"""
import math
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSlider, QVBoxLayout, QGroupBox, QScrollArea
from PyQt5.QtCore import Qt

class JointSliderWidget(QWidget):
    """Custom widget for joint slider with label and value display"""
    def __init__(self, joint_name: str, joint_type: str, lower_limit: float = -180.0, upper_limit: float = 180.0, parent=None):
        super().__init__(parent)
        self.joint_name = joint_name
        self.joint_type = joint_type
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI components"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        # Joint name label
        self.name_label = QLabel(self.joint_name)
        self.name_label.setMinimumWidth(120)
        self.name_label.setStyleSheet("font-weight: bold; color: #333333;")
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        # Set range based on joint limits
        self.slider.setRange(int(self.lower_limit), int(self.upper_limit))
        self.slider.setValue(0)
        self.slider.setMinimumWidth(150)
        # Value label
        self.value_label = QLabel(f"{0}°" if self.joint_type in ["revolute", "continuous"] else f"{0}")
        self.value_label.setMinimumWidth(40)
        self.value_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.value_label.setStyleSheet("color: #666666; font-family: monospace;")
        # Connect slider to update label
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.name_label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)
        # Set background style
        self.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 4px;
                padding: 2px;
            }
            QWidget:hover {
                background-color: #e9ecef;
            }
        """)

    def on_slider_changed(self, value):
        """Update value label when slider changes"""
        if self.joint_type in ["revolute", "continuous"]:
            self.value_label.setText(f"{value}°")
        else:
            self.value_label.setText(f"{value}")

    def set_value(self, value):
        """Set slider value"""
        self.slider.setValue(int(value))

    def get_value(self):
        """Get slider value"""
        return self.slider.value()