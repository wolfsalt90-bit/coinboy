import discord
from discord.ext import commands
import time

class AntiRaid(commands.Cog):

    def __init__(self, bot):

        self.bot = bot
        self.joins = {}

    @commands.Cog.listener()
    async def on_member_join(self, member):

        guild = member.guild.id
        now = time.time()

        self.joins.setdefault(guild, [])

        self.joins[guild] = [t for t in self.joins[guild] if now - t < 10]

        self.joins[guild].append(now)

        if len(self.joins[guild]) > 8:

            channel = member.guild.system_channel

            if channel:
                await channel.send("⚠ Possible raid detected")

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))