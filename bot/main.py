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
from utils import (
    get_random_food,
    add_debt,
    get_debt,
    clear_debt,
    clear_food_cache,
    add_food_to_list,
    remove_food_from_list,
    get_all_foods,
    is_restricted_user,
    check_command_restriction
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
# Reduce httpx logging verbosity 
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Get the absolute path of the script directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Update paths to be absolute
FOOD_LIST_PATH_ABS = os.path.join(BASE_DIR, FOOD_LIST_PATH)
DEBT_DB_PATH_ABS = os.path.join(BASE_DIR, DEBT_DB_PATH)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    # Debug information
    logger.info(f"Start command triggered - update: {update}")
    logger.info(f"Message from chat ID: {update.message.chat_id}")
    logger.info(f"Message from user ID: {update.message.from_user.id}")
    
    user = update.effective_user
    logger.info(f"Effective user: {user}")
    
    # Check if username exists and log it
    if user:
        logger.info(f"Username: {user.username}, First name: {user.first_name}")
    
    # This is the key issue - let's check for None or empty username explicitly
    if user and not user.username:
        logger.warning("User has no username - cannot check restrictions")
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    await update.message.reply_text(
        f'Hi {user.first_name}! I am your Food and Debt Tracker Bot.\n\n'
        f'Commands:\n'
        f'/food - Get a random food suggestion\n'
        f'/newfood - Force a new food suggestion\n'
        f'/clearfood - Clear current food suggestion\n'
        f'/addfood - Add a new food to the list\n'
        f'/removefood - Remove a food from the list\n'
        f'/foodlist - Show all foods in the list\n'
        f'/debt username - Check debt for a user\n'
        f'/done username - Clear debt for a user\n'
        f'/help - Show all available commands\n\n'
        f'You can also tag a user with an amount (e.g. @username 100) to add to their debt.'
    )


async def food_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random food suggestion when the command /food is issued."""
    # Check if the user is restricted
    user = update.effective_user
    logger.info(f"Food command called by user: {user}")
    
    if user:
        logger.info(f"User ID: {user.id}, Username: {user.username}, First Name: {user.first_name}")
    else:
        logger.info("User object is None")
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    logger.info(f"Food list path: {FOOD_LIST_PATH_ABS}")
    food = get_random_food(FOOD_LIST_PATH_ABS)
    
    if food:
        await update.message.reply_text(f'🍽️ Random food suggestion: {food}')
    else:
        await update.message.reply_text('No foods available. Please import a food list first.')


async def newfood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force a new random food suggestion when the command /newfood is issued."""
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    logger.info(f"Food list path: {FOOD_LIST_PATH_ABS}")
    food = get_random_food(FOOD_LIST_PATH_ABS, force_new=True)
    
    if food:
        await update.message.reply_text(f'🍽️ New food suggestion: {food}')
    else:
        await update.message.reply_text('No foods available. Please import a food list first.')


async def clearfood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Clear the current food suggestion when the command /clearfood is issued."""
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    clear_food_cache()
    await update.message.reply_text('Food suggestion cleared! Use /food or /newfood to get a new suggestion.')


async def addfood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a new food to the food list when the command /addfood is issued."""
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    # Check if a food item was provided
    if not context.args or len(context.args) < 1:
        await update.message.reply_text('Please specify a food to add, e.g. /addfood "Fried Rice"')
        return
    
    # Join all args to support food names with spaces
    food_item = ' '.join(context.args)
    
    # Add the food to the list
    success = add_food_to_list(food_item, FOOD_LIST_PATH_ABS)
    
    if success:
        await update.message.reply_text(f'Added "{food_item}" to the food list!')
    else:
        await update.message.reply_text(f'"{food_item}" already exists in the food list or could not be added.')


async def removefood_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove a food from the food list when the command /removefood is issued."""
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    # Check if a food item was provided
    if not context.args or len(context.args) < 1:
        await update.message.reply_text('Please specify a food to remove, e.g. /removefood "Fried Rice"')
        return
    
    # Join all args to support food names with spaces
    food_item = ' '.join(context.args)
    
    # Remove the food from the list
    success, message = remove_food_from_list(food_item, FOOD_LIST_PATH_ABS)
    
    await update.message.reply_text(message)


async def foodlist_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show all foods in the list when the command /foodlist is issued."""
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    # Get all foods with numbered format
    _, formatted_text = get_all_foods(FOOD_LIST_PATH_ABS, numbered=True)
    
    # Telegram has a message limit, so we might need to chunk it
    if len(formatted_text) > 4000:
        chunks = [formatted_text[i:i+4000] for i in range(0, len(formatted_text), 4000)]
        for i, chunk in enumerate(chunks):
            header = f"🍽️ Food List (Part {i+1}/{len(chunks)}):\n\n" if i == 0 else ""
            await update.message.reply_text(f"{header}{chunk}")
    else:
        await update.message.reply_text(f"🍽️ Food List:\n\n{formatted_text}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show help information when the command /help is issued."""
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
    # This is essentially the same as start but without the greeting
    await update.message.reply_text(
        f'Commands:\n'
        f'/food - Get a random food suggestion\n'
        f'/newfood - Force a new food suggestion\n'
        f'/clearfood - Clear current food suggestion\n'
        f'/addfood - Add a new food to the list\n'
        f'/removefood - Remove a food from the list\n'
        f'/foodlist - Show all foods in the list\n'
        f'/debt username - Check debt for a user\n'
        f'/done username - Clear debt for a user\n'
        f'/help - Show all available commands\n\n'
        f'You can also tag a user with an amount (e.g. @username 100) to add to their debt.'
    )


async def debt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show debt for a user when the command /debt is issued."""
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
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
    # Check if the user is restricted
    user = update.effective_user
    
    # Check if the user is restricted - only check if user has a username
    if user and user.username:
        # Check restriction only if username exists
        if await check_command_restriction(update, user.username):
            return
    
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
    
    # Log message info
    user = update.effective_user
    if user:
        logger.info(f"Regular message from user ID: {user.id}, Username: {user.username}, Text: {update.message.text[:20]}...")
    
    # We don't check general restriction for regular messages as users should be able to chat
    # But we do check if the user is restricted when they try to add debt
    text = update.message.text
    
    # Look for pattern @username 100
    # This matches @username followed by a space and then a number
    pattern = r'@(\w+)\s+(-?\d+(\.\d+)?)'
    matches = re.findall(pattern, text)
    
    if matches and user and user.username:
        # If the user is trying to add debt, check if they're restricted
        if is_restricted_user(user.username):
            logger.info(f"Restricted user {user.username} tried to add debt")
            await update.message.reply_text("Bạn cần nạp VIP để thực hiện lệnh này")
            return
    
    for match in matches:
        username = match[0]
        logger.info(f"Found debt message for username: {username}")
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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("food", food_command))
    application.add_handler(CommandHandler("newfood", newfood_command))
    application.add_handler(CommandHandler("clearfood", clearfood_command))
    application.add_handler(CommandHandler("addfood", addfood_command))
    application.add_handler(CommandHandler("removefood", removefood_command))
    application.add_handler(CommandHandler("foodlist", foodlist_command))
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