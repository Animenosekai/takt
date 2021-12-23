from traceback import print_exc

from nasse.logging import LogLevels, log

from config import DEBUG_MODE
from exceptions import TaktException


async def error_handler(context, error):
    if DEBUG_MODE:
        print_exc()
    if isinstance(error, TaktException):
        await context.send(error.SAFE_MESSAGE.format(mention=context.author.mention))
    else:
        log("An unknown error occured: {name} {error}".format(
            name=error.__class__.__name__, error=str(error)), level=LogLevels.ERROR)
        await context.send(TaktException.SAFE_MESSAGE.format(mention=context.author.mention))
