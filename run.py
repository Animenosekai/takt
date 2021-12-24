"""
run.py

Runner for Takt.
"""
from nasse.config import General
from nasse.logging import log

import receivers
try:
    from auth import TOKEN
except ImportError:
    from auth_heroku import TOKEN
from takt import client

General.NAME = "Takt"

if __name__ == '__main__':
    log("Starting up...")
    client.run(TOKEN)
