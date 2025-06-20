import os
import random
import threading
from twitchio.ext import commands
from http.server import HTTPServer, BaseHTTPRequestHandler
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_OAUTH")
BOT_NICK = os.getenv("BOT_NICK")
CHANNELS = os.getenv("CHANNELS")  # comma separated list of channels

DEFAULT_STEAKS = [
    "juicy ribeye steak",
    "tender sirloin steak",
    "spicy peppercorn steak",
    "well-done T-bone steak",
    "medium-rare flank steak",
    "chargrilled tomahawk steak",
    "bloody raw steak",
    "mystery meat steak",
    "dirty steak",
    "steak with mustard",
    "soggy steak"
]

CUSTOM_STEAKS_FILE = "custom_steaks.txt"

def load_custom_steaks():
    if os.path.exists(CUSTOM_STEAKS_FILE):
        with open(CUSTOM_STEAKS_FILE, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def save_custom_steak(steak):
    with open(CUSTOM_STEAKS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{steak}\n")

class SteakBot(commands.Bot):
    def __init__(self):
        super().__init__(
            token=BOT_TOKEN,
            prefix="!",
            initial_channels=[channel.strip() for channel in CHANNELS.split(",")]
        )

    async def event_ready(self):
        print(f"Bot connected as {self.nick}")
        for channel in self.connected_channels:
            print(f"Connected to channel: {channel.name}")

    async def event_message(self, message):
        # Avoid the bot responding to itself
        if message.echo:
            return
        await self.handle_commands(message)

    @commands.command(name="bettersteak")
    async def steak(self, ctx):
        custom_steaks = load_custom_steaks()
        all_steaks = DEFAULT_STEAKS + custom_steaks
        steak = random.choice(all_steaks)

        parts = ctx.message.content.split()
        if len(parts) > 1:
            mention = parts[1]
            if mention.startswith("@"):
                mention_name = mention
            else:
                mention_name = f"@{mention}"
            await ctx.send(f"@{ctx.author.name} has eaten a {steak} with {mention_name}!")
        else:
            await ctx.send(f"@{ctx.author.name} has eaten a {steak}!")

    @commands.command(name="addsteak")
    async def addsteak(self, ctx):
        # Check if the author is a mod or the channel owner (streamer)
        if not (ctx.author.is_mod or ctx.author.name.lower() == ctx.channel.name.lower()):
            await ctx.send(f"@{ctx.author.name} only the streamer or a mod can add steaks.")
            return

        parts = ctx.message.content.split(" ", 1)
        if len(parts) < 2 or not parts[1].strip():
            await ctx.send("Usage: !addsteak [steak name]")
            return

        steak_name = parts[1].strip()
        save_custom_steak(steak_name)
        await ctx.send(f"Added new steak: {steak_name}")

# HTTP handler for uptime checks
class CustomHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is running")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()

def run_web_server():
    server = HTTPServer(('0.0.0.0', 10000), CustomHandler)
    print("Starting webserver on port 10000")
    server.serve_forever()

# Run web server in a separate thread so it doesn't block the bot
threading.Thread(target=run_web_server, daemon=True).start()

if __name__ == "__main__":
    bot = SteakBot()
    bot.run()

