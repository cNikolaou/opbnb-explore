import logging
import time
from pathlib import Path
from queue import Queue
from threading import Thread

from database.loaders import (
    load_blocks_data,
    load_transactions_data,
    load_token_transfers_data,
    load_tokens_data,
)
from utils import remove_file_and_parent_dirs, change_dir


logger = logging.getLogger(__name__)


def load_to_table(file_path: Path, db_table: str, retain_origin_files: bool = True):
    # load data to appropriate table
    try:
        if db_table == "blocks":
            load_blocks_data(file_path)
        elif db_table == "transactions":
            load_transactions_data(file_path)
        elif db_table == "token_transfers":
            load_token_transfers_data(file_path)
        elif db_table == "tokens":
            load_tokens_data(file_path)

        logger.info(f"Loaded data to table `{db_table}` from: {file_path}")

        if not retain_origin_files:
            remove_file_and_parent_dirs(file_path)

    except Exception as e:
        logger.error(f"Loading data from file {file_path} generated error: {e}")


class DBLoadHandler:
    """
    Handle data loading from CSV files to database tables.

    Each file is copied to the appropriate table. Since the tables have
    foreign key relations the data (that refers to a set of blocks) needs
    to be inserted (or copied) in a particular order to follow the
    foreign key constrains.

    The tables need to be populated in the following order:

        blocks -> transactions -> tokens -> token_transfers

    Since the CSV files to populate the tables are not generated in that
    exact order always there are potential race conditions and thus
    there is a need for synchronisation between which data to put first.

    Genearally, we expect the tables to be generated in the following order:

        blocks -> transactions -> token_transfers -> tokens

    The last two will always be in that order, since the `tokens.csv` files
    are generated based on the data on the `token_transfers.csv` files.

    Currently we will handle only that case in the following way:

      - use a buffer (list) `processed_tokens_files` to keep track of
        the `tokens.csv` files that have been processed already

      - when a `token_transfers.csv` file reference is retrieved from the
        queue check if the relevant `tokens.csv` file is in the
        `processed_tokens_files`

          - if yes, then load the data from the `token_transfers.csv`
            and delete the `tokens.csv` entry from the `processed_tokens_files`

          - if NOT, then place the file reference for `token_transfers.csv`
            back in the queue `self.file_path_queue` and processed the
            next file in line

    This approach creates a busy-wait scenario where threads can be consuming
    the `token_transfers.csv` from the queue and placing it back if there
    is nothing else to process. However, this approach works for now.

    NOTE: Currently have tested only spawning a single worker thread. Need
    to test if the approach works with multiple workers in a thread-safe way.
    """

    def __init__(
        self,
        file_path_queue: Queue,
        max_workers: int = 1,
        file_name_to_table: dict = {
            "blocks_transformed": "blocks",
            "transactions_transformed": "transactions",
            "tokens": "tokens",
            "token_transfers": "token_transfers",
        },
        retain_origin_files: bool = True,
    ):

        self.file_path_queue = file_path_queue

        # store the mapping between the directories that will be processed
        # and the tables that the data will be stored in, eg
        # { "transacations_transformed": "trasactions", "tokens": "tokens" }
        self.file_name_to_table = file_name_to_table

        # set of the directories that will be processed; files in
        # the rest of the directories in the queue will be ignored
        self.file_names_to_process = set(file_name_to_table.keys())

        self.max_workers = max_workers
        self.worker_threads = []
        self.processed_tokens_files = []

        self.retain_origin_files = retain_origin_files

    def load(self):
        """
        Task worker threads
        """
        while True:

            file_path = self.file_path_queue.get()

            # if we reached the end of the files to be processed
            if file_path is None:
                self.file_path_queue.task_done()
                break

            parent_dirs = file_path.parent.parts

            # if the file from the queue belongs to the set of files that the
            # worker will process
            if len(self.file_names_to_process.intersection(set(parent_dirs))) == 1:

                db_table = None

                for k, v in self.file_name_to_table.items():
                    if k in parent_dirs:
                        db_table = v
                        break

                # when processing `token_transfers.csv` check if the relevant
                # `tokens.csv` has been processed already; if not put
                # the file_path back to the queue
                if "token_transfers" in parent_dirs:
                    tokens_file_path = self._get_tokens_file_path(file_path)
                    if tokens_file_path not in self.processed_tokens_files:
                        time.sleep(3)
                        self.file_path_queue.put(file_path)
                        self.file_path_queue.task_done()
                        continue

                if db_table is None:
                    raise Exception("DB Table should not be none")

                load_to_table(
                    file_path=file_path,
                    db_table=db_table,
                    retain_origin_files=self.retain_origin_files,
                )

                # if just processed a `tokens.csv` then keep track of if in
                # buffer of processed files
                if "tokens" in parent_dirs:
                    self.processed_tokens_files.append(file_path)

                # when the
                if "token_transfers" in parent_dirs:
                    tokens_file_path = self._get_tokens_file_path(file_path)
                    self.processed_tokens_files.remove(tokens_file_path)

            self.file_path_queue.task_done()

    def _get_tokens_file_path(self, token_transfers_file_path: Path):
        replacements = {
            "token_transfers": "tokens",
            token_transfers_file_path.name: token_transfers_file_path.name.replace(
                "token_transfers", "tokens"
            ),
        }
        tokens_file_path = change_dir(token_transfers_file_path, replacements)

        return tokens_file_path

    def start(self):

        for _ in range(self.max_workers):
            thread = Thread(target=self.load)
            thread.start()
            self.worker_threads.append(thread)

    def stop(self, q_warning: bool = True):
        for _ in range(self.max_workers):
            self.file_path_queue.put(None)

        for thread in self.worker_threads:
            thread.join()

        if q_warning:
            q_size = self.file_path_queue.qsize()
            if q_size != 0:
                logger.warning(f"The queue has {q_size} elements left.")
                while not self.file_path_queue.empty():
                    file_path = self.file_path_queue.get()
                    logger.warning(f"Has not processed file: {file_path}")
                    self.file_path_queue.task_done()

    def wait_for_loads(self, timeout: int = 10):
        """
        Start a thread to wait for all the files from the queue to be uploaded.

        Timeout is necessary in case the queue is in a busy wait mode where
        there are `token_transfers.csv` files to be processed but the relevant
        `tokens.csv` files won't be processed.
        """

        logger.warning(
            f"Terminating file queue with {self.file_path_queue.qsize()} elements left."
        )
        queue_join_thread = Thread(target=self.file_path_queue.join)
        queue_join_thread.start()
        queue_join_thread.join(timeout=timeout)

        if queue_join_thread.is_alive():
            logger.warning("Timeout occurred while waiting for queue to finish.")
        else:
            logger.info("Queue processing completed successfully.")


