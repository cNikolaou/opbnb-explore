import os
import logging
from dotenv import load_dotenv

load_dotenv()

PROVIDER_URI = os.getenv("PROVIDER_URI", "https://opbnb-mainnet-rpc.bnbchain.org")
DATA_DIR = os.getenv("DATA_DIR", "data")

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s: %(levelname)s/%(name)s] %(message)s",
)
