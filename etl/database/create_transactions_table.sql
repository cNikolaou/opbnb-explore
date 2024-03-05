-- NOTE: TIMESTAMP in PostgreSQL uses YYYY-MM-DD HH:MI:SS format but
-- on `timestamp` column we store them in the UNIX format as BIGINTs
CREATE TABLE IF NOT EXISTS transactions (
    hash CHAR(66) PRIMARY KEY,
    nonce BIGINT NOT NULL,
    block_hash CHAR(66) NOT NULL,
    block_number BIGINT NOT NULL,
    transaction_index BIGINT NOT NULL,
    from_address CHAR(42) NOT NULL,
    to_address CHAR(42),
    value DECIMAL(38,0) NOT NULL,
    gas BIGINT NOT NULL,
    gas_price BIGINT NOT NULL,
    input TEXT,
    block_timestamp BIGINT NOT NULL,
    max_fee_per_gas BIGINT,
    max_priority_fee_per_gas BIGINT,
    transaction_type INT,

    FOREIGN KEY (block_hash) REFERENCES blocks(hash)
)
