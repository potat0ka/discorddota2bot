"""
Discord slash commands for the Dota 2 bot
"""

import discord
from discord.ext import commands
from discord import app_commands
import logging
import asyncio
from .hybrid_api_client import HybridAPIClient
from .data_processor import DataProcessor
from .embeds import EmbedBuilder
from .database import SimpleDB
from .rank_tracker import RankTracker

logger = logging.getLogger(__name__)

class DotaCommands(commands.Cog):
    """Cog containing all Dota 2 related commands"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_client = HybridAPIClient()
        self.data_processor = DataProcessor()
        self.embed_builder = EmbedBuilder()
        self.db = SimpleDB()
        self.rank_tracker = RankTracker(self.db, self.api_client.opendota_client)
    
    def _check_channel_permission(self, interaction: discord.Interaction) -> bool:
        """Check if the command can be used in this channel"""
        if not interaction.guild or not interaction.channel:
            return True  # Allow DMs
        
        return self.db.is_channel_allowed(interaction.guild.id, interaction.channel.id)
    
    def _check_admin_permission(self, interaction: discord.Interaction) -> bool:
        """Check if user has admin permissions"""
        if not interaction.guild:
            return False
        
        # Check if user has server admin permissions or is a registered bot admin
        if hasattr(interaction.user, 'guild_permissions') and interaction.user.guild_permissions.administrator:
            return True
        
        return self.db.is_admin_user(interaction.guild.id, interaction.user.id)
    
    @app_commands.command(name="dota", description="Get comprehensive Dota 2 statistics for a player")
    async def dota_stats(self, interaction: discord.Interaction, friend_id: str):
        """
        Fetch comprehensive Dota 2 statistics for a player
        
        Args:
            interaction: Discord interaction object
            friend_id: Dota 2 Friend ID (32-bit Steam ID)
        """
        # Check channel permission
        if not self._check_channel_permission(interaction):
            if interaction.guild:
                allowed_channel_id = self.db.get_allowed_channel(interaction.guild.id)
                if allowed_channel_id:
                    allowed_channel = interaction.guild.get_channel(allowed_channel_id)
                    channel_mention = allowed_channel.mention if allowed_channel else f"<#{allowed_channel_id}>"
                    embed = discord.Embed(
                        title="❌ Wrong Channel",
                        description=f"This bot can only be used in {channel_mention}",
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="❌ No Allowed Channel Set",
                        description="An admin needs to set an allowed channel first using `/set-channel`",
                        color=discord.Color.red()
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Validate friend ID first (before defer)
        if not friend_id.isdigit():
            embed = discord.Embed(
                title="❌ Invalid Friend ID",
                description="Please provide a valid Dota 2 Friend ID (numbers only).\n"
                           "Example: `/dota 122994714`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            
            # OpenDota API uses account_id (Friend ID) directly
            steam_id = friend_id
            
            # Fetch player data
            player_data = await self.api_client.get_player_data(steam_id)
            
            if not player_data:
                embed = discord.Embed(
                    title="❌ Player Not Found",
                    description=f"Could not find player with Friend ID: {friend_id}\n\n"
                               "**Possible reasons:**\n"
                               "• Friend ID might be incorrect\n"
                               "• Profile is private on Steam\n"
                               "• Player hasn't played Dota 2 recently\n"
                               "• Profile not linked to OpenDota\n\n"
                               "**How to fix:**\n"
                               "1. Double-check your Friend ID in Dota 2\n"
                               "2. Make sure your Steam profile is public\n"
                               "3. Play a match to sync with OpenDota\n"
                               "4. Visit opendota.com and login with Steam",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed)
                return
            
            # Check if we have sufficient data to display stats
            profile = player_data.get('profile', {})
            
            # Only flag as private if we explicitly know it's private (profilestate = 0)
            # or if we have absolutely no useful data
            profile_state = profile.get('profilestate')
            has_useful_data = (
                profile.get('personaname') or 
                profile.get('account_id') or 
                player_data.get('steam_profile', {}).get('personaname')
            )
            
            # Only show private warning if explicitly private or completely no data
            if profile_state == 0 or (not has_useful_data and not recent_matches):
                embed = discord.Embed(
                    title="⚠️ Private Profile or No Data",
                    description="This profile appears to be private or has no available data. Make sure the Friend ID is correct and the profile is public on Steam.",
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
        # Check channel permission
        if not self._check_channel_permission(interaction):
            if interaction.guild:
                allowed_channel_id = self.db.get_allowed_channel(interaction.guild.id)
                if allowed_channel_id:
                    embed = discord.Embed(
                        title="❌ Wrong Channel",
                        description=f"This bot can only be used in <#{allowed_channel_id}>",
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="❌ No Allowed Channel Set",
                        description="An admin needs to set an allowed channel first using `/set-channel`",
                        color=discord.Color.red()
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Validate friend IDs first (before defer)
        if not friend_id1.isdigit() or not friend_id2.isdigit():
            embed = discord.Embed(
                title="❌ Invalid Friend IDs",
                description="Please provide valid Dota 2 Friend IDs (numbers only).\n"
                           "Example: `/compare 122994714 987654321`",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        try:
            
            # OpenDota API uses account_id (Friend ID) directly
            steam_id1 = friend_id1
            steam_id2 = friend_id2
            
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
            
            # Check for private profiles - only flag if explicitly private or no data
            profile1 = player1_data.get('profile', {})
            profile2 = player2_data.get('profile', {})
            
            # Only consider private if profilestate is explicitly 0 or no matches available
            profile1_private = (profile1.get('profilestate') == 0 or (not matches1 and not profile1.get('personaname')))
            profile2_private = (profile2.get('profilestate') == 0 or (not matches2 and not profile2.get('personaname')))
            
            if profile1_private or profile2_private:
                embed = discord.Embed(
                    title="⚠️ Private Profile(s)",
                    description="One or both profiles are private or have limited visibility. Please make them public on Steam and OpenDota to compare stats.",
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
            description="Get comprehensive Dota 2 player statistics, comparisons, and rank notifications!",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="📊 **Player Statistics**",
            value="`/dota <friend_id>` - Get comprehensive player stats\n"
                  "`/compare <friend_id1> <friend_id2>` - Compare two players",
            inline=False
        )
        
        embed.add_field(
            name="🔔 **Rank Notifications**",
            value="`/register <friend_id> [user]` - Register for rank-up notifications\n"
                  "`/unregister [user]` - Unregister from notifications\n"
                  "`/list-registered` - Show all registered users",
            inline=False
        )
        
        embed.add_field(
            name="⚙️ **Admin Commands**",
            value="`/set-channel [channel]` - Set allowed channel for bot commands",
            inline=False
        )
        
        embed.add_field(
            name="🔍 **Finding Your Friend ID**",
            value="1. Open Dota 2\n"
                  "2. Go to your profile\n"
                  "3. Look for the Friend ID (8-9 digits)\n"
                  "4. Example: 122994714\n"
                  "5. First make sure your Steam profile is public\n"
                  "6. Play a match to sync with OpenDota",
            inline=False
        )
        
        embed.add_field(
            name="⚠️ **Important Notes**",
            value="• Profile must be public on OpenDota\n"
                  "• Bot checks for rank changes every 30 minutes\n"
                  "• Admin permissions required for channel setup\n"
                  "• Uses OpenDota API for real-time data",
            inline=False
        )
        
        embed.set_footer(text="Made with ❤️ for the Dota 2 community")
        
        await interaction.response.send_message(embed=embed)
    
    # Admin Commands
    @app_commands.command(name="set-channel", description="[ADMIN] Set the channel where bot commands are allowed")
    async def set_channel(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        """Set the allowed channel for bot commands"""
        if not self._check_admin_permission(interaction):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You need administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
        # Use current channel if no channel specified
        target_channel = channel or interaction.channel
        if not isinstance(target_channel, discord.TextChannel):
            await interaction.response.send_message("Please specify a valid text channel.", ephemeral=True)
            return
        
        self.db.set_allowed_channel(interaction.guild.id, target_channel.id)
        
        embed = discord.Embed(
            title="✅ Channel Set",
            description=f"Bot commands are now restricted to {target_channel.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="register", description="Register yourself or another user for rank-up notifications")
    async def register_user(self, interaction: discord.Interaction, friend_id: str, user: discord.Member = None):
        """Register a user for rank notifications"""
        # Check channel permission first
        if not self._check_channel_permission(interaction):
            if interaction.guild:
                allowed_channel_id = self.db.get_allowed_channel(interaction.guild.id)
                if allowed_channel_id:
                    embed = discord.Embed(
                        title="❌ Wrong Channel",
                        description=f"This bot can only be used in <#{allowed_channel_id}>",
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="❌ No Allowed Channel Set",
                        description="An admin needs to set an allowed channel first using `/set-channel`",
                        color=discord.Color.red()
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
        # Target user (self if not specified)
        target_user = user or interaction.user
        
        # Validate friend ID
        if not friend_id.isdigit():
            embed = discord.Embed(
                title="❌ Invalid Friend ID",
                description="Please provide a valid Dota 2 Friend ID (numbers only).",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer()
        
        # Convert to Steam ID and verify player exists
        steam_id = str(int(friend_id) + 76561197960265728)
        player_data = await self.api_client.get_player_data(steam_id)
        
        if not player_data:
            embed = discord.Embed(
                title="❌ Player Not Found",
                description=f"Could not find player with Friend ID: {friend_id}",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            return
        
        # Get current MMR for tracking
        current_mmr = await self.rank_tracker.get_player_mmr(steam_id) or 0
        
        # Register user
        self.db.register_user(interaction.guild.id, target_user.id, steam_id, current_mmr)
        
        player_name = player_data.get('profile', {}).get('personaname', 'Unknown Player')
        current_rank = self.rank_tracker.get_rank_name(self.rank_tracker.mmr_to_rank_tier(current_mmr))
        
        embed = discord.Embed(
            title="✅ Registration Successful",
            description=f"{target_user.mention} has been registered for rank notifications!",
            color=discord.Color.green()
        )
        embed.add_field(name="Player", value=player_name, inline=True)
        embed.add_field(name="Friend ID", value=friend_id, inline=True)
        embed.add_field(name="Current Rank", value=current_rank, inline=True)
        
        await interaction.followup.send(embed=embed)
    
    @app_commands.command(name="unregister", description="Unregister yourself or another user from rank notifications")
    async def unregister_user(self, interaction: discord.Interaction, user: discord.Member = None):
        """Unregister a user from rank notifications"""
        if not self._check_channel_permission(interaction):
            if interaction.guild:
                allowed_channel_id = self.db.get_allowed_channel(interaction.guild.id)
                if allowed_channel_id:
                    embed = discord.Embed(
                        title="❌ Wrong Channel",
                        description=f"This bot can only be used in <#{allowed_channel_id}>",
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="❌ No Allowed Channel Set",
                        description="An admin needs to set an allowed channel first using `/set-channel`",
                        color=discord.Color.red()
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
        target_user = user or interaction.user
        
        # Check if user is registered
        registration = self.db.get_user_registration(interaction.guild.id, target_user.id)
        if not registration:
            embed = discord.Embed(
                title="❌ Not Registered",
                description=f"{target_user.mention} is not registered for rank notifications.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        self.db.unregister_user(interaction.guild.id, target_user.id)
        
        embed = discord.Embed(
            title="✅ Unregistered",
            description=f"{target_user.mention} has been unregistered from rank notifications.",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="list-registered", description="List all users registered for rank notifications")
    async def list_registered(self, interaction: discord.Interaction):
        """List all registered users"""
        if not self._check_channel_permission(interaction):
            if interaction.guild:
                allowed_channel_id = self.db.get_allowed_channel(interaction.guild.id)
                if allowed_channel_id:
                    embed = discord.Embed(
                        title="❌ Wrong Channel",
                        description=f"This bot can only be used in <#{allowed_channel_id}>",
                        color=discord.Color.red()
                    )
                else:
                    embed = discord.Embed(
                        title="❌ No Allowed Channel Set",
                        description="An admin needs to set an allowed channel first using `/set-channel`",
                        color=discord.Color.red()
                    )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return
        
        registered_users = self.db.get_registered_users(interaction.guild.id)
        
        if not registered_users:
            embed = discord.Embed(
                title="📋 Registered Users",
                description="No users are currently registered for rank notifications.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title="📋 Registered Users",
            description="Users registered for rank-up notifications:",
            color=discord.Color.blue()
        )
        
        for user_id_str, data in registered_users.items():
            try:
                user = interaction.guild.get_member(int(user_id_str))
                if user:
                    steam_id = data['steam_id']
                    friend_id = str(int(steam_id) - 76561197960265728)
                    last_mmr = data.get('last_mmr', 0)
                    current_rank = self.rank_tracker.get_rank_name(self.rank_tracker.mmr_to_rank_tier(last_mmr))
                    notifications = "✅" if data.get('notifications_enabled', True) else "❌"
                    
                    embed.add_field(
                        name=f"{user.display_name}",
                        value=f"Friend ID: {friend_id}\nRank: {current_rank}\nNotifications: {notifications}",
                        inline=True
                    )
            except:
                continue
        
        await interaction.response.send_message(embed=embed)

async def setup_commands(bot):
    """Setup function to add commands to the bot"""
    await bot.add_cog(DotaCommands(bot))
