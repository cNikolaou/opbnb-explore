import os

import settings
from extract import extract_data
from transformer import set_csv_file_transformer


if __name__ == "__main__":

    # create the data directory if it doesn't exist
    os.makedirs(settings.DATA_DIR, exist_ok=True)

    # set the Observer that handles the CSV file transformation
    observer = set_csv_file_transformer(settings.DATA_DIR)
    observer.start()

    # start the data retrieval threads
    extract_data(
        end_block_number=10,
        block_batch_size=10,
        output_dir=settings.DATA_DIR,
        max_workers=1,
        concurrent_requests=1,
    )

    extract_data(
        start_block_number=17442490,
        end_block_number=17442590,
        block_batch_size=20,
        output_dir=settings.DATA_DIR,
        max_workers=5,
        concurrent_requests=2,
    )

    # wait for all the file events in the queue to be processed by the Observer
    observer.event_queue.join()
