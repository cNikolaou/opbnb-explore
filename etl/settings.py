import os
import logging
from dotenv import load_dotenv

load_dotenv()

PROVIDER_URI = os.getenv("PROVIDER_URI", "https://opbnb-mainnet-rpc.bnbchain.org")
DATA_DIR = os.getenv("DATA_DIR", "data")

# Pipeline work config
BLOCK_BATCH_SIZE = int(os.getenv("ETL_BLOCK_BATCH_SIZE", 20))
MAX_EXTRACT_WORKERS = int(os.getenv("ETL_MAX_EXTRACT_WORKERS", 5))
CONCURENT_EXTRACT_REQUESTS = int(os.getenv("ETL_CONCURENT_EXTRACT_REQUESTS", 2))
MAX_EXTRACT_BLOCK_RANGE = int(os.getenv("ETL_MAX_EXTRACT_BLOCK_RANGE", 10000))
BLOCK_DATA_PULL_INTERVAL = float(os.getenv("ETL_BLOCK_DATA_PULL_INTERVAL", 2))
OLDEST_FILE_AGE = int(os.getenv("ETL_OLDEST_FILE_AGE", 600))
ETL_STARTING_BLOCK = int(os.getenv("ETL_STARTING_BLOCK", -1))

# Configure the remote storage
STORAGE_ENDPOINT = os.getenv("STORAGE_ENDPOINT", None)
STORAGE_ACCESS_KEY = os.getenv("STORAGE_ACCESS_KEY", None)
STORAGE_ACCESS_SECRET = os.getenv("STORAGE_ACCESS_SECRET", None)
STORAGE_BUCKET_NAME = os.getenv("STORAGE_BUCKET_NAME", None)

# Configure database connection
DB_NAME = os.getenv("DB_NAME", "opbnb")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_CREATE = bool(True if os.getenv("DB_CREATE", "True") == "True" else False)

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s: %(levelname)s/%(name)s:%(lineno)d] %(message)s",
)
