"""manages audio on takt"""
from datetime import datetime

from discord.player import FFmpegOpusAudio
from nasse.logging import log
from nasse.utils.types import URL
from youtube_dl import YoutubeDL as YouTubeDL
from yt_dlp import YoutubeDL as YouTubeDL_P

from takt.exceptions import DownloadError


class TaktAudioPlayer(FFmpegOpusAudio):
    """
    Takt's custom discord audio player
    """

    def __init__(self, info, *, bitrate=128, volume: float = 0.1, codec="nocopy", executable='ffmpeg', pipe=False, stderr=None, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options='-vn'):
        self.info = dict(info)
        self.source = self.info["url"]
        self.played = 0

        # infos
        self.url = self.info.get("webpage_url", None)
        self.title = self.info.get("title", "(Unknown Title)")
        self.description = self.info.get("description", None)
        self.duration = self.info.get("duration", None)  # could have my own probe
        self.view_count = self.info.get("view_count", None)
        self.like_count = self.info.get("like_count", None)
        if "upload_date" in self.info:
            self.upload_date = datetime.strptime(self.info["upload_date"], "%Y%m%d")
        else:
            self.upload_date = None
        self.channel = self.info.get("uploader", None)
        self.channel_link = self.info.get("uploader", None)
        self.thumbnail = self.info.get("thumbnail", None)

        # other
        self.bitrate = bitrate
        self.volume = volume
        self.codec = codec
        self.executable = executable
        self.pipe = pipe
        self.stderr = stderr
        self.before_options = before_options
        self.options = options

        log(f"Setting the volume to {volume}")
        options += f' -filter:a "volume={volume}"'
        super().__init__(self.source, bitrate=bitrate, codec=codec, executable=executable,
                         pipe=pipe, stderr=stderr, before_options=before_options, options=options)

        log(f"Created {self}")

    async def open(link, *, bitrate=128, volume: float = 0.2, codec="nocopy", executable='ffmpeg', pipe=False, stderr=None, before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5", options='-vn'):
        log(f"Creating a new TaktAudioPlayer with {link}")
        info = None
        for WORKER in (YouTubeDL_P, YouTubeDL):
            try:
                with WORKER({
                    "format": "bestaudio",
                    "noplaylist": "True"
                }) as worker:
                    if URL.REGEX and URL.REGEX.match(link):
                        info = worker.extract_info(link, download=False)
                    else:
                        info = worker.extract_info(f"ytsearch:{link}", download=False)["entries"][0]
                log("Found info")
                break
            except Exception:
                continue
        if info is None:
            raise DownloadError

        # i need to change the codec to reencode the audio
        _, bitrate = await FFmpegOpusAudio.probe(info["url"])
        log(f"Found Bitrate: {bitrate}")
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

    def new(self):
        return TaktAudioPlayer(self.info, bitrate=self.bitrate, volume=self.volume, codec=self.codec, executable=self.executable, pipe=self.pipe, stderr=self.stderr, before_options=self.before_options, options=self.options)
