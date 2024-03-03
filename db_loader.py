import logging
from pathlib import Path

from database.loaders import (
    load_blocks_data,
    load_transactions_data,
    load_token_transfers_data,
    load_tokens_data,
)
from utils import remove_file_and_parent_dirs


logger = logging.getLogger(__name__)


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

            # load data to appropriate directory
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

            # only one iteration is valid
            iterated = True
