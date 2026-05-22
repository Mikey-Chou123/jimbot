import os
import sqlite3

import discord
import numpy as np
import pandas as pd
from discord.ext import commands
from dotenv import load_dotenv
from plotly_calplot import calplot

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#setting up sqlite3
conn = sqlite3.connect("gym.db")
cursor = conn.cursor()

#initialize table: gym_sessions
cursor.execute("""
CREATE TABLE IF NOT EXISTS gym_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person TEXT,
    date TEXT,
    duration_minutes INTEGER
)
""")
conn.commit()

@bot.event
async def on_ready():
    print("jimbot online now")


@bot.command()
async def gymmed(ctx):
    username = ctx.author.name
    streak = None
    await ctx.send(f"{username} has exercised today! Current streak:{streak}")

    # run command

    # checks username
        #if the username is not in the database yet, create it


bot.run(TOKEN)
