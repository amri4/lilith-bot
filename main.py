import os
import asyncio

from dotenv import load_dotenv
import discord
from discord.ext import commands

import mycord


# =========================================
# LOAD ENVIRONMENT
# =========================================

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN is missing from .env"
    )


# =========================================
# DATABASE
# =========================================

db = mycord.PunksDB()


# =========================================
# BOT
# =========================================

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="Lilith ",
    intents=intents,
    help_command=None
)


# =========================================
# LOAD COGS
# =========================================

async def load_cogs():

    cogs_folder = "cogs"

    if not os.path.exists(cogs_folder):
        print("⚠️ cogs folder not found.")
        return

    for filename in os.listdir(cogs_folder):

        if not filename.endswith(".py"):
            continue

        if filename.startswith("_"):
            continue

        extension = (
            f"{cogs_folder}.{filename[:-3]}"
        )

        try:

            await bot.load_extension(
                extension
            )

            print(
                f"✅ Loaded cog: {filename}"
            )

        except Exception as e:

            print(
                f"❌ Failed to load "
                f"{filename}: {e}"
            )


# =========================================
# BOT READY
# =========================================

@bot.event
async def on_ready():

    print(
        f"🖤 Lilith is online as "
        f"{bot.user} ({bot.user.id})"
    )

    print(
        f"🏠 Connected to "
        f"{len(bot.guilds)} server(s)"
    )


# =========================================
# STARTUP
# =========================================

async def main():

    await load_cogs()

    await bot.start(TOKEN)


# =========================================
# RUN
# =========================================

if __name__ == "__main__":

    try:

        asyncio.run(main())

    except KeyboardInterrupt:

        print(
            "🛑 Lilith stopped."
)
