
import os
import sqlite3
import discord
from discord.ext import commands

TOKEN = os.getenv("DISCORD_TOKEN")
DB = "gsa_members.db"

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

def setup_db():
    with sqlite3.connect(DB) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS members (
                user_id INTEGER PRIMARY KEY,
                member_number INTEGER UNIQUE NOT NULL
            )
        """)

def get_member_id(user_id):
    with sqlite3.connect(DB) as conn:
        row = conn.execute(
            "SELECT member_number FROM members WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        if row:
            return row[0]

        next_id = conn.execute(
            "SELECT COALESCE(MAX(member_number), 0) + 1 FROM members"
        ).fetchone()[0]

        conn.execute(
            "INSERT INTO members VALUES (?, ?)",
            (user_id, next_id)
        )
        return next_id

async def assign_member(member):
    number = get_member_id(member.id)
    member_id = f"GSA-{number:03d}"
    nickname = f"{member_id} | {member.name}"[:32]

    try:
        await member.edit(nick=nickname, reason="GSA Member ID")
    except discord.Forbidden:
        print(f"Cannot change nickname for {member}")

    return member_id

@bot.event
async def on_ready():
    setup_db()
    await bot.tree.sync()
    print(f"GSA Bot online: {bot.user}")

@bot.event
async def on_member_join(member):
    member_id = await assign_member(member)
    print(f"New member: {member_id}")

@bot.tree.command(name="memberid", description="Check your GSA Member ID")
async def memberid(interaction: discord.Interaction):
    number = get_member_id(interaction.user.id)
    await interaction.response.send_message(
        f"Your GSA Member ID: **GSA-{number:03d}**",
        ephemeral=True
    )

if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")

bot.run(TOKEN)

