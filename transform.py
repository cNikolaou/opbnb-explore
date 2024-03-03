import os
import csv
import logging
from pathlib import Path


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


def transform_tokens_data(input_file_name: str, output_file_name: str):
    """
    Transform the `tokens.csv` file generated by
    `ethereumetl.export_all_common()` for opBNB by removing the last column
    columns (`block_number`) and making NULL the missing values.
    """

    # create the directory if it doesn't exist
    dir_path = os.path.dirname(output_file_name)
    os.makedirs(dir_path, exist_ok=True)

    with open(input_file_name, "r") as infile:
        with open(output_file_name, "w") as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            for row in reader:
                modified_row = ["NULL" if cell == "" else cell for cell in row]
                writer.writerow(modified_row[:-1])


def change_dir(dir: Path, replacements: dict) -> Path:
    """
    Replace the parts of Path `dir` based on the replacements to generate
    a new Path that is returned by the function
    """

    path_parts = list(dir.parts)
    new_path_parts = [replacements.get(part, part) for part in path_parts]
    new_path = Path(*new_path_parts)
    return new_path
