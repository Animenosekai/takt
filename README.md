# takt

<img align="right" src="./assets/icon_cosette.png" height="220px">

***Power your discord calls with music 🎐***

<br>
<br>

[![PyPI version](https://badge.fury.io/py/takt.svg)](https://pypi.org/project/takt/)
[![Downloads](https://static.pepy.tech/personalized-badge/takt?period=total&units=international_system&left_color=grey&right_color=blue&left_text=Total%20Downloads)](https://pepy.tech/project/takt)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/takt)](https://pypistats.org/packages/takt)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/takt)](https://pypi.org/project/takt/)
[![PyPI - Status](https://img.shields.io/pypi/status/takt)](https://pypi.org/project/takt/)
[![GitHub - License](https://img.shields.io/github/license/Animenosekai/takt)](https://github.com/Animenosekai/takt/blob/master/LICENSE)
[![GitHub top language](https://img.shields.io/github/languages/top/Animenosekai/takt)](https://github.com/Animenosekai/takt)
[![CodeQL Checks Badge](https://github.com/Animenosekai/takt/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/Animenosekai/takt/actions/workflows/codeql-analysis.yml)
![Code Size](https://img.shields.io/github/languages/code-size/Animenosekai/takt)
![Repo Size](https://img.shields.io/github/repo-size/Animenosekai/takt)
![Issues](https://img.shields.io/github/issues/Animenosekai/takt)

## Index

- [Index](#index)
- [Purpose](#purpose)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
- [Installing](#installing)
  - [Option 1: From PyPI](#option-1-from-pypi)
  - [Option 2: From Git](#option-2-from-git)
  - [FFmpeg](#ffmpeg)
- [Usage](#usage)
  - [CLI](#cli)
    - [Running](#running)
    - [Prefix](#prefix)
    - [More](#more)
  - [Invite](#invite)
  - [Discord](#discord)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [Built With](#built-with)
- [Authors](#authors)
- [Licensing](#licensing)

## Purpose

`takt` is a simple, lightweight and privacy-focused music bot for your [Discord](http://discord.com) servers.

You are just a few seconds away from having your own private music discord bot !

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Prerequisites

You will need Python 3 to use this module

```bash
Minimum required versions: 3.8
```

Although the code itself is made compatible with Python >=3.6, the dependencies require at least Python 3.8.

Always check if your Python version works with `takt` before using it in production.

## Installing

### Option 1: From PyPI

```bash
pip install --upgrade takt
```

> This will install the latest version from PyPI

### Option 2: From Git

```bash
pip install --upgrade git+https://github.com/Animenosekai/takt.git
```

> This will install the latest development version from the git repository

You can check if you successfully installed it by printing out its version:

```bash
$ takt --version
1.0
```

### FFmpeg

You also need [`ffmpeg`](http://ffmpeg.org) installed on your computer to be able to run `takt` properly.

## Usage

### CLI

#### Running

Running takt is dead simple:

```bash
takt --token=<YOUR DISCORD TOKEN>
```

And this is even easier if you set the `TAKT_DISCORD_BOT_TOKEN` environment variable:

```bash
takt
```

> **Note**  
> You could also try hosting your bot on Heroku directly by using this repository since it already has a [`Procfile`](https://github.com/Animenosekai/takt/blob/main/Procfile)

#### Prefix

You can set the bot's command prefix using the `--prefix` argument:

```bash
takt --prefix=">"
```

#### More

For more information, head over to your terminal and enter:

```bash
takt --help
```

### Invite

Here is the current invite URL for the public version:

> <https://discord.com/api/oauth2/authorize?client_id=923625007333113856&permissions=274881055744&scope=bot%20applications.commands>

You can create your own URL by replacing your Client ID:

```http
https://discord.com/api/oauth2/authorize?client_id=<YOUR_CLIENT_ID>&permissions=274881055744&scope=bot%20applications.commands
```

This Client ID can be found on your Discord Developer Portal, after selecting your bot, under the *OAuth2* section.

> **Warning**  
> The live public version of the bot is almost always down and shouldn't be used for anything other than development

### Discord

Here is a list of commands you can use:

- `+play <search term>`: Searches on YouTube and plays the first result
- `+play <link>`: Play the given link
- `+playing`: Show the current song playing
- `+pause`: Pause the current song
- `+resume`: Resume the current song
- `+skip`: Skip the current song
- `+queue`: Show the current queue
- `+clear`: Clear the queue
- `+stop`: Stop the music and clear the queue
- `+loop`: Toggle looping
- `+loop <true/false>`: Enable or disable looping
- `+looping`: Show the current loop status
- `+latency`: Show the current latency
- `+connected`: Show if the bot is connected to a voice channel
- `+help`: Show this message
- `+help <command>`: Show specific command's help

> **Note**  
> The `+` prefix is the default one and can be changed as explained in [*Prefix*](#prefix)

Head to your discord server and check `+help` or `+help <command>` for further details on the different commands (aliases, examples, etc.)

## Deployment

This module is currently in development and might contain bugs.

Feel free to report any issue you might encounter on takt's GitHub page.

## Contributing

Pull requests are welcome. For major changes, please open a discussion first to discuss what you would like to change.

## Built With

- [nasse](https://github.com/Animenosekai/nasse) - the logging system
- [discord.py](https://github.com/Rapptz/discord.py) - to use the discord API
- [discord-py-slash-command](https://github.com/interactions-py/interactions.py) - to create slash commands on discord
- [youtube-dl](https://github.com/ytdl-org/youtube-dl) - to retrieve sources to play in voice channels
- [youtube-dlp](https://github.com/yt-dlp/yt-dlp) - to retrieve sources to play in voice channels
- [ffmpeg](http://ffmpeg.org) - to process audio

## Authors

- **Animenosekai** - *Initial work* - [Animenosekai](https://github.com/Animenosekai)

## Licensing

This software is licensed under the MIT License. See the [*LICENSE*](./LICENSE) file for more information.
