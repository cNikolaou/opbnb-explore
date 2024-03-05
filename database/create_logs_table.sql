CREATE TABLE IF NOT EXISTS logs (
    log_index BIGINT NOT NULL,
    transaction_hash CHAR(66) NOT NULL,
    transaction_index BIGINT NOT NULL,
    block_hash CHAR(66) NOT NULL,
    block_number BIGINT NOT NULL,
    address CHAR(42) NOT NULL,
    data TEXT,
    topics TEXT[],

    PRIMARY KEY (log_index, transaction_hash),
    FOREIGN KEY (transaction_hash) REFERENCES transactions(hash),
    FOREIGN KEY (block_hash) REFERENCES blocks(hash)
);
