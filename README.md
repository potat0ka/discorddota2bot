# Dota 2 Statistics Discord Bot

A comprehensive Discord bot for fetching and displaying Dota 2 player statistics using the OpenDota API. Features slash commands, player comparisons, hero streak detection, and 24/7 hosting capabilities.

## Features

- 🎮 **Comprehensive Player Stats**: Get detailed statistics for any Dota 2 player
- ⚔️ **Player Comparison**: Compare two players side-by-side
- 🔥 **Hero Streak Detection**: Identify consecutive matches with the same hero
- 📊 **Rich Discord Embeds**: Beautiful, formatted displays with emojis
- 🎯 **Role Suggestions**: Get recommendations based on play patterns
- 📈 **Recent Performance**: Visual win/loss patterns
- 🔒 **Private Profile Handling**: Graceful handling of private profiles
- 🌐 **24/7 Hosting**: Built-in keep-alive system for continuous operation

## Commands

### `/dota <friend_id>`
Get comprehensive statistics for a player including:
- First match ever played
- Today's first match (if any)
- Total matches and win rate
- Last 10 matches visualization
- Most successful hero
- Average GPM, XPM, and KDA
- Suggested best role
- Hero streaks

### `/compare <friend_id1> <friend_id2>`
Compare two players with:
- Win rates and total matches
- Recent performance patterns
- Average statistics
- Most successful heroes

### `/help`
Show detailed help information and usage examples

## Installation

### Prerequisites
- Python 3.8 or higher
- Discord bot token
- Internet connection

### Local Setup

1. **Clone or download the project files**

2. **Install dependencies**:
   ```bash
   pip install discord.py aiohttp python-dotenv flask
   ```

3. **Set up environment variables**:
   - Copy `.env.example` to `.env`
   - Add your Discord bot token

4. **Run the bot**:
   ```bash
   python main.py
   ```

### Deployment Options

#### Option 1: Replit (Recommended for beginners)
1. Create a new Repl on Replit
2. Upload all project files
3. Set `DISCORD_TOKEN` in Replit Secrets
4. Run the project
5. Use the provided URL with UptimeRobot for 24/7 hosting

#### Option 2: VPS/Cloud Server
1. Upload files to your server
2. Install dependencies
3. Set environment variables
4. Run with a process manager like `systemd` or `pm2`

#### Option 3: Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip install discord.py aiohttp python-dotenv flask
CMD ["python", "main.py"]
