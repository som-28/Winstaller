from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QProgressBar
from PyQt5.QtCore import QThread, pyqtSignal

class InstallThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, manager, app_name):
        super().__init__()
        self.manager = manager
        self.app_name = app_name

    def run(self):
        success = self.manager.install(self.app_name)
        self.finished.emit(success)

class InstallDialog(QDialog):
    def __init__(self, app_name, manager):
        super().__init__()
        self.setWindowTitle(f"Install {app_name}")
        self.manager = manager
        self.app_name = app_name

        layout = QVBoxLayout()
        label = QLabel(f"Do you want to install {app_name}?")
        self.install_button = QPushButton("Install")
        self.install_button.clicked.connect(self.start_install)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate

        layout.addWidget(label)
        layout.addWidget(self.install_button)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.progress.hide()

    def start_install(self):
        self.install_button.setEnabled(False)
        self.progress.show()
        self.thread = InstallThread(self.manager, self.app_name)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, success):
        self.progress.hide()
        if success:
            QMessageBox.information(self, "Success", f"{self.app_name} installed successfully!")
        else:
            QMessageBox.warning(self, "Error", f"Failed to install {self.app_name}.")
        self.accept()


class UninstallThread(QThread):
    finished = pyqtSignal(bool)

    def __init__(self, manager, app_name):
        super().__init__()
        self.manager = manager
        self.app_name = app_name

    def run(self):
        success = self.manager.uninstall(self.app_name)
        self.finished.emit(success)


class UninstallDialog(QDialog):
    def __init__(self, app_name, manager):
        super().__init__()
        self.setWindowTitle(f"Uninstall {app_name}")
        self.manager = manager
        self.app_name = app_name

        layout = QVBoxLayout()
        label = QLabel(f"Are you sure you want to uninstall {app_name}?")
        
        # Button layout
        button_layout = QVBoxLayout()
        self.uninstall_button = QPushButton("Uninstall")
        self.cancel_button = QPushButton("Cancel")
        
        self.uninstall_button.clicked.connect(self.start_uninstall)
        self.cancel_button.clicked.connect(self.reject)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate

        layout.addWidget(label)
        layout.addWidget(self.uninstall_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.progress.hide()

    def start_uninstall(self):
        self.uninstall_button.setEnabled(False)
        self.cancel_button.setEnabled(False)
        self.progress.show()
        self.thread = UninstallThread(self.manager, self.app_name)
        self.thread.finished.connect(self.on_finished)
        self.thread.start()

    def on_finished(self, success):
        self.progress.hide()
        if success:
            QMessageBox.information(self, "Success", f"{self.app_name} uninstalled successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", f"Failed to uninstall {self.app_name}.")
            self.reject()