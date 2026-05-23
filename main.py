import os
import sqlite3
from datetime import date, timedelta

import discord
from discord.ext import commands
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from plotly_calplot import calplot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents) # Change the symbol to your own liking!

# ----- Database setup -----

conn = sqlite3.connect("gym.db")
cursor = conn.cursor()

cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
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
            UNIQUE(user_id, date)
        )
        """)

conn.commit()

# ----- Helpers -----

def get_or_create_user(user_id, username):
    cursor.execute(
        "SELECT 1 FROM users WHERE user_id = ?",
        (user_id,)
    )

    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (user_id, username, creation_date) VALUES (?, ?, ?)",
            (user_id, username, date.today().isoformat())
        )
        conn.commit()


def get_today_total(user_id, today):
    cursor.execute(
        "SELECT duration FROM gym_sessions WHERE user_id = ? AND date = ?",
        (user_id, today)
    )
    row = cursor.fetchone()
    return row[0] if row else 0


# ----- Commands ----- 

@bot.event
async def on_ready():
    print("jimbot online now")

async def on_guild_join(guild):
    channel = guild.system_channel

    if channel is None:
        for text_channels in guild.text_channels:
            if text_channels.permissions_for(guild.me).send_messages:
                channel = text_channels
                break

    if channel:
        await channel.send("Hellow I am Jimbot (gym bot), go to the gym")

# !gym_add (time)
@bot.command()
async def gym_add(ctx, duration: int):

    streak = 0

    user_id = ctx.author.id
    username = ctx.author.name
    today = date.today().isoformat()

    get_or_create_user(user_id, username)

    cursor.execute("""
        INSERT INTO gym_sessions (user_id, date, duration)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, date)
        DO UPDATE SET duration = duration + excluded.duration
    """, (user_id, today, duration))

    conn.commit()

    total = get_today_total(user_id, today)

    await ctx.send(
            f"{username} trained {duration} min. Total today: {total} min 🗿"
            f"\n Current streak: {streak}"
    )

    # generate heatmap based on the minutes in each day

# !gym_remove (time)
@bot.command()
async def gym_remove(ctx, duration: int):

    user_id = ctx.author.id
    username = ctx.author.name
    today = date.today().isoformat()

    get_or_create_user(user_id, username)

    cursor.execute("""
        INSERT INTO gym_sessions (user_id, date, duration)
        VALUES (?, ?, 0)
        ON CONFLICT(user_id, date)
        DO UPDATE SET duration = MAX(duration - ?, 0)
    """, (user_id, today, duration))

    conn.commit()

    total = get_today_total(user_id, today)

    await ctx.send(
        f"{username} removed {duration} min. Total today: {total} min"
    )

bot.run(TOKEN)
