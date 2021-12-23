from nasse.exceptions import NasseException


class TaktException(NasseException):
    SAFE_MESSAGE = "{mention} ❌ An error occured while processing your request"

    def __init__(self, message: str = None, *args: object) -> None:
        super().__init__(message=message, *args)
