import discord
from discord.ext import commands
import json
import os

CONFIG_FILE = "data/config.json"


# ---------------- CONFIG ----------------
from utils.permissions import has_command_permission
def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_guild_settings(guild_id):

    config = load_config()

    if str(guild_id) not in config:
        config[str(guild_id)] = {
            "automod": {
                "spam_threshold": 5,
                "caps_percent": 0.7,
                "mention_limit": 5,
                "block_invites": True
            }
        }

        save_config(config)

    return config


# ---------------- SPAM DROPDOWN ----------------

class SpamDropdown(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="3 messages", value="3"),
            discord.SelectOption(label="5 messages", value="5"),
            discord.SelectOption(label="7 messages", value="7"),
            discord.SelectOption(label="10 messages", value="10")
        ]

        super().__init__(
            placeholder="Change spam threshold",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        config = get_guild_settings(interaction.guild.id)
        config[str(interaction.guild.id)]["automod"]["spam_threshold"] = int(self.values[0])

        save_config(config)

        await interaction.response.send_message(
            f"✅ Spam threshold set to **{self.values[0]} messages**.",
            ephemeral=True
        )


# ---------------- CAPS DROPDOWN ----------------

class CapsDropdown(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="60%", value="0.6"),
            discord.SelectOption(label="70%", value="0.7"),
            discord.SelectOption(label="80%", value="0.8"),
            discord.SelectOption(label="90%", value="0.9")
        ]

        super().__init__(
            placeholder="Change caps limit",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        config = get_guild_settings(interaction.guild.id)
        config[str(interaction.guild.id)]["automod"]["caps_percent"] = float(self.values[0])

        save_config(config)

        await interaction.response.send_message(
            f"✅ Caps limit set to **{int(float(self.values[0]) * 100)}%**.",
            ephemeral=True
        )


# ---------------- MENTION DROPDOWN ----------------

class MentionDropdown(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(label="3 mentions", value="3"),
            discord.SelectOption(label="5 mentions", value="5"),
            discord.SelectOption(label="7 mentions", value="7"),
            discord.SelectOption(label="10 mentions", value="10")
        ]

        super().__init__(
            placeholder="Change mention limit",
            options=options
        )

    async def callback(self, interaction: discord.Interaction):

        config = get_guild_settings(interaction.guild.id)
        config[str(interaction.guild.id)]["automod"]["mention_limit"] = int(self.values[0])

        save_config(config)

        await interaction.response.send_message(
            f"✅ Mention limit set to **{self.values[0]} mentions**.",
            ephemeral=True
        )


# ---------------- INVITE TOGGLE ----------------

class ToggleInvites(discord.ui.Button):

    def __init__(self):
        super().__init__(label="Toggle Invite Blocking", style=discord.ButtonStyle.red)

    async def callback(self, interaction: discord.Interaction):

        config = get_guild_settings(interaction.guild.id)

        current = config[str(interaction.guild.id)]["automod"]["block_invites"]
        config[str(interaction.guild.id)]["automod"]["block_invites"] = not current

        save_config(config)

        status = "enabled" if not current else "disabled"

        await interaction.response.send_message(
            f"✅ Invite blocking **{status}**.",
            ephemeral=True
        )


# ---------------- PANEL VIEW ----------------

class SetupPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(SpamDropdown())
        self.add_item(CapsDropdown())
        self.add_item(MentionDropdown())
        self.add_item(ToggleInvites())


# ---------------- COG ----------------

class Setup(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @discord.app_commands.command(
        name="setup",
        description="Configure automod settings"
    )
    async def setup(self, interaction: discord.Interaction):

        if not interaction.user.guild_permissions.administrator:

            await interaction.response.send_message(
                "❌ You must be an administrator to use this.",
                ephemeral=True
            )
            return


        config = get_guild_settings(interaction.guild.id)
        settings = config[str(interaction.guild.id)]["automod"]

        embed = discord.Embed(
            title="⚙️ Automod Control Panel",
            description="Use the menus below to configure automod.",
            color=discord.Color.blurple()
        )

        embed.add_field(
            name="Spam Threshold",
            value=settings["spam_threshold"]
        )

        embed.add_field(
            name="Caps Limit",
            value=f'{int(settings["caps_percent"] * 100)}%'
        )

        embed.add_field(
            name="Mention Limit",
            value=settings["mention_limit"]
        )

        embed.add_field(
            name="Invite Blocking",
            value=settings["block_invites"]
        )


        await interaction.response.send_message(
            embed=embed,
            view=SetupPanel(),
            ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Setup(bot))