def load_to_db_table(
    data_root: str,
    data_dir: str,
    db_table: str,
    start_block: int = 0,
    end_block: int = -1,
    retain_origin_files: bool = True,
):
    """
    Iterate over the `data_root/data_dir` directory and load the data to the
    `db_table` table.

    The data directory is expected to have the structure:

    {data_root}/
        {data_dir}/
            start_block=<start:int>/
                end_block=<end:int>/
                    {db_table}_{start}_{end}.csv

    The process makes sure that there is only one `end_block=<end:int>/`
    within each `start_block=<start:int>/` directory.
    """

    data_path = Path(data_root) / data_dir

    for start_dir in data_path.iterdir():

        # ignore directories that do not start with "start_block"
        if not start_dir.stem.startswith("start_block"):
            logger.warning(f"Non-data directory {start_dir}")
            continue

        # get the start block number from the directory name
        start_block_num = int(start_dir.stem.split("=")[1])

        # decide whether to process the data or not
        if start_block_num < start_block:
            continue

        if end_block > 0 and start_block_num > end_block:
            continue

        # expect to have only one subdirectory so only one iteration is allowed
        iterated = False

        for end_dir in start_dir.iterdir():

            # ignore directories that do not start with "end_block"
            if not end_dir.stem.startswith("end_block"):
                logger.warning(f"Non-data directory {end_dir}")
                continue

            # check if we have already iterated
            if iterated:
                raise Exception(
                    f"More that one data files from a single start "
                    f"block in: {str(start_dir)}"
                )

            # get the end block number from the directory name
            end_block_num = int(end_dir.stem.split("=")[1])

            # if we are not supposed to process these blocks
            if end_block > 0 and end_block_num > end_block:
                continue

            file_path = end_dir / f"{db_table}_{start_block_num}_{end_block_num}.csv"

            load_to_table(
                file_path=file_path,
                db_table=db_table,
                retain_origin_files=retain_origin_files,
            )

            # only one iteration is valid
            iterated = True
