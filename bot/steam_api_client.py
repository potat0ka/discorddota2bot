"""
Steam Web API client for fetching Dota 2 data
"""
import asyncio
import logging
import os
from typing import Dict, List, Optional
import aiohttp

logger = logging.getLogger(__name__)

class SteamAPIClient:
    """Client for interacting with Steam Web API"""
    
    BASE_URL = "https://api.steampowered.com"
    
    def __init__(self):
        self.api_key = os.getenv('STEAM_API_KEY')
        self.session = None
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP request to Steam API"""
        if not self.api_key:
            logger.error("Steam API key not found")
            return None
            
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key to params
        if params is None:
            params = {}
        params['key'] = self.api_key
        params['format'] = 'json'
        
        try:
            session = await self._get_session()
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 403:
                    logger.error("Steam API: Access denied - check API key")
                    return None
                elif response.status == 404:
                    logger.warning(f"Steam API: Resource not found - {url}")
                    return None
                else:
                    logger.error(f"Steam API request failed: {response.status} - {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Steam API timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"Steam API error: {e} - {url}")
            return None
    
    def friend_id_to_steam_id(self, friend_id: str) -> str:
        """Convert Friend ID to 64-bit Steam ID"""
        return str(int(friend_id) + 76561197960265728)
    
    async def get_player_summaries(self, steam_id: str) -> Optional[Dict]:
        """
        Get player profile information
        
        Args:
            steam_id: 64-bit Steam ID
            
        Returns:
            Player summary data or None if not found
        """
        result = await self._make_request(
            "ISteamUser/GetPlayerSummaries/v0002/",
            {"steamids": steam_id}
        )
        
        if result and 'response' in result and 'players' in result['response']:
            players = result['response']['players']
            return players[0] if players else None
        return None
    
    async def get_dota_match_history(self, steam_id: str, matches_requested: int = 50) -> Optional[List[Dict]]:
        """
        Get Dota 2 match history for a player
        
        Args:
            steam_id: 64-bit Steam ID
            matches_requested: Number of matches to fetch
            
        Returns:
            List of match data or None if not found
        """
        account_id = int(steam_id) - 76561197960265728
        
        result = await self._make_request(
            "IDOTA2Match_570/GetMatchHistory/V001/",
            {
                "account_id": account_id,
                "matches_requested": matches_requested
            }
        )
        
        if result and 'result' in result and 'matches' in result['result']:
            return result['result']['matches']
        return None
    
    async def get_dota_match_details(self, match_id: str) -> Optional[Dict]:
        """
        Get detailed Dota 2 match information
        
        Args:
            match_id: Match ID
            
        Returns:
            Match details or None if not found
        """
        result = await self._make_request(
            "IDOTA2Match_570/GetMatchDetails/V001/",
            {"match_id": match_id}
        )
        
        if result and 'result' in result:
            return result['result']
        return None
    
    async def get_dota_heroes(self) -> Optional[List[Dict]]:
        """
        Get list of all Dota 2 heroes
        
        Returns:
            List of hero data or None if failed
        """
        result = await self._make_request("IEconDOTA2_570/GetHeroes/v0001/")
        
        if result and 'result' in result and 'heroes' in result['result']:
            return result['result']['heroes']
        return None
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()