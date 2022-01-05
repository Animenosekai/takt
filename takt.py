import asyncio
from datetime import timedelta

import discord
from discord.ext import commands
from nasse.logging import log

from audio import TaktAudioPlayer
from bot import \
    client  # to redirect the import outside (and at the same time load takt)
from exceptions import NotInVoiceChannel, NoVoiceClient

SERVERS = {}


def human_format(number: int):
    magnitude = 0
    while abs(number) >= 1000:
        magnitude += 1
        number /= 1000
    return f"{round(number, 2)}{['', 'K', 'M', 'B', 'T', 'P'][magnitude]}"


def create_end_event(context: commands.Context, loop: asyncio.events.AbstractEventLoop):
    def on_ended():
        if context.voice_client:
            context.voice_client.stop()
            log("Song ended")
            if context.guild.id not in SERVERS:
                log("No queue for current guild")
                return
            QUEUE = SERVERS[context.guild.id].get("QUEUE", [])
            try:
                now_playing = QUEUE.pop(0)
            except IndexError:
                log("Queue is empty")
                asyncio.run_coroutine_threadsafe(context.voice_client.disconnect(), loop)
                return

            if SERVERS[context.guild.id].get("LOOP", False):  # loop mechanism
                new = now_playing.new()
                new.on_ended = create_end_event(context, loop)
                QUEUE.append(new)

            if len(QUEUE) >= 1:
                log("More than one song in queue")
                log(f"Playing {QUEUE[0]}")
                context.voice_client.play(QUEUE[0])
            else:
                log("No more songs in queue")
                asyncio.run_coroutine_threadsafe(context.voice_client.disconnect(), loop)
                asyncio.run_coroutine_threadsafe(context.send("🛫 No more songs in queue, exiting..."), loop)
    return on_ended


async def play(context: commands.Context, link: str):
    if context.author.voice is None:
        raise NotInVoiceChannel

    if context.voice_client is None:  # not connected yet to any voice channel
        log("Connecting to voice channel")
        await context.author.voice.channel.connect()
    else:
        log("Moving to new channel")
        await context.voice_client.move_to(context.author.voice.channel)
    # context.voice_client.stop()

    player = await TaktAudioPlayer.open(link)
    loop = asyncio.get_event_loop()
    player.on_ended = create_end_event(context, loop)

    if context.guild.id not in SERVERS:
        SERVERS[context.guild.id] = {}

    try:
        SERVERS[context.guild.id]["QUEUE"].append(player)
    except Exception:
        SERVERS[context.guild.id]["QUEUE"] = [player]

    if not context.voice_client.is_playing():
        context.voice_client.play(player)
        log(f"Playing {player}")
        await context.send(f'{context.author.mention} | ✨ Playing **"{player.title}"**')
    else:
        log(f"Adding {player} to queue")
        await context.send(f'{context.author.mention} | 🎏 Added **"{player.title}"** to the queue')


async def pause(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    log("Pausing")
    context.voice_client.pause()
    await context.send(f"{context.author.mention} Paused")


async def resume(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_playing():
        await context.send(f"{context.author.mention} Already playing")
        return
    log("Resuming")
    context.voice_client.resume()
    await context.send(f"{context.author.mention} Resumed")


async def skip(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    log("Skipping")
    loop = asyncio.get_event_loop()
    create_end_event(context, loop)()
    await context.send(f"{context.author.mention} Skipped the current song!")


async def loop(context: commands.Context):
    if context.guild.id not in SERVERS:
        SERVERS[context.guild.id] = {}
    if SERVERS.get(context.guild.id, {}).get("LOOP", False):
        SERVERS[context.guild.id]["LOOP"] = False
        await context.send(f"{context.author.mention} | 🏮 Loop disabled")
    else:
        SERVERS[context.guild.id]["LOOP"] = True
        await context.send(f"{context.author.mention} | 🔁 Loop enabled!")


async def looping(context: commands.Context):
    if SERVERS.get(context.guild.id, {}).get("LOOP", False):
        await context.send(f"{context.author.mention} | 🔁 Loop is ON!")
    else:
        await context.send(f"{context.author.mention} | 🏮 Loop is OFF!")


async def queue(context: commands.Context):
    log(f"Sending the current guild queue (guild: {context.guild.name} | {context.guild.id})")
    if len(SERVERS.get(context.guild.id, {}).get("QUEUE", [])) == 0:
        await context.send(f"{context.author.mention} The queue is empty")
        return
    embed = discord.Embed(title='Current Queue',
                          colour=discord.Colour.blue())
    embed.add_field(name='Queue', value="\n".join(f"{i}. {player.title}" for i, player in enumerate(SERVERS[context.guild.id]["QUEUE"], 1)))

    await context.send(embed=embed)


async def clear(context: commands.Context):
    log("Clearing the queue and looping status")
    SERVERS.pop(context.guild.id, None)
    await context.send(f"{context.author.mention} Cleared the queue")


async def stop(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    log("Stopping and clearing")
    SERVERS.pop(context.guild.id, None)
    context.voice_client.stop()
    await context.voice_client.disconnect()
    await context.send(f"{context.author.mention} Stopped the music!")


async def playing(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_playing():
        log("Creating and sending the 'Now Playing' embed")
        if context.voice_client.source.url:
            embed = discord.Embed(title='Now playing', colour=discord.Colour.blue(), url=context.voice_client.source.url)
        else:
            embed = discord.Embed(title='Now playing', colour=discord.Colour.blue())
        if context.voice_client.source.thumbnail:
            embed.set_thumbnail(url=context.voice_client.source.thumbnail)

        embed.add_field(name='Title', value=context.voice_client.source.title)
        if context.voice_client.source.duration:
            embed.add_field(
                name='Time', value=f"{timedelta(seconds=int(context.voice_client.source.played / 1000))}/{timedelta(seconds=int(context.voice_client.source.duration))}")
        else:
            embed.add_field(name='Time', value=str(timedelta(seconds=int(context.voice_client.source.played / 1000))))
        if context.voice_client.source.view_count:
            value = f"Views: {human_format(context.voice_client.source.view_count)}"
            if context.voice_client.source.like_count:
                value += f"\nLikes: {human_format(context.voice_client.source.like_count)}"
            embed.add_field(name='Counter', value=value)
        elif context.voice_client.source.like_count:
            embed.add_field(name='Counter', value=f"Likes: {human_format(context.voice_client.source.like_count)}")
        if context.voice_client.source.channel:
            embed.add_field(name='Channel', value=context.voice_client.source.channel)
        # embed.add_field(name='Description', value=context.voice_client.source.description)
        if context.voice_client.source.upload_date:
            embed.add_field(name='Uploaded', value=context.voice_client.source.upload_date.strftime("%d/%m/%Y"))

        await context.send(f'{context.author.mention} Now playing: **{context.voice_client.source.title}**', embed=embed)
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
    log(f"Bot Latency: {client.latency}")
    log(f"Voice Latency: {round(context.voice_client.latency * 1000, 4)} (average: {round(context.voice_client.average_latency * 1000, 4)})")
    await context.send(f"{context.author.mention} The current latency is **{round(context.voice_client.latency * 1000, 2)}ms** (average: {round(context.voice_client.average_latency * 1000, 2)}ms)")


# Basic API
"""
discord.VoiceClient().disconnect()
"""
