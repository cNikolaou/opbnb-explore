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
  highestGasPaidTransactions: HighestGasPaidTransactions[];
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

  // Success rate of transactions
  //   const transactionSuccessRateQuery = `
  //   WITH RecentTransactions AS (
  //     SELECT
  //       r.status
  //     FROM
  //       receipts r
  //     JOIN
  //       blocks b ON r.block_number = b.number
  //     WHERE
  //       b.timestamp > EXTRACT(epoch FROM now() - INTERVAL '2 hours')
  //   )
  //   SELECT
  //     ROUND((COUNT(*) FILTER (WHERE status = 1) * 100.0) / COUNT(*), 2) AS avg_success_rate
  //   FROM
  //     RecentTransactions;
  // `;

  //   const transactionSuccessRateResponse = await client.query(
  //     transactionSuccessRateQuery,
  //   );

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
    highestGasPaidTransactions: highestGasPaidTransactionsResponse.rows,
    highestValueTransactions: highestValueTransactionsResponse.rows,
  });
}
