"""
error.py

The error handler for Takt.
"""
from traceback import print_exc

from nasse.logging import LogLevels, log

from discord.ext import commands

from config import DEBUG_MODE
from exceptions import TaktException


async def error_handler(context, error: commands.CommandInvokeError):
    if DEBUG_MODE:
        print_exc()
    if isinstance(error, commands.CommandInvokeError):
        error = error.original
    if isinstance(error, TaktException):
        await context.send(error.MESSAGE.format(mention=context.author.mention))
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        log("An unknown error occured: {name} {error}".format(
            name=error.__class__.__name__, error=str(error)), level=LogLevels.ERROR)
        await context.send(TaktException.MESSAGE.format(mention=context.author.mention))
