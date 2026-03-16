import discord


def success(title, description):
    return discord.Embed(
        title=f"✅ {title}",
        description=description,
        color=discord.Color.green()
    )


def error(title, description):
    return discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )


def mod(title):
    return discord.Embed(
        title=title,
        color=discord.Color.orange()
    )