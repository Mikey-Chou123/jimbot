import os
import sqlite3

import discord
import numpy as np
import pandas as pd
from datetime import date
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
    person TEXT NOT NULL,
    date TEXT NOT NULL,
    duration_minutes INTEGER NOT NULL
)
""")
conn.commit()

@bot.event
async def on_ready():
    print("jimbot online now")


@bot.command()
async def gymmed(ctx, duration: int):

    username = ctx.author.name
    today = date.today().isoformat()

    streak = 0

    # connect to database

    # check if username exists

    # if user does not exist:
        # create user entry

    # insert today's gym session (duration)

    # calculate streak

    # generate heatmap

    await ctx.send(f" {today} {username} has exercised for {duration} minutes. Current daily streak: {streak}")
bot.run(TOKEN)





