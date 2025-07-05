# Dota 2 Statistics Discord Bot

## Overview

This repository contains a comprehensive Discord bot for fetching and displaying Dota 2 player statistics using the OpenDota API. The bot is built with Python and discord.py, featuring slash commands, player comparisons, hero streak detection, and 24/7 hosting capabilities through a Flask web server.

## System Architecture

### Backend Architecture
- **Framework**: Python-based Discord bot using discord.py library
- **API Integration**: OpenDota API client for fetching Dota 2 statistics
- **Web Server**: Flask-based keep-alive server for continuous operation
- **Architecture Pattern**: Modular design with separate components for commands, data processing, and embeds

### Key Design Decisions
- **Asynchronous Programming**: Uses async/await patterns for efficient API calls and Discord interactions
- **Modular Structure**: Separated concerns into different modules (commands, API client, data processor, embeds)
- **Error Handling**: Comprehensive error handling for API failures and invalid inputs
- **24/7 Hosting**: Built-in Flask server to prevent hosting platforms from sleeping the application

## Key Components

### 1. Main Bot (`main.py`)
- **Purpose**: Entry point and bot initialization
- **Features**: Sets up Discord intents, command syncing, and logging
- **Architecture**: Extends discord.py's Bot class with custom setup hooks

### 2. API Client (`bot/api_client.py`)
- **Purpose**: Handles all OpenDota API interactions
- **Features**: Async HTTP requests, session management, error handling
- **Design**: Singleton-like session management for connection reuse

### 3. Command Handler (`bot/commands.py`)
- **Purpose**: Implements Discord slash commands
- **Commands**: `/dota`, `/compare`, `/help`
- **Features**: Input validation, comprehensive error handling, user-friendly responses

### 4. Data Processor (`bot/data_processor.py`)
- **Purpose**: Processes and analyzes raw Dota 2 statistics
- **Features**: Win/loss pattern analysis, hero streak detection, role suggestions
- **Architecture**: Stateless processing with helper methods for different analysis types

### 5. Embed Builder (`bot/embeds.py`)
- **Purpose**: Creates rich Discord embeds for displaying statistics
- **Features**: Hero name mapping, formatted statistics display, visual indicators
- **Design**: Template-based approach for consistent formatting

### 6. Keep-Alive Server (`keep_alive.py`)
- **Purpose**: Maintains bot uptime on hosting platforms
- **Features**: Flask web server, status page, health monitoring
- **Architecture**: Threaded execution to run alongside Discord bot

## Data Flow

1. **Command Reception**: User invokes slash command in Discord
2. **Input Validation**: Command handler validates Friend ID format
3. **ID Conversion**: 32-bit Friend ID converted to 64-bit Steam ID
4. **API Request**: OpenDota API client fetches player data and match history
5. **Data Processing**: Raw data processed into meaningful statistics
6. **Embed Creation**: Statistics formatted into Discord embeds
7. **Response**: Formatted embed sent back to Discord channel

## External Dependencies

### APIs
- **OpenDota API**: Primary data source for Dota 2 statistics
  - Base URL: `https://api.opendota.com/api`
  - No authentication required
  - Rate limiting handled through request delays

### Python Libraries
- **discord.py**: Discord API interaction
- **aiohttp**: Async HTTP requests
- **flask**: Web server for keep-alive functionality
- **python-dotenv**: Environment variable management

### Environment Variables
- **DISCORD_TOKEN**: Bot authentication token (required)
- **PORT**: Web server port (optional, defaults to Flask default)

## Deployment Strategy

### Supported Platforms
- **Replit**: Primary deployment target with built-in environment
- **Heroku**: Alternative cloud platform
- **Local Development**: Direct Python execution

### Keep-Alive Mechanism
- Flask web server runs on separate thread
- Status page accessible via HTTP
- Prevents hosting platform sleep/hibernation
- UptimeRobot integration for external monitoring

### Configuration Requirements
- Discord bot token stored as environment variable
- Bot permissions: Send Messages, Use Slash Commands, Embed Links
- Python 3.8+ runtime environment

## Changelog
- July 05, 2025. Initial setup
- July 05, 2025. Added Docker deployment section to README.md with comprehensive instructions

## User Preferences

Preferred communication style: Simple, everyday language.