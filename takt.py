from datetime import timedelta

import discord
from discord.ext import commands
from nasse.logging import log

from audio import TaktAudioPlayer
from bot import \
    client  # to redirect the import outside (and at the same time load takt)
from exceptions import NotInVoiceChannel, NoVoiceClient

QUEUES = {}


def human_format(number: int):
    magnitude = 0
    while abs(number) >= 1000:
        magnitude += 1
        number /= 1000
    return f"{round(number, 2)}['', 'K', 'M', 'G', 'T', 'P'][magnitude]"


def create_end_event(context: commands.Context):
    def on_ended():
        context.voice_client.stop()
        log("Song ended")
        if context.guild.id not in QUEUES:
            log("No queue for current guild")
            return
        try:
            QUEUES[context.guild.id].pop(0)
        except IndexError:
            log("Queue is empty")
            return
        if len(QUEUES[context.guild.id]) >= 1:
            log("More than one song in queue")
            log(f"Playing {QUEUES[context.guild.id][0]}")
            context.voice_client.play(QUEUES[context.guild.id][0])
    return on_ended


async def play(context: commands.Context, link: str):
    if context.author.voice is None:
        raise NotInVoiceChannel

    if context.voice_client is None:  # not connected yet to any voice channel
        await context.author.voice.channel.connect()
    else:
        await context.voice_client.move_to(context.author.voice.channel)
    # context.voice_client.stop()

    player = await TaktAudioPlayer.open(link)
    player.on_ended = create_end_event(context)

    try:
        QUEUES[context.guild.id].append(player)
    except Exception:
        QUEUES[context.guild.id] = [player]

    # print(QUEUES[context.guild.id])
    if not context.voice_client.is_playing():
        context.voice_client.play(player)
        await context.send(f"{context.author.mention} ✨ Playing {player.title}")
    else:
        await context.send(f"{context.author.mention} 🎏 Added {player.title} to the queue")


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


async def skip(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    create_end_event(context)()
    await context.send(f"{context.author.mention} Skipped the current song!")


async def queue(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    embed = discord.Embed(title='Current Queue',
                          colour=discord.Colour.blue())
    embed.add_field(name='Queue', value="\n".join(f"{i}. {player.title}" for i, player in enumerate(QUEUES[context.guild.id], 1)))

    await context.send(embed=embed)


async def clear(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    QUEUES.pop(context.guild.id, None)
    await context.send(f"{context.author.mention} Cleared the queue")


async def stop(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    QUEUES.pop(context.guild.id, None)
    context.voice_client.stop()
    await context.send(f"{context.author.mention} Stopped the music!")


async def playing(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_playing():
        embed = discord.Embed(title='Now playing', colour=discord.Colour.blue())
        if context.voice_client.source.thumbnail:
            embed.set_thumbnail(url=context.voice_client.source.thumbnail)
        embed.add_field(name='Title', value=context.voice_client.source.title)
        if context.voice_client.source.detailed:
            embed.add_field(
                name='Time', value=f"{timedelta(seconds=int(context.voice_client.source.played / 1000))}/{timedelta(seconds=context.voice_client.source.duration)}")
            embed.add_field(name='Counter', value=f"Views: {human_format(context.voice_client.source.view_count)}\nLikes: {human_format(context.voice_client.source.like_count)}")
            embed.add_field(name='Channel', value=context.voice_client.source.channel)
            # embed.add_field(name='Description', value=context.voice_client.source.description)
            embed.add_field(name='Uploaded', value=context.voice_client.source.upload_date.strftime("%d/%m/%Y"))

        await context.send(f"{context.author.mention} Now playing: {context.voice_client.source.title}", embed=embed)
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
discord.VoiceClient()
"""
