"""
Data processor for analyzing Dota 2 statistics
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

logger = logging.getLogger(__name__)

class DataProcessor:
    """Process and analyze Dota 2 player data"""
    
    def __init__(self):
        self.hero_names = {}
        self.role_mapping = {
            1: "Carry",
            2: "Support", 
            3: "Offlaner",
            4: "Soft Support",
            5: "Hard Support"
        }
    
    async def process_player_stats(self, player_data: Dict, matches: List[Dict], account_id: str) -> Dict:
        """
        Process comprehensive player statistics
        
        Args:
            player_data: Player profile data
            matches: List of recent matches
            steam_id: Player's Steam ID
            
        Returns:
            Dictionary containing processed statistics
        """
        try:
            # Basic player info
            profile = player_data.get('profile', {})
            player_name = profile.get('personaname', 'Unknown Player')
            avatar_url = profile.get('avatarfull', '')
            
            # Process matches
            first_match = self._get_first_match(matches)
            today_match = self._get_today_first_match(matches)
            total_matches = len(matches)
            
            # Win/loss pattern for last 10 matches
            recent_pattern = self._get_recent_win_loss_pattern(matches[:10], account_id)
            
            # Calculate averages
            averages = self._calculate_averages(matches)
            
            # Most successful hero
            successful_hero = self._get_most_successful_hero(matches, account_id)
            
            # Hero streak detection
            hero_streak = self._detect_hero_streak(matches, account_id)
            
            # Role suggestion
            suggested_role = self._suggest_best_role(matches, account_id)
            
            # Overall win rate
            wins = sum(1 for match in matches if self._is_win(match, account_id))
            win_rate = (wins / total_matches * 100) if total_matches > 0 else 0
            
            return {
                'player_name': player_name,
                'avatar_url': avatar_url,
                'first_match': first_match,
                'today_match': today_match,
                'total_matches': total_matches,
                'win_rate': win_rate,
                'recent_pattern': recent_pattern,
                'averages': averages,
                'successful_hero': successful_hero,
                'hero_streak': hero_streak,
                'suggested_role': suggested_role
            }
            
        except Exception as e:
            logger.error(f"Error processing player stats: {e}")
            return {}
    
    async def process_player_comparison(self, player1_data: Dict, player2_data: Dict, 
                                      matches1: List[Dict], matches2: List[Dict],
                                      account_id1: str, account_id2: str) -> Dict:
        """
        Process comparison between two players
        
        Args:
            player1_data: First player's profile data
            player2_data: Second player's profile data
            matches1: First player's matches
            matches2: Second player's matches
            steam_id1: First player's Steam ID
            steam_id2: Second player's Steam ID
            
        Returns:
            Dictionary containing comparison data
        """
        try:
            # Basic info
            player1_name = player1_data.get('profile', {}).get('personaname', 'Player 1')
            player2_name = player2_data.get('profile', {}).get('personaname', 'Player 2')
            
            # Calculate stats for both players
            player1_stats = {
                'name': player1_name,
                'total_matches': len(matches1),
                'wins': sum(1 for match in matches1 if self._is_win(match, account_id1)),
                'averages': self._calculate_averages(matches1),
                'recent_pattern': self._get_recent_win_loss_pattern(matches1[:10], account_id1),
                'successful_hero': self._get_most_successful_hero(matches1, account_id1)
            }
            
            player2_stats = {
                'name': player2_name,
                'total_matches': len(matches2),
                'wins': sum(1 for match in matches2 if self._is_win(match, account_id2)),
                'averages': self._calculate_averages(matches2),
                'recent_pattern': self._get_recent_win_loss_pattern(matches2[:10], account_id2),
                'successful_hero': self._get_most_successful_hero(matches2, account_id2)
            }
            
            # Calculate win rates
            player1_stats['win_rate'] = (player1_stats['wins'] / player1_stats['total_matches'] * 100) if player1_stats['total_matches'] > 0 else 0
            player2_stats['win_rate'] = (player2_stats['wins'] / player2_stats['total_matches'] * 100) if player2_stats['total_matches'] > 0 else 0
            
            return {
                'player1': player1_stats,
                'player2': player2_stats
            }
            
        except Exception as e:
            logger.error(f"Error processing player comparison: {e}")
            return {}
    
    def _get_first_match(self, matches: List[Dict]) -> Optional[Dict]:
        """Get the first match ever played"""
        if not matches:
            return None
        
        # Matches are usually sorted by start_time descending
        first_match = min(matches, key=lambda x: x.get('start_time', 0))
        
        return {
            'date': datetime.fromtimestamp(first_match.get('start_time', 0)).strftime('%Y-%m-%d'),
            'hero_id': first_match.get('hero_id'),
            'match_id': first_match.get('match_id')
        }
    
    def _get_today_first_match(self, matches: List[Dict]) -> Optional[Dict]:
        """Get the first match played today"""
        today = datetime.now().date()
        
        today_matches = []
        for match in matches:
            match_date = datetime.fromtimestamp(match.get('start_time', 0)).date()
            if match_date == today:
                today_matches.append(match)
        
        if not today_matches:
            return None
        
        # Get earliest match today
        first_today = min(today_matches, key=lambda x: x.get('start_time', 0))
        
        return {
            'datetime': datetime.fromtimestamp(first_today.get('start_time', 0)).strftime('%Y-%m-%d %H:%M'),
            'hero_id': first_today.get('hero_id'),
            'result': 'Win' if (first_today.get('radiant_win') and first_today.get('player_slot', 0) < 128) or (not first_today.get('radiant_win') and first_today.get('player_slot', 0) >= 128) else 'Loss'
        }
    
    def _get_recent_win_loss_pattern(self, matches: List[Dict], steam_id: str) -> str:
        """Get win/loss pattern for recent matches"""
        pattern = ""
        for match in matches:
            if self._is_win(match, steam_id):
                pattern += "🟩"
            else:
                pattern += "🟥"
        return pattern
    
    def _is_win(self, match: Dict, account_id: str) -> bool:
        """Check if match was a win for the player"""
        player_slot = match.get('player_slot', 0)
        radiant_win = match.get('radiant_win', False)
        
        # Player slot < 128 means radiant, >= 128 means dire
        is_radiant = player_slot < 128
        
        return (is_radiant and radiant_win) or (not is_radiant and not radiant_win)
    
    def _calculate_averages(self, matches: List[Dict]) -> Dict:
        """Calculate average statistics"""
        if not matches:
            return {'gpm': 0, 'xpm': 0, 'kda': 0}
        
        gpm_values = [match.get('gold_per_min', 0) for match in matches if match.get('gold_per_min')]
        xpm_values = [match.get('xp_per_min', 0) for match in matches if match.get('xp_per_min')]
        
        kda_values = []
        for match in matches:
            kills = match.get('kills', 0)
            deaths = match.get('deaths', 0)
            assists = match.get('assists', 0)
            
            if deaths > 0:
                kda = (kills + assists) / deaths
            else:
                kda = kills + assists
            
            kda_values.append(kda)
        
        return {
            'gpm': round(statistics.mean(gpm_values)) if gpm_values else 0,
            'xpm': round(statistics.mean(xpm_values)) if xpm_values else 0,
            'kda': round(statistics.mean(kda_values), 2) if kda_values else 0
        }
    
    def _get_most_successful_hero(self, matches: List[Dict], steam_id: str) -> Optional[Dict]:
        """Get the most successful hero (highest win rate with 10+ games)"""
        hero_stats = {}
        
        for match in matches:
            hero_id = match.get('hero_id')
            if not hero_id:
                continue
            
            if hero_id not in hero_stats:
                hero_stats[hero_id] = {'wins': 0, 'total': 0}
            
            hero_stats[hero_id]['total'] += 1
            if self._is_win(match, steam_id):
                hero_stats[hero_id]['wins'] += 1
        
        # Filter heroes with 10+ games
        qualified_heroes = {k: v for k, v in hero_stats.items() if v['total'] >= 10}
        
        if not qualified_heroes:
            return None
        
        # Find hero with highest win rate
        best_hero_id = max(qualified_heroes.keys(), 
                          key=lambda x: qualified_heroes[x]['wins'] / qualified_heroes[x]['total'])
        
        best_stats = qualified_heroes[best_hero_id]
        win_rate = best_stats['wins'] / best_stats['total'] * 100
        
        return {
            'hero_id': best_hero_id,
            'win_rate': round(win_rate, 1),
            'games': best_stats['total']
        }
    
    def _detect_hero_streak(self, matches: List[Dict], steam_id: str) -> Optional[Dict]:
        """Detect hero streaks (3+ consecutive games with same hero)"""
        if len(matches) < 3:
            return None
        
        # Sort matches by start time (most recent first)
        sorted_matches = sorted(matches, key=lambda x: x.get('start_time', 0), reverse=True)
        
        current_hero = None
        streak_count = 0
        streak_results = []
        
        for match in sorted_matches:
            hero_id = match.get('hero_id')
            
            if hero_id == current_hero:
                streak_count += 1
                streak_results.append(self._is_win(match, steam_id))
            else:
                if streak_count >= 3:
                    break
                current_hero = hero_id
                streak_count = 1
                streak_results = [self._is_win(match, steam_id)]
        
        if streak_count >= 3:
            return {
                'hero_id': current_hero,
                'count': streak_count,
                'results': streak_results
            }
        
        return None
    
    def _suggest_best_role(self, matches: List[Dict], steam_id: str) -> str:
        """Suggest best role based on most played positions"""
        lane_counts = {}
        
        for match in matches:
            lane = match.get('lane')
            if lane:
                lane_counts[lane] = lane_counts.get(lane, 0) + 1
        
        if not lane_counts:
            return "Unknown"
        
        # Map lanes to roles
        lane_to_role = {
            1: "Safe Lane (Carry)",
            2: "Mid Lane",
            3: "Off Lane",
            4: "Jungle",
            5: "Roaming"
        }
        
        most_played_lane = max(lane_counts, key=lane_counts.get)
        return lane_to_role.get(most_played_lane, "Versatile")
