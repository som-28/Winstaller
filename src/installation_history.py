import json
import os
from datetime import datetime

class InstallationHistoryManager:
    def __init__(self):
        self.history_file = "installation_history.json"
        self.history = self.load_history()
    
    def load_history(self):
        """Load installation history from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"installations": [], "uninstallations": []}
        except Exception as e:
            print(f"Error loading installation history: {e}")
            return {"installations": [], "uninstallations": []}
    
    def save_history(self):
        """Save installation history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving installation history: {e}")
    
    def add_installation(self, app_name, package_id, version="", status="success"):
        """Record an installation"""
        installation = {
            "app_name": app_name,
            "package_id": package_id,
            "version": version,
            "status": status,
            "date": datetime.now().isoformat(),
            "action": "install"
        }
        
        self.history["installations"].append(installation)
        self.save_history()
    
    def add_uninstallation(self, app_name, package_id, status="success"):
        """Record an uninstallation"""
        uninstallation = {
            "app_name": app_name,
            "package_id": package_id,
            "status": status,
            "date": datetime.now().isoformat(),
            "action": "uninstall"
        }
        
        self.history["uninstallations"].append(uninstallation)
        self.save_history()
    
    def get_installation_history(self, limit=50):
        """Get recent installation history"""
        all_history = self.history["installations"] + self.history["uninstallations"]
        # Sort by date (newest first)
        all_history.sort(key=lambda x: x["date"], reverse=True)
        return all_history[:limit]
    
    def get_app_history(self, package_id):
        """Get history for a specific application"""
        app_history = []
        
        for installation in self.history["installations"]:
            if installation["package_id"] == package_id:
                app_history.append(installation)
        
        for uninstallation in self.history["uninstallations"]:
            if uninstallation["package_id"] == package_id:
                app_history.append(uninstallation)
        
        # Sort by date
        app_history.sort(key=lambda x: x["date"])
        return app_history
    
    def get_installation_stats(self):
        """Get installation statistics"""
        total_installations = len(self.history["installations"])
        total_uninstallations = len(self.history["uninstallations"])
        successful_installations = len([i for i in self.history["installations"] if i["status"] == "success"])
        
        return {
            "total_installations": total_installations,
            "total_uninstallations": total_uninstallations,
            "successful_installations": successful_installations,
            "success_rate": (successful_installations / total_installations * 100) if total_installations > 0 else 0
        }
    
    def clear_history(self):
        """Clear all installation history"""
        self.history = {"installations": [], "uninstallations": []}
        self.save_history()
