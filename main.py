import os
import json
import discord
from discord.ext import commands
from discord import app_commands
import copy

# ==============================
# 🔹 Nom du fichier de configuration
# ==============================
CONFIG_FILE = "config.json"


# ==============================
# 🔹 Fonctions utilitaires JSON
# ==============================
def load_config():
    """Charge la configuration depuis le fichier JSON (ou en crée une par défaut)."""
    print("[CONFIG] Chargement du fichier JSON...\n")
    try:
        # On tente d'ouvrir le fichier et de lire son contenu
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"[CONFIG] Fichier chargé avec succès : {len(data)} serveurs configurés \n")
            return data
    except FileNotFoundError:
        # Si le fichier n'existe pas, on en crée un modèle vide
        print("[CONFIG] Aucun fichier trouvé, création d'une configuration vide.\n")
        return {
            "default": {
                "welcome_channel": None,   # Aucun salon défini
                "mention_user": True,      # Mention du nouvel utilisateur activée
                "auto_roles": []           # Aucun rôle automatique
            }
        }

def save_config(data):
    """Sauvegarde la configuration actuelle dans le fichier JSON."""
    print("[CONFIG] Sauvegarde de la configuration...\n")
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print("[CONFIG] Configuration sauvegardée avec succès.\n")


# On charge la configuration au démarrage
config = load_config()


# ==============================
# 🔹 Initialisation du bot
# ==============================
intents = discord.Intents.default()
intents.message_content = True  # Nécessaire pour lire le contenu des messages
intents.members = True          # Permet d'utiliser les événements sur les membres (join/leave)


class MyBot(commands.Bot):
    """Classe personnalisée du bot Discord."""

    def __init__(self):
        super().__init__(command_prefix="..", intents=intents)

    async def setup_hook(self):
        """Synchronise les commandes slash avec Discord au démarrage."""
        await self.tree.sync()
        print("[BOT] Commandes slash synchronisées avec Discord.\n")


# Création de l'instance du bot
bot = MyBot()


# ==============================
# 🔹 Commande /config-welcome
# ==============================
@bot.tree.command(name="config-welcome", description="Configure le salon et le message de bienvenue personnalisé")
@app_commands.describe(
    channel="Salon où envoyer le message de bienvenue",
    message="Texte du message de bienvenue (utilise {user} ou {user.mention})"
)
@app_commands.checks.has_permissions(administrator=True)
async def config_welcome(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str = "🎉 Bienvenue {user.mention} sur le serveur ! 👋"
):
    """Définit le salon et le message de bienvenue personnalisable."""
    guild_id = str(interaction.guild_id)
    print(f"[CONFIG] /config-welcome appelé par {interaction.user} dans {interaction.guild.name}\n")

    # Charger la configuration actuelle (sécurité au cas où elle aurait changé entre temps)
    current_config = load_config()

    # Créer une section propre pour ce serveur s’il n’en a pas
    if guild_id not in current_config:
        current_config[guild_id] = config["default"].copy()

    # Remplacer totalement la config du serveur par la version mise à jour
    current_config[guild_id].update({
        "welcome_channel": channel.id,
        "welcome_message": message,
        "auto_roles": current_config[guild_id].get("auto_roles", [])  # garder les rôles existants
    })

    # Sauvegarder immédiatement dans le fichier
    save_config(current_config)

    # Mettre à jour la variable globale en mémoire
    config[guild_id] = current_config[guild_id]

    # Confirmation dans Discord
    await interaction.response.send_message(
        f"✅ **Configuration mise à jour :**\n"
        f"📢 Salon de bienvenue : {channel.mention}\n"
        f"💬 Message de bienvenue :\n```{message}```"
    )

    print(f"[CONFIG] Configuration de bienvenue mise à jour pour {guild_id} et sauvegardée dans {CONFIG_FILE}\n")

