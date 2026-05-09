import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
import database

load_dotenv()

SIBLING_NAMES = ["Shaka", "Edison", "Pythagoras", "Atlas", "York"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


class LilithBot(commands.Bot):
    async def setup_hook(self):
        database.init_db()
        for ext in ["cogs.help_command", "cogs.evil"]:
            try:
                await self.load_extension(ext)
                print(f"[Lilith] Loaded {ext}")
            except Exception as e:
                print(f"[Lilith] ERROR loading {ext}: {e}")


bot = LilithBot(
    command_prefix=["lilith ", "lilith", "Lilith ", "Lilith"],
    intents=intents,
    help_command=None,
)


@bot.event
async def on_ready():
    print(f"[Lilith] Online as {bot.user} (ID: {bot.user.id})")
    print(f"[Lilith] Prefix: lilith  | Satellite 02 — Evil")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    for name in SIBLING_NAMES:
        if name.lower() in content_lower:
            responses = [
                f"Ha! {name} again? I'm so much more interesting than them.",
                f"{name}? Please. Don't bore me with that name.",
                f"Oh, talking about {name}? I suppose someone has to.",
            ]
            await message.channel.send(random.choice(responses))
            break

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set in .env")
    bot.run(token)
