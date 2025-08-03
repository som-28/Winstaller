import json
import os
from datetime import datetime

class FavoritesManager:
    def __init__(self):
        self.favorites_file = "favorites.json"
        self.favorites = self.load_favorites()
    
    def load_favorites(self):
        """Load favorites from file"""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {"favorites": []}
        except Exception as e:
            print(f"Error loading favorites: {e}")
            return {"favorites": []}
    
    def save_favorites(self):
        """Save favorites to file"""
        try:
            with open(self.favorites_file, 'w', encoding='utf-8') as f:
                json.dump(self.favorites, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving favorites: {e}")
    
    def add_favorite(self, app_name, package_id, description=""):
        """Add an application to favorites"""
        # Check if already exists
        for fav in self.favorites["favorites"]:
            if fav["package_id"] == package_id:
                return False  # Already exists
        
        favorite = {
            "app_name": app_name,
            "package_id": package_id,
            "description": description,
            "added_date": datetime.now().isoformat()
        }
        
        self.favorites["favorites"].append(favorite)
        self.save_favorites()
        return True
    
    def remove_favorite(self, package_id):
        """Remove an application from favorites"""
        original_count = len(self.favorites["favorites"])
        self.favorites["favorites"] = [
            fav for fav in self.favorites["favorites"] 
            if fav["package_id"] != package_id
        ]
        
        if len(self.favorites["favorites"]) < original_count:
            self.save_favorites()
            return True
        return False
    
    def get_favorites(self):
        """Get all favorite applications"""
        return self.favorites["favorites"]
    
    def is_favorite(self, package_id):
        """Check if an application is in favorites"""
        return any(fav["package_id"] == package_id for fav in self.favorites["favorites"])
    
    def clear_favorites(self):
        """Clear all favorites"""
        self.favorites = {"favorites": []}
        self.save_favorites()
