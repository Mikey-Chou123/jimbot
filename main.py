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
intents.message_content = True  # IMPORTANT

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("jimbot online now")


@bot.command()
async def gymmed(ctx):
    username = ctx.author.name
    streak = None
    await ctx.send(f"{username} has exercised today! Current streak:{streak}")


bot.run(TOKEN)
