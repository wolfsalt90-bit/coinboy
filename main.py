import discord
from discord.ext import commands, tasks
import os
import random
from dotenv import load_dotenv

from config import STATUSES, DEV_GUILD

TOKEN = os.getenv("TOKEN")
bot.run(TOKEN)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="*", intents=intents)

# ---------------- STATUS ROTATION ----------------

@tasks.loop(minutes=30)
async def rotate_status():

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=random.choice(STATUSES)
        )
    )

# ---------------- LOAD COGS ----------------

async def load_cogs():

    for file in os.listdir("./cogs"):
        if file.endswith(".py"):
            await bot.load_extension(f"cogs.{file[:-3]}")

# ---------------- READY ----------------

@bot.event
async def on_ready():

    await bot.tree.sync(guild=DEV_GUILD)  # instant dev commands
    await bot.tree.sync()                 # global commands

    rotate_status.start()

    print(f"Logged in as {bot.user}")

# ---------------- SETUP ----------------

@bot.event
async def setup_hook():
    await load_cogs()

bot.run(TOKEN)
