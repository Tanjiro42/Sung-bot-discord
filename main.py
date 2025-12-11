import os
import json
import discord
from discord.ext import commands
from discord import app_commands
import copy
from flask import Flask

# ==============================
# 🔹 Nom du fichier de configuration
# ==============================
CONFIG_FILE = "config.json"

# ==============================
# 🔹 Fonctions utilitaires JSON
# ==============================
def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        return {
            "default": {
                "welcome_channel": None,
                "mention_user": True,
                "auto_roles": []
            }
        }

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# On charge la config au démarrage
config = load_config()

# ==============================
# 🔹 Initialisation du bot
# ==============================
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="..", intents=intents)

    async def setup_hook(self):
        await self.tree.sync()
        print("[BOT] Commandes slash synchronisées.")

bot = MyBot()

# ==============================
# 🔹 COMMANDES & ÉVÉNEMENTS
# ==============================
# (Toutes les commandes et événements de ton main.py restent identiques,
# je ne les recopie pas ici pour ne pas alourdir, mais tu peux les garder)

# ==============================
# 🔹 FLASK POUR KOYEB
# ==============================
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot Discord en ligne ✅"

# ==============================
# 🔹 Lancement du bot
# ==============================
if __name__ == "__main__":
    from threading import Thread

    # Flask en thread
    Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))).start()

    # Bot Discord
    token = os.environ["token_sung"]
    bot.run(token)
