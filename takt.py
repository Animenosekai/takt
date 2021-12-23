import discord
from discord import FFmpegOpusAudio
from discord.ext import commands
from nasse.logging import log
from nasse.utils.regex import is_url
from youtube_dl import YoutubeDL

from bot import client  # to redirect the import outside (and at the same time load takt)

from exceptions import NoVoiceClient, NotInVoiceChannel


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


async def pause(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    context.voice_client.pause()
    await context.send(f"{context.author.mention} Paused")


async def resume(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_playing():
        await context.send(f"{context.author.mention} Already playing")
        return
    context.voice_client.resume()
    await context.send(f"{context.author.mention} Resumed")


async def stop(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    context.voice_client.stop()
    await context.send(f"{context.author.mention} Stopped the music!")


async def playing(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_playing():
        await context.send(f"{context.author.mention} It seems that something is being played")
    else:
        await context.send(f"{context.author.mention} Nope, nothing is being played")


async def paused(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_paused():
        await context.send(f"{context.author.mention} It seems that the music is paused")
    else:
        await context.send(f"{context.author.mention} Nope it seems that no music is paused right now")


async def connected(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_connected():
        await context.send(f"{context.author.mention} Yes I am connected")
    else:
        await context.send(f"{context.author.mention} Nope I'm not connected")


async def latency(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient

    await context.send(f"{context.author.mention} The current latency is {round(context.voice_client.latency * 1000, 2)} (average: {round(context.voice_client.average_latency * 1000, 2)})")


# Basic API
"""
discord.VoiceClient().play
"""

# TODO
"""
queue
clear-queue
now-playing
skip
stop
"""
