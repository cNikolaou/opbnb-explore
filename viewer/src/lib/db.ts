import { Pool } from 'pg';
import { PrismaClient } from '@prisma/client';

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_DB || 'opbnb',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD,
  port: 5432,
});

const prisma = new PrismaClient();

export { pool, prisma };
