# Bot configuration file
import os

# Get the absolute path to the project root directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load token from token.txt file
with open(os.path.join(BASE_DIR, "token.txt"), "r") as file:
    TOKEN = file.read().strip()

# Path to the food list file
FOOD_LIST_PATH = "data/foods.txt"

# Database configuration
# For simplicity, we'll use a simple JSON file to store user debts
DEBT_DB_PATH = "data/debts.json" 