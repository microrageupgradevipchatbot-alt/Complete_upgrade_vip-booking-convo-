import os
from pathlib import Path
from dotenv import load_dotenv
import logging
load_dotenv()

# ==================================== Chroma db and docs function =========================================

def setup_paths():
    current_dir = Path(__file__).parent.parent
    data_dir = current_dir / "DATA"
    db_dir = data_dir / "DB"
    doc_dir = data_dir / "Docs"
    
    # Create directories if they don't exist
    data_dir.mkdir(exist_ok=True)
    db_dir.mkdir(exist_ok=True)
    doc_dir.mkdir(exist_ok=True)

    return current_dir, db_dir, doc_dir

def setup_logging():

    LOGS_DIR = CURRENT_DIR / 'DATA' / 'Logs'
    LOGS_DIR.mkdir(exist_ok=True)
    LOG_FILE = LOGS_DIR / 'UPGRADEVIP_COMPLETE.log'
    logging.basicConfig(
        filename=str(LOG_FILE),
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logger = logging.getLogger("Upgrade-Vip")
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S'))
    logger.addHandler(console_handler)
    return logger

CURRENT_DIR, DB_DIR, DOC_DIR = setup_paths()
logger = setup_logging()


