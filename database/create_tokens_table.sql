    CREATE TABLE IF NOT EXISTS tokens (
        address CHAR(42) PRIMARY KEY,
        symbol VARCHAR(255) NOT NULL,
        name VARCHAR(255) NOT NULL,
        decimals INT,
        total_supply NUMERIC(78, 0)
    )
