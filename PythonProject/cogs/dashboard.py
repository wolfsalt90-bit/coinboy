import discord
from discord.ext import commands
from discord import app_commands

from utils.database import load_config

class Dashboard(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="dashboard", description="Server dashboard")
    async def dashboard(self, interaction: discord.Interaction):

        config = load_config(interaction.guild.id)

        automod = config["automod"]

        embed = discord.Embed(
            title="Server Dashboard",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Logging Channel",
            value=f"<#{config['log_channel']}>" if config["log_channel"] else "Not set"
        )

        embed.add_field(
            name="Spam Threshold",
            value=automod["spam_threshold"]
        )

        embed.add_field(
            name="Caps Percent",
            value=automod["caps_percent"]
        )

        embed.add_field(
            name="Mention Limit",
            value=automod["mention_limit"]
        )

        embed.add_field(
            name="Block Invites",
            value=automod["block_invites"]
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Dashboard(bot))