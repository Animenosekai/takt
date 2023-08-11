"""receives slash commands from discord"""
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option

from takt.bot import slash
from takt.takt import (clear, connected, latency, loop, looping, pause, paused,
                       play, playing, queue, resume, skip, stop)


@slash.slash(name="play",
             description="Plays the given URL in the connected voice channel",
             options=[
                 create_option(
                     name="link",
                     description="The URL or a search term of the song to play",
                     option_type=SlashCommandOptionType.STRING,
                     required=True
                 )
             ])
async def play_receiver_slash(context, link: str):
    await play(context=context, link=link)


@slash.slash(name="pause",
             description="Pauses the currently playing song")
async def pause_receiver_slash(context):
    await pause(context=context)


@slash.slash(name="resume", description="Resumes the current song")
async def resume_receiver_slash(context):
    await resume(context=context)


@slash.slash(name="stop", description="Stops the current song")
async def stop_receiver_slash(context):
    await stop(context=context)


@slash.slash(name="playing", description="Shows the currently playing song")
async def playing_receiver_slash(context):
    await playing(context=context)


@slash.slash(name="queue", description="Shows the current queue")
async def queue_receiver_slash(context):
    await queue(context=context)


@slash.slash(name="skip", description="Skips the current song")
async def skip_receiver_slash(context):
    await skip(context=context)


@slash.slash(name="clear", description="Clears the current queue")
async def clear_receiver_slash(context):
    await clear(context=context)


@slash.slash(name="loop", description="Loops the current song")
async def loop_receiver_slash(context):
    await loop(context=context)
