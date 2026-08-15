import discord
from discord.ext import commands

import mycord
from utils.command import command


# =========================================
# DATABASE
# =========================================

db = mycord.PunksDB()

db.create_table(
    "lilith_staff",
    """
    guild_id INTEGER,
    user_id INTEGER,
    level INTEGER,
    PRIMARY KEY (guild_id, user_id)
    """
)


# =========================================
# STAFF LEVELS
# =========================================

LEVELS = {
    "trial": 1,
    "moderator": 2,
    "senior": 3,
    "head": 4,
}

LEVEL_NAMES = {
    0: "Not Staff",
    1: "🟢 Trial Moderator",
    2: "🔵 Moderator",
    3: "🔴 Senior Moderator",
    4: "🛡️ Head Moderator",
    5: "👑 Server Owner",
}


# =========================================
# STAFF COG
# =========================================

class Staff(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # =====================================
    # GET STAFF LEVEL
    # =====================================

    def get_level(self, guild, user):

        # Server Owner is always level 5
        if user.id == guild.owner_id:
            return 5

        data = db.fetchone(
            "lilith_staff",
            "guild_id = ? AND user_id = ?",
            (guild.id, user.id)
        )

        if not data:
            return 0

        return data["level"]

    # =====================================
    # LEVEL NAME
    # =====================================

    def get_level_name(self, level):

        return LEVEL_NAMES.get(
            level,
            "Unknown"
        )

    # =====================================
    # LEVEL PARSER
    # =====================================

    def parse_level(self, level):

        level = level.lower()

        aliases = {
            "trial": 1,
            "trainee": 1,

            "moderator": 2,
            "mod": 2,

            "senior": 3,
            "seniormod": 3,

            "head": 4,
            "headmod": 4,
        }

        return aliases.get(level)

    # =====================================
    # MOD ADD
    # =====================================

    @command(
        "🖤 Staff",
        "Add a user to Lilith staff",
        name="modadd"
    )
    async def modadd(
        self,
        ctx,
        member: discord.Member,
        level: str = "trial"
    ):

        actor_level = self.get_level(
            ctx.guild,
            ctx.author
        )

        # Head Moderator or above
        if actor_level < 4:

            await ctx.send(
                "❌ You need **Head Moderator** "
                "or above to manage staff."
            )
            return

        # Owner is automatically staff
        if member.id == ctx.guild.owner_id:

            await ctx.send(
                "❌ The Server Owner is "
                "automatically recognized."
            )
            return

        new_level = self.parse_level(level)

        if new_level is None:

            await ctx.send(
                "❌ Invalid staff level.\n\n"
                "Available levels:\n"
                "`trial`\n"
                "`moderator`\n"
                "`senior`\n"
                "`head`"
            )
            return

        target_level = self.get_level(
            ctx.guild,
            member
        )

        if target_level >= actor_level:

            await ctx.send(
                "❌ You cannot modify someone "
                "at or above your own level."
            )
            return

        db.insert(
            "lilith_staff",
            guild_id=ctx.guild.id,
            user_id=member.id,
            level=new_level
        )

        await ctx.send(
            f"✅ {member.mention} is now "
            f"**{self.get_level_name(new_level)}**."
        )

    # =====================================
    # MOD REMOVE
    # =====================================

    @command(
        "🖤 Staff",
        "Remove a user from Lilith staff",
        name="modremove"
    )
    async def modremove(
        self,
        ctx,
        member: discord.Member
    ):

        actor_level = self.get_level(
            ctx.guild,
            ctx.author
        )

        if actor_level < 4:

            await ctx.send(
                "❌ You need **Head Moderator** "
                "or above to manage staff."
            )
            return

        if member.id == ctx.guild.owner_id:

            await ctx.send(
                "❌ The Server Owner cannot "
                "be removed."
            )
            return

        target_level = self.get_level(
            ctx.guild,
            member
        )

        if target_level == 0:

            await ctx.send(
                "❌ That user is not Lilith staff."
            )
            return

        if target_level >= actor_level:

            await ctx.send(
                "❌ You cannot remove someone "
                "at or above your own level."
            )
            return

        db.delete(
            "lilith_staff",
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id)
        )

        await ctx.send(
            f"✅ Removed {member.mention} "
            "from Lilith staff."
        )

    # =====================================
    # MOD LIST
    # =====================================

    @command(
        "🖤 Staff",
        "Show all Lilith staff members",
        name="modlist"
    )
    async def modlist(self, ctx):

        rows = db.fetchall(
            "lilith_staff",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        embed = discord.Embed(
            title="🖤 Lilith Staff",
            color=discord.Color.dark_red()
        )

        owner = ctx.guild.owner

        embed.add_field(
            name="👑 Server Owner",
            value=owner.mention,
            inline=False
        )

        if not rows:

            embed.add_field(
                name="Staff",
                value="No moderators assigned.",
                inline=False
            )

            await ctx.send(embed=embed)
            return

        grouped = {}

        for row in rows:

            level = row["level"]

            grouped.setdefault(
                level,
                []
            ).append(
                row["user_id"]
            )

        for level in sorted(
            grouped,
            reverse=True
        ):

            members = []

            for user_id in grouped[level]:

                member = ctx.guild.get_member(
                    user_id
                )

                if member:

                    members.append(
                        member.mention
                    )

            if members:

                embed.add_field(
                    name=self.get_level_name(level),
                    value="\n".join(members),
                    inline=False
                )

        await ctx.send(embed=embed)

    # =====================================
    # MOD INFO
    # =====================================

    @command(
        "🖤 Staff",
        "Show a user's Lilith staff information",
        name="modinfo"
    )
    async def modinfo(
        self,
        ctx,
        member: discord.Member
    ):

        level = self.get_level(
            ctx.guild,
            member
        )

        embed = discord.Embed(
            title="🖤 Staff Information",
            color=discord.Color.dark_red()
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        embed.add_field(
            name="User",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Level",
            value=self.get_level_name(level),
            inline=False
        )

        await ctx.send(embed=embed)

    # =====================================
    # MOD PROMOTE
    # =====================================

    @command(
        "🖤 Staff",
        "Promote a Lilith staff member",
        name="modpromote"
    )
    async def modpromote(
        self,
        ctx,
        member: discord.Member
    ):

        actor_level = self.get_level(
            ctx.guild,
            ctx.author
        )

        # Senior Moderator or above
        if actor_level < 3:

            await ctx.send(
                "❌ You need **Senior Moderator** "
                "or above to promote staff."
            )
            return

        target_level = self.get_level(
            ctx.guild,
            member
        )

        if target_level == 0:

            await ctx.send(
                "❌ That user is not Lilith staff."
            )
            return

        if target_level >= actor_level:

            await ctx.send(
                "❌ You cannot promote someone "
                "to or above your own level."
            )
            return

        if target_level >= 4:

            await ctx.send(
                "❌ They are already a "
                "**Head Moderator**."
            )
            return

        new_level = target_level + 1

        db.update(
            "lilith_staff",
            {"level": new_level},
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id)
        )

        await ctx.send(
            f"⬆️ {member.mention} has been "
            f"promoted to "
            f"**{self.get_level_name(new_level)}**."
        )

    # =====================================
    # MOD DEMOTE
    # =====================================

    @command(
        "🖤 Staff",
        "Demote a Lilith staff member",
        name="moddemote"
    )
    async def moddemote(
        self,
        ctx,
        member: discord.Member
    ):

        actor_level = self.get_level(
            ctx.guild,
            ctx.author
        )

        # Senior Moderator or above
        if actor_level < 3:

            await ctx.send(
                "❌ You need **Senior Moderator** "
                "or above to demote staff."
            )
            return

        target_level = self.get_level(
            ctx.guild,
            member
        )

        if target_level == 0:

            await ctx.send(
                "❌ That user is not Lilith staff."
            )
            return

        if target_level >= actor_level:

            await ctx.send(
                "❌ You cannot demote someone "
                "at or above your own level."
            )
            return

        if target_level == 1:

            await ctx.send(
                "❌ They are already a "
                "**Trial Moderator**."
            )
            return

        new_level = target_level - 1

        db.update(
            "lilith_staff",
            {"level": new_level},
            "guild_id = ? AND user_id = ?",
            (ctx.guild.id, member.id)
        )

        await ctx.send(
            f"⬇️ {member.mention} has been "
            f"demoted to "
            f"**{self.get_level_name(new_level)}**."
        )


# =========================================
# SETUP
# =========================================

async def setup(bot):

    await bot.add_cog(
        Staff(bot)
        )
