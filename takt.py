import discord_slash
from discord import FFmpegOpusAudio
from discord.ext import commands
from nasse.logging import log
from nasse.utils.regex import is_url
from youtube_dl import YoutubeDL

from exceptions import NotInVoiceChannel
from bot import client, slash


async def play(context: commands.Context, link: str):
    if context.author.voice is None:
        raise NotInVoiceChannel

    if context.voice_client is None:  # not connected yet to any voice channel
        await context.author.voice.channel.connect()
    else:
        await context.voice_client.move_to(context.author.voice.channel)
    context.voice_client.stop()

    with YoutubeDL({
        "format": "bestaudio",
        "noplaylist": "True"
    }) as worker:
        if is_url(link):
            source = await FFmpegOpusAudio.from_probe(
                source=worker.extract_info(link, download=False)["formats"][0]["url"],
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"
            )
        else:
            source = await FFmpegOpusAudio.from_probe(
                source=worker.extract_info(f"ytsearch:{link}", download=False)["entries"][0]["url"],
                before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                options="-vn"
            )
        context.voice_client.play(source)


@client.command(name="play", pass_context=True)
async def play_receiver(context: commands.Context, link: str):
    await play(context, str(context.message).split()[1:])


@slash.slash(name="play",
             description="Plays the given URL in the connected voice channel",
             options=[
                 discord_slash.utils.manage_commands.create_option(
                     name="link",
                     description="the URL of the video to play",
                     option_type=discord_slash.model.SlashCommandOptionType.STRING,
                     required=True
                 )
             ])
async def play_receiver_slash(context, link: str):
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
