import discord
from discord.ext import commands
from discord import app_commands
import json
import os

PERM_FILE = "data/command_permissions.json"


def load_permissions():
    if not os.path.exists(PERM_FILE):
        return {}

    with open(PERM_FILE, "r") as f:
        return json.load(f)


def save_permissions(data):
    with open(PERM_FILE, "w") as f:
        json.dump(data, f, indent=4)


class Permissions(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ---------------- SET COMMAND ROLE ----------------
    @app_commands.command(
        name="setcommandrole",
        description="Set which role can use a command"
    )
    async def set_command_role(
        self,
        interaction: discord.Interaction,
        command: str,
        role: discord.Role
    ):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Only administrators can change command permissions.",
                ephemeral=True
            )
            return

        data = load_permissions()

        guild_id = str(interaction.guild.id)

        data.setdefault(guild_id, {})
        data[guild_id][command] = role.id

        save_permissions(data)

        await interaction.response.send_message(
            f"✅ `{command}` can now be used by {role.mention}"
        )


async def setup(bot):
    await bot.add_cog(Permissions(bot))