"""
Discord embed builder for Dota 2 statistics
"""

import discord
from datetime import datetime
from typing import Dict, Optional

class EmbedBuilder:
    """Builder for Discord embeds"""
    
    def __init__(self):
        self.hero_names = {
            1: "Anti-Mage", 2: "Axe", 3: "Bane", 4: "Bloodseeker", 5: "Crystal Maiden",
            6: "Drow Ranger", 7: "Earthshaker", 8: "Juggernaut", 9: "Mirana", 10: "Morphling",
            11: "Shadow Fiend", 12: "Phantom Lancer", 13: "Puck", 14: "Pudge", 15: "Razor",
            16: "Sand King", 17: "Storm Spirit", 18: "Sven", 19: "Tiny", 20: "Vengeful Spirit",
            21: "Windranger", 22: "Zeus", 23: "Kunkka", 25: "Lina", 26: "Lion",
            27: "Shadow Shaman", 28: "Slardar", 29: "Tidehunter", 30: "Witch Doctor", 31: "Lich",
            32: "Riki", 33: "Enigma", 34: "Tinker", 35: "Sniper", 36: "Necrophos",
            37: "Warlock", 38: "Beastmaster", 39: "Queen of Pain", 40: "Venomancer", 41: "Faceless Void",
            42: "Wraith King", 43: "Death Prophet", 44: "Phantom Assassin", 45: "Pugna", 46: "Templar Assassin",
            47: "Viper", 48: "Luna", 49: "Dragon Knight", 50: "Dazzle", 51: "Clockwerk",
            52: "Leshrac", 53: "Nature's Prophet", 54: "Lifestealer", 55: "Dark Seer", 56: "Clinkz",
            57: "Omniknight", 58: "Enchantress", 59: "Huskar", 60: "Night Stalker", 61: "Broodmother",
            62: "Bounty Hunter", 63: "Weaver", 64: "Jakiro", 65: "Batrider", 66: "Chen",
            67: "Spectre", 68: "Ancient Apparition", 69: "Doom", 70: "Ursa", 71: "Spirit Breaker",
            72: "Gyrocopter", 73: "Alchemist", 74: "Invoker", 75: "Silencer", 76: "Outworld Destroyer",
            77: "Lycan", 78: "Brewmaster", 79: "Shadow Demon", 80: "Lone Druid", 81: "Chaos Knight",
            82: "Meepo", 83: "Treant Protector", 84: "Ogre Magi", 85: "Undying", 86: "Rubick",
            87: "Disruptor", 88: "Nyx Assassin", 89: "Naga Siren", 90: "Keeper of the Light", 91: "Io",
            92: "Visage", 93: "Slark", 94: "Medusa", 95: "Troll Warlord", 96: "Centaur Warrunner",
            97: "Magnus", 98: "Timbersaw", 99: "Bristleback", 100: "Tusk", 101: "Skywrath Mage",
            102: "Abaddon", 103: "Elder Titan", 104: "Legion Commander", 105: "Techies", 106: "Ember Spirit",
            107: "Earth Spirit", 108: "Underlord", 109: "Terrorblade", 110: "Phoenix", 111: "Oracle",
            112: "Winter Wyvern", 113: "Arc Warden", 114: "Monkey King", 115: "Dark Willow", 116: "Pangolier",
            117: "Grimstroke", 118: "Hoodwink", 119: "Void Spirit", 120: "Snapfire", 121: "Mars",
            123: "Dawnbreaker", 124: "Marci", 125: "Primal Beast", 126: "Muerta"
        }
    
    def get_hero_name(self, hero_id: int) -> str:
        """Get hero name by ID"""
        return self.hero_names.get(hero_id, f"Hero {hero_id}")
    
    async def create_player_stats_embed(self, stats: Dict, friend_id: str) -> discord.Embed:
        """
        Create embed for player statistics
        
        Args:
            stats: Processed player statistics
            friend_id: Player's friend ID
            
        Returns:
            Discord embed with player statistics
        """
        player_name = stats.get('player_name', 'Unknown Player')
        
        embed = discord.Embed(
            title=f"🎮 {player_name}'s Dota 2 Statistics",
            description=f"**Friend ID:** {friend_id}",
            color=discord.Color.blue()
        )
        
        # Set thumbnail if avatar available
        avatar_url = stats.get('avatar_url')
        if avatar_url:
            embed.set_thumbnail(url=avatar_url)
        
        # Basic stats
        total_matches = stats.get('total_matches', 0)
        win_rate = stats.get('win_rate', 0)
        rank_name = stats.get('rank_name', 'Unranked')
        current_mmr = stats.get('current_mmr', 0)
        
        embed.add_field(
            name="📊 Overview",
            value=f"**Total Matches:** {total_matches:,}\n"
                  f"**Win Rate:** {win_rate:.1f}%\n"
                  f"**Rank:** {rank_name}\n"
                  f"**MMR:** {current_mmr:,}" if current_mmr > 0 else f"**Rank:** {rank_name}",
            inline=True
        )
        
        # First match
        first_match = stats.get('first_match')
        if first_match:
            hero_name = self.get_hero_name(first_match.get('hero_id', 0))
            embed.add_field(
                name="🎯 First Match",
                value=f"**Date:** {first_match['date']}\n"
                      f"**Hero:** {hero_name}\n"
                      f"**Match ID:** {first_match['match_id']}",
                inline=True
            )
        
        # Today's first match
        today_match = stats.get('today_match')
        if today_match:
            hero_name = self.get_hero_name(today_match.get('hero_id', 0))
            result_emoji = "🟩" if today_match['result'] == 'Win' else "🟥"
            
            embed.add_field(
                name="🌅 Today's First Match",
                value=f"**Time:** {today_match['datetime']}\n"
                      f"**Hero:** {hero_name}\n"
                      f"**Result:** {result_emoji} {today_match['result']}",
                inline=True
            )
        
        # Recent matches pattern
        recent_pattern = stats.get('recent_pattern', '')
        if recent_pattern:
            embed.add_field(
                name="📈 Last 10 Matches",
                value=f"{recent_pattern}",
                inline=False
            )
        
        # Averages
        averages = stats.get('averages', {})
        if averages and averages.get('gpm', 0) > 0:
            embed.add_field(
                name="📊 Average Performance",
                value=f"**GPM:** {averages.get('gpm', 0):,}\n"
                      f"**XPM:** {averages.get('xpm', 0):,}\n"
                      f"**KDA:** {averages.get('kda', 0.0):.2f}",
                inline=True
            )
        
        # Most successful hero
        successful_hero = stats.get('successful_hero')
        if successful_hero:
            hero_name = self.get_hero_name(successful_hero.get('hero_id', 0))
            embed.add_field(
                name="🏆 Most Successful Hero",
                value=f"**Hero:** {hero_name}\n"
                      f"**Win Rate:** {successful_hero.get('win_rate', 0)}%\n"
                      f"**Games:** {successful_hero.get('games', 0)}",
                inline=True
            )
        
        # Suggested role
        suggested_role = stats.get('suggested_role', 'Unknown')
        embed.add_field(
            name="🎯 Suggested Role",
            value=f"**{suggested_role}**",
            inline=True
        )
        
        # Hero streak
        hero_streak = stats.get('hero_streak')
        if hero_streak:
            hero_name = self.get_hero_name(hero_streak.get('hero_id', 0))
            results = hero_streak.get('results', [])
            streak_pattern = ''.join(['🟩' if win else '🟥' for win in results])
            
            embed.add_field(
                name="🔥 Current Hero Streak",
                value=f"**{hero_streak.get('count', 0)}x {hero_name}**\n"
                      f"{streak_pattern}",
                inline=False
            )
        
        embed.set_footer(text=f"Data from OpenDota • {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        
        return embed
    
    async def create_comparison_embed(self, comparison: Dict, friend_id1: str, friend_id2: str) -> discord.Embed:
        """
        Create embed for player comparison
        
        Args:
            comparison: Comparison data
            friend_id1: First player's friend ID
            friend_id2: Second player's friend ID
            
        Returns:
            Discord embed with comparison
        """
        player1 = comparison.get('player1', {})
        player2 = comparison.get('player2', {})
        
        embed = discord.Embed(
            title="⚔️ Player Comparison",
            description=f"**{player1.get('name', 'Player 1')}** vs **{player2.get('name', 'Player 2')}**",
            color=discord.Color.purple()
        )
        
        # Overview comparison
        embed.add_field(
            name=f"📊 {player1.get('name', 'Player 1')} (ID: {friend_id1})",
            value=f"**Total Matches:** {player1.get('total_matches', 0):,}\n"
                  f"**Wins:** {player1.get('wins', 0):,}\n"
                  f"**Win Rate:** {player1.get('win_rate', 0):.1f}%",
            inline=True
        )
        
        embed.add_field(
            name=f"📊 {player2.get('name', 'Player 2')} (ID: {friend_id2})",
            value=f"**Total Matches:** {player2.get('total_matches', 0):,}\n"
                  f"**Wins:** {player2.get('wins', 0):,}\n"
                  f"**Win Rate:** {player2.get('win_rate', 0):.1f}%",
            inline=True
        )
        
        # Determine winner
        if player1.get('win_rate', 0) > player2.get('win_rate', 0):
            winner = f"🏆 {player1.get('name', 'Player 1')} has a higher win rate!"
        elif player2.get('win_rate', 0) > player1.get('win_rate', 0):
            winner = f"🏆 {player2.get('name', 'Player 2')} has a higher win rate!"
        else:
            winner = "🤝 Both players have the same win rate!"
        
        embed.add_field(
            name="🏆 Winner",
            value=winner,
            inline=False
        )
        
        # Recent performance
        pattern1 = player1.get('recent_pattern', '')
        pattern2 = player2.get('recent_pattern', '')
        
        if pattern1 and pattern2:
            embed.add_field(
                name="📈 Recent Performance (Last 10 Matches)",
                value=f"**{player1.get('name', 'Player 1')}:** {pattern1}\n"
                      f"**{player2.get('name', 'Player 2')}:** {pattern2}",
                inline=False
            )
        
        # Average performance
        avg1 = player1.get('averages', {})
        avg2 = player2.get('averages', {})
        
        if avg1 and avg2:
            embed.add_field(
                name=f"📊 Average Performance - {player1.get('name', 'Player 1')}",
                value=f"**GPM:** {avg1.get('gpm', 0)}\n"
                      f"**XPM:** {avg1.get('xpm', 0)}\n"
                      f"**KDA:** {avg1.get('kda', 0)}",
                inline=True
            )
            
            embed.add_field(
                name=f"📊 Average Performance - {player2.get('name', 'Player 2')}",
                value=f"**GPM:** {avg2.get('gpm', 0)}\n"
                      f"**XPM:** {avg2.get('xpm', 0)}\n"
                      f"**KDA:** {avg2.get('kda', 0)}",
                inline=True
            )
        
        # Most successful heroes
        hero1 = player1.get('successful_hero')
        hero2 = player2.get('successful_hero')
        
        if hero1 and hero2:
            hero1_name = self.get_hero_name(hero1.get('hero_id', 0))
            hero2_name = self.get_hero_name(hero2.get('hero_id', 0))
            
            embed.add_field(
                name="🏆 Most Successful Heroes",
                value=f"**{player1.get('name', 'Player 1')}:** {hero1_name} ({hero1.get('win_rate', 0)}%)\n"
                      f"**{player2.get('name', 'Player 2')}:** {hero2_name} ({hero2.get('win_rate', 0)}%)",
                inline=False
            )
        
        embed.set_footer(text=f"Data from OpenDota • {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
        
        return embed
