"""the core"""
import asyncio
from time import time
from datetime import timedelta

import discord
from discord.ext import commands
from nasse.logging import log, LoggingLevel

from takt.config import COMMAND_PREFIX, COOLDOWN
from takt.audio import TaktAudioPlayer
from takt.bot import \
    client  # to redirect the import outside (and at the same time load takt)
from takt.exceptions import NotInVoiceChannel, NoVoiceClient

SERVERS = {}


def decorate(func):
    async def wrapper(context: commands.Context, *args, **kwargs):
        if context.guild.id not in SERVERS:
            SERVERS[context.guild.id] = {}
        if "RATE" not in SERVERS[context.guild.id]:
            SERVERS[context.guild.id]["RATE"] = {}
        distance = time() - SERVERS[context.guild.id]["RATE"].get(context.author.id, 0)
        if distance < COOLDOWN:
            log(f"`{context.author.name}` is rate limited for now ({COOLDOWN - distance} seconds remaining)", level=LoggingLevel.INFO)
            return await context.send(f"🏮 {context.author.mention} You are rate limited for now ({round(COOLDOWN - distance, 2)} seconds remaining)")
        result = await func(context, *args, **kwargs)
        SERVERS[context.guild.id]["RATE"][context.author.id] = time()
        return result
    return wrapper


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


@decorate
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


