"""
OpenDota API client for fetching Dota 2 data
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class OpenDotaClient:
    """Client for interacting with OpenDota API"""
    
    BASE_URL = "https://api.opendota.com/api"
    
    def __init__(self):
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_request(self, endpoint: str) -> Optional[Dict]:
        """Make HTTP request to OpenDota API"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            session = await self._get_session()
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 404:
                    logger.warning(f"Resource not found: {url}")
                    return None
                else:
                    logger.error(f"API request failed: {response.status} - {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Request timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"Request error: {e} - {url}")
            return None
    
    async def get_player_data(self, steam_id: str) -> Optional[Dict]:
        """
        Get player profile data
        
        Args:
            steam_id: 64-bit Steam ID
            
        Returns:
            Player data dictionary or None if not found
        """
        return await self._make_request(f"players/{steam_id}")
    
    async def get_recent_matches(self, steam_id: str, limit: int = 50) -> Optional[List[Dict]]:
        """
        Get recent matches for a player
        
        Args:
            steam_id: 64-bit Steam ID
            limit: Number of matches to fetch
            
        Returns:
            List of match dictionaries or None if not found
        """
        return await self._make_request(f"players/{steam_id}/matches?limit={limit}")
    
    async def get_player_wl(self, steam_id: str) -> Optional[Dict]:
        """
        Get player win/loss statistics
        
        Args:
            steam_id: 64-bit Steam ID
            
        Returns:
            Win/loss data dictionary or None if not found
        """
        return await self._make_request(f"players/{steam_id}/wl")
    
    async def get_player_heroes(self, steam_id: str) -> Optional[List[Dict]]:
        """
        Get player hero statistics
        
        Args:
            steam_id: 64-bit Steam ID
            
        Returns:
            List of hero statistics or None if not found
        """
        return await self._make_request(f"players/{steam_id}/heroes")
    
    async def get_heroes_data(self) -> Optional[List[Dict]]:
        """
        Get all heroes data
        
        Returns:
            List of hero data or None if failed
        """
        return await self._make_request("heroes")
    
    async def get_match_details(self, match_id: str) -> Optional[Dict]:
        """
        Get detailed match information
        
        Args:
            match_id: Match ID
            
        Returns:
            Match details dictionary or None if not found
        """
        return await self._make_request(f"matches/{match_id}")
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
