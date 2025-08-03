import subprocess
import threading
import time
from cache_manager import CacheManager
from typing import List, Optional

class WingetManager:
    def __init__(self):
        self.cache = CacheManager()
        self._installed_apps_cache = None
        self._cache_lock = threading.Lock()
    
    def search(self, query: str, use_cache: bool = True) -> List[str]:
        """Search for applications with caching"""
        if not query or len(query.strip()) < 2:
            return []
        
        cache_key = f"search_{query.lower().strip()}"
        
        # Try cache first (5 minute expiry for searches)
        if use_cache:
            cached_result = self.cache.get_cached_data(cache_key, max_age_seconds=300)
            if cached_result is not None:
                return cached_result
        
        try:
            result = subprocess.run(
                ["winget", "search", query, "--accept-source-agreements"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30  # Add timeout to prevent hanging
            )
            
            if result.stdout is None:
                return []
            
            lines = result.stdout.splitlines()
            apps = []
            
            for line in lines:
                # Skip header and separator lines more efficiently
                if not line.strip() or line.startswith(("Name", "-", "No package")):
                    continue
                
                # More robust parsing
                parts = line.split(None, 2)  # Split into max 3 parts
                if len(parts) >= 2:
                    name = parts[0]
                    app_id = parts[1]
                    # Create more informative display format
                    apps.append(f"{name} ({app_id})")
            
            # Cache the results
            if use_cache and apps:
                self.cache.set_cached_data(cache_key, apps)
            
            return apps
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            print(f"Search error: {e}")
            return []

    def install(self, app_name: str) -> bool:
        """Install application with better error handling"""
        try:
            result = subprocess.run(
                ["winget", "install", "--silent", "--accept-package-agreements", "--accept-source-agreements", app_name],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600  # 10 minute timeout for installations
            )
            
            success = result.returncode == 0
            
            # Clear relevant caches after successful install
            if success:
                self._clear_install_caches()
            
            return success
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            print(f"Install error: {e}")
            return False

    def uninstall(self, app_name: str) -> bool:
        """Uninstall application with better error handling"""
        try:
            result = subprocess.run(
                ["winget", "uninstall", "--silent", app_name], 
                capture_output=True, 
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            success = result.returncode == 0
            
            # Clear relevant caches after successful uninstall
            if success:
                self._clear_install_caches()
            
            return success
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            print(f"Uninstall error: {e}")
            return False

    def upgrade(self, app_name: str) -> bool:
        """Upgrade application with better error handling"""
        try:
            result = subprocess.run(
                ["winget", "upgrade", "--silent", "--accept-package-agreements", "--accept-source-agreements", app_name], 
                capture_output=True, 
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            success = result.returncode == 0
            
            # Clear relevant caches after successful upgrade
            if success:
                self._clear_install_caches()
            
            return success
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            print(f"Upgrade error: {e}")
            return False

    def list_installed(self, use_cache: bool = True) -> List[str]:
        """Get list of installed applications with caching and improved parsing"""
        cache_key = "installed_apps"
        
        # Try cache first (2 minute expiry for installed apps)
        if use_cache:
            with self._cache_lock:
                cached_result = self.cache.get_cached_data(cache_key, max_age_seconds=120)
                if cached_result is not None:
                    return cached_result
        
        try:
            result = subprocess.run(
                ["winget", "list", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=45  # Timeout for list operations
            )
            
            if result.stdout is None:
                return []
            
            lines = result.stdout.splitlines()
            apps = []
            header_found = False
            
            for line_num, line in enumerate(lines):
                # Skip empty lines
                if not line.strip():
                    continue
                
                # Look for the header line to know when data starts
                if "Name" in line and "Id" in line:
                    header_found = True
                    continue
                
                # Skip lines before header
                if not header_found:
                    continue
                
                # Skip separator lines (lines with just dashes)
                if line.strip().replace('-', '').replace(' ', '') == '':
                    continue
                
                # Skip informational lines
                if line.startswith(("The following", "No package", "Found")):
                    continue
                
                # Try to parse the line more carefully
                # winget list output is typically: Name   Id   Version   Available   Source
                try:
                    # Handle lines with multiple spaces/tabs
                    cleaned_line = ' '.join(line.split())
                    
                    # Skip if line is too short or looks like a continuation
                    if len(cleaned_line) < 3:
                        continue
                    
                    # Try to extract meaningful parts
                    parts = cleaned_line.split()
                    
                    if len(parts) >= 1:
                        name = parts[0]
                        
                        # Skip if name looks invalid (too short, only special chars, etc.)
                        if len(name) < 2 or name.replace('.', '').replace('-', '').replace('_', '') == '':
                            continue
                        
                        # Try to get ID and version
                        app_id = parts[1] if len(parts) > 1 else ""
                        version = parts[2] if len(parts) > 2 else "Unknown"
                        
                        # Clean up the version field (remove extra info)
                        if version and len(version) > 20:  # Truncate very long versions
                            version = version[:20] + "..."
                        
                        # Format the display string
                        if app_id and app_id != name and len(app_id) > 1:
                            # Only show ID if it's different from name and meaningful
                            if not app_id.startswith('…') and len(app_id.replace('.', '').replace('-', '')) > 0:
                                display_text = f"{name} ({app_id}) - v{version}"
                            else:
                                display_text = f"{name} - v{version}"
                        else:
                            display_text = f"{name} - v{version}"
                        
                        # Final validation - skip if display text looks corrupted
                        if len(display_text.strip()) > 5 and not display_text.startswith('…'):
                            apps.append(display_text)
                        
                except (IndexError, ValueError) as e:
                    # Skip malformed lines
                    print(f"Skipping malformed line {line_num}: {line[:50]}... Error: {e}")
                    continue
            
            # Remove duplicates while preserving order
            seen = set()
            unique_apps = []
            for app in apps:
                if app not in seen:
                    seen.add(app)
                    unique_apps.append(app)
            
            # Cache the results
            if use_cache and unique_apps:
                with self._cache_lock:
                    self.cache.set_cached_data(cache_key, unique_apps)
            
            return unique_apps
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            print(f"List installed error: {e}")
            return []

    def get_upgradeable(self, use_cache: bool = True) -> List[str]:
        """Get list of applications that can be upgraded with caching"""
        cache_key = "upgradeable_apps"
        
        # Try cache first (5 minute expiry for upgrade info)
        if use_cache:
            cached_result = self.cache.get_cached_data(cache_key, max_age_seconds=300)
            if cached_result is not None:
                return cached_result
        
        try:
            result = subprocess.run(
                ["winget", "upgrade", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=60  # Longer timeout for upgrade checks
            )
            
            if result.stdout is None:
                return []
            
            lines = result.stdout.splitlines()
            apps = []
            
            for line in lines:
                # Skip header and separator lines
                if not line.strip() or line.startswith(("Name", "-", "No applicable", "Everything")):
                    continue
                
                parts = line.split(None, 5)  # Split into max 6 parts
                if len(parts) >= 4:
                    name = parts[0]
                    app_id = parts[1] if len(parts) > 1 else ""
                    current_version = parts[2] if len(parts) > 2 else "Unknown"
                    available_version = parts[3] if len(parts) > 3 else "Unknown"
                    
                    if app_id and app_id != name:
                        apps.append(f"{name} ({app_id}) - v{current_version} → v{available_version}")
                    else:
                        apps.append(f"{name} - v{current_version} → v{available_version}")
            
            # Cache the results
            if use_cache and apps:
                self.cache.set_cached_data(cache_key, apps)
            
            return apps
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, OSError) as e:
            print(f"Get upgradeable error: {e}")
            return []
    
    def _clear_install_caches(self):
        """Clear caches related to installed apps after install/uninstall operations"""
        with self._cache_lock:
            # Remove cached data that might be outdated
            keys_to_remove = [key for key in self.cache.cache.keys() 
                            if key in ["installed_apps", "upgradeable_apps"]]
            for key in keys_to_remove:
                if key in self.cache.cache:
                    del self.cache.cache[key]
            if keys_to_remove:
                self.cache.save_cache()
    
    def clear_all_caches(self):
        """Clear all caches - useful for troubleshooting"""
        self.cache.clear_cache()
    
    def get_raw_winget_output(self, command: str = "list") -> str:
        """Get raw winget output for debugging purposes"""
        try:
            if command == "list":
                cmd = ["winget", "list", "--accept-source-agreements"]
            elif command == "upgrade":
                cmd = ["winget", "upgrade", "--accept-source-agreements"]
            else:
                return f"Unknown command: {command}"
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            
            return f"Command: {' '.join(cmd)}\nReturn code: {result.returncode}\n\nSTDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
            
        except Exception as e:
            return f"Error getting raw output: {str(e)}"