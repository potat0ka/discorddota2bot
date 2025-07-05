"""
Discord slash commands for the Dota 2 bot
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
from .api_client import OpenDotaClient
from .data_processor import DataProcessor
from .embeds import EmbedBuilder

logger = logging.getLogger(__name__)

class DotaCommands(commands.Cog):
    """Cog containing all Dota 2 related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_client = OpenDotaClient()
        self.data_processor = DataProcessor()
        self.embed_builder = EmbedBuilder()
    
    @app_commands.command(name="dota", description="Get comprehensive Dota 2 statistics for a player")
    async def dota_stats(self, interaction: discord.Interaction, friend_id: str):
        """
        Fetch comprehensive Dota 2 statistics for a player
        
        Args:
            interaction: Discord interaction object
            friend_id: Dota 2 Friend ID (32-bit Steam ID)
        """
        await interaction.response.defer()
        
        try:
            # Validate friend ID
            if not friend_id.isdigit():
                embed = discord.Embed(
                    title="❌ Invalid Friend ID",
                    description="Please provide a valid Dota 2 Friend ID (numbers only).\n"
                               "Example: `/dota 122994714`",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Convert to 64-bit Steam ID for OpenDota API
            steam_id = str(int(friend_id) + 76561197960265728)
            
            # Fetch player data
            player_data = await self.api_client.get_player_data(steam_id)
            
            if not player_data:
                embed = discord.Embed(
                    title="❌ Player Not Found",
                    description=f"Could not find player with Friend ID: {friend_id}\n"
                               "Please check the ID and try again.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if profile is private
            if player_data.get('profile', {}).get('profilestate') != 1:
                embed = discord.Embed(
                    title="⚠️ Private Profile",
                    description="This Dota 2 profile is private. Please make it public on OpenDota to view match stats.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Fetch recent matches
            recent_matches = await self.api_client.get_recent_matches(steam_id)
            
            if not recent_matches:
                embed = discord.Embed(
                    title="⚠️ No Match Data",
                    description="No recent match data available for this player.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Process player statistics
            stats = await self.data_processor.process_player_stats(
                player_data, recent_matches, steam_id
            )
            
            # Create and send embed
            embed = await self.embed_builder.create_player_stats_embed(stats, friend_id)
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in dota_stats command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while fetching player data. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="compare", description="Compare two Dota 2 players")
    async def compare_players(self, interaction: discord.Interaction, friend_id1: str, friend_id2: str):
        """
        Compare statistics between two Dota 2 players
        
        Args:
            interaction: Discord interaction object
            friend_id1: First player's Dota 2 Friend ID
            friend_id2: Second player's Dota 2 Friend ID
        """
        await interaction.response.defer()
        
        try:
            # Validate friend IDs
            if not friend_id1.isdigit() or not friend_id2.isdigit():
                embed = discord.Embed(
                    title="❌ Invalid Friend IDs",
                    description="Please provide valid Dota 2 Friend IDs (numbers only).\n"
                               "Example: `/compare 122994714 987654321`",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Convert to 64-bit Steam IDs
            steam_id1 = str(int(friend_id1) + 76561197960265728)
            steam_id2 = str(int(friend_id2) + 76561197960265728)
            
            # Fetch data for both players
            player1_data = await self.api_client.get_player_data(steam_id1)
            player2_data = await self.api_client.get_player_data(steam_id2)
            
            if not player1_data or not player2_data:
                embed = discord.Embed(
                    title="❌ Player(s) Not Found",
                    description="Could not find one or both players. Please check the Friend IDs.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check for private profiles
            if (player1_data.get('profile', {}).get('profilestate') != 1 or 
                player2_data.get('profile', {}).get('profilestate') != 1):
                embed = discord.Embed(
                    title="⚠️ Private Profile(s)",
                    description="One or both profiles are private. Please make them public on OpenDota to compare stats.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Fetch recent matches for both players
            matches1 = await self.api_client.get_recent_matches(steam_id1)
            matches2 = await self.api_client.get_recent_matches(steam_id2)
            
            if not matches1 or not matches2:
                embed = discord.Embed(
                    title="⚠️ No Match Data",
                    description="No recent match data available for one or both players.",
                    color=discord.Color.orange()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Process comparison data
            comparison = await self.data_processor.process_player_comparison(
                player1_data, player2_data, matches1, matches2, steam_id1, steam_id2
            )
            
            # Create and send comparison embed
            embed = await self.embed_builder.create_comparison_embed(
                comparison, friend_id1, friend_id2
            )
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in compare_players command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="An error occurred while comparing players. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="help", description="Show help information for the bot")
    async def help_command(self, interaction: discord.Interaction):
        """Show help information"""
        embed = discord.Embed(
            title="🎮 Dota 2 Statistics Bot",
            description="Get comprehensive Dota 2 player statistics and comparisons!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 `/dota <friend_id>`",
            value="• First match ever played\n"
                  "• Today's first match (if any)\n"
                  "• Total matches played\n"
                  "• Last 10 matches (🟩 win, 🟥 loss)\n"
                  "• Most successful hero\n"
                  "• Average GPM, XPM, KDA\n"
                  "• Suggested best role\n"
                  "• Hero streaks",
            inline=False
        )
        
        embed.add_field(
            name="⚔️ `/compare <friend_id1> <friend_id2>`",
            value="Compare two players side-by-side:\n"
                  "• Win rates and total matches\n"
                  "• Recent performance\n"
                  "• Statistical comparison",
            inline=False
        )
        
        embed.add_field(
            name="🔍 Finding Your Friend ID",
            value="1. Open Dota 2\n"
                  "2. Go to your profile\n"
                  "3. Look for the Friend ID (8-9 digits)\n"
                  "4. Example: 122994714",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ Important Notes",
            value="• Profile must be public on OpenDota\n"
                  "• Uses OpenDota API for data\n"
                  "• Real-time statistics",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ for the Dota 2 community")
        
        await interaction.response.send_message(embed=embed)

async def setup_commands(bot):
    """Setup function to add commands to the bot"""
    await bot.add_cog(DotaCommands(bot))
