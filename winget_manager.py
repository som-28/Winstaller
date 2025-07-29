import subprocess

class WingetManager:
    def search(self, query):
        result = subprocess.run(
            ["winget", "search", query],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if result.stdout is None:
            return []
        lines = result.stdout.splitlines()
        apps = []
        for line in lines:
            columns = line.split()
            if len(columns) >= 3 and not line.startswith("Name") and not line.startswith("-"):
                apps.append(f"{columns[0]} ({columns[1]})")
        return apps

    def install(self, app_name):
        result = subprocess.run(
            ["winget", "install", "--silent", "--accept-package-agreements", app_name],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        return result.returncode == 0

    def uninstall(self, app_name):
        result = subprocess.run(["winget", "uninstall", app_name], capture_output=True, text=True)
        return result.returncode == 0

    def upgrade(self, app_name):
        result = subprocess.run(["winget", "upgrade", app_name], capture_output=True, text=True)
        return result.returncode == 0

    def list_installed(self):
        """Get list of installed applications with their versions"""
        result = subprocess.run(
            ["winget", "list"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if result.stdout is None:
            return []
        
        lines = result.stdout.splitlines()
        apps = []
        for line in lines:
            # Skip header and separator lines
            if line.startswith("Name") or line.startswith("-") or not line.strip():
                continue
            
            # Parse the line to extract app info
            parts = line.split()
            if len(parts) >= 3:
                # Try to extract name, id, and version
                # winget list output format: Name Id Version Available Source
                name = parts[0]
                app_id = parts[1] if len(parts) > 1 else ""
                version = parts[2] if len(parts) > 2 else "Unknown"
                
                # Create a readable format
                if app_id:
                    apps.append(f"{name} ({app_id}) - v{version}")
                else:
                    apps.append(f"{name} - v{version}")
        
        return apps

    def get_upgradeable(self):
        """Get list of applications that can be upgraded"""
        result = subprocess.run(
            ["winget", "upgrade"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        if result.stdout is None:
            return []
        
        lines = result.stdout.splitlines()
        apps = []
        for line in lines:
            # Skip header and separator lines
            if line.startswith("Name") or line.startswith("-") or not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 4:
                name = parts[0]
                app_id = parts[1] if len(parts) > 1 else ""
                current_version = parts[2] if len(parts) > 2 else "Unknown"
                available_version = parts[3] if len(parts) > 3 else "Unknown"
                
                if app_id:
                    apps.append(f"{name} ({app_id}) - v{current_version} → v{available_version}")
                else:
                    apps.append(f"{name} - v{current_version} → v{available_version}")
        
        return apps