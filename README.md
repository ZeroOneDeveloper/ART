# ART GUILD BOT
## This bot is used only for [ART Guild Discord Server](https://discord.gg/FzjHRPH)

## Features
- [x] Welcome, Bye message
- [x] Auto Punishing to artists who didn't post their art in 14 days

## Environment
- Python 3.11.6
- macOS Sonoma, Version 14.3.1 (23D60)
- discord.py 2.3.2

## Usage
1. Clone this repository
2. Install required packages
```bash
pip3 install --upgarde -r requirements.txt
```
3. Create `.env` file and write information below
```dotenv
TOKEN=
MONGO_DB_URL=
MONGO_DB_NAME=
GUILD=
MANAGE_CHANNEL=
WELCOME_CHANNEL=
BYE_CHANNEL=
RULE_CHANNEL=
```
4. Run the bot
```bash
python3 main.py
```

## Issue
Anywhen you have an issue, please create an issue in this repository.
