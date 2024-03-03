-- NOTE: TIMESTAMP in PostgreSQL uses YYYY-MM-DD HH:MI:SS format but
-- on `timestamp` column we store them in the UNIX format as BIGINTs
CREATE TABLE IF NOT EXISTS blocks (
    number BIGINT NOT NULL UNIQUE,
    hash CHAR(66) PRIMARY KEY,
    parent_hash CHAR(66) NOT NULL,
    nonce CHAR(18) NOT NULL,
    sha3_uncles VARCHAR(66) NOT NULL,
    logs_bloom TEXT,
    transactions_root CHAR(66) NOT NULL,
    state_root CHAR(66) NOT NULL,
    receipts_root CHAR(66) NOT NULL,
    miner CHAR(42) NOT NULL,
    difficulty DECIMAL(38,0) NOT NULL,
    total_difficulty DECIMAL(38,0) NOT NULL,
    size BIGINT NOT NULL,
    extra_data TEXT,
    gas_limit BIGINT NOT NULL,
    gas_used BIGINT NOT NULL,
    timestamp BIGINT NOT NULL,
    transaction_count BIGINT NOT NULL,
    base_fee_per_gas BIGINT NOT NULL
)
