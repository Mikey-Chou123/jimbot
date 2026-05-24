import os
import sqlite3
from datetime import date, timedelta

import discord
from discord.ext import commands
import io
from dotenv import load_dotenv
import pandas as pd
from plotly_calplot import calplot

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents) # Change the symbol to your own liking!

# ----- Database setup -----

conn = sqlite3.connect("gym.db", check_same_thread=False)
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    creation_date TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS gym_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    duration INTEGER NOT NULL,
    UNIQUE(user_id, date)
);
""")

conn.commit()

# ----- Helpers -----

def getOrCreateUser(user_id, username):
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


def getTodayTotal(user_id, today):
    cursor.execute(
        "SELECT duration FROM gym_sessions WHERE user_id = ? AND date = ?",
        (user_id, today)
    )

    row = cursor.fetchone()
    return row[0] if row else 0

def calculate_streak(user_id):
    today = date.today()
    streak = 0
    day_offset = 0

    while True:
        day = today - timedelta(days=day_offset)
        day_str = day.isoformat()

        cursor.execute("""
            SELECT duration FROM gym_sessions
            WHERE user_id = ? AND date = ?
        """, (user_id, day_str))

        row = cursor.fetchone()
        duration = row[0] if row else 0

        if duration <= 0:
            break

        streak += 1
        day_offset += 1

    return streak

def generate_heatmap(user_id):
    query = """
        SELECT date, duration AS value
        FROM gym_sessions
        WHERE user_id = ?
    """

    df = pd.read_sql_query(query, conn, params=[user_id])

    df["date"] = pd.to_datetime(df["date"]).astype("datetime64[ns]")

    fig = calplot(df, x="date", y="value", dark_theme=True)

    return fig

# ----- Commands ----- 

@bot.event
async def on_ready():
    print("jimbot online now")

@bot.event
async def on_guild_join(guild):
    channel = guild.system_channel

    if channel is None:
        for text_channel in guild.text_channels:
            if text_channel.permissions_for(guild.me).send_messages:
                channel = text_channel
                break

    if channel:
        await channel.send("Hellow I am Jimbot (gym bot), go to the gym")

# !gym_add (time)
@bot.command()
async def gym_add(ctx, duration: int):

    if duration <= 0:
        await ctx.send("Duration must be a positive integer.")
        return

    user_id = ctx.author.id
    username = ctx.author.display_name

    today = date.today()

    today_str = today.isoformat()


    # adding the duration
    cursor.execute("""
        INSERT INTO gym_sessions (user_id, date, duration)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id, date)
        DO UPDATE SET duration = duration + excluded.duration
    """, (user_id, today_str, duration))

    conn.commit()

    total = getTodayTotal(user_id, today_str)

    streak = calculate_streak(user_id)

    #final output
    await ctx.send(
            f"{username} trained {duration} min. Total today: {total} min"
            )

    # generate heatmap based on the minutes in each day
    fig = generate_heatmap(user_id)

    buf = fig.to_image(format="png")

    await ctx.send(
        file=discord.File(io.BytesIO(buf), filename="heatmap.png")
    )

    await ctx.send(
            f"\n Current streak: {streak}🔥"
            )

# !gym_remove (time)
@bot.command()
async def gym_remove(ctx, duration: int):
    
    if duration <= 0:
        await ctx.send("Duration must be a positive integer.")
        return

    user_id = ctx.author.id
    username = ctx.author.name

    today = date.today()
    today_str = today.isoformat()

    getOrCreateUser(user_id, username)

    cursor.execute("""
        INSERT INTO gym_sessions (user_id, date, duration)
        VALUES (?, ?, 0)
        ON CONFLICT(user_id, date)
        DO UPDATE SET duration = MAX(duration - ?, 0)
    """, (user_id, today_str, duration))

    conn.commit()

    total = getTodayTotal(user_id, today_str)

    if total == 0:
        await ctx.send(f"{username}, you have no time logged today to remove from.")
    else:
        await ctx.send(f"{username} removed {duration} min. Total today: {total} min")

bot.run(TOKEN)
