"""
Simple file-based database for storing bot configuration and user data
"""

import json
import os
import logging
from typing import Dict, List, Optional, Set
from threading import Lock

logger = logging.getLogger(__name__)

class SimpleDB:
    """Simple JSON-based database for bot data"""
    
    def __init__(self, db_file: str = "bot_data.json"):
        self.db_file = db_file
        self.lock = Lock()
        self.data = self._load_data()
    
    def _load_data(self) -> Dict:
        """Load data from JSON file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            else:
                return self._get_default_data()
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return self._get_default_data()
    
    def _get_default_data(self) -> Dict:
        """Get default database structure"""
        return {
            "allowed_channels": {},  # guild_id -> channel_id
            "registered_users": {},  # guild_id -> {user_id -> {steam_id, last_mmr, notifications_enabled}}
            "admin_users": {},       # guild_id -> [user_ids]
            "rank_notifications": {} # guild_id -> {user_id -> last_rank_tier}
        }
    
    def _save_data(self):
        """Save data to JSON file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
    
    def set_allowed_channel(self, guild_id: int, channel_id: int):
        """Set the allowed channel for a guild"""
        with self.lock:
            self.data["allowed_channels"][str(guild_id)] = channel_id
            self._save_data()
    
    def get_allowed_channel(self, guild_id: int) -> Optional[int]:
        """Get the allowed channel for a guild"""
        return self.data["allowed_channels"].get(str(guild_id))
    
    def is_channel_allowed(self, guild_id: int, channel_id: int) -> bool:
        """Check if a channel is allowed for bot commands"""
        allowed = self.get_allowed_channel(guild_id)
        return allowed is None or allowed == channel_id
    
    def add_admin_user(self, guild_id: int, user_id: int):
        """Add an admin user for a guild"""
        with self.lock:
            guild_str = str(guild_id)
            if guild_str not in self.data["admin_users"]:
                self.data["admin_users"][guild_str] = []
            
            if user_id not in self.data["admin_users"][guild_str]:
                self.data["admin_users"][guild_str].append(user_id)
                self._save_data()
    
    def remove_admin_user(self, guild_id: int, user_id: int):
        """Remove an admin user from a guild"""
        with self.lock:
            guild_str = str(guild_id)
            if guild_str in self.data["admin_users"]:
                if user_id in self.data["admin_users"][guild_str]:
                    self.data["admin_users"][guild_str].remove(user_id)
                    self._save_data()
    
    def is_admin_user(self, guild_id: int, user_id: int) -> bool:
        """Check if a user is an admin for a guild"""
        guild_str = str(guild_id)
        return user_id in self.data["admin_users"].get(guild_str, [])
    
    def register_user(self, guild_id: int, user_id: int, steam_id: str, current_mmr: int = 0):
        """Register a user for rank notifications"""
        with self.lock:
            guild_str = str(guild_id)
            user_str = str(user_id)
            
            if guild_str not in self.data["registered_users"]:
                self.data["registered_users"][guild_str] = {}
            
            self.data["registered_users"][guild_str][user_str] = {
                "steam_id": steam_id,
                "last_mmr": current_mmr,
                "notifications_enabled": True
            }
            self._save_data()
    
    def unregister_user(self, guild_id: int, user_id: int):
        """Unregister a user from rank notifications"""
        with self.lock:
            guild_str = str(guild_id)
            user_str = str(user_id)
            
            if guild_str in self.data["registered_users"]:
                if user_str in self.data["registered_users"][guild_str]:
                    del self.data["registered_users"][guild_str][user_str]
                    self._save_data()
    
    def get_registered_users(self, guild_id: int) -> Dict[str, Dict]:
        """Get all registered users for a guild"""
        guild_str = str(guild_id)
        return self.data["registered_users"].get(guild_str, {})
    
    def get_user_registration(self, guild_id: int, user_id: int) -> Optional[Dict]:
        """Get registration data for a specific user"""
        guild_str = str(guild_id)
        user_str = str(user_id)
        return self.data["registered_users"].get(guild_str, {}).get(user_str)
    
    def update_user_mmr(self, guild_id: int, user_id: int, new_mmr: int):
        """Update a user's MMR for rank change detection"""
        with self.lock:
            guild_str = str(guild_id)
            user_str = str(user_id)
            
            if guild_str in self.data["registered_users"]:
                if user_str in self.data["registered_users"][guild_str]:
                    self.data["registered_users"][guild_str][user_str]["last_mmr"] = new_mmr
                    self._save_data()
    
    def toggle_notifications(self, guild_id: int, user_id: int) -> bool:
        """Toggle notifications for a user, returns new state"""
        with self.lock:
            guild_str = str(guild_id)
            user_str = str(user_id)
            
            if guild_str in self.data["registered_users"]:
                if user_str in self.data["registered_users"][guild_str]:
                    current = self.data["registered_users"][guild_str][user_str].get("notifications_enabled", True)
                    self.data["registered_users"][guild_str][user_str]["notifications_enabled"] = not current
                    self._save_data()
                    return not current
            return False