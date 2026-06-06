import discord
from discord.ext import commands
from datetime import datetime
import os

TOKEN = os.getenv("DISCORD_TOKEN")

# Your channel ID
TARGET_CHANNEL_ID = 1394026213747593236

# Only enable the intents we actually need
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

reaction_log = []


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(f"Tracking channel: {TARGET_CHANNEL_ID}")


@bot.event
async def on_message(message):
    # Ignore messages from bots
    if message.author.bot:
        return

    print(f"MESSAGE: {message.author} -> {message.content}")

    await bot.process_commands(message)


@bot.event
async def on_raw_reaction_add(payload):

    # Only monitor the chosen channel
    if payload.channel_id != TARGET_CHANNEL_ID:
        return

    guild = bot.get_guild(payload.guild_id)

    if guild is None:
        return

    member = guild.get_member(payload.user_id)

    if member is None:
        return

    # Ignore bot reactions
    if member.bot:
        return

    entry = {
        "position": len(reaction_log) + 1,
        "name": member.display_name,
        "emoji": str(payload.emoji),
        "time": datetime.now().strftime("%H:%M:%S")
    }

    reaction_log.append(entry)

    print(
        f"{entry['position']}. "
        f"{entry['name']} "
        f"reacted with {entry['emoji']} "
        f"at {entry['time']}"
    )


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


@bot.command()
async def entries(ctx):

    if not reaction_log:
        await ctx.send("No reactions logged yet.")
        return

    lines = []

    for entry in reaction_log:
        lines.append(
            f"{entry['position']}. "
            f"{entry['name']} - "
            f"{entry['emoji']} "
            f"({entry['time']})"
        )

    output = "\n".join(lines)

    # Discord message limit
    if len(output) > 1900:
        await ctx.send("Too many entries to display.")
    else:
        await ctx.send(f"```{output}```")


@bot.command()
async def clearentries(ctx):
    reaction_log.clear()
    await ctx.send("Reaction log cleared.")


bot.run(TOKEN)