# ==============================
# 🔹 Commande /config-goodbye
# ==============================
@bot.tree.command(name="config-goodbye", description="Configure le salon et le message d'au revoir personnalisé")
@app_commands.describe(
    channel="Salon où envoyer le message d'au revoir",
    message="Texte du message de bienvenue (utilise {user} ou {user.mention})"
)
@app_commands.checks.has_permissions(administrator=True)
async def config_goodbye(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str = " Au revoir {user.mention} 👋"
):
    """Définit le salon et le message de bienvenue personnalisable."""
    guild_id = str(interaction.guild_id)
    print(f"[CONFIG] /config-goodbye appelé par {interaction.user} dans {interaction.guild.name}\n")

    # Charger la configuration actuelle (sécurité au cas où elle aurait changé entre temps)
    current_config = load_config()

    # Créer une section propre pour ce serveur s’il n’en a pas
    if guild_id not in current_config:
        current_config[guild_id] = config["default"].copy()

    # Remplacer totalement la config du serveur par la version mise à jour
    current_config[guild_id].update({
        "goodbye_channel": channel.id,
        "goodbye_message": message,
    })

    # Sauvegarder immédiatement dans le fichier
    save_config(current_config)

    # Mettre à jour la variable globale en mémoire
    config[guild_id] = current_config[guild_id]

    # Confirmation dans Discord
    await interaction.response.send_message(
        f"✅ **Configuration mise à jour :**\n"
        f"📢 Salon de départ : {channel.mention}\n"
        f"💬 Message de départ :\n```{message}```"
    )

    print(f"[CONFIG] Configuration de départ mise à jour pour {guild_id} et sauvegardée dans {CONFIG_FILE}\n")

# ==============================
# 🔹 Commande /config-autoroles
# ==============================
@bot.tree.command(name="config-autoroles", description="Ajoute ou retire un rôle automatique à l’arrivée d’un membre")
@app_commands.describe(role="Le rôle à ajouter ou retirer", action="add/remove")
@app_commands.choices(action=[
    app_commands.Choice(name="Ajouter", value="add"),
    app_commands.Choice(name="Retirer", value="remove")
])
@app_commands.checks.has_permissions(manage_roles=True)
async def config_autoroles(interaction: discord.Interaction, role: discord.Role, action: app_commands.Choice[str]):
    """Ajoute ou supprime un rôle automatique dans la configuration du serveur."""
    guild_id = str(interaction.guild_id)
    print(f"[CONFIG] /config-autoroles appelé par {interaction.user} sur {role.name} ({action.value})\n")

    # Si pas de config pour ce serveur → copie du modèle par défaut
    if guild_id not in config:
        config[guild_id] = copy.deepcopy(config["default"])


    # Récupération des rôles auto existants
    roles = config[guild_id].get("auto_roles", [])

    # --- Ajout d'un rôle auto ---
    if action.value == "add":
        if role.id not in roles:
            roles.append(role.id)
            config[guild_id]["auto_roles"] = roles
            save_config(config)
            await interaction.response.send_message(f"✅ Rôle **{role.name}** ajouté à la liste auto.")
            print(f"[CONFIG] Rôle {role.name} ajouté à la config du serveur.\n")
        else:
            await interaction.response.send_message(f"⚠️ Ce rôle est déjà configuré.\n")

    # --- Suppression d'un rôle auto ---
    elif action.value == "remove":
        if role.id in roles:
            roles.remove(role.id)
            config[guild_id]["auto_roles"] = roles
            save_config(config)
            await interaction.response.send_message(f"✅ Rôle **{role.name}** retiré de la liste auto.")
            print(f"[CONFIG] Rôle {role.name} retiré de la config du serveur.\n")
        else:
            await interaction.response.send_message(f"⚠️ Ce rôle n’était pas configuré.\n")


