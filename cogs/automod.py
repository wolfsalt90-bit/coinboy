import discord
from discord.ext import commands
import time
import re
from utils.database import load_config

LINK_REGEX = r"https?://"

class Automod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.message_history = {}
        self.last_message = {}
        self.join_history = []

    # ---------------- MESSAGE CHECKS ----------------

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot or not message.guild:
            return

        config = load_config(message.guild.id)
        automod = config["automod"]

        user_id = message.author.id
        content = message.content.lower()
        now = time.time()

        # ---------------- SPAM DETECTION ----------------

        self.message_history.setdefault(user_id, [])

        self.message_history[user_id] = [
            t for t in self.message_history[user_id]
            if now - t < 5
        ]

        self.message_history[user_id].append(now)

        if len(self.message_history[user_id]) >= automod["spam_threshold"]:

            await message.delete()
            await self.warn_user(message, "Spam detected")
            return

        # ---------------- DUPLICATE MESSAGE ----------------

        if self.last_message.get(user_id) == content:

            await message.delete()
            await self.warn_user(message, "Duplicate spam")
            return

        self.last_message[user_id] = content

        # ---------------- CAPS FILTER ----------------

        if len(content) > 10:

            caps = sum(1 for c in message.content if c.isupper())

            if caps / len(content) > automod["caps_percent"]:
                await message.delete()
                await self.warn_user(message, "Caps spam")
                return

        # ---------------- INVITE BLOCK ----------------

        if automod["block_invites"]:

            if "discord.gg/" in content or "discord.com/invite" in content:

                await message.delete()
                await self.warn_user(message, "Invite links blocked")
                return

        # ---------------- LINK SPAM ----------------

        if re.search(LINK_REGEX, content):

            links = re.findall(LINK_REGEX, content)

            if len(links) > 2:

                await message.delete()
                await self.warn_user(message, "Link spam")
                return

        # ---------------- MENTION SPAM ----------------

        if len(message.mentions) >= automod["mention_limit"]:

            await message.delete()
            await self.warn_user(message, "Mention spam")
            return

        # ---------------- EMOJI SPAM ----------------

        emoji_count = sum(1 for c in message.content if c in "😀😃😄😁😆😅😂🤣🥲☺️😊😍")

        if emoji_count > 8:

            await message.delete()
            await self.warn_user(message, "Emoji spam")
            return


    # ---------------- RAID DETECTION ----------------

    @commands.Cog.listener()
    async def on_member_join(self, member):

        now = time.time()

        self.join_history = [
            t for t in self.join_history
            if now - t < 10
        ]

        self.join_history.append(now)

        if len(self.join_history) >= 8:

            guild = member.guild

            for m in guild.members:
                if not m.bot:
                    try:
                        await m.timeout(
                            discord.utils.utcnow() + discord.timedelta(minutes=5),
                            reason="Raid protection"
                        )
                    except:
                        pass


    # ---------------- WARN / TIMEOUT ----------------

    async def warn_user(self, message, reason):

        try:
            await message.channel.send(
                f"{message.author.mention} {reason}",
                delete_after=5
            )
        except:
            pass

        try:
            await message.author.timeout(
                discord.utils.utcnow() + discord.timedelta(minutes=2),
                reason=reason
            )
        except:
            pass


async def setup(bot):
    await bot.add_cog(Automod(bot))