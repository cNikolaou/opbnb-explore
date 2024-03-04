import os
import logging
from pathlib import Path
from queue import Queue
from typing import Optional

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    EVENT_TYPE_CREATED,
    EVENT_TYPE_MODIFIED,
)

from utils import (
    to_relative_path,
    remove_file_and_parent_dirs,
    csv_has_row_data,
)
from transform import (
    change_dir,
    transform_blocks_data,
    transform_transactions_data,
    transform_tokens_data,
)


logger = logging.getLogger("CSVTransformHandler")


def transform_file(path: Path, cwd: str, retain_origin_file: bool = True):

    parent_dirs = path.parent.parts

    # If the file is located within a `blocks` directory
    if "blocks" in parent_dirs:
        replacements = {"blocks": "blocks_transformed"}
        new_path = change_dir(path, replacements)
        logger.info(
            f"Transform file `{to_relative_path(path, cwd)}` "
            f"to `{to_relative_path(new_path, cwd)}`"
        )
        transform_blocks_data(str(path), str(new_path))

    # If the file is located within a `transactions` directory
    elif "transactions" in parent_dirs:
        replacements = {"transactions": "transactions_transformed"}
        new_path = change_dir(path, replacements)
        logger.info(
            f"Transform file `{to_relative_path(path, cwd)}` "
            f"to `{to_relative_path(new_path, cwd)}`"
        )
        transform_transactions_data(str(path), str(new_path))

    # If the file is located within a `tokens` directory
    # elif "tokens" in parent_dirs:
    #     replacements = {"tokens": "tokens_transformed"}
    #     new_path = change_dir(path, replacements)
    #     logger.info(
    #         f"Transform file `{to_relative_path(path, cwd)}` "
    #         f"to `{to_relative_path(new_path, cwd)}`"
    #     )
    #     transform_tokens_data(str(path), str(new_path))

    if not retain_origin_file:
        remove_file_and_parent_dirs(path)


class CSVTransformHandler(FileSystemEventHandler):
    """
    FileSystemEventHandler called by a watchdog.Observer to transform files
    which are CREATED or MODIFIED, and are under a `/block/` or
    `/transactions/` directory.
    """

    def __init__(self, file_path_queue=None, retain_origin_files=True):
        super().__init__()
        self._cwd = os.getcwd()
        self._file_path_queue = file_path_queue
        self._retain_origin_files = retain_origin_files

    def on_any_event(self, event):

        # CREATED event_type when the file does not exist beforehand
        # MODIFIED event_type when the file exists and is replaced by a new one
        if event.event_type in [EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED]:

            path = Path(event.src_path)
            parent_dirs = path.parent.parts

            if path.is_file() and ".tmp" not in parent_dirs and path.suffix == ".csv":

                if csv_has_row_data(path):

                    # if the handler has a queue then add the filepath there
                    if self._file_path_queue:
                        self._file_path_queue.put(path)

                    transform_file(path, self._cwd, self._retain_origin_files)


def set_csv_file_transformer(data_dir: str, file_path_queue: Optional[Queue] = None):

    event_handler = CSVTransformHandler(file_path_queue)
    observer = Observer()
    observer.schedule(event_handler, data_dir, recursive=True)

    return observer


def transform_files_in(data_root: str, data_dir: str, retain_origin_files: bool = True):
    """
    Transform files in a directory.
    """

    data_path = Path(data_root) / data_dir

    print(data_path.absolute())

    for start_dir in data_path.iterdir():

        # ignore directories that do not start with "start_block"
        if not start_dir.stem.startswith("start_block"):
            logger.warning(f"Non-data directory {start_dir}")
            continue

        # get the start block number from the directory name
        start_block_num = int(start_dir.stem.split("=")[1])

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

            file_path = end_dir / f"{data_dir}_{start_block_num}_{end_block_num}.csv"

            transform_file(file_path, data_root, retain_origin_files)

            # only one iteration is valid
            iterated = True
