import os
from rag_utils.setup import logger
if not os.getenv("DEV_URL"):  
    logger.warning("DEV_URL not found. Please set it in your environment or .env file.")
if not os.getenv("API_KEY"):  
    logger.warning("API_KEY not found. Please set it in your environment or .env file.")  
dev_url = os.getenv("DEV_URL")
api_key = os.getenv("API_KEY")
