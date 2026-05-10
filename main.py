import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import shared_db

load_dotenv()
shared_db.init_db()

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=["lilith ", "lilith", "Lilith ", "Lilith"],
    intents=intents,
    help_command=None,
)

EXTENSIONS = [
    "cogs.help_command",
    "cogs.moderation",
]


async def setup_hook():
    for ext in EXTENSIONS:
        try:
            await bot.load_extension(ext)
            print(f"[LILITH] Loaded {ext}")
        except Exception as e:
            print(f"[LILITH] Failed to load {ext}: {e}")

bot.setup_hook = setup_hook


@bot.event
async def on_ready():
    print(f"[LILITH] Online as {bot.user} | Satellite 02 — Evil (Moderation)")
    print(f"[LILITH] DB path: {shared_db.get_db_path()}")
    print(f"[LILITH] Guilds: {len(bot.guilds)}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing argument: `{error.param.name}`. Use `lilith help` for usage.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("Member not found. Mention them directly.")
    else:
        print(f"[LILITH] Error in {ctx.command}: {error}")


bot.run(os.getenv("DISCORD_TOKEN"))
