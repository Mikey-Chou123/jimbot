import os
import sqlite3
from datetime import date

import discord
import numpy as np
import pandas as pd
from discord.ext import commands
from dotenv import load_dotenv
from plotly_calplot import calplot

# discord side setup
load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

# Change the symbol to your own liking!
bot = commands.Bot(command_prefix="!", intents=intents)

# Database setup
conn = sqlite3.connect('gym.db')
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS gym_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL
        person TEXT NOT NULL,
        date TEXT NOT NULL,
        duration INTEGER NOT NULL
    )
""")

conn.commit()


# codinggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg :)
@bot.event
async def on_ready():
    print("jimbot online now")


@bot.command()
async def gymmed(ctx, duration: int):

    user_id = ctx.author.id
    today = date.today().isoformat()
    streak = 0

    # check if username exists

    # if user does not exist:
    # create user entry

    # insert today's gym session (duration)

    # calculate streak

    await ctx.send(
        f" {today} {ctx.author.name} has exercised for {duration} minutes. Current daily streak: {streak}"
    )

    # generate heatmap


bot.run(TOKEN)
