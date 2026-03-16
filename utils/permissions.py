import json
import os

CONFIG_FILE = "data/config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def has_command_permission(member, command):

    # admins always allowed
    if member.guild_permissions.administrator:
        return True

    config = load_config()
    guild_id = str(member.guild.id)

    if guild_id not in config:
        return False

    allowed_roles = config[guild_id].get("command_roles", {}).get(command, [])

    for role in member.roles:
        if role.id in allowed_roles:
            return True

    return False