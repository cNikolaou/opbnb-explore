# Continuously monitor the blockchain and pull data from newly created
# blocks. Then process and load the data.
import os
import sys
import time
import signal
import logging
from queue import Queue

from web3 import Web3

import settings
from database.utils import create_tables
from jobs.extract import extract_data
from jobs.db_loader import DBLoader
from jobs.file_cleaner import FileCleaner


logger = logging.getLogger(__name__)


def shutdown_signal_handler(signum, frame):

    # Shut down process
    logger.info(
        "Gracefully shutting down; loading the latest data to the database. "
        "WAIT FOR THE PROCESS TO FINISH"
    )

    logger.info(
        f"Wait for the files queued on the db_loader to be processed and loaded. "
        f"Files to process {db_loader.file_path_queue.qsize()}"
    )
    db_loader.wait_for_loads()

    logger.info("Stopping DBLoader threads")
    db_loader.stop()

    logger.info("Processing finished; EXIT")
    sys.exit(0)


# Register signal handlers for graceful shutdown
signal.signal(signal.SIGINT, shutdown_signal_handler)
signal.signal(signal.SIGTERM, shutdown_signal_handler)

# setup the provider
w3 = Web3(Web3.HTTPProvider(settings.PROVIDER_URI))

# create the data directory if it doesn't exist
os.makedirs(settings.DATA_DIR, exist_ok=True)

if (len(sys.argv) == 2 and sys.argv[1] == "create") or (settings.DB_CREATE):
    create_tables()

# queue to keep track of the files that habe to be uploaded to a storage
file_path_queue = Queue()

# start the thread that will be loading the data from CSV files to database
db_loader = DBLoader(file_path_queue, max_workers=1)
db_loader.start()
logger.info("Initisalised DBLoader")

# start cleaner deamon thread
subdirs_to_clean = [
    "blocks",
    "contracts",
    "logs",
    "receipts",
    "token_transfers",
    "tokens",
    "transactions",
]

fc = FileCleaner(
    root_dir="data",
    subdirs=subdirs_to_clean,
    oldest_file_age=settings.OLDEST_FILE_AGE,
)
fc.start()

# set the start block after which to start pulling data from the blockchain
latest_processed_block_number = None
if settings.ETL_STARTING_BLOCK >= 0:
    latest_processed_block_number = settings.ETL_STARTING_BLOCK
else:
    latest_processed_block_number = w3.eth.getBlock("latest")["number"]


# A block is created approximately every 1 second. The thread sleeps for 5
# seconds, checks whether there has been new blocks created and if so, pulls
# the data from the new blocks.
while True:

    time.sleep(settings.BLOCK_DATA_PULL_INTERVAL)
    latest_block_number = w3.eth.getBlock("latest")["number"]

    if latest_block_number > latest_processed_block_number + 1:
        blocks_to_fetch = latest_block_number - latest_processed_block_number - 1

        logger.info(
            "\n" + "-" * 80 + "\n"
            f"Fetch data for {blocks_to_fetch} blocks: "
            f"{latest_processed_block_number + 1} to {latest_block_number}"
            "\n" + "-" * 80
        )

        latest_block_number = min(
            latest_processed_block_number + settings.MAX_EXTRACT_BLOCK_RANGE,
            latest_block_number,
        )

        # process the new blocks
        extract_data(
            start_block_number=latest_processed_block_number + 1,
            end_block_number=latest_block_number,
            block_batch_size=settings.BLOCK_BATCH_SIZE,
            output_dir=settings.DATA_DIR,
            max_workers=settings.MAX_EXTRACT_WORKERS,
            concurrent_requests=settings.CONCURENT_EXTRACT_REQUESTS,
            ready_files_queue=file_path_queue,
        )
        latest_processed_block_number = latest_block_number
