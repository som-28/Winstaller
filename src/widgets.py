from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, QVBoxLayout, 
                             QListWidget, QMessageBox, QHBoxLayout, QLabel, 
                             QProgressBar, QCheckBox, QSplitter, QListWidgetItem, QApplication)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt, QSize
from PyQt5.QtGui import QFont, QIcon
from dialogs import InstallDialog, UninstallDialog

class CheckableListWidgetItem(QListWidgetItem):
    """Custom list widget item with checkbox functionality"""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable)
        self.setCheckState(Qt.Unchecked)

class SearchThread(QThread):
    """Background thread for search operations"""
    results_ready = pyqtSignal(list)
    search_finished = pyqtSignal()
    
    def __init__(self, manager, query):
        super().__init__()
        self.manager = manager
        self.query = query
    
    def run(self):
        try:
            results = self.manager.search(self.query)
            self.results_ready.emit(results)
        except Exception as e:
            print(f"Search thread error: {e}")
            self.results_ready.emit([])
        finally:
            self.search_finished.emit()

class SearchWidget(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.search_thread = None
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Modern search section with card design
        search_card = QWidget()
        search_card.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        search_layout = QVBoxLayout(search_card)
        search_layout.setSpacing(16)
        
        # Search input row
        search_input_layout = QHBoxLayout()
        search_input_layout.setSpacing(12)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search for applications...")
        self.search_box.textChanged.connect(self.on_search_text_changed)
        self.search_box.returnPressed.connect(self.search_apps)
        self.search_box.setMinimumHeight(44)
        
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_apps)
        self.search_button.setMinimumHeight(44)
        self.search_button.setMinimumWidth(100)
        
        search_input_layout.addWidget(self.search_box, 1)
        search_input_layout.addWidget(self.search_button)
        
        # Progress indicator with modern styling
        self.search_progress = QProgressBar()
        self.search_progress.setRange(0, 0)  # Indeterminate
        self.search_progress.hide()
        self.search_progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(229, 231, 235, 0.8);
                border: none;
                border-radius: 6px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #3b82f6, stop: 1 #1d4ed8);
                border-radius: 6px;
            }
        """)
        
        search_layout.addLayout(search_input_layout)
        search_layout.addWidget(self.search_progress)
        
        # Batch operations section
        batch_layout = QHBoxLayout()
        batch_layout.setSpacing(8)
        
        self.select_all_btn = QPushButton("☑️ Select All")
        self.select_all_btn.clicked.connect(self.toggle_select_all_items)
        self.select_all_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #8b5cf6, stop: 1 #7c3aed);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #7c3aed, stop: 1 #6d28d9);
            }
        """)
        
        self.install_selected_btn = QPushButton("📦 Install Selected")
        self.install_selected_btn.clicked.connect(self.install_selected_apps)
        self.install_selected_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #10b981, stop: 1 #059669);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 11px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #059669, stop: 1 #047857);
            }
        """)
        
        self.add_to_favorites_btn = QPushButton("⭐ Add to Favorites")
        self.add_to_favorites_btn.clicked.connect(self.add_selected_to_favorites)
        self.add_to_favorites_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f59e0b, stop: 1 #d97706);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 11px;
                min-width: 110px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #d97706, stop: 1 #b45309);
            }
        """)
        
        batch_layout.addWidget(self.select_all_btn)
        batch_layout.addWidget(self.install_selected_btn)
        batch_layout.addWidget(self.add_to_favorites_btn)
        batch_layout.addStretch()
        
        search_layout.addLayout(batch_layout)
        
        # Status and selection labels with modern styling
        self.status_label = QLabel("💡 Enter search terms to find applications")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
                padding: 8px 12px;
                background-color: rgba(249, 250, 251, 0.8);
                border-radius: 8px;
                border: 1px solid rgba(229, 231, 235, 0.5);
            }
        """)
        
        self.search_selection_label = QLabel("")
        self.search_selection_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(34, 197, 94, 0.1), stop: 1 rgba(34, 197, 94, 0.05));
                border: 1px solid rgba(34, 197, 94, 0.2);
                border-radius: 8px;
                padding: 5px;
                color: #006600;
                font-weight: bold;
            }
        """)
        self.search_selection_label.hide()
        
        # Results list
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.install_app)
        self.results_list.itemChanged.connect(self.on_search_item_changed)
        
        # Improve search results styling with premium design
        self.results_list.setAlternatingRowColors(False)
        self.results_list.setToolTip("Check boxes to select • Double-click to install individual apps")
        
        # Add custom premium styling
        self.results_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(209, 213, 219, 0.3);
                border-radius: 12px;
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                padding: 16px 20px;
                margin: 4px 2px;
                border-radius: 10px;
                background-color: transparent;
                border: 1px solid transparent;
                font-size: 14px;
                min-height: 20px;
                color: #374151;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(59, 130, 246, 0.08), stop: 1 rgba(59, 130, 246, 0.04));
                border-color: rgba(59, 130, 246, 0.2);
                color: #1f2937;
            }
            QListWidget::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #d1d5db;
                background-color: white;
                margin-right: 8px;
            }
            QListWidget::indicator:hover {
                border-color: #3b82f6;
                background-color: rgba(59, 130, 246, 0.1);
            }
            QListWidget::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDVMNCA4TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                background-repeat: no-repeat;
                background-position: center;
            }
        """)
        self.search_selection_label.hide()
        
        # Clear cache button with modern styling
        cache_layout = QHBoxLayout()
        self.clear_cache_btn = QPushButton("🗑️ Clear Search Cache")
        self.clear_cache_btn.clicked.connect(self.clear_search_cache)
        self.clear_cache_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #6b7280, stop: 1 #4b5563);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4b5563, stop: 1 #374151);
            }
        """)
        cache_layout.addWidget(self.clear_cache_btn)
        cache_layout.addStretch()
        
        # Add everything to main layout
        layout.addWidget(search_card)
        layout.addWidget(self.status_label)
        layout.addWidget(self.search_selection_label)
        layout.addWidget(self.results_list, 1)  # Give results list most space
        layout.addLayout(cache_layout)
        
        self.setLayout(layout)

    def on_search_text_changed(self, text):
        """Handle real-time search with debouncing"""
        if len(text.strip()) >= 2:
            # Restart timer for debounced search
            self.search_timer.stop()
            self.search_timer.start(500)  # 500ms delay
        else:
            self.search_timer.stop()
            self.results_list.clear()
            self.status_label.setText("Enter at least 2 characters to search")

    def search_apps(self):
        """Trigger immediate search"""
        self.search_timer.stop()
        self.perform_search()

    def perform_search(self):
        """Perform the actual search in background thread"""
        query = self.search_box.text().strip()
        if len(query) < 2:
            return
            
        # Don't start new search if one is already running
        if self.search_thread and self.search_thread.isRunning():
            return
        
        self.search_button.setEnabled(False)
        self.search_progress.show()
        self.status_label.setText(f"Searching for '{query}'...")
        
        # Start background search
        self.search_thread = SearchThread(self.manager, query)
        self.search_thread.results_ready.connect(self.on_search_results)
        self.search_thread.search_finished.connect(self.on_search_finished)
        self.search_thread.start()

    def on_search_results(self, results):
        """Handle search results"""
        self.results_list.clear()
        self.search_selection_label.hide()  # Hide selection when loading new results
        
        if not results:
            item = QListWidgetItem("No applications found. Try different search terms.")
            item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)  # Remove checkbox for status messages
            self.results_list.addItem(item)
            self.status_label.setText("No results found")
        else:
            for app_text in results:
                # Create checkable list item
                item = CheckableListWidgetItem(app_text)
                self.results_list.addItem(item)
            
            self.status_label.setText(f"Found {len(results)} applications")
            self.update_selection_status()
    
    def on_search_finished(self):
        """Clean up after search completes"""
        self.search_button.setEnabled(True)
        self.search_progress.hide()

    def clear_search_cache(self):
        """Clear search cache"""
        self.manager.cache.clear_cache()
        QMessageBox.information(self, "Cache Cleared", "Search cache has been cleared!")
    
    def toggle_select_all_items(self):
        """Toggle select all items in search results"""
        # Check if any items are selected
        selected_count = 0
        total_count = 0
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if not item.text().startswith("No applications found") and hasattr(item, 'setCheckState'):
                total_count += 1
                if item.checkState() == Qt.Checked:
                    selected_count += 1
        
        # If all are selected, unselect all. Otherwise, select all
        if selected_count == total_count and total_count > 0:
            # Unselect all
            for i in range(self.results_list.count()):
                item = self.results_list.item(i)
                if not item.text().startswith("No applications found") and hasattr(item, 'setCheckState'):
                    item.setCheckState(Qt.Unchecked)
            self.select_all_btn.setText("☑️ Select All")
        else:
            # Select all
            for i in range(self.results_list.count()):
                item = self.results_list.item(i)
                if not item.text().startswith("No applications found") and hasattr(item, 'setCheckState'):
                    item.setCheckState(Qt.Checked)
            self.select_all_btn.setText("☐ Unselect All")
        
        self.update_selection_status()
    
    def install_selected_apps(self):
        """Install all selected applications"""
        selected_items = []
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if hasattr(item, 'checkState') and item.checkState() == Qt.Checked:
                selected_items.append(item)
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please check the boxes next to applications you want to install.")
            return
        
        # Extract app names for confirmation
        app_names = []
        for item in selected_items:
            app_text = item.text()
            if not app_text.startswith("No applications found"):
                # Parse the format: "AppName (Publisher.AppID)"
                if "(" in app_text and ")" in app_text:
                    app_name = app_text.split("(")[0].strip()
                else:
                    app_name = app_text.strip()
                app_names.append(app_name)
        
        if not app_names:
            return
        
        # Show confirmation dialog
        msg = f"Install {len(app_names)} selected applications?\n\n" + "\n".join(f"• {name}" for name in app_names[:10])
        if len(app_names) > 10:
            msg += f"\n... and {len(app_names) - 10} more"
        
        reply = QMessageBox.question(self, "Batch Install", msg, 
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.start_batch_install(selected_items)
    
    def start_batch_install(self, selected_items):
        """Start batch installation process"""
        from PyQt5.QtWidgets import QProgressDialog
        
        progress = QProgressDialog("Installing applications...", "Cancel", 0, len(selected_items), self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        successful = 0
        failed = 0
        
        for i, item in enumerate(selected_items):
            if progress.wasCanceled():
                break
                
            app_text = item.text()
            if app_text.startswith("No applications found"):
                continue
                
            # Parse the format: "AppName (Publisher.AppID)"
            if "(" in app_text and ")" in app_text:
                app_name = app_text.split("(")[0].strip()
            else:
                app_name = app_text.strip()
                
            progress.setLabelText(f"Installing {app_name}...")
            progress.setValue(i)
            
            try:
                # Extract package ID from the app text format: "AppName (Publisher.AppID)"
                if "(" in app_text and ")" in app_text:
                    package_id = app_text.split("(")[1].split(")")[0].strip()
                else:
                    # Fallback - use the app name
                    package_id = app_name
                
                if package_id:
                    result = self.manager.install(package_id)
                    if result and "successfully" in result.lower():
                        successful += 1
                    else:
                        failed += 1
                else:
                    failed += 1
                    
            except Exception as e:
                print(f"Failed to install {app_name}: {e}")
                failed += 1
        
        progress.close()
        
        # Show results
        result_msg = f"Batch installation completed!\n\nSuccessful: {successful}\nFailed: {failed}"
        QMessageBox.information(self, "Batch Install Complete", result_msg)
    
    def add_selected_to_favorites(self):
        """Add selected applications to favorites"""
        selected_items = []
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if hasattr(item, 'checkState') and item.checkState() == Qt.Checked:
                selected_items.append(item)
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please check the boxes next to applications you want to add to favorites.")
            return
        
        # Import favorites manager
        try:
            from .favorites_manager import FavoritesManager
        except ImportError:
            # Fallback for when running directly
            import sys
            import os
            sys.path.append(os.path.dirname(__file__))
            from favorites_manager import FavoritesManager
        favorites = FavoritesManager()
        
        added_count = 0
        for item in selected_items:
            app_text = item.text()
            if not app_text.startswith("No applications found"):
                # Parse the format: "AppName (Publisher.AppID)"
                if "(" in app_text and ")" in app_text:
                    # Extract app name and package ID
                    app_name = app_text.split("(")[0].strip()
                    package_id = app_text.split("(")[1].split(")")[0].strip()
                    
                    if package_id:
                        favorites.add_favorite(app_name, package_id)
                        added_count += 1
                else:
                    # Fallback - use the whole text as both name and ID
                    lines = app_text.split('\n')
                    app_name = lines[0].strip()
                    favorites.add_favorite(app_name, app_name)
                    added_count += 1
        
        QMessageBox.information(self, "Favorites Updated", 
                              f"Added {added_count} applications to favorites!")
    
    def update_selection_status(self):
        """Update selection status label"""
        selected_count = 0
        total_count = 0
        for i in range(self.results_list.count()):
            item = self.results_list.item(i)
            if hasattr(item, 'checkState') and not item.text().startswith("No applications found"):
                total_count += 1
                if item.checkState() == Qt.Checked:
                    selected_count += 1
        
        # Update button text based on selection state
        if selected_count == total_count and total_count > 0:
            self.select_all_btn.setText("☐ Unselect All")
        else:
            self.select_all_btn.setText("☑️ Select All")
        
        if selected_count > 0:
            self.search_selection_label.setText(f"📦 Selected: {selected_count} applications\n💡 Use batch operations or double-click to install individual apps")
            self.search_selection_label.show()
        else:
            self.search_selection_label.hide()

    def on_search_item_changed(self, item):
        """Handle checkbox state changes in search results"""
        self.update_selection_status()

    def install_app(self, item):
        app_info = item.text()
        if app_info.startswith("No applications found"):
            return
            
        if "(" in app_info and ")" in app_info:
            app_id = app_info.split("(")[-1].split(")")[0].strip()
        else:
            app_id = app_info
        dialog = InstallDialog(app_id, self.manager)
        dialog.exec_()


class LoadAppsThread(QThread):
    """Background thread for loading installed/upgradeable apps"""
    apps_loaded = pyqtSignal(list, str)  # apps, operation_type
    load_finished = pyqtSignal()
    
    def __init__(self, manager, operation_type):
        super().__init__()
        self.manager = manager
        self.operation_type = operation_type  # 'installed' or 'upgradeable'
    
    def run(self):
        try:
            if self.operation_type == 'installed':
                apps = self.manager.list_installed()
            else:  # upgradeable
                apps = self.manager.get_upgradeable()
            self.apps_loaded.emit(apps, self.operation_type)
        except Exception as e:
            print(f"Load apps thread error: {e}")
            self.apps_loaded.emit([], self.operation_type)
        finally:
            self.load_finished.emit()

class InstalledAppsWidget(QWidget):
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        self.load_thread = None
        
        self.init_ui()
        
        # Auto-load on startup
        QTimer.singleShot(1000, self.refresh_installed_apps)  # Delay initial load
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        layout.setContentsMargins(24, 16, 24, 24)
        
        # Compact header - single line with title and info
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("📦 Installed Applications")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 700;
                color: #1f2937;
            }
        """)
        
        info_label = QLabel("💡 Double-click to uninstall")
        info_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 12px;
                font-style: italic;
                margin-left: 16px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addWidget(info_label)
        header_layout.addStretch()
        
        # Compact button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        button_layout.setContentsMargins(0, 8, 0, 0)
        button_layout.setSpacing(12)
        
        self.refresh_button = QPushButton("🔄 Refresh")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #10b981, stop: 1 #059669);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #059669, stop: 1 #047857);
            }
        """)
        
        self.show_upgrades_button = QPushButton("⬆️ Updates")
        self.show_upgrades_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f59e0b, stop: 1 #d97706);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #d97706, stop: 1 #b45309);
            }
        """)
        
        # Progress indicator
        self.load_progress = QProgressBar()
        self.load_progress.setRange(0, 0)  # Indeterminate
        self.load_progress.hide()
        self.load_progress.setStyleSheet("""
            QProgressBar {
                background-color: rgba(229, 231, 235, 0.8);
                border: none;
                border-radius: 6px;
                height: 8px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #10b981, stop: 1 #059669);
                border-radius: 6px;
            }
        """)
        
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.show_upgrades_button)
        
        # Add batch operation buttons
        self.select_all_installed_btn = QPushButton("☑️ Select All")
        self.select_all_installed_btn.clicked.connect(self.toggle_select_all_installed_items)
        self.select_all_installed_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #8b5cf6, stop: 1 #7c3aed);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                min-width: 90px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #7c3aed, stop: 1 #6d28d9);
            }
        """)
        
        self.uninstall_selected_btn = QPushButton("🗑️ Uninstall Selected")
        self.uninstall_selected_btn.clicked.connect(self.uninstall_selected_apps)
        self.uninstall_selected_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ef4444, stop: 1 #dc2626);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #dc2626, stop: 1 #b91c1c);
            }
        """)
        
        self.view_history_btn = QPushButton("📜 History")
        self.view_history_btn.clicked.connect(self.show_installation_history)
        self.view_history_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #8b5cf6, stop: 1 #7c3aed);
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 600;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #7c3aed, stop: 1 #6d28d9);
            }
        """)
        
        button_layout.addWidget(self.select_all_installed_btn)
        button_layout.addWidget(self.uninstall_selected_btn)
        button_layout.addWidget(self.view_history_btn)
        button_layout.addStretch()
        
        # Status label
        self.status_label = QLabel("🔄 Loading installed applications...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #6b7280;
                font-size: 14px;
                padding: 8px 12px;
                background-color: rgba(249, 250, 251, 0.8);
                border-radius: 8px;
                border: 1px solid rgba(229, 231, 235, 0.5);
            }
        """)
        
        # Selection info label
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("""
            QLabel {
                background-color: #f0f8ff;
                border: 1px solid #b3d9ff;
                border-radius: 4px;
                padding: 5px;
                color: #0066cc;
                font-weight: bold;
            }
        """)
        
        # Selection info label
        self.selection_label = QLabel("")
        self.selection_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(59, 130, 246, 0.1), stop: 1 rgba(59, 130, 246, 0.05));
                border: 1px solid rgba(59, 130, 246, 0.2);
                border-radius: 8px;
                padding: 12px 16px;
                color: #1d4ed8;
                font-weight: 600;
                font-size: 13px;
            }
        """)
        self.selection_label.hide()
        
        # Modern apps list
        self.app_list = QListWidget()  # Changed from installed_list to app_list to match the method calls
        self.app_list.itemDoubleClicked.connect(self.uninstall_app)
        self.app_list.itemChanged.connect(self.on_installed_item_changed)
        
        # Apply modern styling to installed list
        self.app_list.setAlternatingRowColors(False)
        self.app_list.setToolTip("Check boxes to select • Double-click to uninstall individual apps")
        
        self.app_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid rgba(209, 213, 219, 0.3);
                border-radius: 12px;
                padding: 8px;
                outline: none;
            }
            QListWidget::item {
                padding: 18px 20px;
                margin: 6px 2px;
                border-radius: 10px;
                background-color: transparent;
                border: 1px solid transparent;
                font-size: 13px;
                min-height: 35px;
                color: #374151;
                line-height: 1.4;
            }
            QListWidget::item:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(245, 158, 11, 0.08), stop: 1 rgba(245, 158, 11, 0.04));
                border-color: rgba(245, 158, 11, 0.2);
                color: #1f2937;
            }
            QListWidget::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #d1d5db;
                background-color: white;
                margin-right: 8px;
            }
            QListWidget::indicator:hover {
                border-color: #ef4444;
                background-color: rgba(239, 68, 68, 0.1);
            }
            QListWidget::indicator:checked {
                background-color: #ef4444;
                border-color: #ef4444;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDVMNCA4TDExIDEiIHN0cm9rZT0id2hpdGUiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIi8+Cjwvc3ZnPgo=);
                background-repeat: no-repeat;
                background-position: center;
            }
        """)
        
        # Compact cache management section
        cache_layout = QHBoxLayout()
        cache_layout.setSpacing(8)
        cache_layout.setContentsMargins(0, 8, 0, 0)
        cache_layout.setSpacing(12)
        
        self.clear_cache_btn = QPushButton("🗑️ Clear Cache")
        self.clear_cache_btn.clicked.connect(self.clear_cache)
        self.clear_cache_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ef4444, stop: 1 #dc2626);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #dc2626, stop: 1 #b91c1c);
            }
        """)
        
        self.auto_refresh_check = QCheckBox("🔄 Auto-refresh (5 min)")
        self.auto_refresh_check.setChecked(False)
        self.auto_refresh_check.toggled.connect(self.toggle_auto_refresh)
        self.auto_refresh_check.setStyleSheet("""
            QCheckBox {
                color: #374151;
                font-size: 11px;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 14px;
                height: 14px;
                border-radius: 2px;
                border: 1px solid #d1d5db;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
        """)
        
        self.debug_btn = QPushButton("🔍 Debug")
        self.debug_btn.clicked.connect(self.show_debug_output)
        self.debug_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #6b7280, stop: 1 #4b5563);
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: 500;
                font-size: 11px;
                min-width: 60px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #4b5563, stop: 1 #374151);
            }
        """)
        
        cache_layout.addWidget(self.clear_cache_btn)
        cache_layout.addWidget(self.debug_btn)
        cache_layout.addWidget(self.auto_refresh_check)
        cache_layout.addStretch()
        
        # Auto-refresh timer
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_installed_apps)
        
        # Add all components to main layout
        layout.addLayout(header_layout)
        layout.addLayout(button_layout)
        layout.addWidget(self.load_progress)
        layout.addWidget(self.status_label)
        layout.addWidget(self.selection_label)
        layout.addWidget(self.app_list, 1)  # Give list most space
        layout.addLayout(cache_layout)
        
        self.setLayout(layout)
        
        # Connect signals
        self.refresh_button.clicked.connect(self.refresh_installed_apps)
        self.show_upgrades_button.clicked.connect(self.show_upgradeable_apps)
    
    def toggle_auto_refresh(self, enabled):
        """Toggle auto-refresh functionality"""
        if enabled:
            self.auto_refresh_timer.start(300000)  # 5 minutes
            self.status_label.setText("Auto-refresh enabled (every 5 minutes)")
        else:
            self.auto_refresh_timer.stop()
    
    def refresh_installed_apps(self):
        """Refresh the list of installed applications in background"""
        self.load_apps('installed')
    
    def show_upgradeable_apps(self):
        """Show applications that can be upgraded in background"""
        self.load_apps('upgradeable')
    
    def load_apps(self, operation_type):
        """Load apps in background thread"""
        # Don't start new load if one is already running
        if self.load_thread and self.load_thread.isRunning():
            return
        
        self.refresh_button.setEnabled(False)
        self.show_upgrades_button.setEnabled(False)
        self.load_progress.show()
        
        if operation_type == 'installed':
            self.status_label.setText("Loading installed applications...")
        else:
            self.status_label.setText("Checking for available updates...")
        
        # Start background loading
        self.load_thread = LoadAppsThread(self.manager, operation_type)
        self.load_thread.apps_loaded.connect(self.on_apps_loaded)
        self.load_thread.load_finished.connect(self.on_load_finished)
        self.load_thread.start()
    
    def on_apps_loaded(self, apps, operation_type):
        """Handle loaded apps"""
        self.app_list.clear()
        self.selection_label.hide()  # Hide selection when loading new data
        
        if not apps:
            if operation_type == 'installed':
                item = QListWidgetItem("🔍 No installed applications found\n   Try refreshing or check if winget is properly installed")
                item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)  # Remove checkbox for status messages
                self.app_list.addItem(item)
                self.status_label.setText("❌ No installed applications detected")
            else:
                item = QListWidgetItem("✅ No updates available\n   All your applications are up to date!")
                item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)  # Remove checkbox for status messages
                self.app_list.addItem(item)
                self.status_label.setText("✅ All applications are up to date")
        else:
            for app_text in apps:
                # Clean and format the app information
                cleaned_app = self.format_app_display(app_text, operation_type)
                
                # Create checkable list item
                item = CheckableListWidgetItem(cleaned_app)
                self.app_list.addItem(item)
            
            if operation_type == 'installed':
                self.status_label.setText(f"� Loaded {len(apps)} installed applications")
            else:
                self.status_label.setText(f"⬆️ Found {len(apps)} available updates")
    
    def format_app_display(self, app_text, operation_type):
        """Format app text for better display"""
        try:
            # Handle different formats of app text
            if "(" in app_text and ")" in app_text:
                # Format: AppName (Publisher.AppID) - vVersion
                parts = app_text.split("(")
                app_name = parts[0].strip()
                
                # Extract publisher and version info
                remaining = "(".join(parts[1:])
                if ") - v" in remaining:
                    id_part = remaining.split(") - v")[0]
                    version_part = remaining.split(") - v")[1] if len(remaining.split(") - v")) > 1 else ""
                else:
                    id_part = remaining.rstrip(")")
                    version_part = ""
                
                # Clean up publisher info
                publisher = ""
                if "." in id_part:
                    publisher = id_part.split(".")[0]
                
                # Format the display text
                if operation_type == 'upgradeable':
                    if version_part:
                        return f"⬆️  {app_name}\n    📦 {publisher} • 🔄 Update to v{version_part}"
                    else:
                        return f"⬆️  {app_name}\n    📦 {publisher} • 🔄 Update available"
                else:
                    if version_part:
                        return f"📱  {app_name}\n    📦 {publisher} • ✅ v{version_part}"
                    else:
                        return f"📱  {app_name}\n    📦 {publisher}"
            
            elif " - v" in app_text:
                # Format: AppName - vVersion
                parts = app_text.split(" - v")
                app_name = parts[0].strip()
                version = parts[1] if len(parts) > 1 else ""
                
                if operation_type == 'upgradeable':
                    return f"⬆️  {app_name}\n    🔄 Update to v{version}"
                else:
                    return f"📱  {app_name}\n    ✅ v{version}"
            
            else:
                # Simple format: just app name
                if operation_type == 'upgradeable':
                    return f"⬆️  {app_text}\n    🔄 Update available"
                else:
                    return f"📱  {app_text}\n    ✅ Installed"
                    
        except Exception as e:
            print(f"Error formatting app display: {e}")
            # Fallback to original format with just an icon
            if operation_type == 'upgradeable':
                return f"⬆️ {app_text}"
            else:
                return f"📱 {app_text}"
    
    def on_load_finished(self):
        """Clean up after loading completes"""
        self.refresh_button.setEnabled(True)
        self.show_upgrades_button.setEnabled(True)
        self.load_progress.hide()
    
    def clear_cache(self):
        """Clear all caches"""
        self.manager.clear_all_caches()
        QMessageBox.information(self, "Cache Cleared", "All caches have been cleared!")
    
    def update_installed_selection_status(self):
        """Update selection status label for installed apps"""
        selected_count = 0
        total_count = 0
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if hasattr(item, 'checkState') and not item.text().startswith(("No installed", "No updates")):
                total_count += 1
                if item.checkState() == Qt.Checked:
                    selected_count += 1
        
        # Update button text based on selection state
        if selected_count == total_count and total_count > 0:
            self.select_all_installed_btn.setText("☐ Unselect All")
        else:
            self.select_all_installed_btn.setText("☑️ Select All")
        
        if selected_count > 0:
            self.selection_label.setText(f"🗑️ Selected: {selected_count} applications for uninstallation\n💡 Use batch operations or double-click to uninstall individual apps")
            self.selection_label.show()
        else:
            self.selection_label.hide()
    
    def on_installed_item_changed(self, item):
        """Handle checkbox state changes in installed apps"""
        self.update_installed_selection_status()
    
    def toggle_select_all_installed_items(self):
        """Toggle select all items in installed apps list"""
        # Check if any items are selected
        selected_count = 0
        total_count = 0
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if hasattr(item, 'setCheckState') and not item.text().startswith(("No installed", "No updates")):
                total_count += 1
                if item.checkState() == Qt.Checked:
                    selected_count += 1
        
        # If all are selected, unselect all. Otherwise, select all
        if selected_count == total_count and total_count > 0:
            # Unselect all
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                if hasattr(item, 'setCheckState') and not item.text().startswith(("No installed", "No updates")):
                    item.setCheckState(Qt.Unchecked)
            self.select_all_installed_btn.setText("☑️ Select All")
        else:
            # Select all
            for i in range(self.app_list.count()):
                item = self.app_list.item(i)
                if hasattr(item, 'setCheckState') and not item.text().startswith(("No installed", "No updates")):
                    item.setCheckState(Qt.Checked)
            self.select_all_installed_btn.setText("☐ Unselect All")
        
        self.update_installed_selection_status()
    
    def show_debug_output(self):
        """Show raw winget output for debugging"""
        import subprocess
        try:
            result = subprocess.run(
                ["winget", "list", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            
            # Create a dialog to show the raw output
            from PyQt5.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QPushButton
            
            dialog = QDialog(self)
            dialog.setWindowTitle("Debug: Raw Winget Output")
            dialog.resize(800, 600)
            
            layout = QVBoxLayout()
            
            text_edit = QTextEdit()
            text_edit.setPlainText(f"Command: winget list --accept-source-agreements\n"
                                  f"Return code: {result.returncode}\n"
                                  f"STDOUT:\n{result.stdout}\n\n"
                                  f"STDERR:\n{result.stderr}")
            text_edit.setReadOnly(True)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.accept)
            
            layout.addWidget(text_edit)
            layout.addWidget(close_btn)
            dialog.setLayout(layout)
            
            dialog.exec_()
            
        except Exception as e:
            QMessageBox.warning(self, "Debug Error", f"Failed to get winget output: {str(e)}")
    
    def uninstall_app(self, item):
        """Handle uninstalling an application"""
        app_info = item.text()
        
        # Skip if it's a status message
        if app_info.startswith(("No installed", "No updates")):
            return
        
        # Extract app information from the new multi-line format
        lines = app_info.split('\n')
        if len(lines) > 0:
            first_line = lines[0]
            # Remove emoji and get app name
            if first_line.startswith(("⬆️  ", "📱  ")):
                app_name = first_line[3:].strip()
            elif first_line.startswith(("🔄 ", "📱 ")):
                app_name = first_line[2:].strip()
            else:
                app_name = first_line.strip()
        else:
            app_name = app_info
        
        # For now, use app name as app_id (this could be improved with better parsing)
        app_id = app_name
        
        # Try to extract better app ID if we have publisher info
        if len(lines) > 1 and "📦" in lines[1]:
            # Look for publisher info to create better app ID
            publisher_line = lines[1]
            if "📦" in publisher_line:
                publisher_part = publisher_line.split("📦")[1].split("•")[0].strip()
                if publisher_part and not publisher_part == "Unknown":
                    app_id = f"{publisher_part}.{app_name.replace(' ', '')}"
        
        # Show uninstall dialog
        dialog = UninstallDialog(app_id, self.manager)
        if dialog.exec_() == dialog.Accepted:
            # Refresh the list after uninstall
            self.refresh_installed_apps()
    
    def uninstall_selected_apps(self):
        """Uninstall multiple selected applications"""
        selected_items = []
        for i in range(self.app_list.count()):
            item = self.app_list.item(i)
            if hasattr(item, 'checkState') and item.checkState() == Qt.Checked:
                selected_items.append(item)
        
        if not selected_items:
            QMessageBox.information(self, "No Selection", "Please check the boxes next to applications you want to uninstall.")
            return
        
        # Filter out status messages
        valid_items = []
        for item in selected_items:
            app_info = item.text()
            if not app_info.startswith(("No installed", "No updates")):
                valid_items.append(item)
        
        if not valid_items:
            QMessageBox.information(self, "No Valid Selection", "No valid applications selected for uninstallation.")
            return
        
        # Show confirmation dialog
        app_names = []
        for item in valid_items:
            app_info = item.text()
            lines = app_info.split('\n')
            if len(lines) > 0:
                first_line = lines[0]
                # Remove emoji and get app name
                if first_line.startswith(("⬆️  ", "📱  ")):
                    app_name = first_line[3:].strip()
                elif first_line.startswith(("🔄 ", "📱 ")):
                    app_name = first_line[2:].strip()
                else:
                    app_name = first_line.strip()
                app_names.append(app_name)
        
        reply = QMessageBox.question(
            self,
            "Confirm Batch Uninstallation",
            f"Are you sure you want to uninstall {len(app_names)} applications?\n\n" +
            "\n".join(f"• {name}" for name in app_names[:10]) +
            (f"\n... and {len(app_names) - 10} more" if len(app_names) > 10 else ""),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.start_batch_uninstall(valid_items)
    
    def start_batch_uninstall(self, selected_items):
        """Start the batch uninstallation process"""
        from PyQt5.QtWidgets import QProgressDialog
        from PyQt5.QtCore import QTimer
        import time
        
        # Create progress dialog
        progress = QProgressDialog("Uninstalling applications...", "Cancel", 0, len(selected_items), self)
        progress.setWindowModality(2)  # Qt.WindowModal
        progress.setAutoClose(True)
        progress.setAutoReset(True)
        
        successful_uninstalls = []
        failed_uninstalls = []
        
        for i, item in enumerate(selected_items):
            if progress.wasCanceled():
                break
            
            app_info = item.text()
            lines = app_info.split('\n')
            if len(lines) > 0:
                first_line = lines[0]
                # Remove emoji and get app name
                if first_line.startswith(("⬆️  ", "📱  ")):
                    app_name = first_line[3:].strip()
                elif first_line.startswith(("🔄 ", "📱 ")):
                    app_name = first_line[2:].strip()
                else:
                    app_name = first_line.strip()
            else:
                app_name = app_info
            
            # For now, use app name as app_id
            app_id = app_name
            
            # Try to extract better app ID if we have publisher info
            if len(lines) > 1 and "📦" in lines[1]:
                publisher_line = lines[1]
                if "📦" in publisher_line:
                    publisher_part = publisher_line.split("📦")[1].split("•")[0].strip()
                    if publisher_part and not publisher_part == "Unknown":
                        app_id = f"{publisher_part}.{app_name.replace(' ', '')}"
            
            progress.setLabelText(f"Uninstalling: {app_name}")
            progress.setValue(i)
            
            # Process events to keep UI responsive
            QApplication.processEvents()
            
            try:
                # Perform uninstallation
                success = self.manager.uninstall_app(app_id)
                if success:
                    successful_uninstalls.append(app_name)
                    # Add to installation history
                    from .installation_history import InstallationHistoryManager
                    history = InstallationHistoryManager()
                    history.add_uninstallation(app_name, app_id, "success")
                else:
                    failed_uninstalls.append(app_name)
                    # Add failed uninstallation to history
                    from .installation_history import InstallationHistoryManager
                    history = InstallationHistoryManager()
                    history.add_uninstallation(app_name, app_id, "failed")
            except Exception as e:
                failed_uninstalls.append(f"{app_name} (Error: {str(e)})")
                # Add failed uninstallation to history
                from .installation_history import InstallationHistoryManager
                history = InstallationHistoryManager()
                history.add_uninstallation(app_name, app_id, "failed")
        
        progress.setValue(len(selected_items))
        
        # Show results
        result_message = f"Batch uninstallation completed!\n\n"
        if successful_uninstalls:
            result_message += f"Successfully uninstalled ({len(successful_uninstalls)}):\n"
            result_message += "\n".join(f"✅ {app}" for app in successful_uninstalls[:5])
            if len(successful_uninstalls) > 5:
                result_message += f"\n... and {len(successful_uninstalls) - 5} more"
            result_message += "\n\n"
        
        if failed_uninstalls:
            result_message += f"Failed to uninstall ({len(failed_uninstalls)}):\n"
            result_message += "\n".join(f"❌ {app}" for app in failed_uninstalls[:5])
            if len(failed_uninstalls) > 5:
                result_message += f"\n... and {len(failed_uninstalls) - 5} more"
        
        QMessageBox.information(self, "Batch Uninstallation Results", result_message)
        
        # Refresh the installed apps list
        self.refresh_installed_apps()
    
    def show_installation_history(self):
        """Show installation history dialog"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QComboBox
        from .installation_history import InstallationHistoryManager
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Installation History")
        dialog.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Header with filter options
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Filter:"))
        
        filter_combo = QComboBox()
        filter_combo.addItems(["All", "Installations", "Uninstallations", "Successful", "Failed"])
        header_layout.addWidget(filter_combo)
        
        header_layout.addStretch()
        
        # Stats button
        stats_btn = QPushButton("📊 Show Statistics")
        header_layout.addWidget(stats_btn)
        
        layout.addLayout(header_layout)
        
        # History display
        history_text = QTextEdit()
        history_text.setReadOnly(True)
        layout.addWidget(history_text)
        
        # Load and display history
        def load_history():
            history_manager = InstallationHistoryManager()
            history = history_manager.get_installation_history()
            
            filter_value = filter_combo.currentText().lower()
            
            if not history:
                history_text.setPlainText("No installation history found.")
                return
            
            # Filter history based on selection
            filtered_history = history
            if filter_value == "installations":
                filtered_history = [h for h in history if h.get('operation') == 'install']
            elif filter_value == "uninstallations":
                filtered_history = [h for h in history if h.get('operation') == 'uninstall']
            elif filter_value == "successful":
                filtered_history = [h for h in history if h.get('status') == 'success']
            elif filter_value == "failed":
                filtered_history = [h for h in history if h.get('status') == 'failed']
            
            # Format history for display
            history_display = []
            for entry in filtered_history:
                timestamp = entry.get('timestamp', 'Unknown time')
                app_name = entry.get('app_name', 'Unknown app')
                operation = entry.get('operation', 'unknown').title()
                status = entry.get('status', 'unknown')
                
                status_emoji = "✅" if status == "success" else "❌" if status == "failed" else "⚠️"
                operation_emoji = "📦" if operation == "Install" else "🗑️"
                
                history_display.append(
                    f"{operation_emoji} {operation} - {app_name}\n"
                    f"   {status_emoji} Status: {status.title()}\n"
                    f"   🕒 Time: {timestamp}\n"
                )
            
            if history_display:
                history_text.setPlainText("\n".join(history_display))
            else:
                history_text.setPlainText(f"No {filter_value} found in history.")
        
        def show_statistics():
            history_manager = InstallationHistoryManager()
            stats = history_manager.get_installation_stats()
            
            stats_text = f"""Installation Statistics:

📊 Total Operations: {stats['total_operations']}

📦 Installations:
   • Successful: {stats['successful_installs']}
   • Failed: {stats['failed_installs']}
   • Total: {stats['total_installs']}

🗑️ Uninstallations:
   • Successful: {stats['successful_uninstalls']}
   • Failed: {stats['failed_uninstalls']}
   • Total: {stats['total_uninstalls']}

📈 Success Rate:
   • Overall: {stats['success_rate']:.1f}%
   • Installations: {stats['install_success_rate']:.1f}%
   • Uninstallations: {stats['uninstall_success_rate']:.1f}%
"""
            QMessageBox.information(dialog, "Installation Statistics", stats_text)
        
        # Connect signals
        filter_combo.currentTextChanged.connect(lambda: load_history())
        stats_btn.clicked.connect(show_statistics)
        
        # Load initial history
        load_history()
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        # Show dialog
        dialog.exec_()