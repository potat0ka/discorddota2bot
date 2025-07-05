"""
Dota 2 Statistics Discord Bot
A comprehensive bot for fetching and displaying Dota 2 player statistics
"""

import os
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands
from keep_alive import keep_alive
from bot.commands import setup_commands

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
