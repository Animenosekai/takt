from bot import slash
from discord_slash.utils.manage_commands import create_option
from discord_slash.model import SlashCommandOptionType

from takt import play, pause, resume, stop, playing, paused, connected, latency, queue, skip, clear


@slash.slash(name="play",
             description="Plays the given URL in the connected voice channel",
             options=[
                 create_option(
                     name="link",
                     description="The URL or a search term of the video to play",
                     option_type=SlashCommandOptionType.STRING,
                     required=True
                 )
             ])
async def play_receiver_slash(context, link: str):
    await play(context=context, link=link)
