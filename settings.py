import os
import logging
from dotenv import load_dotenv

load_dotenv()

PROVIDER_URI = os.getenv("PROVIDER_URI", "https://opbnb-mainnet-rpc.bnbchain.org")
DATA_DIR = os.getenv("DATA_DIR", "data")

# Pipeline work config
BLOCK_BATCH_SIZE = int(os.getenv("BLOCK_BATCH_SIZE", 20))
MAX_EXTRACT_WORKERS = int(os.getenv("MAX_EXTRACT_WORKERS", 5))
CONCURENT_EXTRACT_REQUESTS = int(os.getenv("CONCURENT_EXTRACT_REQUESTS", 2))
MAX_EXTRACT_BLOCK_RANGE = int(os.getenv("MAX_EXTRACT_BLOCK_RANGE", 10000))
RETAIN_INTERMEDIATE_FILES = (
    True if os.getenv("RETAIN_INTERMEDIATE_FILES", "True") == "True" else False
)
OLDEST_FILE_AGE = int(os.getenv("OLDEST_FILE_AGE", 600))

# Configure the remote storage
STORAGE_ENDPOINT = os.getenv("ENDPOINT", None)
STORAGE_ACCESS_KEY = os.getenv("ACCESS_KEY", None)
STORAGE_ACCESS_SECRET = os.getenv("ACCESS_SECRET", None)
STORAGE_BUCKET_NAME = os.getenv("BUCKET_NAME", None)

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
