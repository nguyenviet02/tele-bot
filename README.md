# Telegram Food and Debt Tracker Bot

A simple Telegram bot that suggests random foods and tracks debts between users in a group chat.

## Features

- Suggests random foods with the `/food` command
- Tracks debt when users are tagged with amounts (e.g., @username 100)
- Shows debt for a specific user with the `/debt username` command
- Clears debt for a user with the `/done username` command

## Setup

1. **Install Dependencies**

```bash
pip install -r requirements.txt
```

2. **Get a Telegram Bot Token**

- Open Telegram and search for `@BotFather`
- Start a chat and send `/newbot` to create a new bot
- Follow the instructions to set a name and username for your bot
- Copy the token provided by BotFather

3. **Configure the Bot**

- Open `bot/config.py` and replace the placeholder token with your actual token:
```python
TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"  # Replace with your actual bot token
```

4. **Customize the Food List**

- Edit `data/foods.txt` to add your preferred food items, one per line

5. **Run the Bot**

```bash
cd bot
python main.py
```

## Usage

1. **Start the Bot**

- Open Telegram and search for your bot username
- Start a chat and send `/start` to get information about available commands

2. **Add the Bot to a Group**

- Add the bot to your group chat
- Make sure the bot has permission to read messages

3. **Available Commands**

- `/start` - Get information about available commands
- `/food` - Get a random food suggestion from the list
- `/debt username` - Check the debt for a specific user
- `/done username` - Clear the debt for a specific user

4. **Track Debts**

- To add debt to a user, mention them with an amount: `@username 100`
- The bot will automatically track this and add it to the user's total debt

## Contributing

Feel free to submit issues or pull requests to improve the bot. 