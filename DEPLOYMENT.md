# Deployment Guide - Dota 2 Statistics Discord Bot

This guide will walk you through setting up and deploying your Dota 2 statistics Discord bot for 24/7 operation.

## Table of Contents

1. [Creating a Discord Bot](#creating-a-discord-bot)
2. [Setting Up the Bot](#setting-up-the-bot)
3. [Inviting the Bot to Your Server](#inviting-the-bot-to-your-server)
4. [Deployment Options](#deployment-options)
5. [24/7 Hosting Setup](#247-hosting-setup)
6. [UptimeRobot Configuration](#uptimerobot-configuration)
7. [Troubleshooting](#troubleshooting)

## Creating a Discord Bot

### Step 1: Discord Developer Portal

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Enter a name for your bot (e.g., "Dota 2 Stats Bot")
4. Click "Create"

### Step 2: Bot Configuration

1. Navigate to the "Bot" section in the left sidebar
2. Click "Add Bot"
3. Confirm by clicking "Yes, do it!"
4. Under "Token", click "Copy" to copy your bot token
5. **Important**: Keep this token secret and never share it publicly

### Step 3: Bot Permissions

1. In the "Bot" section, scroll down to "Privileged Gateway Intents"
2. Enable "Message Content Intent" (required for some features)
3. Save changes

## Setting Up the Bot

### Option A: Replit (Easiest for beginners)

1. **Create a Replit Account**: Go to [Replit.com](https://replit.com) and sign up
2. **Create a New Repl**: Click "Create Repl" and select "Python"
3. **Upload Files**: Upload all bot files to your Repl
4. **Set Environment Variables**:
   - Click on "Secrets" (lock icon) in the left sidebar
   - Add a new secret with key `DISCORD_TOKEN` and your bot token as the value
5. **Install Dependencies**: Replit will automatically install required packages
6. **Run the Bot**: Click the "Run" button

### Option B: Local Development

1. **Clone/Download Files**: Get all the bot files on your local machine
2. **Install Python**: Make sure you have Python 3.8+ installed
3. **Install Dependencies**:
   ```bash
   pip install discord.py aiohttp python-dotenv flask
   ```
4. **Set Environment Variables**:
   - Copy `.env.example` to `.env`
   - Edit `.env` and add your Discord token:
     ```
     DISCORD_TOKEN=your_actual_bot_token_here
     ```
5. **Run the Bot**:
   ```bash
   python main.py
   ```

## Inviting the Bot to Your Server

### Step 1: Generate Invite Link

1. Go back to Discord Developer Portal
2. Navigate to "OAuth2" → "URL Generator"
3. Select scopes:
   - ✅ `bot`
   - ✅ `applications.commands`
4. Select bot permissions:
   - ✅ `Send Messages`
   - ✅ `Use Slash Commands`
   - ✅ `Embed Links`
   - ✅ `Read Message History`
5. Copy the generated URL at the bottom

### Step 2: Invite to Server

1. Open the generated URL in your browser
2. Select the server you want to add the bot to
3. Click "Authorize"
4. Complete the CAPTCHA if prompted

### Step 3: Test the Bot

1. Go to your Discord server
2. Type `/dota` to see if the command appears
3. Try `/help` to see all available commands

## Deployment Options

### Option 1: Replit (Recommended for beginners)

**Pros:**
- Free tier available
- Easy to set up
- Web-based editor
- Automatic dependency management

**Cons:**
- Limited resources on free tier
- May sleep after inactivity (requires keep-alive)

**Setup:**
1. Follow the Replit setup instructions above
2. The bot includes a built-in web server for keep-alive
3. Use UptimeRobot to ping your Repl URL

### Option 2: Heroku

**Pros:**
- Free tier available
- Good for production
- Easy deployment with Git

**Cons:**
- Requires credit card for verification
- Free dyno hours are limited

**Setup:**
1. Create a Heroku account
2. Install Heroku CLI
3. Create a new app
4. Deploy using Git
5. Set environment variables in Heroku dashboard

### Option 3: VPS/Cloud Server

**Pros:**
- Full control
- Better performance
- 24/7 uptime

**Cons:**
- Requires server management knowledge
- Usually costs money

**Setup:**
1. Get a VPS (DigitalOcean, AWS, etc.)
2. Upload bot files
3. Install dependencies
4. Set up process manager (systemd, pm2)
5. Configure firewall

## 24/7 Hosting Setup

### Using the Built-in Keep-Alive System

The bot includes a `keep_alive.py` file that runs a web server to prevent the bot from sleeping.

**How it works:**
1. Flask web server runs on port 5000
2. Provides a status page and health checks
3. External monitoring service pings the URL
4. Keeps the hosting service active

**Configuration:**
- No additional setup required
- Web server starts automatically when bot runs
- Access your bot's URL to see the status page

### Environment Variables Setup

**For Replit:**
1. Click on "Secrets" in the left sidebar
2. Add key-value pairs:
   - Key: `DISCORD_TOKEN`
   - Value: Your bot token

**For other platforms:**
1. Set environment variables in your hosting platform
2. Or use a `.env` file with the same format

## UptimeRobot Configuration

UptimeRobot is a free service that monitors your bot and keeps it alive by pinging it regularly.

### Step 1: Create UptimeRobot Account

1. Go to [UptimeRobot.com](https://uptimerobot.com)
2. Sign up for a free account
3. Verify your email

### Step 2: Add Monitor

1. Click "Add New Monitor"
2. Select "HTTP(s)" monitor type
3. Enter details:
   - **Friendly Name**: "Dota 2 Bot"
   - **URL**: Your bot's URL (e.g., `https://your-repl-name.username.repl.co`)
   - **Monitoring Interval**: 5 minutes
4. Click "Create Monitor"

### Step 3: Get Your Bot URL

**For Replit:**
1. Run your bot
2. A web preview will appear
3. Copy the URL from the address bar
4. Use this URL in UptimeRobot

**For other platforms:**
- Use your app's public URL
- Make sure port 5000 is accessible

### Step 4: Verify Setup

1. Check that UptimeRobot shows "Up" status
2. Visit your bot's URL to see the status page
3. Test Discord commands to ensure bot is responding

## Troubleshooting

### Common Issues

#### Bot Token Issues
- **Problem**: Bot doesn't start or gives authentication error
- **Solution**: Double-check your bot token is correct and properly set

#### Permission Issues
- **Problem**: Bot can't send messages or use slash commands
- **Solution**: Check bot permissions in Discord server settings

#### Commands Not Appearing
- **Problem**: Slash commands don't show up
- **Solution**: Wait a few minutes for commands to sync, or restart the bot

#### Web Server Issues
- **Problem**: UptimeRobot shows "Down" status
- **Solution**: Check that port 5000 is accessible and Flask server is running

#### Private Profile Errors
- **Problem**: All players show as private
- **Solution**: Players must make their profiles public on OpenDota

### Debug Mode

Enable debug logging by setting `DEBUG=True` in your environment variables.

### Getting Help

1. Check the bot's status page
2. Review Discord Developer Portal for any issues
3. Check UptimeRobot monitoring status
4. Look at console logs for error messages

## Advanced Configuration

### Custom Prefixes

You can customize the bot by modifying the configuration in `main.py`:

```python
# Change command prefix
command_prefix='!'

# Change bot status
activity=discord.Game(name="Your custom status")
