"""receives plain text commands from discord"""
from discord.ext import commands

from takt.bot import client
from takt.takt import (clear, connected, help, latency, loop, looping, pause,
                       paused, play, playing, queue, resume, skip, stop)


@client.command(name="play", pass_context=True, aliases=["p", "start"])
async def play_receiver(context: commands.Context, *args):
    await play(context, " ".join(args))


@client.command(name="pause", pass_context=True)
async def pause_receiver(context: commands.Context):
    await pause(context)


@client.command(name="resume", pass_context=True, aliases=["continue", "unpause"])
async def resume_receiver(context: commands.Context):
    await resume(context)


@client.command(name="stop", pass_context=True)
async def stop_receiver(context: commands.Context):
    await stop(context)


@client.command(name="playing", pass_context=True, aliases=["now", "now-playing", "nowplaying", "np"])
async def playing_receiver(context: commands.Context):
    await playing(context)


@client.command(name="paused", pass_context=True, aliases=["ispaused"])
async def paused_receiver(context: commands.Context):
    await paused(context)


@client.command(name="connected", pass_context=True, aliases=["isconnected"])
async def connected_receiver(context: commands.Context):
    await connected(context)


@client.command(name="latency", pass_context=True)
async def latency_receiver(context: commands.Context):
    await latency(context)


@client.command(name="queue", pass_context=True, aliases=["q", "list", "list-queue", "listqueue", "song-queue", "songs", "musics", "songqueue"])
async def queue_receiver(context: commands.Context):
    await queue(context)


@client.command(name="skip", pass_context=True, aliases=["s", "next"])
async def skip_receiver(context: commands.Context):
    await skip(context)


@client.command(name="clear", pass_context=True)
async def clear_receiver(context: commands.Context):
    await clear(context)


@client.command(name="loop", pass_context=True, aliases=["repeat", "repeat-song", "repeatsong"])
async def loop_receiver(context: commands.Context, *args):
    await loop(context, " ".join(args))


@client.command(name="looping", pass_context=True, aliases=["is-looping", "islooping"])
async def looping_receiver(context: commands.Context):
    await looping(context)

client.remove_command("help")


@client.command(name="help", pass_context=True, aliases=["h", "commands", "command", "cmds", "cmd"])
async def help_receiver(context: commands.Context, *args):
    await help(context, " ".join(args))
