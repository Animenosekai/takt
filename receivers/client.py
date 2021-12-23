from discord.ext import commands
from bot import client

from takt import play, pause, resume, stop, playing, paused, connected, latency


@client.command(name="play", pass_context=True)
async def play_receiver(context: commands.Context, *args):
    await play(context, " ".join(args))

@client.command(name="pause", pass_context=True)
async def pause_receiver(context: commands.Context):
    await pause(context)

@client.command(name="resume", pass_context=True)
async def resume_receiver(context: commands.Context):
    await resume(context)

@client.command(name="stop", pass_context=True)
async def stop_receiver(context: commands.Context):
    await stop(context)

@client.command(name="playing", pass_context=True)
async def playing_receiver(context: commands.Context):
    await playing(context)

@client.command(name="paused", pass_context=True)
async def paused_receiver(context: commands.Context):
    await paused(context)

@client.command(name="connected", pass_context=True)
async def connected_receiver(context: commands.Context):
    await connected(context)

@client.command(name="latency", pass_context=True)
async def latency_receiver(context: commands.Context):
    await latency(context)
