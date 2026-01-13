import streamlit as st
from rag_utils.setup import logger
if not st.secrets.get("DEV_URL"):  
    logger.warning("DEV_URL not found. Please set it in your environment or .env file.")
if not st.secrets.get("API_KEY"):  
    logger.warning("API_KEY not found. Please set it in your environment or .env file.")  
dev_url = st.secrets.get("DEV_URL")
api_key = st.secrets.get("API_KEY")
