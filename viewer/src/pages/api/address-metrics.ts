import type { NextApiRequest, NextApiResponse } from 'next';

import { pool } from '../../lib/db';

export type MostActiveAddresses = {
  address: string;
  transaction_count: number;
};

export type ResponseData = {
  mostActiveAddresses: MostActiveAddresses[];
};

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse<ResponseData>,
) {
  const client = await pool.connect();

  // Array of the most active addresses
  // TODO: Validate if there are any addresses that refer to contracts and
  // separate them to a different array
  const mostActiveAddressesQuery = `
    WITH RecentTransactions AS (
      SELECT
        t.from_address,
        t.to_address
      FROM
        transactions t
      JOIN
        blocks b ON t.block_number = b.number
      WHERE
        b.timestamp > EXTRACT(EPOCH FROM NOW() - INTERVAL '2 hours')
    ),
    AllAddresses AS (
      SELECT from_address AS address FROM RecentTransactions
      UNION ALL
      SELECT to_address AS address FROM RecentTransactions
    )
    SELECT
      address,
      COUNT(*) AS transaction_count
    FROM
      AllAddresses
    GROUP BY
      address
    ORDER BY
      transaction_count DESC
    LIMIT
      30;
  `;

  const mostActiveAddressesResponse = await client.query(
    mostActiveAddressesQuery,
  );

  client.release();

  res.status(200).json({
    mostActiveAddresses: mostActiveAddressesResponse.rows,
  });
}
