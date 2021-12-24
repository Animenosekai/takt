"""
config.py

Configuration for Takt.
"""
from nasse.utils.args import Args

COMMAND_PREFIX = "+"
DEBUG_MODE = Args.exists(("-d", "--debug"))
