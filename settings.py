from dotenv import load_dotenv
import os

load_dotenv()

PROVIDER_URI = os.getenv("PROVIDER_URI", "https://opbnb-mainnet-rpc.bnbchain.org")
