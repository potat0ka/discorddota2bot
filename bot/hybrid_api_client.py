"""
Hybrid API client that uses both OpenDota and Steam Web API for maximum reliability
"""
import asyncio
import logging
from typing import Dict, List, Optional
from bot.api_client import OpenDotaClient
from bot.steam_api_client import SteamAPIClient

logger = logging.getLogger(__name__)

class HybridAPIClient:
    """Hybrid client that tries OpenDota first, then falls back to Steam API"""
    
    def __init__(self):
        self.opendota_client = OpenDotaClient()
        self.steam_client = SteamAPIClient()
    
    async def get_player_data(self, friend_id: str) -> Optional[Dict]:
        """
        Get player profile data using both APIs
        
        Args:
            friend_id: Dota 2 Friend ID
            
        Returns:
            Player data dictionary or None if not found
        """
        # Try OpenDota first
        opendota_data = await self.opendota_client.get_player_data(friend_id)
        
        # Convert Friend ID to Steam ID for Steam API
        steam_id = self.steam_client.friend_id_to_steam_id(friend_id)
        
        # Try Steam API for profile info
        steam_data = await self.steam_client.get_player_summaries(steam_id)
        
        if opendota_data:
            # If OpenDota works, use it but supplement with Steam profile data
            if steam_data:
                # Merge Steam profile data into OpenDota response
                opendota_data['steam_profile'] = steam_data
                
                # Update profile information with Steam data
                if 'profile' not in opendota_data:
                    opendota_data['profile'] = {}
                
                opendota_data['profile'].update({
                    'personaname': steam_data.get('personaname', 'Unknown'),
                    'avatarfull': steam_data.get('avatarfull', ''),
                    'profileurl': steam_data.get('profileurl', ''),
                    'profilestate': 1 if steam_data.get('communityvisibilitystate', 0) == 3 else 0
                })
            
            return opendota_data
        
        elif steam_data:
            # If OpenDota fails but Steam works, create compatible data structure
            logger.info(f"OpenDota failed for {friend_id}, using Steam API fallback")
            
            # Get match history from Steam API
            steam_matches = await self.steam_client.get_dota_match_history(steam_id, 50)
            
            return {
                'profile': {
                    'account_id': int(friend_id),
                    'personaname': steam_data.get('personaname', 'Unknown'),
                    'avatarfull': steam_data.get('avatarfull', ''),
                    'profileurl': steam_data.get('profileurl', ''),
                    'profilestate': 1 if steam_data.get('communityvisibilitystate', 0) == 3 else 0,
                    'steamid': steam_id
                },
                'steam_profile': steam_data,
                'matches_available': len(steam_matches) if steam_matches else 0,
                'api_source': 'steam'
            }
        
        return None
    
    async def get_recent_matches(self, friend_id: str, limit: int = 50) -> Optional[List[Dict]]:
        """
        Get recent matches using both APIs
        
        Args:
            friend_id: Dota 2 Friend ID
            limit: Number of matches to fetch
            
        Returns:
            List of match data or None if not found
        """
        # Try OpenDota first
        opendota_matches = await self.opendota_client.get_recent_matches(friend_id, limit)
        
        if opendota_matches:
            return opendota_matches
        
        # Fall back to Steam API
        steam_id = self.steam_client.friend_id_to_steam_id(friend_id)
        steam_matches = await self.steam_client.get_dota_match_history(steam_id, limit)
        
        if steam_matches:
            logger.info(f"Using Steam API matches for {friend_id}")
            
            # Convert Steam match format to OpenDota-compatible format
            converted_matches = []
            for match in steam_matches:
                # Get detailed match info to extract player-specific data
                match_details = await self.steam_client.get_dota_match_details(str(match['match_id']))
                
                if match_details and 'players' in match_details:
                    # Find this player in the match
                    account_id = int(friend_id)
                    player_data = None
                    
                    for player in match_details['players']:
                        if player.get('account_id') == account_id:
                            player_data = player
                            break
                    
                    if player_data:
                        converted_match = {
                            'match_id': match['match_id'],
                            'player_slot': player_data.get('player_slot', 0),
                            'radiant_win': match_details.get('radiant_win', False),
                            'duration': match_details.get('duration', 0),
                            'game_mode': match_details.get('game_mode', 0),
                            'hero_id': player_data.get('hero_id', 0),
                            'start_time': match_details.get('start_time', 0),
                            'kills': player_data.get('kills', 0),
                            'deaths': player_data.get('deaths', 0),
                            'assists': player_data.get('assists', 0),
                            'gold_per_min': player_data.get('gold_per_min', 0),
                            'xp_per_min': player_data.get('xp_per_min', 0),
                            'api_source': 'steam'
                        }
                        converted_matches.append(converted_match)
                
                # Limit API calls to avoid rate limiting
                if len(converted_matches) >= 10:  # Get detailed data for first 10 matches only
                    break
                    
                await asyncio.sleep(0.1)  # Small delay between requests
            
            return converted_matches
        
        return None
    
    async def get_player_wl(self, friend_id: str) -> Optional[Dict]:
        """Get player win/loss statistics"""
        # Try OpenDota first
        result = await self.opendota_client.get_player_wl(friend_id)
        
        if result:
            return result
        
        # For Steam API, we'd need to calculate from match history
        # This is more complex, so for now return None
        logger.info(f"Win/loss data not available via Steam API for {friend_id}")
        return None
    
    async def get_player_heroes(self, friend_id: str) -> Optional[List[Dict]]:
        """Get player hero statistics"""
        # Try OpenDota first
        result = await self.opendota_client.get_player_heroes(friend_id)
        
        if result:
            return result
        
        # For Steam API, we'd need to analyze match history
        logger.info(f"Hero statistics not available via Steam API for {friend_id}")
        return None
    
    async def get_heroes_data(self) -> Optional[List[Dict]]:
        """Get all heroes data"""
        # Try Steam API first for this one as it's more reliable
        steam_heroes = await self.steam_client.get_dota_heroes()
        
        if steam_heroes:
            return steam_heroes
        
        # Fall back to OpenDota
        return await self.opendota_client.get_heroes_data()
    
    async def get_match_details(self, match_id: str) -> Optional[Dict]:
        """Get detailed match information"""
        # Try Steam API first for match details
        steam_details = await self.steam_client.get_dota_match_details(match_id)
        
        if steam_details:
            return steam_details
        
        # Fall back to OpenDota
        return await self.opendota_client.get_match_details(match_id)
    
    async def close(self):
        """Close both API clients"""
        await self.opendota_client.close()
        await self.steam_client.close()