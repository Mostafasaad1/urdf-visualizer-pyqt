# main.py
"""Application entry point"""
import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from .urdf_visualizer_app import URDFVisualizerWindow

def main():
    """Application entry point"""
    # Set application style
    QApplication.setStyle("Fusion")
    app = QApplication(sys.argv)
    # Set application palette for better looking widgets
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(240, 240, 240))
    palette.setColor(QPalette.WindowText, QColor(50, 50, 50))
    palette.setColor(QPalette.Base, QColor(255, 255, 255))
    palette.setColor(QPalette.AlternateBase, QColor(240, 240, 240))
    palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 220))
    palette.setColor(QPalette.ToolTipText, QColor(0, 0, 0))
    palette.setColor(QPalette.Text, QColor(50, 50, 50))
    palette.setColor(QPalette.Button, QColor(240, 240, 240))
    palette.setColor(QPalette.ButtonText, QColor(50, 50, 50))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
    app.setPalette(palette)
    window = URDFVisualizerWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()