"""
exceptions.py

Exceptions models for Takt.
"""

from nasse.exceptions import NasseException


class TaktException(NasseException):
    # NasseException already handles the logging
    MESSAGE = "{mention} ❌ An error occured while processing your request"

    def __init__(self, message: str = None, *args: object) -> None:
        super().__init__(message=message, *args)


class NotInVoiceChannel(TaktException):
    MESSAGE = "{mention} ❌ You do not seem to be in a voice channel"
