import discord

from discord import FFmpegOpusAudio
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.context import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from nasse.logging import LogLevels, log
from youtube_dl import YoutubeDL

from config import COMMAND_PREFIX
from error import error_handler

# DEFINING CLIENT/BOT AND ITS PREFIX
client = commands.Bot(command_prefix=COMMAND_PREFIX, case_insensitive=True)
slash = SlashCommand(client, sync_commands=True)


@client.event
async def on_ready():
    # GAME ACTIVITY
    await client.change_presence(activity=discord.Game(name='!saikihelp'))
    log("Takt is ready", level=LogLevels.INFO)


async def play(context: SlashContext, link: str):
    try:
        if context.author.voice is None:
            await context.send("You do not seem to be in a voice channel")
        if context.voice_client is None:
            await context.author.voice.channel.connect()
        else:
            await context.voice_client.move_to(context.author.voice.channel)
        context.voice_client.stop()
        with YoutubeDL({
            "format": "bestaudio",
        }) as worker:
            source = await FFmpegOpusAudio.from_probe(
                source=worker.extract_info(link, download=False)["formats"][0]["url"],
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"
            )
            context.voice_client.play(source)
    except Exception as err:
        await error_handler(context=context, error=err)


@client.command(name="play", pass_context=True)
async def play_receiver(context, link: str):
    await play(context, link)


@slash.slash(name="play",
             description="Plays the given URL in the connected voice channel",
             options=[
                 create_option(
                     name="link",
                     description="the URL of the video to play",
                     option_type=SlashCommandOptionType.STRING,
                     required=True
                 )
             ])
async def play_receiver_slash(context: SlashContext, link: str):
    await play(context=context, link=link)


# Basic API
"""
discord.VoiceClient().play
discord.VoiceClient().pause
discord.VoiceClient().average_latency
discord.VoiceClient().is_connected
discord.VoiceClient().is_paused
discord.VoiceClient().latency
discord.VoiceClient().resume
discord.VoiceClient().stop
discord.VoiceClient().is_playing
"""

# TODO
"""
queue
clear-queue
now-playing
skip
stop
"""