import os
import sqlite3
from datetime import date, timedelta

import discord
from discord.ext import commands
from dotenv import load_dotenv

# heatmap creation
import numpy as np
import pandas as pd
from plotly_calplot import calplot

# discord side setup

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

# Change the symbol to your own liking!
bot = commands.Bot(command_prefix="!", intents=intents)

# Database setup
conn = sqlite3.connect("gym.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT NOT NULL,
        creation_date TEXT NOT NULL
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS gym_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        duration INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(user_id)
    )
""")

conn.commit()


def get_or_create_user(user_id, name):
    cursor.execute("SELECT EXISTS(SELECT 1 FROM users WHERE user_id = ?)", (user_id,))

    if not cursor.fetchone()[0]:
        cursor.execute(
            "INSERT INTO users (user_id, username, creation_date) VALUES (?, ?, ?)",
            (user_id, name, date.today().isoformat())
        )
        conn.commit()

# codinggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg :)
@bot.event
async def on_ready():
    print("jimbot online now")


@bot.command()
#TODO: give users a hint that its in minutes
async def gymmed(ctx, duration: int):

    user_id = ctx.author.id
    username = ctx.author.name
    today = date.today().isoformat()

    # check if username exists
    get_or_create_user(user_id, username)

    # insert a gym session (duration)
    cursor.execute(
            """
            INSERT INTO gym_sessions(user_id, date, duration) VALUES (?, ?, ?)
            """, (user_id, today, duration)
            )

    # calculate totalDuration
    totalDuration = 0
    totalDuration += duration

    # calculate streak
    streak = 0

    await ctx.send(
        f" {today} {username} has exercised for {totalDuration} minutes. Current daily streak: {streak}"
    )

    # generate heatmap


bot.run(TOKEN)
