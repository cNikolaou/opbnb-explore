CREATE TABLE IF NOT EXISTS receipts (
    transaction_hash CHAR(66),
    transaction_index INTEGER NOT NULL,
    block_hash CHAR(66),
    block_number BIGINT NOT NULL,
    cumulative_gas_used BIGINT NOT NULL,
    gas_used BIGINT NOT NULL,
    contract_address CHAR(42),
    root VARCHAR,
    status INTEGER NOT NULL,
    effective_gas_price BIGINT NOT NULL,
    l1_fee BIGINT,
    l1_gas_used BIGINT,
    l1_gas_price BIGINT,
    l1_fee_scalar NUMERIC,

    FOREIGN KEY (transaction_hash) REFERENCES transactions(hash),
    FOREIGN KEY (block_hash) REFERENCES blocks(hash)
)
