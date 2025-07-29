from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QVBoxLayout, QListWidget, QMessageBox, QHBoxLayout
from dialogs import InstallDialog, UninstallDialog

class SearchWidget(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search for apps...")
        self.search_button = QPushButton("Search")
        self.results_list = QListWidget()
        self.search_button.clicked.connect(self.search_apps)
        self.results_list.itemDoubleClicked.connect(self.install_app)
        layout = QVBoxLayout()
        layout.addWidget(self.search_box)
        layout.addWidget(self.search_button)
        layout.addWidget(self.results_list)
        self.setLayout(layout)

    def search_apps(self):
        query = self.search_box.text()
        results = self.manager.search(query)
        self.results_list.clear()
        for app in results:
            self.results_list.addItem(app)

    def install_app(self, item):
        app_info = item.text()
        if "(" in app_info and ")" in app_info:
            app_id = app_info.split("(")[-1].split(")")[0].strip()
        else:
            app_id = app_info
        dialog = InstallDialog(app_id, self.manager)
        dialog.exec_()


class InstalledAppsWidget(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
        # Create UI elements
        self.refresh_button = QPushButton("Refresh Installed Apps")
        self.show_upgrades_button = QPushButton("Show Available Updates")
        self.installed_list = QListWidget()
        
        # Create layout
        layout = QVBoxLayout()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.show_upgrades_button)
        
        layout.addLayout(button_layout)
        layout.addWidget(self.installed_list)
        
        self.setLayout(layout)
        
        # Connect signals
        self.refresh_button.clicked.connect(self.refresh_installed_apps)
        self.show_upgrades_button.clicked.connect(self.show_upgradeable_apps)
        self.installed_list.itemDoubleClicked.connect(self.uninstall_app)
        
        # Load installed apps on startup
        self.refresh_installed_apps()
    
    def refresh_installed_apps(self):
        """Refresh the list of installed applications"""
        try:
            installed_apps = self.manager.list_installed()
            self.installed_list.clear()
            
            if not installed_apps:
                self.installed_list.addItem("No installed applications found or winget not accessible")
                return
            
            for app in installed_apps:
                self.installed_list.addItem(app)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load installed apps: {str(e)}")
    
    def show_upgradeable_apps(self):
        """Show applications that can be upgraded"""
        try:
            upgradeable_apps = self.manager.get_upgradeable()
            self.installed_list.clear()
            
            if not upgradeable_apps:
                self.installed_list.addItem("No updates available")
                return
            
            for app in upgradeable_apps:
                self.installed_list.addItem(f"🔄 {app}")
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to check for updates: {str(e)}")
    
    def uninstall_app(self, item):
        """Handle uninstalling an application"""
        app_info = item.text()
        
        # Skip if it's a status message
        if app_info.startswith("No installed") or app_info.startswith("No updates"):
            return
        
        # Remove update emoji if present
        if app_info.startswith("🔄 "):
            app_info = app_info[2:]
        
        # Extract app ID from the formatted string
        if "(" in app_info and ")" in app_info:
            app_id = app_info.split("(")[-1].split(")")[0].strip()
        else:
            # If no ID in parentheses, use the first word as app name
            app_id = app_info.split()[0] if app_info.split() else app_info
        
        # Show uninstall dialog
        dialog = UninstallDialog(app_id, self.manager)
        if dialog.exec_() == dialog.Accepted:
            # Refresh the list after uninstall
            self.refresh_installed_apps()