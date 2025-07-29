from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget
from widgets import SearchWidget, InstalledAppsWidget
from dialogs import InstallDialog
from winget_manager import WingetManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Winstaller - Windows Package Manager GUI")
        self.setMinimumSize(800, 600)
        
        self.manager = WingetManager()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create widgets for each tab
        self.search_widget = SearchWidget(self.manager)
        self.installed_widget = InstalledAppsWidget(self.manager)
        
        # Add tabs
        self.tab_widget.addTab(self.search_widget, "🔍 Search & Install")
        self.tab_widget.addTab(self.installed_widget, "📦 Installed Apps")
        
        # Set as central widget
        self.setCentralWidget(self.tab_widget)