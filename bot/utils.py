import json
import os
import random
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Constants
FOOD_CACHE_FILE = "data/food_cache.json"
CACHE_DURATION = timedelta(hours=12)

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