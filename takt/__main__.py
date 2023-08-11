"""
Runner for Takt
"""
import argparse
import os

from nasse.logging import log, logger

logger.config.name = "takt"
DEFAULT_ENV = "TAKT_DISCORD_BOT_TOKEN"


def entry():
    """the CLI entrypoint"""
    parser = argparse.ArgumentParser("takt", description="Power your discord calls with music 🎐")
    parser.add_argument("--version", "-v", action="version", version="1.0")
    parser.add_argument("--token", "-t", action="store",
                        help=f"the discord bot token to use (the `{DEFAULT_ENV}` env var is used by default)", required=False, default=None)
    parser.add_argument("--prefix", "--command-prefix", "-p", action="store",
                        help="the prefix for the different commands", default="+", required=False)
    parser.add_argument("--debug", "-d", action="store_true", help="enabling debug logging")
    parser.add_argument("--cooldown", "-c", action="store", type=float, help="the cooldown between each command (per user) (in sec.)", default=1)

    args = parser.parse_args()
    from takt import config

    logger.config.debug = args.debug

    config.COMMAND_PREFIX = args.prefix
    config.DEBUG_MODE = args.debug
    config.COOLDOWN = args.cooldown

    from takt import takt
    from takt.receivers import client as _  # loading the receivers
    from takt.receivers import slash as _

    log("Starting up...")
    takt.client.run(args.token or os.environ[DEFAULT_ENV])


if __name__ == '__main__':
    entry()
