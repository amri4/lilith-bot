import discord
from discord.ext import commands

COMMANDS_DATA = {
    "🔒 Moderation": {
        "lilith kick @user [reason]": "Kick a member. (Kick Members permission required)",
        "lilith ban @user [reason]": "Ban a member. (Ban Members permission required)",
        "lilith unban <user_id>": "Unban a user by ID. (Ban Members required)",
        "lilith warn @user <reason>": "Issue a warning. Logged in SHAKA database.",
        "lilith warnings @user": "View all warnings for a user.",
        "lilith clearwarnings @user": "Clear all warnings for a user. (Admin only)",
        "lilith mute @user <duration> [reason]": "Timeout a member. Duration: 10m, 1h, 2d.",
        "lilith unmute @user": "Remove a timeout from a member.",
        "lilith clear <amount>": "Delete up to 100 messages from this channel.",
    },
    "🤖 Satellite Info": {
        "lilith siblings": "List all six Vegapunk satellites and their roles.",
    },
    "❓ Help": {
        "lilith help": "Show this help menu.",
    },
}


class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=category, description=f"{len(cmds)} command(s)")
            for category, cmds in COMMANDS_DATA.items()
        ]
        super().__init__(placeholder="Select a command category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        cmds = COMMANDS_DATA[category]
        embed = discord.Embed(
            title=f"🔒 Lilith — {category}",
            color=discord.Color.red(),
        )
        for name, desc in cmds.items():
            embed.add_field(name=f"`{name}`", value=desc, inline=False)
        embed.set_footer(text="Satellite 02 — Lilith (Evil) | Moderation | Prefix: lilith")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CategorySelect())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["?"])
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🔒 LILITH — Satellite 02 (Evil)",
            description=(
                "Hi, I'm Lilith. I handle levels, welcome members, and enforcement.\n"
                "Moderation tools, warnings, timeouts — all logged through SHAKA.\n\n"
                "**Prefix:** `lilith`\n"
                "⚠️ Most commands require Manage Messages or higher."
            ),
            color=discord.Color.red(),
        )
        embed.set_footer(text="Select a category below to view commands.")
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
