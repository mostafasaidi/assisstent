"""
Configuration module for the AI Assistant Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = int(os.getenv('TELEGRAM_USER_ID', 0))
ADMIN_USER_ID = TELEGRAM_USER_ID  # Admin has full access to all features

# Groq Configuration
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Cal.com Configuration
CALCOM_API_KEY = os.getenv('CALCOM_API_KEY')
CALCOM_API_URL = os.getenv('CALCOM_API_URL', 'https://api.cal.com/v1')

# Bot Settings
BOT_NAME = "Smart Calendar Assistant"
BOT_VERSION = "1.0.0"
