# Website Follower Telegram Bot

## Introduction
The **Website Follower** Telegram Bot is a Python script that utilizes the Telegram Bot API to monitor changes in a specified website and perform additional functionalities such as spell-checking. This bot is designed to provide real-time update on new URL added to the monitored website and check the spelling of words on a specified URL.

## Features
1. **Real-time Monitoring:** The bot allows users to monitor a specific website for new URL. When a new URL is detected, the bot sends a notification to the Telegram chat.

2. **Admin Control:** The bot includes an admin functionality that allows privileged users to set the default website URL for monitoring.

3. **Spell Checking:** Users can request the bot to perform spell-checking on the text extracted from a specified URL. The bot checks each word's spelling and provides suggestions for corrections if needed.

4. **Confidence Threshold:** Users can set the confidence threshold for the spell-checking functionality. The bot offers options for high, medium, and low confidence levels.

## Commands
- **/start:** Displays a welcome message and provides information on available commands.
- **/set_url:** Set URL for monitoring website or spell checker.
- **/check:** Initiates the monitoring process to detect new URLs on the specified website.
- **/spell_checker:** Initiates the spell-checking process on the specified URL.
- **/set_confidence:** Sets the confidence threshold for spell-checking.
- **/get_target_url:** Displays the current target website URL.

## Usage
1. Start the bot by sending the "/start" command.
2. Use the "/admin" command to set the default website URL for monitoring (privileged users only).
3. Initiate monitoring using the "/check" command to detect new URLs.
4. Use the "/url_spell" command to specify the URL for spell-checking.
5. Start spell-checking with the "/spell_checker" command.
6. Optionally, use "/set_confidence" to set the confidence threshold for spell-checking.

## Dependencies
- **python-telegram-bot:** Telegram Bot API wrapper for Python.
- **textblob:** Python library for processing textual data.
- **requests:** Library for making HTTP requests.
- **beautifulsoup4:** Library for pulling data out of HTML and XML files.

## Configuration
1. Obtain a Telegram Bot token from the BotFather on Telegram.
2. Replace `'YOUR_BOT_TOKEN'` in the script with the obtained token.

## How to Run
1. Install the required dependencies using:
   ```bash
   pip install python-telegram-bot==13.13
   pip install textblob 
   pip install requests 
   pip install beautifulsoup4

2. Run the script:
   ```bash
   python bot.py
