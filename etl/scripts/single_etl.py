import os
from queue import Queue
import time

import settings
from jobs.extract import extract_data
from jobs.transformer import set_csv_file_transformer

# from uploader import UploadHandler

from database.utils import create_tables
from jobs.db_loader import DBLoadHandler


if __name__ == "__main__":

    # create the data directory if it doesn't exist
    os.makedirs(settings.DATA_DIR, exist_ok=True)

    # queue to keep track of the files that habe to be uploaded to a storage
    file_path_queue = Queue()

    # set the Observer that handles the CSV file transformation
    observer = set_csv_file_transformer(settings.DATA_DIR, file_path_queue)
    observer.start()

    # uploader = UploadHandler(file_path_queue, 10)
    # uploader.start()

    create_tables()
    db_loader = DBLoadHandler(file_path_queue, max_workers=1, retain_origin_files=True)
    db_loader.start()

    # # start the data retrieval threads
    # extract_data(
    #     end_block_number=10,
    #     block_batch_size=10,
    #     output_dir=settings.DATA_DIR,
    #     max_workers=1,
    #     concurrent_requests=1,
    # )

    start = time.time()
    extract_data(
        start_block_number=15002737,
        end_block_number=15002746,
        block_batch_size=10,
        output_dir=settings.DATA_DIR,
        max_workers=5,
        concurrent_requests=2,
    )

    # wait for all the file events in the queue to be processed by the Observer
    # and to be added to the `file_path_queue`
    observer.event_queue.join()
    end = time.time()

    print("Total time:", end - start)

    # wait for the files queued on the uploader to be processed
    # uploader.wait_for_uploads()
    # uploader.stop()

    # wait for the files queued on the db_loader to be processed
    db_loader.stop()