# ==============================
# 🔹 Commande /voir-config
# ==============================
@bot.tree.command(name="voir-config", description="Affiche la configuration actuelle du serveur")
async def voir_config(interaction: discord.Interaction):
    """Affiche la configuration enregistrée pour le serveur actuel."""
    guild_id = str(interaction.guild_id)
    print(f"[CONFIG] /voir-config exécuté par {interaction.user}\n")

    # On récupère les paramètres du serveur ou ceux par défaut
    data = config.get(guild_id, config["default"])

    welcome_channel = data.get("welcome_channel")
    mention_user = data.get("mention_user", True)
    roles = data.get("auto_roles", [])

    # Mise en forme pour affichage Discord
    channel_text = f"<#{welcome_channel}>" if welcome_channel else "❌ Aucun"
    roles_text = "\n".join([f"<@&{r}>" for r in roles]) if roles else "❌ Aucun"

    await interaction.response.send_message(
        f"📋 **Configuration actuelle :**\n"
        f"📢 Salon de bienvenue : {channel_text}\n"
        f"🔔 Mention utilisateur : {'Oui' if mention_user else 'Non'}\n"
        f"🎭 Rôles auto :\n{roles_text}"
    )

# ==============================
# 🔹 Commande /aide
# ==============================
@bot.tree.command(name="aide", description="Affiche les commandes disponibles")
async def aide(interaction: discord.Interaction):
    """Affiche les commandes disponibles du bot avec une jolie mise en forme."""

    print(f"[CMD] /aide exécuté par {interaction.user} dans {interaction.guild.name}\n")

    help_text = (
        "📚 **Commandes disponibles :**\n\n"
        "🛠️ **Configuration :**\n"
        "• `/config-welcome` — Configure le salon de bienvenue et la mention automatique.\n"
        "• `/config-autoroles` — Ajoute ou retire des rôles automatiques à l’arrivée.\n"
        "• `/voir-config` — Affiche la configuration actuelle du serveur.\n\n"
        "👋 **Utilitaires :**\n"
        "• `/aide` — Affiche cette aide.\n"
    )

    await interaction.response.send_message(help_text, ephemeral=True)
    print("[CMD] Message d’aide envoyé avec succès ✅")


