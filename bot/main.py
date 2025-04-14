#!/usr/bin/env python
import logging
import re
import os
from typing import Dict, List, Tuple, Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from config import TOKEN, FOOD_LIST_PATH, DEBT_DB_PATH
from utils import get_random_food, add_debt, get_debt, clear_debt, clear_food_cache

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get the absolute path of the script directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Update paths to be absolute
FOOD_LIST_PATH_ABS = os.path.join(BASE_DIR, FOOD_LIST_PATH)
DEBT_DB_PATH_ABS = os.path.join(BASE_DIR, DEBT_DB_PATH)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_text(
        f'Hi {user.first_name}! I am your Food and Debt Tracker Bot.\n\n'
        f'Commands:\n'
        f'/food - Get a random food suggestion\n'
        f'/newfood - Force a new food suggestion\n'
        f'/clearfood - Clear current food suggestion\n'
        f'/debt username - Check debt for a user\n'
        f'/done username - Clear debt for a user\n\n'
        f'You can also tag a user with an amount (e.g. @username 100) to add to their debt.'
    )


async def food_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random food suggestion when the command /food is issued."""
    logger.info(f"Food list path: {FOOD_LIST_PATH_ABS}")
    food = get_random_food(FOOD_LIST_PATH_ABS)
    
    if food:
        await update.message.reply_text(f'🍽️ Random food suggestion: {food}')
    else:
        await update.message.reply_text('No foods available. Please import a food list first.')


async def newfood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force a new random food suggestion when the command /newfood is issued."""
    logger.info(f"Food list path: {FOOD_LIST_PATH_ABS}")
    food = get_random_food(FOOD_LIST_PATH_ABS, force_new=True)
    
    if food:
        await update.message.reply_text(f'🍽️ New food suggestion: {food}')
    else:
        await update.message.reply_text('No foods available. Please import a food list first.')


async def clearfood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the current food suggestion when the command /clearfood is issued."""
    clear_food_cache()
    await update.message.reply_text('Food suggestion cleared! Use /food or /newfood to get a new suggestion.')


async def debt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show debt for a user when the command /debt is issued."""
    # Check if a username was provided
    if not context.args or len(context.args) < 1:
        await update.message.reply_text('Please specify a username, e.g. /debt username')
        return
    
    # Get the username (remove @ if present)
    username = context.args[0]
    if username.startswith('@'):
        username = username[1:]
    
    # Get the debt
    debt = get_debt(username, DEBT_DB_PATH_ABS)
    
    await update.message.reply_text(f'@{username} has a debt of {debt:.2f}')


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear debt for a user when the command /done is issued."""
    # Check if a username was provided
    if not context.args or len(context.args) < 1:
        await update.message.reply_text('Please specify a username, e.g. /done username')
        return
    
    # Get the username (remove @ if present)
    username = context.args[0]
    if username.startswith('@'):
        username = username[1:]
    
    # Get the current debt
    old_debt = get_debt(username, DEBT_DB_PATH_ABS)
    
    # Clear the debt
    clear_debt(username, DEBT_DB_PATH_ABS)
    
    await update.message.reply_text(f'Cleared debt of {old_debt:.2f} for @{username}')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Process messages and look for user tags with amounts."""
    if not update.message or not update.message.text:
        return
    
    text = update.message.text
    
    # Look for pattern @username 100
    # This matches @username followed by a space and then a number
    pattern = r'@(\w+)\s+(-?\d+(\.\d+)?)'
    matches = re.findall(pattern, text)
    
    for match in matches:
        username = match[0]
        try:
            amount = float(match[1])
            # Add to user's debt
            new_total = add_debt(username, amount, DEBT_DB_PATH_ABS)
            await update.message.reply_text(f'Added {amount:.2f} to @{username}\'s debt. New total: {new_total:.2f}')
        except ValueError:
            logger.warning(f"Could not convert {match[1]} to float")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log errors caused by updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)
    if update and update.message:
        await update.message.reply_text('An error occurred while processing your request.')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("food", food_command))
    application.add_handler(CommandHandler("newfood", newfood_command))
    application.add_handler(CommandHandler("clearfood", clearfood_command))
    application.add_handler(CommandHandler("debt", debt_command))
    application.add_handler(CommandHandler("done", done_command))
    
    # Register message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start the Bot
    application.run_polling()


if __name__ == '__main__':
    main() 