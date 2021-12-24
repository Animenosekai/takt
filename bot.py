"""
bot.py

Initialization of Takt and event registrations
"""
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from nasse.logging import LogLevels, log
from error import error_handler

from config import COMMAND_PREFIX


async def prefix(bot, msg):
    """Defines the prefix for the bot"""
    return commands.when_mentioned_or(COMMAND_PREFIX)(bot, msg)

# DEFINING CLIENT/BOT AND ITS PREFIX
log("Defining client and slash client")
log(f"The defined prefix is '{COMMAND_PREFIX}' (or mention)")
client = commands.Bot(command_prefix=prefix, case_insensitive=True)
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    # GAME ACTIVITY
    await client.change_presence(activity=discord.Game(name=f'{COMMAND_PREFIX}help'))
    log("Takt is ready", level=LogLevels.INFO)


@client.event
async def on_connect():
    log(f"Takt is connected to Discord (latency: {round(client.latency * 1000, 2)} ms)", level=LogLevels.INFO)


@client.event
async def on_disconnect():
    log(f"Takt got disconnected from Discord", level=LogLevels.INFO)


@client.event
async def on_command_error(context, exception):
    await error_handler(context, exception)
