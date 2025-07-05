"""
The code has been modified to improve the averages calculation with better error handling.
"""
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
            
            # Extract MMR properly
            mmr_estimate = profile.get('mmr_estimate', {})
            if isinstance(mmr_estimate, dict) and 'estimate' in mmr_estimate:
                mmr = mmr_estimate['estimate']
            else:
                mmr = profile.get('solo_competitive_rank') or profile.get('competitive_rank') or 0
            
            # Extract rank tier and convert to name
            rank_tier = profile.get('rank_tier', 0)
            if rank_tier and rank_tier > 0:
                rank_name = self._get_rank_name_from_tier(rank_tier)
            else:
                rank_name = 'Unranked'

            # Process matches
            first_match = self._get_first_match(matches)
            today_match = self._get_today_first_match(matches)
            today_matches_count = self._get_today_matches_count(matches)
            total_matches = len(matches)

            # Win/loss pattern for last 10 matches
            recent_pattern = self._get_recent_win_loss_pattern(matches[:10], account_id)

            # Calculate averages
            averages = self._calculate_averages(matches)

            # Most successful hero
            successful_hero = self._get_most_successful_hero(matches, account_id)

            # Hero streak detection
            hero_streak = self._detect_hero_streak(matches, account_id)

            # Peak rank calculation
            peak_rank_info = self._get_peak_rank(profile, mmr)

            # Overall win rate
            wins = sum(1 for match in matches if self._is_win(match, account_id))
            win_rate = (wins / total_matches * 100) if total_matches > 0 else 0

            return {
                'player_name': player_name,
                'avatar_url': avatar_url,
                'current_mmr': mmr,
                'rank_name': rank_name,
                'peak_rank': peak_rank_info,
                'first_match': first_match,
                'today_match': today_match,
                'today_matches_count': today_matches_count,
                'total_matches': total_matches,
                'win_rate': win_rate,
                'recent_pattern': recent_pattern,
                'averages': averages,
                'successful_hero': successful_hero,
                'hero_streak': hero_streak
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
        """Calculate average performance metrics"""
        if not matches:
            return {'gpm': 0, 'xpm': 0, 'kda': 0.0}

        valid_matches = [m for m in matches if m.get('gold_per_min', 0) > 0]
        if not valid_matches:
            return {'gpm': 0, 'xpm': 0, 'kda': 0.0}

        total_gpm = sum(match.get('gold_per_min', 0) for match in valid_matches)
        total_xpm = sum(match.get('xp_per_min', 0) for match in valid_matches)

        # Calculate KDA
        total_kills = sum(match.get('kills', 0) for match in valid_matches)
        total_deaths = sum(match.get('deaths', 0) for match in valid_matches)
        total_assists = sum(match.get('assists', 0) for match in valid_matches)

        avg_gpm = total_gpm // len(valid_matches)
        avg_xpm = total_xpm // len(valid_matches)
        avg_kda = round((total_kills + total_assists) / max(total_deaths, 1), 2)

        return {
            'gpm': avg_gpm,
            'xpm': avg_xpm, 
            'kda': avg_kda
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
            # Reverse results to show newest match first (left to right)
            streak_results.reverse()
            return {
                'hero_id': current_hero,
                'count': streak_count,
                'results': streak_results
            }

        return None

    def _get_peak_rank(self, profile: Dict, current_mmr: int) -> Dict:
        """Get peak rank information"""
        # Try to get peak MMR from different sources
        peak_mmr = current_mmr  # Start with current MMR as baseline
        
        # Check for leaderboard rank (Immortal players)
        if profile.get('leaderboard_rank'):
            peak_mmr = max(peak_mmr, 6000)  # Assume at least 6000 MMR for leaderboard
        
        # Check solo competitive rank
        solo_rank = profile.get('solo_competitive_rank', 0)
        if solo_rank and solo_rank > 0:
            peak_mmr = max(peak_mmr, solo_rank)
        
        # Check regular competitive rank
        comp_rank = profile.get('competitive_rank', 0)
        if comp_rank and comp_rank > 0:
            peak_mmr = max(peak_mmr, comp_rank)
        
        # Check rank tier and convert to approximate MMR
        rank_tier = profile.get('rank_tier', 0)
        if rank_tier and rank_tier > 0:
            estimated_mmr = self._estimate_mmr_from_rank_tier(rank_tier)
            if estimated_mmr > 0:
                peak_mmr = max(peak_mmr, estimated_mmr)
        
        # Convert to rank name
        if peak_mmr > 0:
            peak_rank_tier = self._mmr_to_rank_tier(peak_mmr)
            peak_rank_name = self._get_rank_name_from_tier(peak_rank_tier)
        else:
            peak_rank_name = "Unranked"
        
        return {
            'mmr': peak_mmr,
            'rank_name': peak_rank_name
        }
    
    def _estimate_mmr_from_rank_tier(self, rank_tier: int) -> int:
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
    
    def _get_rank_name_from_tier(self, rank_tier: int) -> str:
        """Convert rank tier to rank name"""
        rank_names = {
            0: "Unranked",
            11: "Herald I", 12: "Herald II", 13: "Herald III", 14: "Herald IV", 15: "Herald V",
            21: "Guardian I", 22: "Guardian II", 23: "Guardian III", 24: "Guardian IV", 25: "Guardian V",
            31: "Crusader I", 32: "Crusader II", 33: "Crusader III", 34: "Crusader IV", 35: "Crusader V",
            41: "Archon I", 42: "Archon II", 43: "Archon III", 44: "Archon IV", 45: "Archon V",
            51: "Legend I", 52: "Legend II", 53: "Legend III", 54: "Legend IV", 55: "Legend V",
            61: "Ancient I", 62: "Ancient II", 63: "Ancient III", 64: "Ancient IV", 65: "Ancient V",
            71: "Divine I", 72: "Divine II", 73: "Divine III", 74: "Divine IV", 75: "Divine V",
            80: "Immortal"
        }
        return rank_names.get(rank_tier, f"Rank {rank_tier}")
    
    def _mmr_to_rank_tier(self, mmr: int) -> int:
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
    
    def _get_today_matches_count(self, matches: List[Dict]) -> int:
        """Count matches played today"""
        today = datetime.now().date()
        today_count = 0
        
        for match in matches:
            match_date = datetime.fromtimestamp(match.get('start_time', 0)).date()
            if match_date == today:
                today_count += 1
        
        return today_count