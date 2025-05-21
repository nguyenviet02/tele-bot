import json
import os
import random
import logging
from typing import Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Constants
FOOD_CACHE_FILE = "data/food_cache.json"
CACHE_DURATION = timedelta(hours=12)
# List of restricted usernames - users in this list will receive a VIP message
# when attempting to use any bot commands
RESTRICTED_USERS = ["phuongtung99"]

def load_food_cache() -> Dict:
    """
    Load the cached food and timestamp from JSON file.
    
    Returns:
        Dictionary containing the cached food and timestamp
    """
    if not os.path.exists(FOOD_CACHE_FILE):
        return {}
    
    try:
        with open(FOOD_CACHE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}

def save_food_cache(food: str) -> None:
    """
    Save the current food and timestamp to cache.
    
    Args:
        food: The food to cache
    """
    cache_data = {
        'food': food,
        'timestamp': datetime.now().isoformat()
    }
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(FOOD_CACHE_FILE), exist_ok=True)
    
    with open(FOOD_CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2)

def load_food_list(file_path: str) -> List[str]:
    """
    Load the list of foods from a text file.
    Each food item should be on a new line.
    
    Args:
        file_path: Path to the food list file
        
    Returns:
        List of food items
    """
    # Convert to absolute path if it's relative
    abs_path = os.path.abspath(file_path)
    logger.info(f"Loading food list from: {abs_path}")
    logger.info(f"File exists: {os.path.exists(abs_path)}")
    
    if not os.path.exists(abs_path):
        logger.warning(f"Food list file not found at: {abs_path}")
        return []
    
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            # Strip whitespace and filter out empty lines
            foods = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(foods)} foods from list")
            return foods
    except Exception as e:
        logger.error(f"Error loading food list: {str(e)}")
        return []


def clear_food_cache() -> None:
    """
    Clear the cached food suggestion by removing the cache file.
    """
    if os.path.exists(FOOD_CACHE_FILE):
        try:
            os.remove(FOOD_CACHE_FILE)
            logger.info("Food cache cleared successfully")
        except Exception as e:
            logger.error(f"Error clearing food cache: {str(e)}")

def get_random_food(file_path: str, force_new: bool = False) -> Optional[str]:
    """
    Get a random food from the food list.
    Will return the same food for 12 hours before selecting a new one,
    unless force_new is True.
    
    Args:
        file_path: Path to the food list file
        force_new: If True, ignore cache and get a new random food
        
    Returns:
        Random food item or None if the list is empty
    """
    # Check cache first (unless force_new is True)
    if not force_new:
        cache = load_food_cache()
        now = datetime.now()
        
        if cache:
            cached_time = datetime.fromisoformat(cache['timestamp'])
            # If cache is still valid (less than 12 hours old)
            if now - cached_time < CACHE_DURATION:
                logger.info(f"Returning cached food: {cache['food']}")
                return cache['food']
    
    # If we get here, either cache is empty/expired or force_new is True
    foods = load_food_list(file_path)
    if not foods:
        return None
    
    # Select new random food
    food = random.choice(foods)
    logger.info(f"Selected new random food: {food}")
    
    # Save to cache
    save_food_cache(food)
    
    return food


def load_debts(file_path: str) -> Dict[str, float]:
    """
    Load user debts from JSON file.
    
    Args:
        file_path: Path to the debt database file
        
    Returns:
        Dictionary mapping usernames to debt amounts
    """
    if not os.path.exists(file_path):
        # Create the directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def save_debts(debts: Dict[str, float], file_path: str) -> None:
    """
    Save user debts to JSON file.
    
    Args:
        debts: Dictionary mapping usernames to debt amounts
        file_path: Path to the debt database file
    """
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(debts, f, indent=2)


def add_debt(username: str, amount: float, file_path: str) -> float:
    """
    Add debt to a user.
    
    Args:
        username: Username of the user
        amount: Amount to add to the debt
        file_path: Path to the debt database file
        
    Returns:
        New total debt for the user
    """
    debts = load_debts(file_path)
    
    # Initialize debt for new users
    if username not in debts:
        debts[username] = 0
    
    # Add to existing debt
    debts[username] += amount
    
    # Save updated debts
    save_debts(debts, file_path)
    
    return debts[username]


def get_debt(username: str, file_path: str) -> float:
    """
    Get the debt of a user.
    
    Args:
        username: Username of the user
        file_path: Path to the debt database file
        
    Returns:
        Total debt for the user
    """
    debts = load_debts(file_path)
    return debts.get(username, 0)


def clear_debt(username: str, file_path: str) -> None:
    """
    Clear the debt of a user.
    
    Args:
        username: Username of the user
        file_path: Path to the debt database file
    """
    debts = load_debts(file_path)
    
    if username in debts:
        debts[username] = 0
        save_debts(debts, file_path)


