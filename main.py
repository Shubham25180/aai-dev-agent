import sys
import os
from PyQt6.QtWidgets import QApplication
from gui.nexus_gui import NexusMainWindow  # Import the main window (which uses only UI widgets)

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("NEXUS AI Agent")
    app.setApplicationVersion("1.0.0")

    # Set application icon (if available)
    icon_path = os.path.join(os.path.dirname(__file__), 'gui', 'icon.png')
    if os.path.exists(icon_path):
        from PyQt6.QtGui import QIcon
        app.setWindowIcon(QIcon(icon_path))

    window = NexusMainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 