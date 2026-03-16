import discord
from discord.ext import commands
from discord import app_commands
import json
import os

WARN_FILE = "data/warnings.json"


def load_warnings():
    if not os.path.exists(WARN_FILE):
        return {}

    with open(WARN_FILE, "r") as f:
        return json.load(f)


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="userinfo", description="View detailed information about a user")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):

        user = user or interaction.user

        # Fetch banner
        user_full = await self.bot.fetch_user(user.id)

        warns = load_warnings()
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        warning_count = len(warns.get(guild_id, {}).get(user_id, []))

        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        role_list = ", ".join(roles) if roles else "None"

        perms = []

        if user.guild_permissions.administrator:
            perms.append("Administrator")
        if user.guild_permissions.manage_messages:
            perms.append("Manage Messages")
        if user.guild_permissions.kick_members:
            perms.append("Kick Members")
        if user.guild_permissions.ban_members:
            perms.append("Ban Members")

        perm_list = ", ".join(perms) if perms else "None"

        embed = discord.Embed(
            title=f"👤 User Info • {user}",
            color=user.color if user.color != discord.Color.default() else discord.Color.blurple()
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        if user_full.banner:
            embed.set_image(url=user_full.banner.url)

        embed.add_field(name="🆔 User ID", value=user.id, inline=False)

        embed.add_field(
            name="📅 Account Created",
            value=f"<t:{int(user.created_at.timestamp())}:F>",
            inline=False
        )

        embed.add_field(
            name="📥 Joined Server",
            value=f"<t:{int(user.joined_at.timestamp())}:F>",
            inline=False
        )

        embed.add_field(name="🤖 Bot", value="Yes" if user.bot else "No")

        embed.add_field(name="⚠ Warnings", value=warning_count)

        embed.add_field(name="⭐ Top Role", value=user.top_role.mention)

        embed.add_field(name="🔑 Key Permissions", value=perm_list, inline=False)

        embed.add_field(
            name=f"🎭 Roles ({len(roles)})",
            value=role_list[:1000],
            inline=False
        )

        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Utility(bot))