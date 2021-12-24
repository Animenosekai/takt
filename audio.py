from asyncio import run
from datetime import datetime

from discord.player import FFmpegOpusAudio
from nasse.logging import log
from nasse.utils.regex import is_url
from youtube_dl import YoutubeDL


class TaktAudioPlayer(FFmpegOpusAudio):
    """
    Takt's custom discord audio player
    """

    def __init__(self, info, *, bitrate=128, volume: float = 0.1, codec="nocopy", executable='ffmpeg', pipe=False, stderr=None, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options='-vn'):
        self.info = dict(info)
        self.source = self.info["url"]
        self.played = 0
        self.detailed = self.info["extractor"] == "youtube"

        if self.detailed:
            self.title = self.info["title"]
            self.description = self.info["description"]
            self.duration = self.info["duration"]
            self.view_count = self.info["view_count"]
            self.like_count = self.info["like_count"]
            self.upload_date = datetime.strptime(self.info["upload_date"], "%Y%m%d")
            self.channel = self.info["uploader"]
            self.channel_link = self.info["uploader_url"]
            self.thumbnail = self.info["thumbnail"]
        else:
            # should test afterward if anything other than youtube works
            # i could also run my own probe
            self.title = "Unknown"
            self.description = "N/A"
            self.duration = 0
            self.view_count = 0
            self.like_count = 0
            self.upload_date = datetime.now()
            self.channel = "Unknown"
            self.channel_link = None
            self.thumbnail = None

        options += f' -filter:a "volume={volume}"'
        super().__init__(self.source, bitrate=bitrate, codec=codec, executable=executable,
                         pipe=pipe, stderr=stderr, before_options=before_options, options=options)

    async def open(link, *, bitrate=128, volume: float = 0.2, codec="nocopy", executable='ffmpeg', pipe=False, stderr=None, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options='-vn'):
        with YoutubeDL({
            "format": "bestaudio",
            "noplaylist": "True"
        }) as worker:
            if is_url(link):
                info = worker.extract_info(link, download=False)
            else:
                info = worker.extract_info(f"ytsearch:{link}", download=False)["entries"][0]

        # i need to change the codec to reencode the audio
        _, bitrate = await FFmpegOpusAudio.probe(info["url"])
        return TaktAudioPlayer(info, bitrate=bitrate, volume=volume, codec=codec, executable=executable, pipe=pipe, stderr=stderr, before_options=before_options, options=options)

    def on_ended(self) -> bool:
        log(f"{self} has ended")

    def read(self):
        data = super().read()
        if data != b"":
            self.played += 20
        else:
            self.on_ended()
        return data

    def __repr__(self) -> str:
        return "TaktAudio(title={}, duration={}, played={} sec)".format(self.title, self.duration, round(self.played / 1000, 2))
