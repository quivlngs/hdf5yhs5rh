import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from datetime import datetime, timedelta


with open('config.json', 'r') as config_file:
    config = json.load(config_file)

TOKEN = config['token']
COMMAND_CHANNELS = config['command_channels'] 
COOLDOWN_TIMES = config['cooldown_times'] 
CUSTOM_THUMBNAIL = config.get("custom_thumbnail", None)  


intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)


def setup_folders():
    for folder in ['bulk', 'ultra', 'free']:
        if not os.path.exists(folder):
            os.makedirs(folder)
        file_path = os.path.join(folder, 'chicken.txt')
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                for _ in range(30):
                    f.write("chicken:skibidi\n")

setup_folders()


cooldowns = {
    'fgen': {},
    'bgen': {},
    'ugen': {},
}


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"Logged in as {bot.user}. Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


def check_cooldown(command_name, user_id):
    current_time = datetime.utcnow()
    last_used = cooldowns.get(command_name, {}).get(user_id, None)
    
    if last_used:
        cooldown_time = timedelta(seconds=COOLDOWN_TIMES[command_name])
        if current_time - last_used < cooldown_time:
            return False, last_used
    return True, None


def update_cooldown(command_name, user_id):
    cooldowns.setdefault(command_name, {})[user_id] = datetime.utcnow()


def confirmation_embed(user, server_icon):
    embed = discord.Embed(
        title="✅ Generated account! Check your DMs.",
        description="Looking for a higher percent? upgrade at <#1309976626926190682>",
        color=0x00FF00,
        timestamp=datetime.utcnow()
    )
    if server_icon:
        embed.set_thumbnail(url=server_icon)
    embed.set_footer(text=f"Requested by {user.name}", icon_url=user.display_avatar.url)
    return embed


def dm_embed(username, password, user, server_icon):
    embed = discord.Embed(
        title="✅ Account Generated!",
        description="Looking for a higher percent? upgrade at <#1309976626926190682> also make sure to leave a review if u got a hit ",
        color=0x00FF00,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="Username", value=username, inline=False)
    embed.add_field(name="Password", value=password, inline=False)
    embed.add_field(name="Combo", value=f"{username}:{password}", inline=False)
    if server_icon:
        embed.set_thumbnail(url=server_icon)
    embed.set_footer(text=f"Generated by {user.name}", icon_url=user.display_avatar.url)
    return embed


def get_account(file_path):
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return None
    with open(file_path, "r") as f:
        lines = f.readlines()
    account = lines[0].strip()
    with open(file_path, "w") as f:
        f.writelines(lines[1:])
    return account.split(":")


@bot.tree.command(name="fgen", description="Generate a free account.")
@app_commands.describe(service="Service name for the account")
async def fgen(interaction: discord.Interaction, service: str):
    if interaction.channel.id != COMMAND_CHANNELS['fgen']:
        await interaction.response.send_message(f"Wrong channel! Use the command in <#{COMMAND_CHANNELS['fgen']}>.", ephemeral=True)
        return

    
    is_on_cooldown, last_used = check_cooldown('fgen', interaction.user.id)
    if not is_on_cooldown:
        time_left = timedelta(seconds=COOLDOWN_TIMES['fgen']) - (datetime.utcnow() - last_used)
        await interaction.response.send_message(f"You're on cooldown! Try again in {time_left}.", ephemeral=True)
        return

    file_path = f"free/{service}.txt"
    account = get_account(file_path)
    if not account:
        await interaction.response.send_message("No accounts available in stock!", ephemeral=True)
        return

    username, password = account
    server_icon = interaction.guild.icon.url if interaction.guild.icon else CUSTOM_THUMBNAIL

    
    confirmation = confirmation_embed(interaction.user, server_icon)
    await interaction.response.send_message(embed=confirmation)

    
    embed = dm_embed(username, password, interaction.user, server_icon)
    await interaction.user.send(embed=embed)

    
    update_cooldown('fgen', interaction.user.id)


