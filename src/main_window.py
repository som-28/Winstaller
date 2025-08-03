from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTabWidget, QStatusBar, QMenuBar, QAction
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QKeySequence
from widgets import SearchWidget, InstalledAppsWidget
from dialogs import InstallDialog
from winget_manager import WingetManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = WingetManager()
        self.init_ui()
        self.init_menu()
        self.init_statusbar()
        
        # Clean up expired cache periodically
        self.cache_cleanup_timer = QTimer()
        self.cache_cleanup_timer.timeout.connect(self.cleanup_cache)
        self.cache_cleanup_timer.start(1800000)  # 30 minutes
        
    def init_ui(self):
        self.setWindowTitle("✨ Winstaller - Windows Package Manager")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Set application icon
        try:
            icon = QIcon("package.png")
            self.setWindowIcon(icon)
        except Exception as e:
            print(f"Could not load icon: {e}")
        
        # Apply premium modern styling inspired by macOS and Windows 11
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #fafbfc, stop: 1 #f2f4f8);
                color: #1f2937;
            }
            
            /* Modern Tab Widget */
            QTabWidget::pane {
                border: none;
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                margin-top: 0px;
            }
            
            QTabWidget::tab-bar {
                alignment: center;
                background-color: transparent;
            }
            
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.8), stop: 1 rgba(248, 250, 252, 0.8));
                border: 1px solid rgba(209, 213, 219, 0.4);
                border-bottom: none;
                padding: 12px 24px;
                margin-right: 4px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                color: #6b7280;
                min-width: 120px;
            }
            
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8fafc);
                color: #1f2937;
                border-color: rgba(59, 130, 246, 0.3);
                border-bottom: 2px solid #3b82f6;
            }
            
            QTabBar::tab:hover:!selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.95), stop: 1 rgba(243, 244, 246, 0.95));
                color: #374151;
            }
            
            /* Premium Buttons */
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3b82f6, stop: 1 #1d4ed8);
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                min-height: 20px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2563eb, stop: 1 #1e40af);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1d4ed8, stop: 1 #1e3a8a);
            }
            
            QPushButton:disabled {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #e5e7eb, stop: 1 #d1d5db);
                color: #9ca3af;
            }
            
            /* Modern Text Inputs */
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(209, 213, 219, 0.6);
                border-radius: 10px;
                padding: 12px 16px;
                font-size: 14px;
                color: #1f2937;
                selection-background-color: #3b82f6;
            }
            
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: #ffffff;
            }
            
            QLineEdit:hover {
                border-color: rgba(59, 130, 246, 0.4);
            }
            
            /* Premium List Widgets */
            QListWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(209, 213, 219, 0.3);
                border-radius: 12px;
                padding: 8px;
                font-size: 14px;
                outline: none;
                alternate-background-color: rgba(248, 250, 252, 0.5);
            }
            
            QListWidget::item {
                padding: 16px;
                margin: 4px;
                border-radius: 8px;
                background-color: transparent;
                border: 1px solid transparent;
            }
            
            QListWidget::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(59, 130, 246, 0.08), stop: 1 rgba(59, 130, 246, 0.04));
                border-color: rgba(59, 130, 246, 0.2);
            }
            
            QListWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(59, 130, 246, 0.15), stop: 1 rgba(59, 130, 246, 0.08));
                border-color: rgba(59, 130, 246, 0.3);
                color: #1f2937;
            }
            
            /* Progress Bars */
            QProgressBar {
                background-color: rgba(229, 231, 235, 0.8);
                border: none;
                border-radius: 6px;
                height: 12px;
                text-align: center;
            }
            
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3b82f6, stop: 1 #1d4ed8);
                border-radius: 6px;
            }
            
            /* Labels */
            QLabel {
                color: #374151;
                font-size: 14px;
            }
            
            /* Scrollbars */
            QScrollBar:vertical {
                background-color: rgba(243, 244, 246, 0.5);
                width: 12px;
                border-radius: 6px;
                margin: 0px;
            }
            
            QScrollBar::handle:vertical {
                background-color: rgba(156, 163, 175, 0.6);
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: rgba(107, 114, 128, 0.8);
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* Status Bar */
            QStatusBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(255, 255, 255, 0.9), stop: 1 rgba(243, 244, 246, 0.9));
                border-top: 1px solid rgba(209, 213, 219, 0.3);
                padding: 4px 12px;
                color: #6b7280;
                font-size: 12px;
            }
            
            /* Menu Bar */
            QMenuBar {
                background-color: rgba(255, 255, 255, 0.95);
                border-bottom: 1px solid rgba(209, 213, 219, 0.3);
                padding: 4px 8px;
                font-size: 13px;
                color: #374151;
            }
            
            QMenuBar::item {
                padding: 6px 12px;
                border-radius: 6px;
                margin: 2px;
            }
            
            QMenuBar::item:selected {
                background-color: rgba(59, 130, 246, 0.1);
            }
            
            QMenu {
                background-color: rgba(255, 255, 255, 0.98);
                border: 1px solid rgba(209, 213, 219, 0.4);
                border-radius: 8px;
                padding: 4px;
                color: #374151;
            }
            
            QMenu::item {
                padding: 8px 16px;
                border-radius: 4px;
                margin: 1px;
            }
            
            QMenu::item:selected {
                background-color: rgba(59, 130, 246, 0.1);
            }
        """)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create widgets for each tab
        self.search_widget = SearchWidget(self.manager)
        self.installed_widget = InstalledAppsWidget(self.manager)
        
        # Add tabs with modern icons
        self.tab_widget.addTab(self.search_widget, "🔍 Discover")
        self.tab_widget.addTab(self.installed_widget, "📦 Installed")
        
        # Set as central widget
        self.setCentralWidget(self.tab_widget)
        
    def init_menu(self):
        """Initialize menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('&File')
        
        refresh_action = QAction('&Refresh All', self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('&Tools')
        
        clear_cache_action = QAction('&Clear All Caches', self)
        clear_cache_action.triggered.connect(self.clear_all_caches)
        tools_menu.addAction(clear_cache_action)
        
        # Help menu
        help_menu = menubar.addMenu('&Help')
        
        about_action = QAction('&About Winstaller', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def init_statusbar(self):
        """Initialize status bar"""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready - Winstaller v1.0.0")
        
    def refresh_all(self):
        """Refresh all data"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 1:  # Installed apps tab
            self.installed_widget.refresh_installed_apps()
        self.statusbar.showMessage("Refreshed data", 3000)
        
    def clear_all_caches(self):
        """Clear all application caches"""
        self.manager.clear_all_caches()
        self.statusbar.showMessage("All caches cleared", 3000)
        
    def cleanup_cache(self):
        """Periodic cache cleanup"""
        self.manager.cache.clear_expired_cache()
        
    def show_about(self):
        """Show about dialog"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.about(self, "About Winstaller", 
                         "Winstaller v1.0.0\n\n"
                         "A modern GUI for Windows Package Manager (winget)\n\n"
                         "Features:\n"
                         "• Search and install applications\n"
                         "• View and manage installed apps\n"
                         "• Check for updates\n"
                         "• Fast caching system\n"
                         "• Background operations\n\n"
                         "Built with Python & PyQt5")