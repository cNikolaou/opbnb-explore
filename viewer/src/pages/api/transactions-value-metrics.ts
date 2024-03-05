import type { NextApiRequest, NextApiResponse } from 'next';

import { pool } from '../../lib/db';

export type HighestValueTransactions = {
  transaction_hash: string;
  from_address: string;
  to_address: string;
  block_number: number;
  value: bigint;
};

export type ResponseData = {
  avgTransactionValue: number;
  transactionSuccessRate: number | null;
  highestValueTransactions: HighestValueTransactions[];
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>,
) {
  const client = await pool.connect();

  // Average transaction value
  const avgTransactionValueQuery = `
    SELECT
      AVG(t.value::numeric) AS avg_transaction_value
    FROM
      transactions t
    JOIN
      blocks b ON t.block_number = b.number
    WHERE
      b.timestamp >  EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours');
  `;

  const avgTransactionValueResponse = await client.query(
    avgTransactionValueQuery,
  );

  // Array of transactions that had the highest value
  const highestValueTransactionsQuery = `
    SELECT
      t.hash AS transaction_hash,
      t.block_number,
      t.from_address,
      t.to_address,
      t.value
    FROM
      transactions t
    JOIN
      blocks b ON t.block_number = b.number
    WHERE
      b.timestamp > EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours')
    ORDER BY
      t.value DESC
    LIMIT
      25;
  `;

  const highestValueTransactionsResponse = await client.query(
    highestValueTransactionsQuery,
  );

  client.release();

  res.status(200).json({
    avgTransactionValue:
      avgTransactionValueResponse.rows[0].avg_transaction_value,
    transactionSuccessRate: null,
    highestValueTransactions: highestValueTransactionsResponse.rows,
  });
}
