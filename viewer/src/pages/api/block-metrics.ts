import type { NextApiRequest, NextApiResponse } from 'next';

import { pool } from '../../lib/db';

export type ResponseData = {
  avgBlockTime: number;
  avgTransactionsPerBlock: number;
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>,
) {
  const client = await pool.connect();

  // Average time between blocks
  const avgBlockTimeQuery = `
    WITH BlockDifferences AS (
      SELECT
        number,
        timestamp,
        LEAD(timestamp) OVER (ORDER BY number) - timestamp AS time_diff
      FROM
        blocks
      WHERE
        timestamp > EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours')
    )
    SELECT
      AVG(time_diff) AS avg_block_time
    FROM
      BlockDifferences
    WHERE
      time_diff IS NOT NULL;
  `;

  const avgBlockTimeResult = await client.query(avgBlockTimeQuery);

  // Average number of transactions per block
  const avgTransactionsPerBlockQuery = `
    SELECT
      AVG(transaction_count) as avg_transactions_per_block
    FROM
      blocks
    WHERE
      timestamp > EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours');
  `;

  const avgTransactionsPerBlockResult = await client.query(
    avgTransactionsPerBlockQuery,
  );

  client.release();

  res.status(200).json({
    avgBlockTime: avgBlockTimeResult.rows[0].avg_block_time,
    avgTransactionsPerBlock:
      avgTransactionsPerBlockResult.rows[0].avg_transactions_per_block,
  });
}
