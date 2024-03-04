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
from extract import extract_data
from transformer import set_csv_file_transformer
from database.utils import create_tables
from db_loader import DBLoadHandler

logger = logging.getLogger(__name__)


def shutdown_signal_handler(signum, frame):

    # Shut down process
    logger.info(
        "Gracefully shutting down; loading the latest data to the database. "
        "WAIT FOR THE PROCESS TO FINISH"
    )

    logger.info(
        f"Wait for all the file events to be processed. "
        f"Events to process {observer.event_queue.qsize()}"
    )
    observer.event_queue.join()

    logger.info(
        f"Wait for the files queued on the db_loader to be processed and loaded. "
        f"Files to process {db_loader.file_path_queue.qsize()}"
    )
    db_loader.wait_for_loads(timeout=10)

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

# set the Observer that handles the CSV file transformation
observer = set_csv_file_transformer(settings.DATA_DIR, file_path_queue)
observer.start()
logger.info("Initisalised CSVTransformer")

# start the thread that will be loading the data from CSV files to database
db_loader = DBLoadHandler(file_path_queue, max_workers=1, retain_origin_files=True)
db_loader.start()
logger.info("Initisalised DBLoader")

# read the latest block number that has been processed
latest_processed_block_number = w3.eth.getBlock("latest")["number"]

# A block is created approximately every 1 second. The thread sleeps for 5
# seconds, checks whether there has been new blocks created and if so, pulls
# the data from the new blocks.
while True:

    time.sleep(1)
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
        )
        latest_processed_block_number = latest_block_number
