import discord
from discord.ext import commands
import sqlite3

TOKEN = 'MTI5NDUwNjczNjc4NjQ3MzAyMg.G3eMmT.J7KfoEqs4MWUFyA20Of97qjZlaQyfHid_pV9ps'

db = sqlite3.connect('scoreboard.db')
cursor = db.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS scores (
        user_id TEXT PRIMARY KEY,
        username TEXT,
        kills INTEGER DEFAULT 0,
        deaths INTEGER DEFAULT 0
    )
''')
db.commit()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

def update_score(user_id, username, kills=0, deaths=0):
    cursor.execute('''
        INSERT INTO scores (user_id, username, kills, deaths)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
        kills = kills + ?, deaths = deaths + ?, username = ?
    ''', (user_id, username, kills, deaths, kills, deaths, username))
    db.commit()

@bot.command()
async def snipe(ctx, target: discord.Member):
    sniper = ctx.author
    if sniper.id == target.id:
        await ctx.send("You can't snipe yourself!")
        return

    update_score(str(sniper.id), sniper.name, kills=1)
    update_score(str(target.id), target.name, deaths=1)

    await ctx.send(f"{sniper.mention} sniped {target.mention}! (+1 kill for {sniper.name}, +1 death for {target.name})")

@bot.command()
async def scoreboard(ctx):
    cursor.execute('SELECT username, kills, deaths FROM scores')
    results = cursor.fetchall()

    if not results:
        await ctx.send("The scoreboard is empty!")
        return
    scoreboard_text = "**Scoreboard:**\n"
    for username, kills, deaths in results:
        kd_ratio = kills / deaths if deaths > 0 else kills
        scoreboard_text += f"{username}: {kills} Kills, {deaths} Deaths, KD Ratio: {kd_ratio:.2f}\n"

    await ctx.send(scoreboard_text)

@bot.command()
async def reset(ctx):
    cursor.execute('DELETE FROM scores')
    db.commit()
    await ctx.send("The scoreboard has been reset!")

@bot.command()
async def reversesnipe(ctx, target: discord.Member):
    sniper = ctx.author
    if sniper.id == target.id:
        await ctx.send("You can't reverse-snipe yourself!")
        return

    reverse_snipe(str(sniper.id), kills=1)
    reverse_snipe(str(target.id), deaths=1)

    await ctx.send(f"{sniper.mention} reversed their snipe on {target.mention}. (-1 kill for {sniper.name}, -1 death for {target.name})")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
bot.run(TOKEN)
