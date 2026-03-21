import discord
from discord.ext import commands


class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    # ---------------- LARP ----------------

    @discord.app_commands.command(
        name="larp",
        description="Call someone out as a LARPer"
    )
    async def larp(self, interaction: discord.Interaction, user: discord.Member):

        await interaction.response.send_message(
            f"🚨 {user.mention} is a certified larp larp larp SAHUR"
        )


    # ---------------- SLANDER ----------------

    @discord.app_commands.command(
        name="slander",
        description="Slander your opps"
    )
    async def slander(self, interaction: discord.Interaction, user: discord.Member):

        await interaction.response.send_message(
            f"Fuck {user.display_name}, from {interaction.user.mention}"
        )


async def setup(bot):
    await bot.add_cog(Fun(bot))
