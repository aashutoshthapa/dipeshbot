import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import asyncio
import os
from dotenv import load_dotenv
import json

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='.', intents=intents)

# === Google Sheets Setup ===
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

gcp_creds_json = os.getenv("GCP_CREDS_JSON")
if gcp_creds_json:
    creds_dict = json.loads(gcp_creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.getenv("GOOGLE_CREDS_FILE"), scope)
client = gspread.authorize(creds)

sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1BJQGOS6uiy_urusrf4ZvMbYL6-A0KDtgczNWKpmnCDk/edit")
worksheet = sheet.get_worksheet(0)  # First sheet (index 0)

# === Signup Command ===
@bot.command()
async def signup(ctx):
    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel

    async def ask(prompt):
        await ctx.send(prompt)
        try:
            return (await bot.wait_for("message", check=check, timeout=600)).content
        except asyncio.TimeoutError:
            await ctx.send(f"⏰ {ctx.author.mention}, you took too long to reply. Please restart using `.signup` and respond within 10 minutes.")
            raise

    try:
        team_name = await ask("📝 What is your **team name**?")
        clan_tag = await ask("🏰 What is your **clan tag**?")
        username = str(ctx.author)

        th_tags = {}
        for th in [15, 14, 13, 12, 11]:
            tag = await ask(f"🔰 Please enter the **TH{th} player tag**:")
            th_tags[f"th{th}"] = tag

        subs = {"15sub": "", "14sub": "", "13sub": "", "12sub": "", "11sub": ""}
        while True:
            answer = await ask("➕ Do you want to add a sub? (yes/no)")
            if answer.lower() == "no":
                break
            sub_th = await ask("🏷 What is the sub's **Townhall level**? (e.g., 13)")
            if sub_th not in ["15", "14", "13", "12", "11"]:
                await ctx.send("⚠️ Invalid TH level. Try again.")
                continue
            sub_tag = await ask(f"🔁 Enter **TH{sub_th} sub player tag**:")
            subs[f"{sub_th}sub"] = sub_tag

        # Prepare final row
        row = [
            team_name,            # A
            clan_tag,             # B
            username,             # C
            th_tags["th15"],      # D
            th_tags["th14"],      # E
            th_tags["th13"],      # F
            th_tags["th12"],      # G
            th_tags["th11"],      # H
            subs["15sub"],        # I
            subs["14sub"],        # J
            subs["13sub"],        # K
            subs["12sub"],        # L
            subs["11sub"]         # M
        ]

        worksheet.append_row(row)
        await ctx.send("✅ **Registration complete!** Your team has been added to the sheet.")

    except asyncio.TimeoutError:
        return  # Timeout already handled in `ask`

# === Run Bot ===
bot.run(os.getenv("DISCORD_TOKEN"))