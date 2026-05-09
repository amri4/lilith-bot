import random
import discord
from discord.ext import commands
import database

TAUNTS = [
    "You call yourself a threat? I've seen sea kings more intimidating.",
    "Aww, did I hurt your feelings? Good.",
    "You're not even worth a bounty. That's how pathetic you are.",
    "Shaka would lecture you. I'll just laugh at you. Ha!",
    "The difference between us is that I know exactly how worthless you are.",
    "Don't look at me like that. It makes you look even more pitiful.",
    "I'd steal your dignity, but it seems someone already took it.",
    "Hah! Even Stella would be embarrassed to be seen with you.",
    "You? A problem? Please. You're barely an inconvenience.",
    "Better run before I get bored enough to actually try.",
]

SIBLINGS = [
    ("Shaka", "01", "Good", "shaka"),
    ("Lilith", "02", "Evil", "lilith"),
    ("Edison", "03", "Thinker", "edison"),
    ("Pythagoras", "04", "Wisdom", "py"),
    ("Atlas", "05", "Violence", "atlas"),
    ("York", "06", "Greed", "york"),
]


class EvilCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="steal")
    async def steal(self, ctx, member: discord.Member):
        if member.id == ctx.author.id:
            await ctx.send("I can't steal from myself. That would be pointless.")
            return
        if member.bot:
            await ctx.send("Steal from a bot? There's nothing worth taking there.")
            return
        amount = random.randint(10, 500)
        database.add_steal(ctx.guild.id, ctx.author.id, member.id, amount)
        embed = discord.Embed(
            title="💀 Theft Successful",
            description=f"I relieved {member.mention} of **{amount} gems**. Too easy.",
            color=discord.Color.red(),
        )
        embed.set_footer(text="Satellite 02 — Lilith (Evil)")
        await ctx.send(embed=embed)

    @commands.command(name="hoard")
    async def hoard(self, ctx):
        total = database.get_hoard(ctx.guild.id, ctx.author.id)
        top = database.get_total_stolen(ctx.guild.id)
        embed = discord.Embed(
            title="💎 Stolen Goods — Server Leaderboard",
            color=discord.Color.red(),
        )
        embed.add_field(name="Your total gems stolen", value=f"**{total}**", inline=False)
        if top:
            board = "\n".join(
                [f"{i+1}. <@{r[0]}> — **{r[1]} gems**" for i, r in enumerate(top)]
            )
            embed.add_field(name="Top thieves", value=board, inline=False)
        embed.set_footer(text="Satellite 02 — Lilith (Evil)")
        await ctx.send(embed=embed)

    @commands.command(name="bounty")
    async def bounty(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("A bounty must be greater than 0. Don't waste my time.")
            return
        if member.id == ctx.author.id:
            await ctx.send("Putting a bounty on yourself? Interesting strategy. No.")
            return
        database.add_bounty(ctx.guild.id, ctx.author.id, member.id, amount)
        embed = discord.Embed(
            title="🎯 Bounty Posted",
            description=f"A bounty of **{amount} gems** has been placed on {member.mention}.",
            color=discord.Color.dark_red(),
        )
        embed.set_footer(text="Posted by Lilith | Satellite 02")
        await ctx.send(embed=embed)

    @commands.command(name="bounties")
    async def bounties(self, ctx):
        rows = database.get_active_bounties(ctx.guild.id)
        if not rows:
            await ctx.send("No active bounties. How boring.")
            return
        embed = discord.Embed(
            title="🎯 Active Bounties",
            color=discord.Color.dark_red(),
        )
        for row in rows:
            b_id, poster_id, target_id, amount, timestamp = row
            embed.add_field(
                name=f"#{b_id} — {amount} gems",
                value=f"**Target:** <@{target_id}>\n**Posted by:** <@{poster_id}>\n**Date:** {timestamp[:10]}",
                inline=False,
            )
        embed.set_footer(text="Satellite 02 — Lilith (Evil)")
        await ctx.send(embed=embed)

    @commands.command(name="taunt")
    async def taunt(self, ctx, member: discord.Member):
        taunt = random.choice(TAUNTS)
        embed = discord.Embed(
            title=f"💀 Lilith taunts {member.display_name}",
            description=f"{member.mention} — *\"{taunt}\"*",
            color=discord.Color.red(),
        )
        embed.set_footer(text="Satellite 02 — Lilith (Evil)")
        await ctx.send(embed=embed)

    @commands.command(name="siblings")
    async def siblings(self, ctx):
        embed = discord.Embed(
            title="🤖 The Six Vegapunk Satellites",
            description="We share the same origin. That doesn't mean I like any of them.",
            color=discord.Color.red(),
        )
        for name, number, trait, prefix in SIBLINGS:
            marker = " ← you are here" if name == "Lilith" else ""
            embed.add_field(
                name=f"Satellite {number} — {name} ({trait}){marker}",
                value=f"Prefix: `{prefix}`",
                inline=False,
            )
        await ctx.send(embed=embed)

    @steal.error
    async def steal_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `lilith steal @user`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Can't find that user. Pick a real target.")

    @bounty.error
    async def bounty_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `lilith bounty @user <amount>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("The amount must be a number.")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I can't place a bounty on someone who doesn't exist.")

    @taunt.error
    async def taunt_error(self, ctx, error):
        if isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
            await ctx.send("Usage: `lilith taunt @user`")


async def setup(bot):
    await bot.add_cog(EvilCog(bot))
