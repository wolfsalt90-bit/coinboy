import discord
from discord.ext import commands


class Intro(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_guild_join(self, guild):

        owner = guild.owner

        embed = discord.Embed(
            title="👋 Thanks for inviting me!",
            description="I'm a moderation and utility bot.",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="⚙ Setup",
            value="Run `/setup` to configure the bot.",
            inline=False
        )

        embed.add_field(
            name="🛡 Moderation",
            value="""
`/warn`
`/kick`
`/ban`
`/mute`
""",
            inline=False
        )

        embed.add_field(
            name="📚 Help",
            value="Run `/help` to see all commands.",
            inline=False
        )

        try:
            await owner.send(embed=embed)
        except:
            pass


async def setup(bot):
    await bot.add_cog(Intro(bot))