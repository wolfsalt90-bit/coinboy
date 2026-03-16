import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import timedelta

from utils.permissions import has_command_permission

WARN_FILE = "data/warnings.json"
CASE_FILE = "data/cases.json"

AUTO_MUTE = 3
AUTO_KICK = 5
AUTO_BAN = 7


# ---------------- WARN DATABASE ----------------

def load_warnings():
    if not os.path.exists(WARN_FILE):
        return {}

    with open(WARN_FILE, "r") as f:
        return json.load(f)


def save_warnings(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ---------------- CASE SYSTEM ----------------

def get_next_case():

    if not os.path.exists(CASE_FILE):
        with open(CASE_FILE, "w") as f:
            json.dump({"case": 0}, f)

    with open(CASE_FILE, "r") as f:
        data = json.load(f)

    data["case"] += 1

    with open(CASE_FILE, "w") as f:
        json.dump(data, f, indent=4)

    return data["case"]


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ---------------- AUTO PUNISH ----------------

    async def check_auto_punishment(self, interaction, user, warn_count):

        if warn_count == AUTO_MUTE:

            duration = discord.utils.utcnow() + timedelta(minutes=10)
            await user.timeout(duration)

            embed = discord.Embed(
                title="🔇 Auto Mute",
                description=f"{user.mention} reached {AUTO_MUTE} warnings.",
                color=discord.Color.blue()
            )

            await interaction.channel.send(embed=embed)
            await self.log_action(interaction, embed)

        elif warn_count == AUTO_KICK:

            await user.kick(reason="Auto punishment: too many warnings")

            embed = discord.Embed(
                title="👢 Auto Kick",
                description=f"{user} reached {AUTO_KICK} warnings.",
                color=discord.Color.red()
            )

            await interaction.channel.send(embed=embed)
            await self.log_action(interaction, embed)

        elif warn_count == AUTO_BAN:

            await user.ban(reason="Auto punishment: too many warnings")

            embed = discord.Embed(
                title="🔨 Auto Ban",
                description=f"{user} reached {AUTO_BAN} warnings.",
                color=discord.Color.dark_red()
            )

            await interaction.channel.send(embed=embed)
            await self.log_action(interaction, embed)

    # ---------------- WARN ----------------

    @app_commands.command(name="warn", description="Warn a user")
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str):

        if not has_command_permission(interaction.user, "warn"):
            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )
            return

        warns = load_warnings()

        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        warns.setdefault(guild_id, {})
        warns[guild_id].setdefault(user_id, [])

        warns[guild_id][user_id].append({
            "moderator": interaction.user.id,
            "reason": reason
        })

        save_warnings(warns)

        warn_count = len(warns[guild_id][user_id])

        case = get_next_case()

        embed = discord.Embed(
            title=f"⚠ Case #{case} | User Warned",
            color=discord.Color.orange()
        )

        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="Total Warnings", value=warn_count)

        await interaction.response.send_message(embed=embed)

        await self.log_action(interaction, embed)

        await self.check_auto_punishment(interaction, user, warn_count)

    # ---------------- WARNINGS ----------------

    @app_commands.command(name="warnings", description="View a user's warnings")
    async def warnings(self, interaction: discord.Interaction, user: discord.Member):

        if not has_command_permission(interaction.user, "warnings"):

            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )
            return

        warns = load_warnings()

        guild_id = str(interaction.guild.id)
        user_id = str(user.id)

        user_warns = warns.get(guild_id, {}).get(user_id, [])

        if not user_warns:
            await interaction.response.send_message(
                f"{user.mention} has no warnings."
            )
            return

        embed = discord.Embed(
            title=f"⚠ Warnings for {user}",
            color=discord.Color.orange()
        )

        for i, warn in enumerate(user_warns, start=1):

            mod = interaction.guild.get_member(warn["moderator"])
            mod_name = mod.mention if mod else "Unknown"

            embed.add_field(
                name=f"Warning {i}",
                value=f"Moderator: {mod_name}\nReason: {warn['reason']}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    # ---------------- KICK ----------------

    @app_commands.command(name="kick", description="Kick a member")
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):

        if not has_command_permission(interaction.user, "kick"):
            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )
            return

        await user.kick(reason=reason)

        case = get_next_case()

        embed = discord.Embed(
            title=f"👢 Case #{case} | User Kicked",
            color=discord.Color.red()
        )

        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)

        await interaction.response.send_message(embed=embed)

        await self.log_action(interaction, embed)

    # ---------------- BAN ----------------

    @app_commands.command(name="ban", description="Ban a member")
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason"):

        if not has_command_permission(interaction.user, "ban"):
            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )
            return

        await user.ban(reason=reason)

        case = get_next_case()

        embed = discord.Embed(
            title=f"🔨 Case #{case} | User Banned",
            color=discord.Color.dark_red()
        )

        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason)

        await interaction.response.send_message(embed=embed)

        await self.log_action(interaction, embed)

    # ---------------- MUTE ----------------

    @app_commands.command(name="mute", description="Mute a user")
    async def mute(self, interaction: discord.Interaction, user: discord.Member, minutes: int):

        if not has_command_permission(interaction.user, "mute"):
            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )
            return

        duration = discord.utils.utcnow() + timedelta(minutes=minutes)

        await user.timeout(duration)

        case = get_next_case()

        embed = discord.Embed(
            title=f"🔇 Case #{case} | User Muted",
            color=discord.Color.blue()
        )

        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Duration", value=f"{minutes} minutes")

        await interaction.response.send_message(embed=embed)

        await self.log_action(interaction, embed)

    # ---------------- UNMUTE ----------------

    @app_commands.command(name="unmute", description="Unmute a user")
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):

        if not has_command_permission(interaction.user, "unmute"):
            await interaction.response.send_message(
                "❌ You don't have permission.",
                ephemeral=True
            )
            return

        await user.timeout(None)

        case = get_next_case()

        embed = discord.Embed(
            title=f"🔊 Case #{case} | User Unmuted",
            color=discord.Color.green()
        )

        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)

        await interaction.response.send_message(embed=embed)

        await self.log_action(interaction, embed)

    # ---------------- LOGGING ----------------

    async def log_action(self, interaction, embed):

        logging_cog = self.bot.get_cog("Logging")

        if logging_cog:
            await logging_cog.send_log(interaction.guild, embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))