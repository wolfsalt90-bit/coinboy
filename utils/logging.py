import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "data/config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def send_log(self, guild, embed):

        config = load_config()
        guild_id = str(guild.id)

        if guild_id not in config:
            return

        log_channel_id = config[guild_id].get("log_channel")

        if not log_channel_id:
            return

        channel = guild.get_channel(log_channel_id)

        if channel:
            await channel.send(embed=embed)

    @discord.app_commands.command(
        name="setlog",
        description="Set the server log channel"
    )
    async def setlog(self, interaction: discord.Interaction, channel: discord.TextChannel):

        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "You need administrator permission.",
                ephemeral=True
            )
            return

        config = load_config()

        guild_id = str(interaction.guild.id)

        config.setdefault(guild_id, {})
        config[guild_id]["log_channel"] = channel.id

        save_config(config)

        await interaction.response.send_message(
            f"✅ Log channel set to {channel.mention}"
        )


async def setup(bot):
    await bot.add_cog(Logging(bot))