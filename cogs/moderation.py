import discord
from discord.ext import commands
from datetime import timedelta
import re
import shared_db


def parse_duration(duration_str: str) -> timedelta | None:
    match = re.fullmatch(r"(\d+)([smhd])", duration_str.lower())
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    return {"s": timedelta(seconds=value), "m": timedelta(minutes=value), "h": timedelta(hours=value), "d": timedelta(days=value)}.get(unit)


class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author:
            await ctx.send("You cannot kick yourself.")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot kick someone with an equal or higher role.")
            return
        try:
            await member.send(f"You have been kicked from **{ctx.guild.name}**.\nReason: {reason}")
        except Exception:
            pass
        await member.kick(reason=reason)
        embed = discord.Embed(title="🔒 Member Kicked", color=discord.Color.red())
        embed.add_field(name="Member", value=f"{member} (`{member.id}`)", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.set_footer(text="Satellite 02 — Lilith (Moderation)")
        await ctx.send(embed=embed)

    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        if member == ctx.author:
            await ctx.send("You cannot ban yourself.")
            return
        if member.top_role >= ctx.author.top_role:
            await ctx.send("You cannot ban someone with an equal or higher role.")
            return
        try:
            await member.send(f"You have been banned from **{ctx.guild.name}**.\nReason: {reason}")
        except Exception:
            pass
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔒 Member Banned", color=discord.Color.dark_red())
        embed.add_field(name="Member", value=f"{member} (`{member.id}`)", inline=False)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.set_footer(text="Satellite 02 — Lilith (Moderation)")
        await ctx.send(embed=embed)

    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user} (`{user_id}`) has been unbanned.")
        except discord.NotFound:
            await ctx.send(f"No ban found for user ID `{user_id}`.")

    @commands.command(name="warn")
    @commands.has_permissions(manage_messages=True)
    async def warn(self, ctx, member: discord.Member, *, reason: str):
        if member == ctx.author:
            await ctx.send("You cannot warn yourself.")
            return
        shared_db.add_warning(ctx.guild.id, member.id, ctx.author.id, reason)
        warnings = shared_db.get_warnings(member.id, ctx.guild.id)
        try:
            await member.send(f"⚠️ You have received a warning in **{ctx.guild.name}**.\nReason: {reason}\nTotal warnings: {len(warnings)}")
        except Exception:
            pass
        embed = discord.Embed(title="⚠️ Warning Issued", color=discord.Color.yellow())
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Total Warnings", value=str(len(warnings)), inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.set_footer(text="Satellite 02 — Lilith (Moderation) | Logged in SHAKA")
        await ctx.send(embed=embed)

    @commands.command(name="warnings")
    @commands.has_permissions(manage_messages=True)
    async def warnings(self, ctx, member: discord.Member):
        rows = shared_db.get_warnings(member.id, ctx.guild.id)
        embed = discord.Embed(
            title=f"⚠️ Warnings — {member.display_name}",
            color=discord.Color.yellow(),
        )
        if not rows:
            embed.description = "This user has no warnings."
        else:
            for warn_id, mod_id, reason, ts in rows:
                embed.add_field(
                    name=f"#{warn_id} — {ts[:10]}",
                    value=f"**Reason:** {reason}\n**Moderator:** <@{mod_id}>",
                    inline=False,
                )
        embed.set_footer(text="Satellite 02 — Lilith | Data from SHAKA")
        await ctx.send(embed=embed)

    @commands.command(name="clearwarnings")
    @commands.has_permissions(administrator=True)
    async def clearwarnings(self, ctx, member: discord.Member):
        shared_db.clear_warnings(member.id, ctx.guild.id)
        await ctx.send(f"✅ All warnings cleared for {member.mention}.")

    @commands.command(name="mute")
    @commands.has_permissions(moderate_members=True)
    async def mute(self, ctx, member: discord.Member, duration: str, *, reason: str = "No reason provided"):
        delta = parse_duration(duration)
        if not delta:
            await ctx.send("Invalid duration. Use formats like `10m`, `1h`, `2d`, `30s`.")
            return
        if member == ctx.author:
            await ctx.send("You cannot mute yourself.")
            return
        await member.timeout(delta, reason=reason)
        embed = discord.Embed(title="🔇 Member Muted (Timeout)", color=discord.Color.orange())
        embed.add_field(name="Member", value=member.mention, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)
        embed.add_field(name="Reason", value=reason, inline=False)
        embed.add_field(name="Moderator", value=ctx.author.mention, inline=False)
        embed.set_footer(text="Satellite 02 — Lilith (Moderation)")
        await ctx.send(embed=embed)

    @commands.command(name="unmute")
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(None)
        await ctx.send(f"✅ {member.mention}'s timeout has been removed.")

    @commands.command(name="clear")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            await ctx.send("Amount must be between 1 and 100.")
            return
        deleted = await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title="🔒 Messages Cleared",
            description=f"Deleted **{len(deleted) - 1}** messages.",
            color=discord.Color.red(),
        )
        embed.set_footer(text="Satellite 02 — Lilith (Moderation)")
        msg = await ctx.send(embed=embed)
        await msg.delete(delay=5)

    @commands.command(name="siblings")
    async def siblings(self, ctx):
        embed = discord.Embed(
            title="🤖 The Six Vegapunk Satellites",
            description="I'm Lilith. I keep the others in line.",
            color=discord.Color.red(),
        )
        data = [
            ("Shaka", "01", "Central Brain / Database", "shaka"),
            ("Lilith", "02", "Moderation", "lilith"),
            ("Edison", "03", "Analysis & Strategy", "edison"),
            ("Pythagoras", "04", "Knowledge & Trivia", "py"),
            ("Atlas", "05", "Economy & Utility", "atlas"),
            ("York", "06", "Hunger & Trust", "york"),
        ]
        for name, num, role, prefix in data:
            marker = " ← you are here" if name == "Lilith" else ""
            embed.add_field(name=f"Satellite {num} — {name}{marker}", value=f"Role: {role} | Prefix: `{prefix}`", inline=False)
        await ctx.send(embed=embed)

    @kick.error
    async def kick_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to kick members.")
        elif isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
            await ctx.send("Usage: `lilith kick @user [reason]`")

    @ban.error
    async def ban_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to ban members.")
        elif isinstance(error, (commands.MissingRequiredArgument, commands.MemberNotFound)):
            await ctx.send("Usage: `lilith ban @user [reason]`")

    @warn.error
    async def warn_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You don't have permission to warn members.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `lilith warn @user <reason>`")

    @mute.error
    async def mute_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `lilith mute @user <duration> [reason]` — e.g. `lilith mute @user 10m Spamming`")


async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
