"""
Dota 2 Statistics Discord Bot
A comprehensive bot for fetching and displaying Dota 2 player statistics
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
from keep_alive import keep_alive
from bot.commands import setup_commands
from bot.database import SimpleDB
from bot.rank_tracker import RankTracker
from bot.api_client import OpenDotaClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DotaBot(commands.Bot):
    """Main bot class"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        
        super().__init__(
            command_prefix='!',
            intents=intents,
            help_command=None
        )
        
        self.db = SimpleDB()
        self.api_client = OpenDotaClient()
        self.rank_tracker = RankTracker(self.db, self.api_client)
    
    @tasks.loop(minutes=30)  # Check every 30 minutes
    async def check_rank_changes(self):
        """Background task to check for rank changes"""
        try:
            logger.info("Checking for rank changes...")
            
            for guild in self.guilds:
                try:
                    # Get allowed channel for notifications
                    allowed_channel_id = self.db.get_allowed_channel(guild.id)
                    if not allowed_channel_id:
                        continue
                    
                    notification_channel = guild.get_channel(allowed_channel_id)
                    if not notification_channel:
                        continue
                    
                    # Check for rank changes
                    rank_changes = await self.rank_tracker.check_rank_changes(guild.id)
                    
                    for user_id, steam_id, old_mmr, new_mmr in rank_changes:
                        try:
                            message = self.rank_tracker.get_rank_change_message(user_id, old_mmr, new_mmr)
                            
                            embed = discord.Embed(
                                title="🎮 Rank Change Detected!",
                                description=message,
                                color=discord.Color.gold() if new_mmr > old_mmr else discord.Color.orange()
                            )
                            
                            await notification_channel.send(embed=embed)
                            logger.info(f"Sent rank change notification for user {user_id} in guild {guild.id}")
                            
                        except Exception as e:
                            logger.error(f"Error sending rank notification: {e}")
                        
                        # Add small delay to avoid rate limiting
                        await asyncio.sleep(1)
                
                except Exception as e:
                    logger.error(f"Error checking rank changes for guild {guild.id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in rank checking task: {e}")
    
    @check_rank_changes.before_loop
    async def before_rank_check(self):
        """Wait until bot is ready before starting rank checks"""
        await self.wait_until_ready()
        logger.info("Starting rank change monitoring...")
    
    async def setup_hook(self):
        """Setup hook called when bot is starting"""
        logger.info("Setting up bot commands...")
        await setup_commands(self)
        
        # Sync commands globally
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot status
        await self.change_presence(
            activity=discord.Game(name="Dota 2 Statistics | /dota")
        )
        
        # Start rank checking task
        if not self.check_rank_changes.is_running():
            self.check_rank_changes.start()
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        logger.error(f"Command error: {error}")
        if isinstance(error, commands.CommandNotFound):
            return
        
        embed = discord.Embed(
            title="❌ Error",
            description=f"An error occurred: {str(error)}",
            color=discord.Color.red()
        )
        
        try:
            await ctx.send(embed=embed)
        except:
            pass

def main():
    """Main function to run the bot"""
    # Get Discord token from environment variables
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error("Please set your Discord bot token in the .env file or environment variables")
        return
    
    # Start keep-alive server for 24/7 hosting
    keep_alive()
    
    # Create and run bot
    bot = DotaBot()
    
    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid Discord token provided!")
    except Exception as e:
        logger.error(f"Failed to run bot: {e}")

if __name__ == "__main__":
    main()
