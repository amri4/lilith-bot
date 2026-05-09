import discord
from discord.ext import commands

COMMANDS_DATA = {
    "💀 Evil Schemes": {
        "lilith steal @user": "Steal a random amount of gems from a user. Tracked in the database.",
        "lilith hoard": "Show the total gems Lilith has stolen in this server.",
        "lilith bounty @user <amount>": "Place a bounty on someone's head.",
        "lilith bounties": "Show all active bounties in this server.",
        "lilith taunt @user": "Unleash a devastating taunt on a user.",
        "lilith siblings": "List all six Vegapunk satellites.",
    },
    "❓ Help": {
        "lilith?": "Show this help menu.",
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
            title=f"Lilith — {category}",
            color=discord.Color.red(),
        )
        for name, desc in cmds.items():
            embed.add_field(name=f"`{name}`", value=desc, inline=False)
        embed.set_footer(text="Satellite 02 — Lilith (Evil) | Prefix: lilith")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CategorySelect())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="?")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="💀 Lilith — Satellite 02 (Evil)",
            description=(
                "Heh. You need *help*? How pathetic.\n"
                "Fine. Pick a category and I'll show you what I can do.\n\n"
                "**Prefix:** `lilith`"
            ),
            color=discord.Color.red(),
        )
        embed.set_footer(text="Use the menu below to explore commands.")
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
