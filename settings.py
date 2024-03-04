import os
import logging
from dotenv import load_dotenv

load_dotenv()

PROVIDER_URI = os.getenv("PROVIDER_URI", "https://opbnb-mainnet-rpc.bnbchain.org")
DATA_DIR = os.getenv("DATA_DIR", "data")

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

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s: %(levelname)s/%(name)s:%(lineno)d] %(message)s",
)
