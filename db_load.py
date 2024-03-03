import sys

from database.utils import create_tables
from db_loader import load_to_db_table


if __name__ == "__main__":

    if len(sys.argv) >= 2 and "create" in sys.argv:
        create_tables()

    retain_origin_files = True
    if len(sys.argv) >= 2 and "remove" in sys.argv:
        retain_origin_files = False

    load_to_db_table(
        "data", "blocks_transformed", "blocks", retain_origin_files=retain_origin_files
    )
    load_to_db_table(
        "data",
        "transactions_transformed",
        "transactions",
        retain_origin_files=retain_origin_files,
    )
    load_to_db_table(
        "data", "tokens", "tokens", retain_origin_files=retain_origin_files
    )
    load_to_db_table(
        "data",
        "token_transfers",
        "token_transfers",
        retain_origin_files=retain_origin_files,
    )
