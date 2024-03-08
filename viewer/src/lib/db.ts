import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'opbnb',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'wordpas',
  port: 5432,
});

export { pool };
