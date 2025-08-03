import json
import time
import os
from typing import Dict, List, Optional

class CacheManager:
    def __init__(self, cache_file="app_cache.json"):
        self.cache_file = cache_file
        self.cache = {}
        self.load_cache()
    
    def load_cache(self):
        """Load cache from file"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.cache = {}
        else:
            self.cache = {}
    
    def save_cache(self):
        """Save cache to file"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except IOError:
            pass  # Silently fail if can't save cache
    
    def get_cached_data(self, key: str, max_age_seconds: int = 300) -> Optional[List]:
        """Get cached data if it's still valid (default 5 minutes)"""
        if key not in self.cache:
            return None
        
        cached_item = self.cache[key]
        if time.time() - cached_item.get('timestamp', 0) > max_age_seconds:
            # Cache expired
            del self.cache[key]
            return None
        
        return cached_item.get('data')
    
    def set_cached_data(self, key: str, data: List):
        """Cache data with current timestamp"""
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
        self.save_cache()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache = {}
        self.save_cache()
    
    def clear_expired_cache(self, max_age_seconds: int = 3600):
        """Clear cache entries older than specified age (default 1 hour)"""
        current_time = time.time()
        expired_keys = []
        
        for key, value in self.cache.items():
            if current_time - value.get('timestamp', 0) > max_age_seconds:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.save_cache()
