import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from main_window import MainWindow

def setup_application():
    """Setup application with performance optimizations"""
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    app.setApplicationName("Winstaller")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Winstaller")
    
    try:
        icon = QIcon("package.png")
        app.setWindowIcon(icon)
    except Exception as e:
        print(f"Could not load application icon: {e}")
    
    if sys.platform == "win32":
        app.setStyle('Fusion')
    
    return app

if __name__ == "__main__":
    app = setup_application()
    window = MainWindow()
    window.setWindowOpacity(0.0)
    window.show()
    
    from PyQt5.QtCore import QPropertyAnimation, QEasingCurve
    fade_in = QPropertyAnimation(window, b"windowOpacity")
    fade_in.setDuration(600)  # 600ms fade-in
    fade_in.setStartValue(0.0)
    fade_in.setEndValue(1.0)
    fade_in.setEasingCurve(QEasingCurve.OutCubic)
    fade_in.start()
    
    window.fade_animation = fade_in
    
    sys.exit(app.exec_())