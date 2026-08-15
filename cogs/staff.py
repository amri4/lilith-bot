import discord
from discord.ext import commands

import mycord


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
    # GET USER LEVEL
    # =====================================

    def get_level(self, guild, user):

        # Server owner
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
    # GET LEVEL NAME
    # =====================================

    def get_level_name(self, level):

        return LEVEL_NAMES.get(
            level,
            "No Staff Rank"
        )

    # =====================================
    # CHECK STAFF
    # =====================================

    def is_staff(self, guild, user):

        return self.get_level(
            guild,
            user
        ) > 0

    # =====================================
    # MOD ADD
    # =====================================

    @commands.group(
        name="mod",
        invoke_without_command=True
    )
    async def mod(self, ctx):

        await ctx.send(
            "🖤 Use `mod add`, `mod remove`, "
            "`mod list`, `mod info`, "
            "`mod promote`, or `mod demote`."
        )

    # =====================================
    # MOD ADD
    # =====================================

    @mod.command(
        name="add"
    )
    async def mod_add(
        self,
        ctx,
        member: discord.Member,
        level: str = "trial"
    ):

        actor_level = self.get_level(
            ctx.guild,
            ctx.author
        )

        # Only Head Moderator or Owner
        if actor_level < 4:

            await ctx.send(
                "❌ You need **Head Moderator** "
                "or above to manage staff."
            )
            return

        level = level.lower()

        if level not in LEVELS:

            await ctx.send(
                "❌ Invalid level.\n\n"
                "Available levels:\n"
                "`trial`\n"
                "`moderator`\n"
                "`senior`\n"
                "`head`"
            )
            return

        new_level = LEVELS[level]

        target_level = self.get_level(
            ctx.guild,
            member
        )

        # Don't modify someone equal/higher
        if target_level >= actor_level:

            await ctx.send(
                "❌ You cannot modify a "
                "staff member at or above "
                "your level."
            )
            return

        # Owner cannot be manually added
        if member.id == ctx.guild.owner_id:

            await ctx.send(
                "❌ The Server Owner is "
                "automatically recognized."
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

    @mod.command(
        name="remove"
    )
    async def mod_remove(
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

        target_level = self.get_level(
            ctx.guild,
            member
        )

        if target_level == 0:

            await ctx.send(
                "❌ That user is not a "
                "Lilith staff member."
            )
            return

        if member.id == ctx.guild.owner_id:

            await ctx.send(
                "❌ The Server Owner cannot "
                "be removed."
            )
            return

        if target_level >= actor_level:

            await ctx.send(
                "❌ You cannot remove a "
                "staff member at or above "
                "your level."
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

    @mod.command(
        name="list"
    )
    async def mod_list(
        self,
        ctx
    ):

        rows = db.fetchall(
            "lilith_staff",
            "guild_id = ?",
            (ctx.guild.id,)
        )

        embed = discord.Embed(
            title="🖤 Lilith Staff",
            color=discord.Color.dark_red()
        )

        # Owner
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

    @mod.command(
        name="info"
    )
    async def mod_info(
        self,
        ctx,
        member: discord.Member
    ):

        level = self.get_level(
            ctx.guild,
            member
        )

        embed = discord.Embed(
            title="🖤 Moderator Information",
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

        await ctx.send(
            embed=embed
        )

    # =====================================
    # MOD PROMOTE
    # =====================================

    @mod.command(
        name="promote"
    )
    async def mod_promote(
        self,
        ctx,
        member: discord.Member
    ):

        actor_level = self.get_level(
            ctx.guild,
            ctx.author
        )

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
                "❌ That user is not a "
                "Lilith staff member."
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
                "❌ That user is already "
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

    @mod.command(
        name="demote"
    )
    async def mod_demote(
        self,
        ctx,
        member: discord.Member
    ):

        actor_level = self.get_level(
            ctx.guild,
            ctx.author
        )

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
                "❌ That user is not a "
                "Lilith staff member."
            )
            return

        if target_level >= actor_level:

            await ctx.send(
                "❌ You cannot demote a "
                "staff member at or above "
                "your level."
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
