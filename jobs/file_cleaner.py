import time
import threading
import logging
from pathlib import Path

from .utils import remove_file_and_parent_dirs


logger = logging.getLogger("FileCleaner")


class FileCleaner(threading.Thread):
    """
    Thread subclass which spawns a demon thread for cleaning the files in a
    directory and the selected subdirectories.
    """

    def __init__(
        self, root_dir: str = "data", subdirs: list = [], oldest_file_age: int = 600
    ):
        super().__init__()
        self.oldest_file_age = oldest_file_age
        self.root_dir = root_dir
        self.subdirs = subdirs
        self.daemon = True

    def run(self):

        while True:
            now = time.time()

            for subdir in self.subdirs:
                subdir_path = Path(self.root_dir) / subdir

                for start_dir in subdir_path.iterdir():

                    # ignore directories that do not start with "start_block"
                    if not start_dir.stem.startswith("start_block"):
                        continue

                    for end_dir in start_dir.iterdir():

                        # ignore directories that do not start with "end_block"
                        if not end_dir.stem.startswith("end_block"):
                            continue

                        for file_path in end_dir.iterdir():

                            if file_path.stat().st_mtime + self.oldest_file_age < now:
                                logger.info(
                                    f"Removing file: {file_path} w/ "
                                    f"last mod time: {file_path.stat().st_mtime} "
                                    f"time since: {now - file_path.stat().st_mtime}"
                                )
                                remove_file_and_parent_dirs(file_path)

            time.sleep(self.oldest_file_age)
