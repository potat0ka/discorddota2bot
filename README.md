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

## Deployment

### Docker Setup

The easiest way to deploy this bot is using Docker. This ensures consistent behavior across all environments.

#### Prerequisites
- Docker installed on your system
- Discord bot token from Discord Developer Portal

#### Step 1: Create Environment File

Create a `.env` file in your project directory with your Discord bot token:

```bash
# Create .env file
touch .env
```

Add your Discord bot token to the `.env` file:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

**Important:** Never commit your `.env` file to version control. Keep your bot token secure.

#### Step 2: Create Dockerfile

Create a `Dockerfile` in your project root:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for keep-alive server
EXPOSE 5000

# Run the bot
CMD ["python", "main.py"]
```

#### Step 3: Create Requirements File

Create a `requirements.txt` file with the following dependencies:

```txt
discord.py==2.5.2
aiohttp==3.12.13
python-dotenv==1.1.1
flask==3.1.1
```

**Note:** If you already have these packages installed (such as in a Replit environment), you can skip this step and modify the Dockerfile to install packages directly:

```dockerfile
# Alternative: Install packages directly in Dockerfile
RUN pip install --no-cache-dir discord.py==2.5.2 aiohttp==3.12.13 python-dotenv==1.1.1 flask==3.1.1
```

#### Step 4: Build and Run

Build the Docker image:

```bash
docker build -t dota2-stats-bot .
```

Run the container:

```bash
docker run -d \
  --name dota2-bot \
  --env-file .env \
  -p 5000:5000 \
  --restart unless-stopped \
  dota2-stats-bot
```

#### Step 5: Verify Deployment

Check if the bot is running:

```bash
# View container logs
docker logs dota2-bot

# Check container status
docker ps

# Access the web interface
curl http://localhost:5000
```

You should see the bot connect to Discord and the web server start on port 5000.

#### Docker Management Commands

```bash
# Stop the bot
docker stop dota2-bot

# Start the bot
docker start dota2-bot

# Restart the bot
docker restart dota2-bot

# Remove the container
docker rm dota2-bot

# View real-time logs
docker logs -f dota2-bot
```

#### Production Considerations

For production deployment, consider:
- Using Docker Compose for easier management
- Setting up proper logging and monitoring
- Using a reverse proxy (nginx) for the web interface
- Implementing health checks and auto-restart policies

