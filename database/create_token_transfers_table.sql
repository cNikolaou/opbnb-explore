CREATE TABLE IF NOT EXISTS token_transfers (
    id SERIAL PRIMARY KEY,
    token_address CHAR(42) NOT NULL,
    from_address CHAR(42) NOT NULL,
    to_address CHAR(42) NOT NULL,
    value NUMERIC(78, 0) NOT NULL CHECK (value >= 0),
    transaction_hash CHAR(66) NOT NULL,
    log_index BIGINT NOT NULL,
    block_number BIGINT NOT NULL,

    FOREIGN KEY (transaction_hash) REFERENCES transactions(hash),
    FOREIGN KEY (token_address) REFERENCES tokens(address)
)
