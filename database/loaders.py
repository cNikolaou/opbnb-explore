import csv
import logging

import psycopg2

from settings import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


logger = logging.getLogger(__name__)


BLOCKS_CSV_FILE_PATH = "./blocks_transformed.csv"
TRANSACTIONS_CSV_FILE_PATH = "./transactions_transformed.csv"
TOKEN_TRANSFERS_CSV_FILE_PATH = "./token_transfers_transformed.csv"


def load_blocks_data(input_filename: str, table_name: str = "blocks"):

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()

    with open(input_filename, "r") as f:

        # skip header and copy the rest
        next(f)
        cur.copy_from(
            f,
            table_name,
            sep=",",
            columns=(
                "number",
                "hash",
                "parent_hash",
                "nonce",
                "sha3_uncles",
                "logs_bloom",
                "transactions_root",
                "state_root",
                "receipts_root",
                "miner",
                "difficulty",
                "total_difficulty",
                "size",
                "extra_data",
                "gas_limit",
                "gas_used",
                "timestamp",
                "transaction_count",
                "base_fee_per_gas",
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def load_transactions_data(input_filename: str, table_name: str = "transactions"):

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()

    with open(input_filename) as f:

        # skip header and copy the rest
        next(f)
        cur.copy_from(
            f,
            table_name,
            sep=",",
            columns=(
                "hash",
                "nonce",
                "block_hash",
                "block_number",
                "transaction_index",
                "from_address",
                "to_address",
                "value",
                "gas",
                "gas_price",
                "input",
                "block_timestamp",
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def load_token_transfers_data(input_filename: str, table_name: str = "token_transfers"):

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()

    with open(input_filename) as f:

        # skip header and copy the rest
        next(f)
        cur.copy_from(
            f,
            table_name,
            sep=",",
            columns=(
                "token_address",
                "from_address",
                "to_address",
                "value",
                "transaction_hash",
                "log_index",
                "block_number",
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def load_tokens_data(input_filename: str, table_name: str = "tokens"):

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()

    with open(input_filename) as f:

        reader = csv.reader(f)

        # skip header and copy the rest
        next(reader)

        # use the less efficient INSERT INTO (instead of the `copy_from`)
        # to handle duplicate tokens individually
        for row in reader:

            modified_row = ["NULL" if cell == "" else cell for cell in row]
            modified_row = modified_row[:-1]

            try:
                sql_cmd = """
                INSERT INTO %s(address, symbol, name, decimals, total_supply)
                VALUES('%s', '%s', '%s', %s, %s)
                ON CONFLICT DO NOTHING;
                """ % (
                    table_name,
                    *modified_row,
                )

                cur.execute(sql_cmd)

            except Exception as e:
                logger.error(e)

    conn.commit()
    cur.close()
    conn.close()