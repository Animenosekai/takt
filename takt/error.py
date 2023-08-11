"""
error.py

The error handler for Takt.
"""
from nasse.logging import LoggingLevel, log, logger

from discord.ext import commands

from takt.config import DEBUG_MODE
from takt.exceptions import TaktException


async def error_handler(context, error: commands.CommandInvokeError):
    if DEBUG_MODE:
        logger.print_exception()
    if isinstance(error, commands.CommandInvokeError):
        error = error.original
    if isinstance(error, TaktException):
        await context.send(error.MESSAGE.format(mention=context.author.mention))
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        log("An unknown error occured: {name} {error}".format(
            name=error.__class__.__name__, error=str(error)), level=LoggingLevel.ERROR)
        await context.send(TaktException.MESSAGE.format(mention=context.author.mention))
