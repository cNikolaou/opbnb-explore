import type { NextApiRequest, NextApiResponse } from 'next';

import { pool } from '../../lib/db';

export type HighestGasPaidTransactions = {
  transaction_hash: string;
  from_address: string;
  to_address: string;
  block_number: number;
  gas_used: bigint;
  effective_gas_price: bigint;
  gas_fee: bigint;
};

export type ResponseData = {
  highestGasPaidTransactions: HighestGasPaidTransactions[];
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>,
) {
  const client = await pool.connect();

  // Array of transactions that paid the highest gas fees
  const highestGasPaidTransactionsQuery = `
    SELECT
      t.hash as transaction_hash,
      t.from_address,
      t.to_address,
      t.block_number,
      r.gas_used,
      r.effective_gas_price,
      (r.gas_used * r.effective_gas_price) as gas_fee
    FROM
      transactions t
    JOIN
      blocks b ON t.block_number = b.number
    JOIN
      receipts r ON t.hash = r.transaction_hash
    WHERE
      b.timestamp >  EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours')
    ORDER BY
      gas_fee DESC
    LIMIT 25;
  `;

  const highestGasPaidTransactionsResponse = await client.query(
    highestGasPaidTransactionsQuery,
  );

  client.release();

  res.status(200).json({
    highestGasPaidTransactions: highestGasPaidTransactionsResponse.rows,
  });
}
