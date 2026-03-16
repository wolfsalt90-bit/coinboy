import discord
from discord.ext import commands
from discord import app_commands


class Help(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="help", description="View all bot commands")
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="📚 Bot Commands",
            description="Here are the available commands.",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="🛡 Moderation",
            value="""
`/warn` Warn a user
`/warnings` View warnings
`/kick` Kick a user
`/ban` Ban a user
`/mute` Timeout a user
`/unmute` Remove timeout
""",
            inline=False
        )

        embed.add_field(
            name="⚙ Administration",
            value="""
`/setup` Configure the bot
`/setcommandrole` Set role permissions
""",
            inline=False
        )

        embed.add_field(
            name="🎮 Fun",
            value="""
`/larp`
`/slander`
""",
            inline=False
        )

        embed.set_footer(text="Use /help anytime to see commands")

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Help(bot))