"""
Flask web server to keep the bot alive for 24/7 hosting
"""

from flask import Flask, render_template_string
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML template for the status page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Dota 2 Stats Bot</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin: 0;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            text-align: center;
            background: rgba(255, 255, 255, 0.1);
            padding: 30px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        }
        .status {
            font-size: 24px;
            margin: 20px 0;
        }
        .emoji {
            font-size: 48px;
            margin: 20px 0;
        }
        .info {
            margin: 15px 0;
            font-size: 18px;
        }
        .footer {
            margin-top: 30px;
            font-size: 14px;
            opacity: 0.8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">🎮</div>
        <h1>Dota 2 Statistics Bot</h1>
        <div class="status">🟢 Bot is online and running!</div>
        <div class="info">
            <p><strong>Features:</strong></p>
            <ul style="text-align: left; display: inline-block;">
                <li>📊 Comprehensive player statistics</li>
                <li>⚔️ Player comparison</li>
                <li>🔥 Hero streak detection</li>
                <li>🎯 Role suggestions</li>
                <li>📈 Recent match performance</li>
            </ul>
        </div>
        <div class="info">
            <p><strong>Commands:</strong></p>
            <p><code>/dota &lt;friend_id&gt;</code> - Get player stats</p>
            <p><code>/compare &lt;friend_id1&gt; &lt;friend_id2&gt;</code> - Compare players</p>
            <p><code>/help</code> - Show help information</p>
        </div>
        <div class="footer">
            <p>This page keeps the bot alive for 24/7 hosting.</p>
            <p>Add this URL to UptimeRobot to maintain uptime.</p>
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    """Main status page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {
        'status': 'healthy',
        'service': 'dota2-stats-bot',
        'uptime': True
    }

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return 'pong'

def run_server():
    """Run the Flask server"""
    try:
        app.run(host='0.0.0.0', port=5000, debug=False)
    except Exception as e:
        logger.error(f"Failed to start web server: {e}")

def keep_alive():
    """Start the web server in a separate thread"""
    logger.info("Starting keep-alive web server...")
    server_thread = threading.Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    logger.info("Keep-alive server started on port 5000")

if __name__ == "__main__":
    keep_alive()
