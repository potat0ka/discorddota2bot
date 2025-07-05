# Dota 2 Bot Setup Guide

## Quick Start

### 1. Setting Up Bot Channel (Admin Only)

To allow the bot to work in your server, an admin needs to set up a channel first:

1. Go to any channel where you want the bot to work
2. Type: `/set-channel`
3. Press Enter

Or specify a different channel:
1. Type: `/set-channel #your-channel-name`
2. Press Enter

The bot will now only respond to commands in that channel.

### 2. Using Player Statistics

Once the channel is set up, anyone can use:
- `/dota 122994714` - Get player stats (replace with your Friend ID)
- `/compare 122994714 384181524` - Compare two players

### 3. Setting Up Rank Notifications

To get notified when you rank up:
1. Type: `/register 122994714` (replace with your Friend ID)
2. The bot will check your rank every 30 minutes
3. You'll get a notification when your rank changes

### 4. Finding Your Friend ID

1. Open Dota 2
2. Go to your Profile
3. Look for "Friend ID" (8-9 digit number)
4. Example: 122994714

### 5. Common Issues

**"Player Not Found" Error:**
- Double-check your Friend ID
- Make sure your Steam profile is public
- Play a match to sync with OpenDota
- Visit opendota.com and login with Steam

**"Wrong Channel" Error:**
- Ask an admin to run `/set-channel` first
- Commands only work in the designated channel

**Bot Not Responding:**
- Make sure the bot has permissions to read/send messages
- Check if the bot is online (green status)

## All Commands

### Player Commands (Everyone)
- `/dota <friend_id>` - Get comprehensive player statistics
- `/compare <friend_id1> <friend_id2>` - Compare two players
- `/help` - Show help information

### Notification Commands (Everyone)
- `/register <friend_id>` - Register for rank notifications
- `/unregister` - Stop rank notifications
- `/list-registered` - See who's registered

### Admin Commands (Admins Only)
- `/set-channel [channel]` - Set allowed channel for bot commands

## Need Help?

If you're still having issues:
1. Check that your Friend ID is correct
2. Make sure your Steam profile is public
3. Try playing a match to sync with OpenDota
4. Ask an admin to set up the channel if needed