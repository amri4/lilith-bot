import os
import asyncio

import discord
from discord.ext import commands
from dotenv import load_dotenv


# =========================================
# SETUP
# =========================================

load_dotenv()


intents = discord.Intents.default()

intents.message_content = True
intents.members = True


bot = commands.Bot(
    command_prefix="Lilith ",
    help_command=None,
    intents=intents
)


# =========================================
# LOAD COGS
# =========================================

async def load_extensions():

    print("📂 Lilith: Scanning for cogs...")

    folder = "./lilith/cogs"

    if not os.path.exists(folder):

        print("⚠️ Lilith: No 'cogs' folder found.")

        return

    for filename in os.listdir(folder):

        if (
            filename.endswith(".py")
            and not filename.startswith("__")
        ):

            try:

                await bot.load_extension(
                    f"lilith.cogs.{filename[:-3]}"
                )

                print(
                    f"  └─ Loaded cog: {filename}"
                )

            except Exception as e:

                print(
                    f"  ❌ Failed to load "
                    f"{filename}: {e}"
                )


# =========================================
# READY
# =========================================

@bot.event
async def on_ready():

    print(
        f"🤖 Success! Logged in as "
        f"{bot.user.name}"
    )

    print(
        "⚡ Lilith is online and listening."
    )


# =========================================
# MAIN
# =========================================

async def main():

    await load_extensions()

    token = os.getenv("LILITH_TOKEN")

    if not token:

        print(
            "❌ CRITICAL ERROR: "
            "'LILITH_TOKEN' is missing!"
        )

        return

    await bot.start(token)


asyncio.run(main())
