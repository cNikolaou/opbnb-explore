import csv
import logging
import io

import psycopg2

from settings import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST


logger = logging.getLogger(__name__)


BLOCKS_CSV_FILE_PATH = "./blocks_transformed.csv"
TRANSACTIONS_CSV_FILE_PATH = "./transactions_transformed.csv"
TOKEN_TRANSFERS_CSV_FILE_PATH = "./token_transfers_transformed.csv"


def get_streamed_csv_data(input_filename: list, columns_to_remove: int = 1):

    buffer = io.StringIO()

    with open(input_filename, "r") as f:
        # skip header and copy the rest
        next(f)

        reader = csv.reader(f)
        for row in reader:
            transformed_row = ",".join(row[:-columns_to_remove]) + "\n"
            buffer.write(transformed_row)

    return buffer


def load_blocks_data(input_filename: str, table_name: str = "blocks"):

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()

    buffer = get_streamed_csv_data(input_filename, 2)
    buffer.seek(0)

    cur.copy_from(
        buffer,
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
            null="",
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
                "max_fee_per_gas",
                "max_priority_fee_per_gas",
                "transaction_type",
            ),
        )

    conn.commit()
    cur.close()
    conn.close()


def load_receipts_data(input_filename: str, table_name: str = "receipts"):

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
                "transaction_hash",
                "transaction_index",
                "block_hash",
                "block_number",
                "cumulative_gas_used",
                "gas_used",
                "contract_address",
                "root",
                "status",
                "effective_gas_price",
                "l1_fee",
                "l1_gas_used",
                "l1_gas_price",
                "l1_fee_scalar",
            ),
            null="",
        )

    conn.commit()
    cur.close()
    conn.close()


def load_logs_data(input_filename: str, table_name: str = "logs"):

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
    )
    cur = conn.cursor()

    with open(input_filename) as f:

        reader = csv.reader(f)

        # skip header and copy the rest
        next(reader)

        # use the less efficient INSERT INTO (instead of the `copy_from`)
        # to handle the topics array; potentially could be optimised with
        # a buffer and copy_from
        for row in reader:

            topics = row[-1]
            topics_array = "{" + topics + "}"

            try:
                sql_cmd = """
                INSERT INTO %s(log_index, transaction_hash, transaction_index,
                                block_hash, block_number, address, data, topics)
                VALUES(%s, '%s', %s, '%s', %s, '%s', '%s', '%s')
                ON CONFLICT DO NOTHING;
                """ % (
                    table_name,
                    *row[:-1],
                    topics_array,
                )

                print(sql_cmd)
                cur.execute(sql_cmd)

            except Exception as e:
                logger.error(e)

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
