from discord.ext import commands
import youtube_dl

class Music(commands.Cog):

    def __init__(self, client) -> None:
        self.client = client

    @commands.command()
    async def play():
        pass