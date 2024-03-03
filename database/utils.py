from pathlib import Path

import psycopg2

from settings import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST

CREATE_BLOCKS_TABLE = "create_blocks_table.sql"
CREATE_TRANSACTIONS_TABLE = "create_transactions_table.sql"
CREATE_TOKENS_TABLE = "create_tokens_table.sql"
CREATE_TOKEN_TRANSFERS_TABLE = "create_token_transfers_table.sql"


def create_tables():

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST
        )
        cur = conn.cursor()

        # get the current dir since all .sql files are located in the same dir
        current_dir = Path(__file__).resolve().parent

        with open(current_dir / CREATE_BLOCKS_TABLE, "r") as f:
            sql_script = f.read()
            cur.execute(sql_script)
            conn.commit()

        print("`blocks` table created successfully")

        with open(current_dir / CREATE_TRANSACTIONS_TABLE, "r") as f:
            sql_script = f.read()
            cur.execute(sql_script)
            conn.commit()

        print("`transactions` table created successfully")

        with open(current_dir / CREATE_TOKENS_TABLE, "r") as f:
            sql_script = f.read()
            cur.execute(sql_script)
            conn.commit()

        print("`tokens` table created successfully")

        with open(current_dir / CREATE_TOKEN_TRANSFERS_TABLE, "r") as f:
            sql_script = f.read()
            cur.execute(sql_script)
            conn.commit()

        print("`token_transfers` table created successfully")

    except (Exception, psycopg2.DatabaseError) as error:
        print("Error while creating table:", error)

    finally:
        if conn is not None:
            cur.close()
            conn.close()


if __name__ == "__main__":
    create_tables()