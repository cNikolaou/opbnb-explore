import os
import csv
import logging
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import (
    FileSystemEventHandler,
    EVENT_TYPE_CREATED,
    EVENT_TYPE_MODIFIED,
)


logger = logging.getLogger(__name__)


def transform_blocks_data(input_file_name: str, output_file_name: str):
    """
    Transform the `blocks.csv` file generated by
    `ethereumetl.export_all_common()` for opBNB by removing the last two
    columns (`withdrawals_root`, `withdrawals`)
    """

    # create the directory if it doesn't exist
    dir_path = os.path.dirname(output_file_name)
    os.makedirs(dir_path, exist_ok=True)

    with open(input_file_name, "r") as infile:
        with open(output_file_name, "w") as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            for row in reader:
                writer.writerow(row[:-2])


def transform_transactions_data(input_file_name: str, output_file_name: str):
    """
    Transform the `transactions.csv` file generated by
    `ethereumetl.export_all_common()` for opBNB by removing the last three
    columns (`max_fee_per_gas`, `max_priority_fee_per_gas`, `transaction_type`)
    """

    # create the directory if it doesn't exist
    dir_path = os.path.dirname(output_file_name)
    os.makedirs(dir_path, exist_ok=True)

    with open(input_file_name, "r") as infile:
        with open(output_file_name, "w") as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            for row in reader:
                writer.writerow(row[:-3])


def change_dir(dir: Path, replacements: dict) -> Path:
    """
    Replace the parts of Path `dir` based on the replacements to generate
    a new Path that is returned by the function
    """

    path_parts = list(dir.parts)
    new_path_parts = [replacements.get(part, part) for part in path_parts]
    new_path = Path(*new_path_parts)
    return new_path


def to_relative_path(file_path: Path, base_dir: Path) -> Path:
    """
    Helper function to return the relative path of `file_path` with
    respect to `base_dir`
    """

    relative_path = file_path.relative_to(base_dir)
    return relative_path


class CSVTransformHandler(FileSystemEventHandler):
    """
    FileSystemEventHandler called by a watchdog.Observer to transform files
    which are CREATED or MODIFIED, and are under a `/block/` or
    `/transactions/` directory.
    """

    def __init__(self):
        super().__init__()

    def on_any_event(self, event):

        # CREATED event_type when the file does not exist beforehand
        # MODIFIED event_type when the file exists and is replaced by a new one
        if event.event_type in [EVENT_TYPE_CREATED, EVENT_TYPE_MODIFIED]:

            path = Path(event.src_path)
            parent_dirs = path.parent.parts

            if path.is_file() and path.suffix == ".csv" and ".tmp" not in parent_dirs:

                cwd = os.getcwd()

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


def set_csv_file_transformer(data_dir: str):

    event_handler = CSVTransformHandler()
    observer = Observer()
    observer.schedule(event_handler, data_dir, recursive=True)

    return observer