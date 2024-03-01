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

from utils import to_relative_path
from transform import change_dir, transform_blocks_data, transform_transactions_data


logger = logging.getLogger("CSVTransformHandler")


class CSVTransformHandler(FileSystemEventHandler):
    """
    FileSystemEventHandler called by a watchdog.Observer to transform files
    which are CREATED or MODIFIED, and are under a `/block/` or
    `/transactions/` directory.
    """

    def __init__(self, file_path_queue=None):
        super().__init__()
        self._cwd = os.getcwd()
        self._file_path_queue = file_path_queue

    def on_any_event(self, event):

        # CREATED event_type when the file does not exist beforehand
        # MODIFIED event_type when the file exists and is replaced by a new one
        if event.event_type in [EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED]:

            path = Path(event.src_path)
            parent_dirs = path.parent.parts

            if path.is_file() and ".tmp" not in parent_dirs and path.suffix == ".csv":

                # if there handler has a queue then add the filepath there
                if self._file_path_queue:
                    self._file_path_queue.put(path)

                # If the file is located within a `blocks` directory
                if "blocks" in parent_dirs:
                    replacements = {"blocks": "blocks_transformed"}
                    new_path = change_dir(path, replacements)
                    logger.info(
                        f"Transform file `{to_relative_path(path, self._cwd)}` "
                        f"to `{to_relative_path(new_path, self._cwd)}`"
                    )
                    transform_blocks_data(str(path), str(new_path))

                # If the file is located within a `transactions` directory
                elif "transactions" in parent_dirs:
                    replacements = {"transactions": "transactions_transformed"}
                    new_path = change_dir(path, replacements)
                    logger.info(
                        f"Transform file `{to_relative_path(path, self._cwd)}` "
                        f"to `{to_relative_path(new_path, self._cwd)}`"
                    )
                    transform_transactions_data(str(path), str(new_path))


def set_csv_file_transformer(data_dir: str, file_path_queue: Optional[Queue] = None):

    event_handler = CSVTransformHandler(file_path_queue)
    observer = Observer()
    observer.schedule(event_handler, data_dir, recursive=True)

    return observer
