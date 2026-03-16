import json
import os

BASE = "data/guilds"

def ensure_guild(guild_id):

    path = f"{BASE}/{guild_id}"

    os.makedirs(path, exist_ok=True)

    config_file = f"{path}/config.json"

    if not os.path.exists(config_file):

        default = {
            "log_channel": None,
            "raid_protection": True,
            "automod": {
                "spam_threshold": 5,
                "caps_percent": 0.7,
                "mention_limit": 5,
                "block_invites": True
            }
        }

        with open(config_file,"w") as f:
            json.dump(default,f,indent=4)

def load_config(guild_id):

    ensure_guild(guild_id)

    with open(f"{BASE}/{guild_id}/config.json") as f:
        return json.load(f)

def save_config(guild_id,data):

    with open(f"{BASE}/{guild_id}/config.json","w") as f:
        json.dump(data,f,indent=4)