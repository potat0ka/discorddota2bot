"""
Rank tracking and notification system for Dota 2 players
"""

import logging
import asyncio
from typing import Dict, List, Optional, Tuple
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .hybrid_api_client import HybridAPIClient
from .database import SimpleDB

logger = logging.getLogger(__name__)

class RankTracker:
    """Tracks player ranks and detects rank changes"""
    
    def __init__(self, db: SimpleDB, api_client):
        self.db = db
        self.api_client = api_client
        self.rank_tiers = {
            0: "Unranked",
            11: "Herald 1", 12: "Herald 2", 13: "Herald 3", 14: "Herald 4", 15: "Herald 5",
            21: "Guardian 1", 22: "Guardian 2", 23: "Guardian 3", 24: "Guardian 4", 25: "Guardian 5",
            31: "Crusader 1", 32: "Crusader 2", 33: "Crusader 3", 34: "Crusader 4", 35: "Crusader 5",
            41: "Archon 1", 42: "Archon 2", 43: "Archon 3", 44: "Archon 4", 45: "Archon 5",
            51: "Legend 1", 52: "Legend 2", 53: "Legend 3", 54: "Legend 4", 55: "Legend 5",
            61: "Ancient 1", 62: "Ancient 2", 63: "Ancient 3", 64: "Ancient 4", 65: "Ancient 5",
            71: "Divine 1", 72: "Divine 2", 73: "Divine 3", 74: "Divine 4", 75: "Divine 5",
            80: "Immortal"
        }
    
    def get_rank_name(self, rank_tier: int) -> str:
        """Get rank name from rank tier"""
        return self.rank_tiers.get(rank_tier, "Unknown")
    
    def mmr_to_rank_tier(self, mmr: int) -> int:
        """Convert MMR to approximate rank tier"""
        if mmr == 0:
            return 0
        elif mmr < 770:
            return 11 + min(4, mmr // 154)  # Herald 1-5
        elif mmr < 1540:
            return 21 + min(4, (mmr - 770) // 154)  # Guardian 1-5
        elif mmr < 2310:
            return 31 + min(4, (mmr - 1540) // 154)  # Crusader 1-5
        elif mmr < 3080:
            return 41 + min(4, (mmr - 2310) // 154)  # Archon 1-5
        elif mmr < 3850:
            return 51 + min(4, (mmr - 3080) // 154)  # Legend 1-5
        elif mmr < 4620:
            return 61 + min(4, (mmr - 3850) // 154)  # Ancient 1-5
        elif mmr < 5420:
            return 71 + min(4, (mmr - 4620) // 160)  # Divine 1-5
        else:
            return 80  # Immortal
    
    async def get_player_mmr(self, steam_id: str) -> Optional[int]:
        """Get player's current MMR from OpenDota API"""
        try:
            # Get player data
            player_data = await self.api_client.get_player_data(steam_id)
            if not player_data:
                return None
            
            # Check if we have MMR data
            mmr_estimate = player_data.get('mmr_estimate', {})
            if mmr_estimate and 'estimate' in mmr_estimate:
                return mmr_estimate['estimate']
            
            # Fallback: try to get from competitive rank
            competitive_rank = player_data.get('competitive_rank')
            if competitive_rank:
                return competitive_rank
            
            # If no MMR available, try to estimate from rank tier
            rank_tier = player_data.get('rank_tier', 0)
            if rank_tier:
                return self.estimate_mmr_from_rank_tier(rank_tier)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting MMR for {steam_id}: {e}")
            return None
    
    def estimate_mmr_from_rank_tier(self, rank_tier: int) -> int:
        """Estimate MMR from rank tier (rough approximation)"""
        if rank_tier == 0:
            return 0
        elif 11 <= rank_tier <= 15:
            return 154 * (rank_tier - 11) + 77
        elif 21 <= rank_tier <= 25:
            return 770 + 154 * (rank_tier - 21) + 77
        elif 31 <= rank_tier <= 35:
            return 1540 + 154 * (rank_tier - 31) + 77
        elif 41 <= rank_tier <= 45:
            return 2310 + 154 * (rank_tier - 41) + 77
        elif 51 <= rank_tier <= 55:
            return 3080 + 154 * (rank_tier - 51) + 77
        elif 61 <= rank_tier <= 65:
            return 3850 + 154 * (rank_tier - 61) + 77
        elif 71 <= rank_tier <= 75:
            return 4620 + 160 * (rank_tier - 71) + 80
        elif rank_tier == 80:
            return 5420
        else:
            return 0
    
    async def check_rank_changes(self, guild_id: int) -> List[Tuple[int, str, int, int]]:
        """
        Check for rank changes among registered users
        Returns list of tuples: (user_id, steam_id, old_mmr, new_mmr)
        """
        rank_changes = []
        registered_users = self.db.get_registered_users(guild_id)
        
        for user_id_str, user_data in registered_users.items():
            if not user_data.get('notifications_enabled', True):
                continue
            
            user_id = int(user_id_str)
            steam_id = user_data['steam_id']
            last_mmr = user_data.get('last_mmr', 0)
            
            # Get current MMR
            current_mmr = await self.get_player_mmr(steam_id)
            if current_mmr is None:
                continue
            
            # Check for significant rank change (at least 150 MMR difference)
            mmr_diff = abs(current_mmr - last_mmr)
            if mmr_diff >= 150:
                old_rank = self.mmr_to_rank_tier(last_mmr)
                new_rank = self.mmr_to_rank_tier(current_mmr)
                
                # Only notify if rank tier actually changed
                if old_rank != new_rank:
                    rank_changes.append((user_id, steam_id, last_mmr, current_mmr))
                    # Update stored MMR
                    self.db.update_user_mmr(guild_id, user_id, current_mmr)
            elif mmr_diff >= 25:
                # Update MMR even for small changes to keep it current
                self.db.update_user_mmr(guild_id, user_id, current_mmr)
        
        return rank_changes
    
    def get_rank_change_message(self, user_id: int, old_mmr: int, new_mmr: int) -> str:
        """Generate rank change notification message"""
        old_rank = self.mmr_to_rank_tier(old_mmr)
        new_rank = self.mmr_to_rank_tier(new_mmr)
        
        old_rank_name = self.get_rank_name(old_rank)
        new_rank_name = self.get_rank_name(new_rank)
        
        mmr_change = new_mmr - old_mmr
        
        if mmr_change > 0:
            emoji = "🎉"
            direction = "up"
        else:
            emoji = "📉"
            direction = "down"
        
        return (
            f"{emoji} <@{user_id}> ranked {direction}!\n"
            f"**{old_rank_name}** → **{new_rank_name}**\n"
            f"MMR: {old_mmr} → {new_mmr} ({mmr_change:+d})"
        )