# ==============================
# 🔹 Commande /auto-role-ajout-rapide (avec barre de progression)
# ==============================
@bot.tree.command(
    name="auto-role-ajout-rapide",
    description="Ajoute à tous les membres humains les rôles auto configurés pour ce serveur (avec progression)."
)
@app_commands.checks.has_permissions(manage_roles=True)
async def auto_role_ajout_rapide(interaction: discord.Interaction):
    """Ajoute les rôles configurés automatiquement à tous les membres humains avec une barre de progression."""
    guild = interaction.guild
    guild_id = str(guild.id)

    # Charger la configuration actuelle
    current_config = load_config()
    settings = current_config.get(guild_id, config["default"])

    # Rôles auto configurés
    auto_roles = settings.get("auto_roles", [])

    if not auto_roles:
        await interaction.response.send_message(
            "⚠️ Aucun rôle automatique configuré pour ce serveur.\n"
            "Utilise `/config-autoroles` pour en ajouter un.",
            ephemeral=True
        )
        return

    # Envoi du message initial
    await interaction.response.send_message(
        f"🚀 Démarrage de l'ajout des rôles auto ({len(auto_roles)} rôles)...",
        ephemeral=False
    )

    msg = await interaction.original_response()

    members = [m for m in guild.members if not m.bot]
    total = len(members)
    added = 0
    skipped = 0

    # Boucle principale avec mise à jour de progression
    for i, member in enumerate(members, start=1):
        for rid in auto_roles:
            role = guild.get_role(rid)
            if not role:
                continue
            if role not in member.roles:
                try:
                    await member.add_roles(role, reason="Ajout auto via /auto-role-ajout-rapide")
                    added += 1
                except discord.Forbidden:
                    skipped += 1
                except Exception:
                    skipped += 1

        # Mise à jour toutes les 10 % de progression
        progress = int((i / total) * 100)
        if progress % 10 == 0 or i == total:
            bar_filled = "█" * (progress // 10)
            bar_empty = "░" * (10 - progress // 10)
            progress_bar = f"[{bar_filled}{bar_empty}] {progress}%"
            await msg.edit(content=f"⏳ Progression : {progress_bar}\n"
                                   f"👤 Membres traités : {i}/{total}\n"
                                   f"✅ Ajouts : {added} | ⚠️ Ignorés : {skipped}")

    # Message final
    await msg.edit(content=(
        f"✅ **Terminé !**\n"
        f"🎭 Rôles auto ajoutés à **{added}** membres humains.\n"
        f"⚠️ {skipped} membres ignorés (erreurs ou permissions).\n\n"
        f"🧾 Rôles appliqués : " +
        ", ".join([f"<@&{r}>" for r in auto_roles])
    ))

    print(f"[AUTO-ROLE] Terminé pour {guild.name} → {added} membres mis à jour, {skipped} ignorés.")



# ==============================
# 🔹 Événements du bot
# ==============================

@bot.event
async def on_ready():
    """S’exécute quand le bot est connecté et prêt."""
    print(f"\n✅ Bot prêt : {bot.user} ({len(bot.guilds)} serveurs connectés)\n")


@bot.event
async def on_member_join(member: discord.Member):
    """Événement déclenché lorsqu’un membre rejoint un serveur."""
    guild_id = str(member.guild.id)
    settings = config.get(guild_id, config["default"])
    print(f"[JOIN] {member.name} a rejoint {member.guild.name}\n")

    # Récupération des paramètres de bienvenue
    channel_id = settings.get("welcome_channel")
    roles_ids = settings.get("auto_roles", [])

    # Récupération du message configuré
    welcome_message = settings.get("welcome_message", "🎉 Bienvenue {user.mention} sur le serveur ! 👋")

    # Envoi du message de bienvenue
    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            msg = welcome_message.format(user=member)
            await channel.send(msg)
            print(f"[JOIN] Message de bienvenue envoyé dans {channel.name}\n")
        else:
            print(f"[JOIN] ⚠️ Salon introuvable (ID: {channel_id})\n")
    else:
        print("[JOIN] ⚠️ Aucun salon de bienvenue configuré.\n")

    # Attribution des rôles automatiques
    for rid in roles_ids:
        role = member.guild.get_role(rid)
        if role:
            try:
                await member.add_roles(role)
                print(f"[JOIN] ✅ Rôle {role.name} attribué à {member.name}\n")
            except discord.Forbidden:
                print(f"[JOIN] ❌ Permission refusée pour {role.name}\n")
        else:
            print(f"[JOIN] ⚠️ Rôle introuvable (ID: {rid})\n")


@bot.event
async def on_member_remove(member):
    """Événement déclenché lorsqu’un membre quitte le serveur."""
    guild_id = str(member.guild.id)
    settings = config.get(guild_id, config["default"])
    print(f"[LEAVE] {member.name} a quitté {member.guild.name}\n")

    # Récupération du salon et du message de départ configurés
    channel_id = settings.get("goodbye_channel")
    goodbye_message = settings.get("goodbye_message", "👋 {user.mention} a quitté le serveur.")

    if channel_id:
        channel = bot.get_channel(channel_id)
        if channel:
            msg = goodbye_message.format(user=member)
            await channel.send(msg)
            print(f"[LEAVE] Message de départ envoyé dans {channel.name}\n")
        else:
            print(f"[LEAVE] ⚠️ Salon introuvable (ID: {channel_id})\n")
    else:
        print("[LEAVE] ⚠️ Aucun salon de départ configuré.\n")



# ==============================
# 🔹 Lancement du bot
# ==============================
# Le token doit être stocké dans les variables d'environnement
token = os.environ["token_sung"]
bot.run(token)
