import os
from queue import Queue

import settings
from extract import extract_data
from transformer import set_csv_file_transformer
from uploader import UploadHandler

if __name__ == "__main__":

    # create the data directory if it doesn't exist
    os.makedirs(settings.DATA_DIR, exist_ok=True)

    # queue to keep track of the files that habe to be uploaded to a storage
    file_path_queue = Queue()

    # set the Observer that handles the CSV file transformation
    observer = set_csv_file_transformer(settings.DATA_DIR, file_path_queue)
    observer.start()

    uploader = UploadHandler(file_path_queue, 5)
    uploader.start()

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
    # and to be added to the `file_path_queue`
    observer.event_queue.join()

    # wait for the files queued on the uploader to be processed
    uploader.wait_for_uploads()
    uploader.stop()