@bot.tree.command(name="bgen", description="Generate 50 bulk accounts.")
@app_commands.describe(service="Service name for the accounts")
async def bgen(interaction: discord.Interaction, service: str):
    if interaction.channel.id != COMMAND_CHANNELS['bgen']:
        await interaction.response.send_message(f"Wrong channel! Use the command in <#{COMMAND_CHANNELS['bgen']}>.", ephemeral=True)
        return

    
    is_on_cooldown, last_used = check_cooldown('bgen', interaction.user.id)
    if not is_on_cooldown:
        time_left = timedelta(seconds=COOLDOWN_TIMES['bgen']) - (datetime.utcnow() - last_used)
        await interaction.response.send_message(f"You're on cooldown! Try again in {time_left}.", ephemeral=True)
        return

    file_path = f"bulk/{service}.txt"
    accounts = []
    for _ in range(50):
        account = get_account(file_path)
        if account:
            accounts.append(account)
        else:
            break
    if not accounts:
        await interaction.response.send_message("No accounts available in stock!", ephemeral=True)
        return

    server_icon = interaction.guild.icon.url if interaction.guild.icon else CUSTOM_THUMBNAIL

    
    confirmation = confirmation_embed(interaction.user, server_icon)
    await interaction.response.send_message(embed=confirmation)

    
    for username, password in accounts:
        embed = dm_embed(username, password, interaction.user, server_icon)
        await interaction.user.send(embed=embed)

    
    update_cooldown('bgen', interaction.user.id)


@bot.tree.command(name="ugen", description="Generate an ultra account.")
@app_commands.describe(service="Service name for the account")
async def ugen(interaction: discord.Interaction, service: str):
    if interaction.channel.id != COMMAND_CHANNELS['ugen']:
        await interaction.response.send_message(f"Wrong channel! Use the command in <#{COMMAND_CHANNELS['ugen']}>.", ephemeral=True)
        return

    
    is_on_cooldown, last_used = check_cooldown('ugen', interaction.user.id)
    if not is_on_cooldown:
        time_left = timedelta(seconds=COOLDOWN_TIMES['ugen']) - (datetime.utcnow() - last_used)
        await interaction.response.send_message(f"You're on cooldown! Try again in {time_left}.", ephemeral=True)
        return

    file_path = f"ultra/{service}.txt"
    account = get_account(file_path)
    if not account:
        await interaction.response.send_message("No accounts available in stock!", ephemeral=True)
        return

    username, password = account
    server_icon = interaction.guild.icon.url if interaction.guild.icon else CUSTOM_THUMBNAIL

    
    confirmation = confirmation_embed(interaction.user, server_icon)
    await interaction.response.send_message(embed=confirmation)

    
    embed = dm_embed(username, password, interaction.user, server_icon)
    await interaction.user.send(embed=embed)

    
    update_cooldown('ugen', interaction.user.id)


@bot.tree.command(name="fstock", description="Check stock for free accounts.")
async def fstock(interaction: discord.Interaction):
    if interaction.channel.id != COMMAND_CHANNELS['fstock']:
        await interaction.response.send_message(f"Wrong channel! Use the command in <#{COMMAND_CHANNELS['fstock']}>.", ephemeral=True)
        return

    stock = []
    for file in os.listdir("free"):
        if file.endswith(".txt"):
            with open(f"free/{file}", 'r') as f:
                count = len(f.readlines())
            stock.append(f"{file.split('.')[0]} - {count}")
    if not stock:
        await interaction.response.send_message("No accounts in stock!", ephemeral=True)
        return

    embed = discord.Embed(
        title="Free Stock",
        description="\n".join(stock),
        color=0x808080
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="bstock", description="Check stock for bulk accounts.")
async def bstock(interaction: discord.Interaction):
    if interaction.channel.id != COMMAND_CHANNELS['bstock']:
        await interaction.response.send_message(f"Wrong channel! Use the command in <#{COMMAND_CHANNELS['bstock']}>.", ephemeral=True)
        return

    stock = []
    for file in os.listdir("bulk"):
        if file.endswith(".txt"):
            with open(f"bulk/{file}", 'r') as f:
                count = len(f.readlines())
            stock.append(f"{file.split('.')[0]} - {count}")
    if not stock:
        await interaction.response.send_message("No accounts in stock!", ephemeral=True)
        return

    embed = discord.Embed(
        title="Bulk Stock",
        description="\n".join(stock),
        color=0x808080
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="ustock", description="Check stock for ultra accounts.")
async def ustock(interaction: discord.Interaction):
    if interaction.channel.id != COMMAND_CHANNELS['ustock']:
        await interaction.response.send_message(f"Wrong channel! Use the command in <#{COMMAND_CHANNELS['ustock']}>.", ephemeral=True)
        return

    stock = []
    for file in os.listdir("ultra"):
        if file.endswith(".txt"):
            with open(f"ultra/{file}", 'r') as f:
                count = len(f.readlines())
            stock.append(f"{file.split('.')[0]} - {count}")
    if not stock:
        await interaction.response.send_message("No accounts in stock!", ephemeral=True)
        return

    embed = discord.Embed(
        title="Ultra Stock",
        description="\n".join(stock),
        color=0x808080
    )
    await interaction.response.send_message(embed=embed)


bot.run(TOKEN)