def add_food_to_list(food: str, file_path: str) -> bool:
    """
    Add a new food item to the food list.
    
    Args:
        food: The food item to add
        file_path: Path to the food list file
        
    Returns:
        True if food was added successfully, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if the food already exists in the list
        existing_foods = load_food_list(file_path)
        food = food.strip()
        
        if food in existing_foods:
            logger.info(f"Food '{food}' already exists in the list")
            return False
        
        # Append the new food to the file
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(f"\n{food}")
        
        logger.info(f"Added new food '{food}' to the list")
        return True
    
    except Exception as e:
        logger.error(f"Error adding food to list: {str(e)}")
        return False


def remove_food_from_list(food: str, file_path: str) -> Tuple[bool, str]:
    """
    Remove a food item from the food list.
    
    Args:
        food: The food item to remove
        file_path: Path to the food list file
        
    Returns:
        Tuple of (success, message) where success is True if food was removed 
        successfully, and message contains additional information
    """
    try:
        # Load existing foods
        existing_foods = load_food_list(file_path)
        
        if not existing_foods:
            return False, "Food list is empty"
        
        food = food.strip()
        # Case insensitive search
        food_lower = food.lower()
        
        # Find potential matches
        matches = [f for f in existing_foods if f.lower() == food_lower]
        
        if not matches:
            # Try to find if it's a partial match
            partial_matches = [f for f in existing_foods if food_lower in f.lower()]
            if partial_matches:
                # Return the matches so the user can be more specific
                match_str = ", ".join([f"'{m}'" for m in partial_matches[:5]])
                return False, f"Food '{food}' not found exactly. Did you mean one of: {match_str}" + \
                       (f" (and {len(partial_matches) - 5} more)" if len(partial_matches) > 5 else "")
            return False, f"Food '{food}' not found in the list"
        
        # Remove the exact match
        updated_foods = [f for f in existing_foods if f.lower() != food_lower]
        
        # Write back to file
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(updated_foods))
        
        # If we've removed the current food cache, clear it
        cache = load_food_cache()
        if cache and any(match.lower() == cache.get('food', '').lower() for match in matches):
            clear_food_cache()
            logger.info(f"Cleared food cache as removed food was currently cached")
        
        logger.info(f"Removed food '{matches[0]}' from the list")
        
        if len(matches) > 1:
            return True, f"Removed {len(matches)} items matching '{food}'"
        return True, f"Removed '{matches[0]}' from the food list"
    
    except Exception as e:
        logger.error(f"Error removing food from list: {str(e)}")
        return False, f"Error removing food: {str(e)}"


def get_all_foods(file_path: str, numbered: bool = False) -> Tuple[List[str], str]:
    """
    Get all foods from the food list with optional formatting.
    
    Args:
        file_path: Path to the food list file
        numbered: If True, return a numbered list
        
    Returns:
        Tuple of (list of foods, formatted text)
    """
    foods = load_food_list(file_path)
    
    if not foods:
        return [], "No foods available in the list."
    
    # Sort alphabetically for better readability
    foods.sort()
    
    if numbered:
        # Create a numbered list
        formatted_text = "\n".join([f"{i+1}. {food}" for i, food in enumerate(foods)])
    else:
        # Create a bullet list
        formatted_text = "\n".join([f"• {food}" for food in foods])
    
    return foods, formatted_text


def is_restricted_user(username: str) -> bool:
    """
    Check if a username is in the restricted list.
    
    Args:
        username: Username to check (with or without @ symbol)
        
    Returns:
        True if the user is restricted, False otherwise
    """
    # Remove @ symbol if present
    if username.startswith('@'):
        username = username[1:]
    
    # Convert to lowercase for case-insensitive comparison
    username_lower = username.lower()
    
    # Log the check
    logger.info(f"Checking if user '{username}' is in restricted list: {RESTRICTED_USERS}")
    logger.info(f"Lowercase username for comparison: '{username_lower}'")
    
    # Log each individual comparison
    for restricted_user in RESTRICTED_USERS:
        restricted_user_lower = restricted_user.lower()
        is_match = username_lower == restricted_user_lower
        logger.info(f"Comparing '{username_lower}' with restricted user '{restricted_user_lower}': Match = {is_match}")
    
    # Check against the restricted usernames list
    result = username_lower in [user.lower() for user in RESTRICTED_USERS]
    logger.info(f"Final result of restriction check for '{username}': {result}")
    return result


async def check_command_restriction(update, username: str) -> bool:
    """
    Check if a user is restricted from using commands and send a message if they are.
    This should only be called when processing command handlers, not regular messages.
    
    Args:
        update: The telegram update object
        username: Username to check
        
    Returns:
        True if the user is restricted, False otherwise
    """
    logger.info(f"Checking command restriction for user: {username}")
    if is_restricted_user(username):
        logger.info(f"User {username} is restricted, sending VIP message")
        await update.message.reply_text("Bạn cần nạp VIP để thực hiện lệnh này")
        return True
    logger.info(f"User {username} is not restricted")
    return False 