@decorate
async def pause(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    log("Pausing")
    context.voice_client.pause()
    await context.send(f"{context.author.mention} Paused")


@decorate
async def resume(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_playing():
        await context.send(f"{context.author.mention} Already playing")
        return
    log("Resuming")
    context.voice_client.resume()
    await context.send(f"{context.author.mention} Resumed")


@decorate
async def skip(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    log("Skipping")
    loop = asyncio.get_event_loop()
    create_end_event(context, loop)()
    await context.send(f"{context.author.mention} Skipped the current song!")


@decorate
async def loop(context: commands.Context, loop: str = None):
    if context.guild.id not in SERVERS:
        SERVERS[context.guild.id] = {}
    if loop is not None:
        loop = str(loop).lower().replace(' ', '')
        if loop in ("yes", "1", "true", "enable", "active", "activate"):
            loop = True
        elif loop in ("no", "0", "false", "disable", "inactive", "deactivate"):
            loop = False
        else:
            await context.send(f"{context.author.mention} Invalid argument `{loop}`")
            return
    else:
        loop = not SERVERS.get(context.guild.id, {}).get("LOOP", False)

    if loop:
        SERVERS[context.guild.id]["LOOP"] = True
        await context.send(f"{context.author.mention} | 🔁 Loop enabled!")
    else:
        SERVERS[context.guild.id]["LOOP"] = False
        await context.send(f"{context.author.mention} | 🏮 Loop disabled")


@decorate
async def looping(context: commands.Context):
    if SERVERS.get(context.guild.id, {}).get("LOOP", False):
        await context.send(f"{context.author.mention} | 🔁 Loop is ON!")
    else:
        await context.send(f"{context.author.mention} | 🏮 Loop is OFF!")


@decorate
async def queue(context: commands.Context):
    log(f"Sending the current guild queue (guild: {context.guild.name} | {context.guild.id})")
    if len(SERVERS.get(context.guild.id, {}).get("QUEUE", [])) == 0:
        await context.send(f"{context.author.mention} The queue is empty")
        return
    embed = discord.Embed(title='Current Queue',
                          colour=discord.Colour.blue())
    embed.add_field(name='Queue', value="\n".join(f"{i}. {player.title}" for i, player in enumerate(SERVERS[context.guild.id]["QUEUE"], 1)))
    length = len(SERVERS[context.guild.id]['QUEUE'])
    footer = f"{length} song{'s' if length > 1 else ''} in queue"
    if SERVERS.get(context.guild.id, {}).get("LOOP", False):
        footer += "\n🔁 Loop enabled"
    embed.set_footer(text=footer)

    await context.send(embed=embed)


@decorate
async def clear(context: commands.Context):
    log("Clearing the queue and looping status")
    SERVERS.pop(context.guild.id, None)
    await context.send(f"{context.author.mention} Cleared the queue")


@decorate
async def stop(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    log("Stopping and clearing")
    SERVERS.pop(context.guild.id, None)
    context.voice_client.stop()
    await context.voice_client.disconnect()
    await context.send(f"{context.author.mention} Stopped the music!")


@decorate
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

        if SERVERS.get(context.guild.id, {}).get("LOOP", False):
            embed.add_field(name="Options", value="🔁 Loop enabled")

        await context.send(f'{context.author.mention} Now playing: **{context.voice_client.source.title}**', embed=embed)
    else:
        await context.send(f"{context.author.mention} Nope, nothing is being played")


@decorate
async def paused(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_paused():
        await context.send(f"{context.author.mention} It seems that the music is paused")
    else:
        await context.send(f"{context.author.mention} Nope it seems that no music is paused right now")


@decorate
async def connected(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    if context.voice_client.is_connected():
        await context.send(f"{context.author.mention} Yes I am connected")
    else:
        await context.send(f"{context.author.mention} Nope I'm not connected")


@decorate
async def latency(context: commands.Context):
    if context.voice_client is None:
        raise NoVoiceClient
    log(f"Bot Latency: {client.latency}")
    log(f"Voice Latency: {round(context.voice_client.latency * 1000, 4)} (average: {round(context.voice_client.average_latency * 1000, 4)})")
    await context.send(f"{context.author.mention} The current latency is **{round(context.voice_client.latency * 1000, 2)}ms** (average: {round(context.voice_client.average_latency * 1000, 2)}ms)")


HELP = {
    "play <search term>": {
        "msg": "Searches on YouTube and plays the first result",
        "example": "play Bad Apple",
        "aliases": ["p <search term>", "start <search term>"]
    },
    "play <link>": {
        "msg": "Play the given link",
        "example": "play https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "aliases": ["p <link>", "start <link>"]
    },
    "playing": {
        "msg": "Show the current song playing",
        "aliases": ["now", "now-playing", "nowplaying", "np"]
    },
    "pause": {
        "msg": "Pause the current song"
    },
    "resume": {
        "msg": "Resume the current song",
        "aliases": ["continue", "unpause"]
    },
    "skip": {
        "msg": "Skip the current song",
        "aliases": ["s", "next"]
    },
    "queue": {
        "msg": "Show the current queue",
        "aliases": ["q", "list", "list-queue", "listqueue", "song-queue", "songs", "musics", "songqueue"]
    },
    "clear": {
        "msg": "Clear the queue"
    },
    "stop": {
        "msg": "Stop the music and clear the queue"
    },
    "loop": {
        "msg": "Toggle looping",
        "aliases": ["repeat", "repeat-song", "repeatsong"]
    },
    "loop <true/false>": {
        "msg": "Enable or disable looping",
        "example": "loop true"
    },
    "looping": {
        "msg": "Show the current loop status",
        "aliases": ["is-looping", "islooping"]
    },
    "latency": {
        "msg": "Show the current latency"
    },
    "connected": {
        "msg": "Show if the bot is connected to a voice channel",
        "aliases": ["isconnected"]
    },
    "help": {
        "msg": "Show this message",
        "aliases": ["h", "commands", "command", "cmds", "cmd"]
    },
    "help <command>": {
        "msg": "Show specific command's help",
        "example": "help play"
    }
}

ALIASES = {}
for cmd, data in HELP.items():
    for alias in data.get("aliases", []):
        a = str(alias).replace(" ", "").lower()
        ALIASES[a] = cmd
        ALIASES[a.split("<")[0]] = cmd
    c = str(cmd).replace(" ", "").lower()
    ALIASES[c] = cmd
    ALIASES[c.split("<")[0]] = cmd


@decorate
async def help(context: commands.Context, command: str = ""):
    embed = discord.Embed(title='🏮 Help Center', colour=discord.Colour.blue())
    embed.set_author(name=f"Requested by {context.author}")
    embed.set_footer(text="© Takt by Anise")
    command = str(command).replace(" ", "").lower()
    if command == "":
        embed.add_field(name='Commands', value="\n".join(
            f"`{COMMAND_PREFIX}{cmd}`{': ' + str(data['msg']) if 'msg' in data else ''}" for cmd, data in HELP.items()))
        await context.send(embed=embed)
        return
    if command.startswith(COMMAND_PREFIX):
        command = command[1:]
    if command not in ALIASES:
        await context.send(f"{context.author.mention} I don't know that command")
        return
    command = ALIASES[command]
    data = HELP[command]
    embed.title = f"🏮 Help Center — `{COMMAND_PREFIX}{command}`"
    if 'msg' in data:
        embed.add_field(name="Description", value=data['msg'], inline=False)
    if 'example' in data:
        embed.add_field(name="Example", value="**" + COMMAND_PREFIX + data['example'] + "**", inline=False)
    if 'aliases' in data:
        embed.add_field(name="Aliases", value=", ".join(f"`{COMMAND_PREFIX}{alias}`" for alias in data['aliases']), inline=False)
    await context.send(embed=embed)
